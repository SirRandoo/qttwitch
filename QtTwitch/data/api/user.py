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
from typing import Optional, Dict, List, Union

from PySide6 import QtCore, QtGui

from ...enums import BroadcasterTypes, UserTypes

__all__ = ['User']


class User(QtCore.QObject):
    """A user on Twitch."""
    on_banned = QtCore.Signal(object, str, int)  # Channel (User), reason, duration
    """Fired when the user has been banned."""
    on_subscribed = QtCore.Signal(object, bool)  # Channel, resubscription
    """Fired when the user subscribed."""
    on_cheer = QtCore.Signal(int)  # Amount
    """Fired when the user cheered X amount of bits."""
    on_modded = QtCore.Signal()
    """Fired when the user has been modded by the streamer."""
    on_unmodded = QtCore.Signal()
    """Fired when the user has been unmodded by the streamer."""

    def __init__(self, state, **kwargs):
        # Super Call #
        super(User, self).__init__(parent=kwargs.get('parent'))

        # "Private" Attributes #
        self._state = state
        self._login: str = kwargs.get('login')
        self._broadcaster_type: BroadcasterTypes = kwargs.get('broadcaster_type')
        self._description: str = kwargs.get('description')
        self._display_name: str = kwargs.get('display_name', self._login.title())
        self._email: Optional[str] = kwargs.get('email')
        self._id: str = kwargs.get('id')
        self._offline_image_url: QtCore.QUrl = kwargs.get('offline_image_url')
        self._profile_image_url: QtCore.QUrl = kwargs.get('profile_image_url')
        self._type: UserTypes = kwargs.get('type')
        self._view_count: int = kwargs.get('view_count')

        # Chat Attributes
        self._nick_hex: QtGui.QColor = kwargs.get('nick_hex')
        self._emote_sets: List[str] = kwargs.get('emote_sets')

        # Channel Attributes
        self._modded_in: List[str] = []
        self._subscriptions: List[str] = []
        self._badges: Dict[str, List[object]] = {}

        # Aliases #
        self.username: str = self.login

    @property
    def login(self) -> str:
        """The user's username."""
        return self._login

    @property
    def display_name(self) -> str:
        """The user's name with custom capitalization."""
        return self._display_name

    @property
    def broadcaster_type(self) -> BroadcasterTypes:
        """The type of broadcaster the user is."""
        return self._broadcaster_type

    @property
    def description(self) -> str:
        """The user's channel description, or bio."""
        return self._description

    @property
    def email(self) -> Optional[str]:
        """The user's email address."""
        return self._email

    @property
    def id(self) -> str:
        """The user's Twitch ID."""
        return self._id

    @property
    def type(self) -> UserTypes:
        """The type of user this user is."""
        return self._type

    @property
    def view_count(self) -> int:
        """The amount of views the user's channel has obtained."""
        return self._view_count

    @property
    def user_color(self) -> QtGui.QColor:
        """The color hex of the user's name as it appears in chat."""
        return self._nick_hex

    @user_color.setter
    def user_color(self, value: Union[str, QtGui.QColor]):
        if not isinstance(value, QtGui.QColor):
            if not value.startswith("#"):
                value = f'#{value}'

            self._nick_hex = QtGui.QColor(value)

        else:
            self._nick_hex = value

    def is_mod(self, channel: str) -> bool:
        """Returns whether or not the user could be considered a
        moderator in a given channel."""
        return channel.lower() in self._modded_in

    def is_subbed(self, channel: str) -> bool:
        """Returns whether or not the user could be considered a
        subscriber in a given channel."""
        return channel.lower() in self._subscriptions
