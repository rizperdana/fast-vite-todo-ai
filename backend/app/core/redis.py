import decimal
import functools
import hashlib
import json
from collections.abc import Awaitable, Callable
from datetime import date, datetime
from typing import Any, ParamSpec, TypeVar

import redis.asyncio as redis
from loguru import logger
from redis.asyncio import Redis

from app.core.config import settings


# Custom JSON encoder to handle Decimal and other non-serializable types
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle types like Decimal, date, and datetime"""

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, date | datetime):
            return obj.isoformat()
        return super().default(obj)


def json_dumps(obj: Any) -> str:
    """Serialize obj to a JSON formatted string with custom encoder"""
    return json.dumps(obj, cls=CustomJSONEncoder)


def get_redis_connection() -> Redis:
    """Get an async Redis connection using settings"""
    redis_url = "rediss://"
    if settings.REDIS_PASSWORD:
        redis_url += f":{settings.REDIS_PASSWORD}@"
    redis_url += f"{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

    return redis.from_url(redis_url, decode_responses=True)


def hash_dict(data: Any) -> str:
    """Create a stable hash of a dictionary or other data for use as a Redis key"""
    # Handle Pydantic models directly
    if hasattr(data, "model_dump"):
        data_to_serialize = data.model_dump()
    # Handle regular dictionaries
    elif isinstance(data, dict):
        # Convert dictionary items to serializable format
        data_to_serialize = {}
        for key, value in data.items():
            # Handle Pydantic models in dictionary values
            if hasattr(value, "model_dump"):
                data_to_serialize[key] = value.model_dump()
            else:
                data_to_serialize[key] = value
    else:
        # For any other type, use as is
        data_to_serialize = data

    # Sort the dictionary keys to ensure consistent hashing
    serialized = json.dumps(data_to_serialize, sort_keys=True, cls=CustomJSONEncoder)
    return hashlib.sha256(serialized.encode()).hexdigest()


async def check_duplicate(key: str) -> Any:
    """Check if a key exists in Redis (used for duplicate detection)"""
    redis_conn = get_redis_connection()
    try:
        value = await redis_conn.get(key)
        if value:
            return json.loads(value)
        return None
    finally:
        await redis_conn.close()


async def set_key_with_expiry(key: str, value: Any, expiry_hours: int) -> None:
    """Set a key in Redis with expiry time in hours"""
    redis_conn = get_redis_connection()
    try:
        expiry_seconds = expiry_hours * 60 * 60

        # If value is a list, store each item in a Redis list
        if isinstance(value, list) and len(value) > 0:
            # Create a metadata key to store information about the list
            meta_key = f"{key}:meta"
            await redis_conn.set(
                meta_key, json_dumps({"count": len(value), "is_list": True})
            )
            await redis_conn.expire(meta_key, expiry_seconds)

            # Store each item in the list separately
            pipeline = redis_conn.pipeline()
            list_key = f"{key}:items"

            # Delete existing list if present
            pipeline.delete(list_key)

            # Push all items to the list
            for item in value:
                item_json = json_dumps(item)
                pipeline.rpush(list_key, item_json)

            pipeline.expire(list_key, expiry_seconds)
            await pipeline.execute()

            logger.info(f"Stored list with {len(value)} items for key {key}")
        else:
            # For non-list values, store normally
            await redis_conn.set(key, json_dumps(value))
            await redis_conn.expire(key, expiry_seconds)
    except Exception as e:
        logger.error(f"Error in set_key_with_expiry: {e}")
    finally:
        await redis_conn.close()


async def get_key(key: str) -> Any | None:
    """Get a value from Redis by key"""
    redis_conn = get_redis_connection()
    try:
        # First check if this is a list by checking the metadata
        meta_key = f"{key}:meta"
        meta_data = await redis_conn.get(meta_key)

        if meta_data:
            # We have metadata, parse it
            meta = json.loads(meta_data)
            if meta.get("is_list", False):
                # This is a list, retrieve it
                list_key = f"{key}:items"

                # Get all items from the list - ignore mypy issues with redis-py types
                items_json = await redis_conn.lrange(list_key, 0, -1)  # type: ignore
                if not items_json:
                    logger.warning(f"List metadata exists but no items found for {key}")
                    return None

                # Parse each item
                items = []
                for item_json in items_json:
                    items.append(json.loads(item_json))

                logger.info(f"Retrieved list with {len(items)} items for key {key}")
                return items

        # Not a list or no metadata, try regular key
        value = await redis_conn.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Error in get_key: {e}")
        return None
    finally:
        await redis_conn.close()


# Type hints for the decorator
P = ParamSpec("P")
R = TypeVar("R")


def redis_cache(
    prefix: str,
    expiry_hours: int = 24,
    key_builder: Callable[..., str] | None = None,
):
    """
    A decorator for caching function results in Redis.

    Args:
        prefix: A prefix for the Redis key
        expiry_hours: Number of hours to keep the data in cache
        key_builder: Optional function to build a custom key from function arguments

    Example:
        @redis_cache(prefix="users", expiry_hours=12)
        async def get_user(user_id: int):
            # Expensive database operation
            return await db.fetch_user(user_id)
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Generate cache key
            if key_builder:
                cache_key = f"{prefix}:{key_builder(*args, **kwargs)}"
            else:
                # Handle FastAPI function case with a single Pydantic model parameter
                if len(args) > 0 and len(kwargs) == 1 and "request" in kwargs:
                    request = kwargs["request"]
                    try:
                        # Try Pydantic v1 method first (ignoring type error)
                        dict_attr = getattr(request, "dict", None)
                        if callable(dict_attr):
                            model_dict = dict_attr()  # type: ignore
                            cache_key = f"{prefix}:{hash_dict(model_dict)}"
                        # Then try Pydantic v2 method (ignoring type error)
                        elif callable(getattr(request, "model_dump", None)):
                            model_dict = request.model_dump()  # type: ignore
                            cache_key = f"{prefix}:{hash_dict(model_dict)}"
                        else:
                            raise AttributeError("Not a Pydantic model")
                    except (AttributeError, TypeError):
                        # Not a Pydantic model or error converting
                        key_dict = dict(kwargs)
                        # Add positional arguments
                        if args and len(args) > 0:
                            start_idx = (
                                1
                                if args[0].__class__.__name__
                                in ["APIRouter", "Request"]
                                else 0
                            )
                            for i, arg in enumerate(args[start_idx:], start=start_idx):
                                key_dict[f"arg_{i}"] = arg
                        cache_key = f"{prefix}:{hash_dict(key_dict)}"
                else:
                    # Create a dictionary from all keyword arguments
                    key_dict = dict(kwargs)

                    # Add positional arguments except 'self' and 'cls'
                    if args and len(args) > 0:
                        # Skip first arg if it's self or cls
                        start_idx = (
                            1
                            if args[0].__class__.__name__ in ["APIRouter", "Request"]
                            else 0
                        )
                        for i, arg in enumerate(args[start_idx:], start=start_idx):
                            key_dict[f"arg_{i}"] = arg

                    cache_key = f"{prefix}:{hash_dict(key_dict)}"

            # Try to get from cache
            try:
                cached_data = await get_key(cache_key)
                if cached_data is not None:
                    logger.info(f"Cache hit for {cache_key}")
                    return cached_data
            except Exception as e:
                logger.error(f"Error retrieving from cache: {str(e)}")

            # Cache miss, call the original function
            logger.info(f"Cache miss for {cache_key}, calling function")
            result = await func(*args, **kwargs)

            # Store in cache if result is not None
            if result is not None:
                try:
                    await set_key_with_expiry(
                        cache_key, result, expiry_hours=expiry_hours
                    )
                except Exception as e:
                    logger.error(f"Cache storage error: {str(e)}")

            return result

        return wrapper

    return decorator
