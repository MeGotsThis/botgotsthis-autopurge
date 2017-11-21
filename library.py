import json
from typing import Dict, Optional

import aioodbc.cursor

from lib.cache import CacheStore
from lib.database import DatabaseMain


def _redisKey(broadcaster: str) -> str:
    return f'twitch:{broadcaster}:auto-purge'


async def get_auto_purges(broadcaster: str,
                          data: CacheStore) -> Dict[str, bool]:
    purges: Dict[str, bool]
    key: str = _redisKey(broadcaster)
    val: Optional[str] = await data.redis.get(key)
    if val is None:
        purges = await get_auto_purges_db(broadcaster)
        await data.redis.setex(key, 3600, json.dumps(purges))
    else:
        purges = json.loads(val)
    return purges


async def get_auto_purges_db(broadcaster: str) -> Dict[str, bool]:
    db: DatabaseMain
    cursor: aioodbc.cursor.Cursor
    purges: Dict[str, bool] = {}
    async with DatabaseMain.acquire() as db, await db.cursor() as cursor:
        query: str = '''
SELECT twitchUser, stopcommands FROM auto_purge WHERE broadcaster=?
'''
        user: str
        stop: bool
        async for user, stop in await cursor.execute(query, (broadcaster,)):
            purges[user] = stop
        return purges


async def reset_auto_purges(broadcaster: str, data: CacheStore) -> None:
    await data.redis.delete(_redisKey(broadcaster))
