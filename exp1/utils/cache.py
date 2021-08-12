import json
from typing import Union

from cachetools.lru import LRUCache
from redis import Redis, exceptions
from redisbloom.client import Client as RedisBloom

from utils.dgraph import get_client


class LayeredCache(object):
    """
    Multi-Layered key value store.
    Layer 1: In Memory LRU Key Value Map
    Layer 2: Redis Key Value Store
    This cache type is great for things that can exist in memory, either
    locally in the LRU layer or in the redis layer.
    """

    def __init__(self, node_name: str, lru_size: int):
        """
        Initialize the first two layers of a multi-layered cache

        :param node_name:
        :param lru_size:
        """
        super(LayeredCache, self).__init__()

        # Track the name of the node Type. This should be whatever
        # unique identifier can be used in dgraph queries.
        self.node_name = node_name

        # Initialize a Least Recently Used in-memory cache
        # with a maximum number of elements.
        # layer 1
        self.lru_local_cache = LRUCache(maxsize=lru_size)

        # Initialize a redis client.
        # layer 2 cache
        self.redis = Redis("localhost")

        # This should be set to True if we should add a timeout to the
        # redis key value store values.
        self.set_timeout = False

    def _get_key(self, key: str) -> str:
        """
        Get the unique key that is used at each cached layer.
        :param key:
        :return:
        """
        return f"{self.node_name}-{key}"

    def __setitem__(self, key: str, value: str):
        """
        Store a key value pair in each cache layer.
        :param key:
        :param value:
        :return:
        """

        # Store in layer 1 local LRU cache
        self.lru_local_cache[self._get_key(key)] = value

        # Store in layer 2 redis cache
        # If we want to have key value pairs timeout in redis, use setex with 5
        # minutes before until timeout
        if self.set_timeout:
            timeout = 300
            self.redis.setex(self._get_key(key), timeout, value)
        else:
            self.redis.set(self._get_key(key), value)

    def __contains__(self, key: str) -> bool:
        """
        Check to see if key is in a layer of the cache. We will start at
        layer 1 and go walk through each layer until we find a result.
        We will update previous layers if we cache miss.
        We'll return True if the key was found at a layer, False if we
        cache miss.
        :param key:
        :return:
        """

        # Check the layer 1 local LRU cache
        local_result = self.lru_local_cache.get(self._get_key(key), None)
        if local_result is not None:
            return True

        # Check the layer 2 redis cache
        redis_result = self.redis.get(self._get_key(key))
        if redis_result is not None:
            # Update the each layer with the value
            self[key] = redis_result.decode()
            return True

        # Cache miss, return False
        return False

    def __getitem__(self, key: str) -> Union[str, None]:
        """
        Check each layer iteratively for the key specified. If we find the result
        at a given layer, we update previous layers with the result.
        If the result was not found, return None.
        :param key:
        :return:
        """

        # Check the layer 1 local LRU cache
        local_result = self.lru_local_cache.get(self._get_key(key), None)
        if local_result is not None:
            return local_result

        # Check the layer 2 redis cache
        redis_result = self.redis.get(self._get_key(key))
        if redis_result is not None:
            # Update the each layer with the value
            self[key] = redis_result.decode()
            return redis_result.decode()

        # Cache miss, return None
        return None

    def close(self):
        """
        Close any outstanding connections.
        :return:
        """
        self.redis.close()


class FullLayeredCache(LayeredCache):
    """
    Multi-Layered key value store with bloom filter and dgraph.
    Layer 1: In Memory LRU Key Value Map
    Layer 2: Redis Key Value Store
    Layer 3: Bloom filter
    Layer 4: DGraph
    The primary difference between this class and the LayeredCache class is that this
    one includes the bloom filter and DGraph.
    """

    def __init__(self, node_name: str, lru_size: int, p=1.0e-6, n=1000000):
        """
        Initialize last two layers of cache
        :param node_name:
        :param lru_size:
        """
        super(FullLayeredCache, self).__init__(node_name, lru_size)

        # Set to true so we add a timeout to layer 2 redis key value stores
        self.set_timeout = True

        # Create the bloom filter client object
        self.bloom = RedisBloom(port=6378)

        # Create a dgraph client, stub, and transaction
        self.dgraph, self.stub = get_client()
        self.txn = self.dgraph.txn()

        # Initialize the bloom filter (if it doesnt already exist)
        try:
            self.bloom.bfInfo(node_name)
        except exceptions.ResponseError:
            self.bloom.bfCreate(node_name, p, n)

    def __contains__(self, key: str) -> bool:
        """
        Check to see if key is in a layer of the cache. We will start at
        layer 1 and go walk through each layer until we find a result.
        We will update previous layers if we cache miss.
        We'll return True if the key was found at a layer, False if we
        cache miss.
        :param key:
        :return:
        """

        # Check layer 1 and 2
        if super(FullLayeredCache, self).__contains__(key):
            return True

        # Check the layer 3 bloom filter
        exists_in_bloom = self.bloom.bfExists(self.node_name, self._get_key(key))
        if exists_in_bloom == 1:
            # Unfortunately, we can't store the actual value in the bloom filter.
            # For this, we can't update previous layers with the value for this key.
            return True

        # All else has failed, we must now check dgraph. This is super super slow.
        query = """query all($a: string) { all(func: eq(%s, $a)) { uid } }""" % self.node_name
        dgraph_result = self.txn.query(query, variables={"$a": str(key)})
        thing = json.loads(dgraph_result.json)
        if len(thing["all"]) > 0:
            # Update previous layers
            self[key] = thing["all"][0]["uid"]
            return True

        # Cache miss, return False
        return False

    def __getitem__(self, key: str) -> Union[str, None]:
        """
        Check each layer iteratively for the key specified. If we find the result
        at a given layer, we update previous layers with the result.
        If the result was not found, return None.
        :param key:
        :return:
        """
        # Check layer 1 and 2
        item = super(FullLayeredCache, self).__getitem__(key)
        if item is not None:
            return item

        # Check layer 3 bloom filter
        exists_in_bloom = self.bloom.bfExists(self.node_name, self._get_key(key))
        if exists_in_bloom == 1:
            return True

        # All else has failed, we must now check dgraph. This is super super slow.
        query = """query all($a: string) { all(func: eq(%s, $a)) { uid } }""" % self.node_name
        dgraph_result = self.txn.query(query, variables={"$a": str(key)})
        thing = json.loads(dgraph_result.json)
        if len(thing["all"]) > 0:
            # Update previous layers
            self[key] = thing["all"][0]["uid"]
            return thing["all"][0]["uid"]

        # Cache miss, return None
        return None

    def close(self):
        """
        Close all outstanding connections
        :return:
        """

        # Close the layer 2 redis connection
        super(FullLayeredCache, self).close()

        # Close layer 3 bloom filter connection
        self.bloom.close()

        # Close layer 4 dgraph connections
        self.stub.close()