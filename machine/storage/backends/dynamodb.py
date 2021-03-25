import logging
import datetime
import calendar
import pickle
import codecs
import boto3
import botocore
from machine.storage.backends.base import MachineBaseStorage

logger = logging.getLogger(__name__)


class DynamoDBStorage(MachineBaseStorage):
    """
        A storage plugin to allow native slack-machine storage
        into AWS DynamoDB

        Configuration of the connection to AWS itself is done via
        standard environment variables or pre-written configuration
        files, such as ~/.aws/{config}

        For local testing, the endpoint URL can be modified using
        slack-machine setting `DYNAMODB_ENDPOINT_URL`

        If `DYNAMODB_CREATE_TABLE` is set within slack-machine
        settings, this driver will create the table in AWS automatically

        Additionally, if you need a DynamoDB client to be customized,
        a custom client can be passed in with the `DYNAMODB_CLIENT`
        slack-machine setting

        Data in DynamoDB is stored as a pickled base64 string to 
        avoid complications in setting and fetching (bytes)
    """

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
        """
            Given a slack-machine lookup key, generate a prefixed-key
            to be used in the DynamoDB table lookup

            :param key: the SM key to prefix
        """
        return '{}:{}'.format(self._key_prefix, key)

    def has(self, key):
        """
            Check if the key exists in DynamoDB

            :param key: the SM key to check
            :return: ``True/False`` whether the key exists in DynamoDB
            :raises ClientError: if the client was unable to communicate with DynamoDB
        """
        try:
            r = self._table.get_item(Key={'sm-key': self._prefix(key)})
            return True if 'Item' in r else False
        except botocore.exceptions.ClientError as e:
            logger.error('Unable to get item[{}]'.format(self._prefix(key)))
            raise e

    def get(self, key):
        """
            Retrieve item data by key

            :param key: the SM key to fetch against
            :return: the raw data for the provided key, as (byte)string. Returns ``None`` when
                the key is unknown or the data has expired
            :raises ClientError: if the client was unable to communicate with DynamoDB
        """
        try:
            r = self._table.get_item(Key={'sm-key': self._prefix(key)})
            if 'Item' in r:
                v = r['Item']['sm-value']
                return pickle.loads(codecs.decode(v.encode(), 'base64'))
            else:
                return None
        except botocore.exceptions.ClientError as e:
            logger.error('Unable to get item[{}]'.format(self._prefix(key)))
            raise e

    def set(self, key, value, expires=None):
        """
            Store item data by key

            :param key: the key under which to store the data
            :param value: data as (byte)string
            :param expires: optional expiration time in seconds, after which the
                data should not be returned any more
            :raises ClientError: if the client was unable to communicate with DynamoDB
        """
        item = {
            'sm-key': self._prefix(key),
            'sm-value': codecs.encode(pickle.dumps(value), 'base64').decode()
        }
        if expires:
            ttl = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires)
            item['sm-expire'] = calendar.timegm(ttl.timetuple())

        try:
            self._table.put_item(Item=item)
        except botocore.exceptions.ClientError as e:
            logger.error('Unable to set item[{}]'.format(self._prefix(key)))
            raise e

    def delete(self, key):
        """
            Delete item data by key

            :param key: key for which to delete the data
            :raises ClientError: if the client was unable to communicate with DynamoDB
        """
        try:
            self._table.delete_item(Key={'sm-key': self._prefix(key)})
        except botocore.exceptions.ClientError as e:
            logger.error('Unable to delete item[{}]'.format(self._prefix(key)))
            raise e

    def size(self):
        """
            Calculate the total size of the storage

            :return: total size of storage in bytes (integer)
        """
        t = self._table.meta.client.describe_table(TableName=self._table_name)
        return t['Table']['TableSizeBytes']
