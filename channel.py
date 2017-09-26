import aioodbc.cursor  # noqa: F401

from typing import Optional, Tuple  # noqa: F401

from lib.data import ChatCommandArgs
from lib.helper import timeout
from lib.helper.chat import feature, min_args
from lib.helper.chat import permission
from lib.helper import parser


@feature('autopurge')
@permission('bannable')
@permission('chatModerator')
async def filterAutoPurge(args: ChatCommandArgs) -> bool:
    cursor: aioodbc.cursor.Cursor
    async with await args.database.cursor() as cursor:
        query: str = '''
SELECT stopcommands FROM auto_purge WHERE broadcaster=? AND twitchUser=?
'''
        await cursor.execute(query, (args.chat.channel, args.nick.lower()))
        row: Optional[Tuple[bool]] = await cursor.fetchone()
        if row is not None:
            message: str = f'.timeout {args.nick} 1'
            args.chat.send(message)
            await timeout.record_timeout(args.chat, args.nick, message,
                                         str(args.message), 'autopurge')
            if row[0] and not args.permissions.owner:
                return True
    return False


@feature('autopurge')
@min_args(2)
@permission('broadcaster')
async def commandSetAutoPurge(args: ChatCommandArgs) -> bool:
    twitchUser: str = args.message.lower[1]
    nick: str = args.message[1]
    cursor: aioodbc.cursor.Cursor
    async with await args.database.cursor() as cursor:
        query: str = '''\
SELECT 1 FROM auto_purge WHERE broadcaster=? AND twitchUser=?
'''
        await cursor.execute(query, (args.chat.channel, twitchUser))
        row: Optional[Tuple[int]] = await cursor.fetchone()
        if row is None:
            value: bool = False
            if len(args.message) >= 3:
                response: parser.Response
                value = bool(parser.get_response(args.message.lower[2],
                                                 default=parser.Yes))
            query = '''
INSERT INTO auto_purge (broadcaster, twitchUser, stopcommands) VALUES (?, ?, ?)
'''
            await cursor.execute(query, (args.chat.channel, twitchUser, value))
            args.chat.send(f'Enabled Auto-Purge on {nick}')
        else:
            query = '''
DELETE FROM auto_purge WHERE broadcaster=? AND twitchUser=?
'''
            await cursor.execute(query, (args.chat.channel, twitchUser))
            args.chat.send(f'Disabled Auto-Purge on {nick}')
        await args.database.commit()
    return True
