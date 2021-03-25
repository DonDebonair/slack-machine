import logging
import datetime
import calendar
import boto3
import botocore
from machine.storage.backends.base import MachineBaseStorage

logger = logging.getLogger(__name__)


class DynamoDBStorage(MachineBaseStorage):
    def __init__(self, settings):
        super().__init__(settings)
        args = {}
        if 'DYNAMODB_ENDPOINT_URL' in settings:
            args['endpoint_url'] = settings['DYNAMODB_ENDPOINT_URL']
        self._key_prefix = settings.get('DYNAMODB_KEY_PREFIX', 'SM')
        self._table_name = settings.get('DYNAMODB_TABLE_NAME', 'slack-machine-state')

        if 'DYNAMODB_CLIENT' in settings:
            self._db = settings['DYNAMODB_CLIENT']
        else:
            db = boto3.resource('dynamodb', **args)
            self._db = db

        create_table = settings.get('DYNAMODB_CREATE_TABLE', False)
        if create_table:
            try:
                self._table = self._db.create_table(
                    TableName=self._table_name,
                    KeySchema=[
                        {'AttributeName': 'sm-key', 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'sm-key', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                self._table.meta.client.get_waiter('table_exists').wait(TableName=self._table_name)
                ttl = {'Enabled': True, 'AttributeName': 'sm-expire'}
                self._table.meta.client.update_time_to_live(
                    TableName=self._table_name, TimeToLiveSpecification=ttl)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'ResourceInUseException':
                    logger.info(
                        'DynamoDB table[{}] exists, skipping creation'.format(self._table_name))
                else:
                    raise e

        self._table = self._db.Table(self._table_name)

    def _prefix(self, key):
        return '{}:{}'.format(self._key_prefix, key)

    def has(self, key):
        try:
            r = self._table.get_item(Key={'sm-key': self._prefix(key)})
            return True if 'Item' in r else False
        except botocore.exceptions.ClientError as e:
            logger.error('Unable to get item[{}]'.format(self._prefix(key)))
            raise e

    def get(self, key):
        try:
            r = self._table.get_item(Key={'sm-key': self._prefix(key)})
            if 'Item' in r:
                return r['Item']['sm-value']
            else:
                return None
        except botocore.exceptions.ClientError as e:
            logger.error('Unable to get item[{}]'.format(self._prefix(key)))
            raise e

    def set(self, key, value, expires=None):
        item = {
            'sm-key': self._prefix(key),
            'sm-value': value
        }
        if expires:
            ttl = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires)
            item['sm-expire'] = calendar.timegm(ttl.timetuple())

        try:
            self._table.put_item(Item=item)
        except botocore.exceptions.ClientError as e:
            logger.error('Unable to set item[{}]'.format(self._prefix(key)))

    def delete(self, key):
        try:
            self._table.delete_item(Key={'sm-key': self._prefix(key)})
        except botocore.exceptions.ClientError as e:
            logger.error('Unable to delete item[{}]'.format(self._prefix(key)))

    def size(self):
        t = self._table.meta.client.describe_table(TableName=self._table_name)
        return t['Table']['TableSizeBytes']
