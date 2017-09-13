class MachineBaseStorage:
    """Base class for storage backends

    Extending classes should implement the five methods in this base class. Slack Machine takes
    care of a lot of details regarding the persistent storage of data. So storage backends
    **do not** have to deal with the following, because Slack Machine takes care of these:

    - Serialization/Deserialization of data
    - Namespacing of keys (so data stored by different plugins doesn't clash)
    """
    def __init__(self, settings):
        self.settings = settings

    def get(self, key):
        """Retrieve data by key

        :param key: key for which to retrieve data
        :return: the raw data for the provided key, as (byte)string. Should return ``None`` when
            the key is unknown or the data has expired.
        """
        raise NotImplementedError

    def set(self, key, value, expires=None):
        """Store data by key

        :param key: the key under which to store the data
        :param value: data as (byte)string
        :param expires: optional expiration time in seconds, after which the data should not be
            returned any more.
        """
        raise NotImplementedError

    def delete(self, key):
        """Delete data by key

        :param key: key for which to delete the data
        """
        raise NotImplementedError

    def has(self, key):
        """Check if the key exists

        :param key: key to check
        :return: ``True/False`` wether the key exists
        """
        raise NotImplementedError

    def size(self):
        """Calculate the total size of the storage

        :return: total size of storage in bytes (integer)
        """
        raise NotImplementedError
