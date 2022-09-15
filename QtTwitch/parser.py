"""
The MIT License (MIT)

Copyright (c) 2021 SirRandoo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import inspect
import logging
import re
from typing import TYPE_CHECKING, Union

from QtTwitch import dataclasses, enums


if TYPE_CHECKING:
    from .client import Client

__all__ = ['Parser']

logger = logging.getLogger(__name__)


class Parser:
    """A class to house the IRC message parsers."""
    PATTERN = re.compile(r'(?:@(?P<tags>.*?) )?:(?:(?P<prefix>.*?) ?) (?P<command>\w+|\d+) (?P<params>.*)')
    SYSTEM_ID = 'tmi.twitch.tv'
    LOOKUP = {
        1: 'welcome',
        2: 'your_host',
        3: 'created',
        4: 'my_info',

        375: 'motd_start',
        372: 'motd',
        376: 'motd_end',

        353: 'name_reply',
        366: 'name_end',

        421: 'unknown_command'
    }

    def __init__(self, state: 'Client'):
        self._state = state

    # noinspection PyTypeChecker
    @classmethod
    def parse(cls, message: str) -> Union[dataclasses.PrivateMessage, dataclasses.SystemMessage]:
        """Parses a raw IRC message into a message dataclass."""
        match = Parser.PATTERN.match(message)

        if not match:
            logger.warning(f'Could not parse {message}')
            raise ValueError

        groups = match.groupdict()
        c = groups.copy()
        tags = {}

        if 'tags' in c:
            cls._extract_tags(c, tags)

        c['tags'] = tags

        # Pass the message on to its dedicated method.
        for name, instance in inspect.getmembers(Parser):
            # Ensure we're only getting parser methods
            if not name.startswith('parse_'):
                continue

            # Ensure we only get methods
            if not inspect.isfunction(instance):
                continue

            # Ensure the command isn't a response code
            if groups['command'].isdigit():
                # noinspection PyTypeChecker
                groups['command'] = int(groups['command'])

            # Ensure the parser is the one we're looking for
            if name != f'parse_{groups["command"]}':
                continue

            return instance(groups)

        raise ValueError(f'No parser found for command {groups["command"]}')

    @classmethod
    def _extract_tags(cls, c, tags):
        for segment in c['tags'].split(';'):
            parts = segment.split('=')

            try:
                tags[parts[0]] = parts[1]

            except IndexError:
                tags[parts[0]] = ""

    @classmethod
    def parse_welcome(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts a "welcome" message into a SystemMessage."""
        message = data['params'].split(' ', 1)[-1]

        return dataclasses.SystemMessage(
            enums.SysMessageTypes.GENERIC,
            data['prefix'],
            message[1:],
            enums.IrcResponses.WELCOME
        )

    @classmethod
    def parse_your_host(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts a "your host" message into a SystemMessage."""
        message = data['params'].split(' ', 1)[-1]

        return dataclasses.SystemMessage(
            enums.SysMessageTypes.GENERIC,
            Parser.SYSTEM_ID,
            message[1:],
            enums.IrcResponses.YOUR_HOST
        )

    @classmethod
    def parse_created(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts a "created" message into a SystemMessage."""
        message = data['params'].split(' ', 1)[-1]

        return dataclasses.SystemMessage(
            enums.SysMessageTypes.GENERIC,
            Parser.SYSTEM_ID,
            message[1:],
            enums.IrcResponses.CREATED
        )

    @classmethod
    def parse_my_info(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts a "my info" message into a SystemMessage."""
        user, message = data['params'].split(' ', 1)

        return dataclasses.SystemMessage(
            enums.SysMessageTypes.GENERIC,
            user,
            '',
            enums.IrcResponses.MY_INFO
        )

    @classmethod
    def parse_motd_start(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts a "motd start" message into a SystemMessage."""
        message = data['params'].split(' ', 1)[-1]

        return dataclasses.SystemMessage(
            enums.SysMessageTypes.GENERIC,
            Parser.SYSTEM_ID,
            message[1:],
            enums.IrcResponses.MOTD_START
        )

    @classmethod
    def parse_motd(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts a "motd" message into a SystemMessage."""
        motd = data['params'].split(' ')[-1]

        return dataclasses.SystemMessage(
            enums.SysMessageTypes.GENERIC,
            Parser.SYSTEM_ID,
            motd[1:],
            enums.IrcResponses.MOTD
        )

    @classmethod
    def parse_motd_end(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts a "message of the day end" message into a SystemMessage."""
        end = data['params'].split(' ', 1)[-1]

        return dataclasses.SystemMessage(
            enums.SysMessageTypes.GENERIC,
            Parser.SYSTEM_ID,
            end[1:],
            enums.IrcResponses.MOTD_END
        )

    @classmethod
    def parse_name_reply(cls, data: dict) -> dataclasses.NamesMessage:
        """Converts a "name reply" message into a SystemMessage."""
        us, _, channel, names = data['params'].split(' ', 3)

        return dataclasses.NamesMessage(channel, names.split(' '))

    @classmethod
    def parse_name_end(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts a "name end" message into a SystemMessage."""
        us, channel, message = data['params'].split(' ', 2)

        return dataclasses.SystemMessage(
            enums.SysMessageTypes.GENERIC,
            channel[1:],
            message[1:],
            enums.IrcResponses.NAME_END
        )

    @classmethod
    def parse_unknown_command(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts an "unknown command" message into a SystemMessage."""
        message = data['params'].split(' ', 2)[-1]

        return dataclasses.SystemMessage(
            enums.SysMessageTypes.GENERIC,
            Parser.SYSTEM_ID,
            message[1:],
            enums.IrcResponses.UNKNOWN_COMMAND
        )

    @classmethod
    def parse_mode(cls, data: dict) -> dataclasses.ModeMessage:
        """Converts a "mode" message into a ModeMessage."""
        channel, status, user = data['params'].split(' ')

        return dataclasses.ModeMessage(channel[1:], user, status[0] == '+')

    @classmethod
    def parse_join(cls, data: dict) -> dataclasses.JoinMessage:
        """Converts a "join" message into a JoinMessage."""
        user, _ = data['prefix'].split('!', 1)

        return dataclasses.JoinMessage(data['params'][1:], user)

    @classmethod
    def parse_part(cls, data: dict) -> dataclasses.PartMessage:
        """Converts a "part" message into a PartMessage."""
        user, _ = data['prefix'].split('!', 1)

        return dataclasses.PartMessage(data['params'][1:], user)

    @classmethod
    def parse_hosttarget(cls, data: dict) -> dataclasses.HostMessage:
        """Converts a "hosttarget" message into a HostMessage."""
        channel, target, *_ = data['params'].split(' ')

        return dataclasses.HostMessage(channel[1:], target[1:])

    @classmethod
    def parse_cap(cls, data: dict) -> dataclasses.SystemMessage:
        """Converts a "cap" message into a SystemMessage."""
        return dataclasses.SystemMessage(enums.SysMessageTypes.CAP, data['prefix'], data['params'][2:])

    @classmethod
    def parse_clearchat(cls, data: dict) -> dataclasses.ClearChatMessage:
        """Converts a "clearchat" message into a ClearChatMessage."""
        return dataclasses.ClearChatMessage(*data['params'].split(' '))

    @classmethod
    def parse_clearmsg(cls, data: dict) -> dataclasses.ClearMsgMessage:
        """Converts a "clearmsg" message into a ClearMsgMessage."""
        return dataclasses.ClearMsgMessage(data['params'].split(' ')[0], data['tags'].get('target-msg-id'))

    @classmethod
    def parse_globaluserstate(cls, data: dict) -> object:
        """"""
