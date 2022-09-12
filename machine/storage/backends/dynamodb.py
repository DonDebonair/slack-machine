from __future__ import annotations

import calendar
import base64
import datetime
import logging
import typing
from contextlib import AsyncExitStack
from typing import Mapping, Any, cast

import aioboto3
from botocore.exceptions import ClientError

if typing.TYPE_CHECKING:
    from types_aiobotocore_dynamodb.service_resource import DynamoDBServiceResource, Table


from machine.storage.backends.base import MachineBaseStorage

logger = logging.getLogger(__name__)
DEFAULT_ENCODING = "utf-8"


class DynamoDBStorage(MachineBaseStorage):
    """
    A storage plugin to allow native slack-machine storage
    into AWS DynamoDB

    Configuration of the connection to AWS itself is done via
    standard environment variables or pre-written configuration
    files, such as ~/.aws/config and ~/.aws/credentials.

    For local testing, the endpoint URL can be modified using
    slack-machine setting `DYNAMODB_ENDPOINT_URL`

    If `DYNAMODB_CREATE_TABLE` is set within slack-machine
    settings, this driver will create the table in AWS automatically

    Additionally, if you need a DynamoDB client to be customized,
    a custom client can be passed in with the `DYNAMODB_CLIENT`
    slack-machine setting

    Data in DynamoDB is stored as a base64 string to
    avoid complications in setting and fetching (bytes)
    """

    _table: Table
    _db: DynamoDBServiceResource
    _context_stack: AsyncExitStack

    async def close(self) -> None:
        await self._context_stack.aclose()

    def __init__(self, settings: Mapping[str, Any]):
        super().__init__(settings)

        self._key_prefix = settings.get("DYNAMODB_KEY_PREFIX", "SM")
        self._table_name = settings.get("DYNAMODB_TABLE_NAME", "slack-machine-state")

    async def init(self) -> None:
        self._context_stack = AsyncExitStack()
        session = aioboto3.Session()
        args = {}
        if "DYNAMODB_ENDPOINT_URL" in self.settings:
            args["endpoint_url"] = self.settings["DYNAMODB_ENDPOINT_URL"]

        if "DYNAMODB_CLIENT" in self.settings:
            self._db = self.settings["DYNAMODB_CLIENT"]
        else:
            self._db = await self._context_stack.enter_async_context(session.resource("dynamodb", **args))

        create_table = self.settings.get("DYNAMODB_CREATE_TABLE", False)
        if create_table:
            try:
                await self._db.create_table(
                    TableName=self._table_name,
                    KeySchema=[{"AttributeName": "sm-key", "KeyType": "HASH"}],
                    AttributeDefinitions=[{"AttributeName": "sm-key", "AttributeType": "S"}],
                    BillingMode="PAY_PER_REQUEST",
                )
                self._table = await self._db.Table(self._table_name)
                await self._table.wait_until_exists()
                ttl = {"Enabled": True, "AttributeName": "sm-expire"}
                await self._table.meta.client.update_time_to_live(
                    TableName=self._table_name, TimeToLiveSpecification=ttl
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceInUseException":
                    logger.info("DynamoDB table[%s] exists, skipping creation", self._table_name)
                else:
                    raise e
        self._table = await self._db.Table(self._table_name)

    def _prefix(self, key: str) -> str:
        """
        Given a slack-machine lookup key, generate a prefixed-key
        to be used in the DynamoDB table lookup

        :param key: the SM key to prefix
        """
        return f"{self._key_prefix}:{key}"

    async def has(self, key: str) -> bool:
        """
        Check if the key exists in DynamoDB

        :param key: the SM key to check
        :return: ``True/False`` whether the key exists in DynamoDB
        :raises ClientError: if the client was unable to communicate with DynamoDB
        """
        try:
            r = await self._table.get_item(Key={"sm-key": self._prefix(key)})
            return "Item" in r
        except ClientError as e:
            logger.error("Unable to get item[%s]", self._prefix(key))
            raise e

    async def get(self, key: str) -> bytes | None:
        """
        Retrieve item data by key

        :param key: the SM key to fetch against
        :return: the raw data for the provided key, as (byte)string. Returns ``None`` when
            the key is unknown or the data has expired
        :raises ClientError: if the client was unable to communicate with DynamoDB
        """
        try:
            r = await self._table.get_item(Key={"sm-key": self._prefix(key)})
            if "Item" in r:
                v = r["Item"]["sm-value"]
                casted_v = cast(bytes, v)
                return base64.b64decode(casted_v)
            else:
                return None
        except ClientError as e:
            logger.error("Unable to get item[%s]", self._prefix(key))
            raise e

    async def set(self, key: str, value: bytes, expires: int | None = None) -> None:
        """
        Store item data by key

        :param key: the key under which to store the data
        :param value: data as (byte)string
        :param expires: optional expiration time in seconds, after which the
            data should not be returned any more
        :raises ClientError: if the client was unable to communicate with DynamoDB
        """
        item: dict[str, Any] = {
            "sm-key": self._prefix(key),
            "sm-value": base64.b64encode(value).decode(DEFAULT_ENCODING),
        }
        if expires:
            ttl = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires)
            item["sm-expire"] = calendar.timegm(ttl.timetuple())

        try:
            await self._table.put_item(Item=item)
        except ClientError as e:
            logger.error("Unable to set item[%s]", self._prefix(key))
            raise e

    async def delete(self, key: str) -> None:
        """
        Delete item data by key

        :param key: key for which to delete the data
        :raises ClientError: if the client was unable to communicate with DynamoDB
        """
        try:
            await self._table.delete_item(Key={"sm-key": self._prefix(key)})
        except ClientError as e:
            logger.error("Unable to delete item[%s]", self._prefix(key))
            raise e

    async def size(self) -> int:
        """
        Calculate the total size of the storage

        :return: total size of storage in bytes (integer)
        """
        t = await self._table.meta.client.describe_table(TableName=self._table_name)
        return t["Table"]["TableSizeBytes"]
