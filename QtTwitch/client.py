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
import logging
from typing import Optional

from PySide6 import QtCore, QtNetwork

from QtUtilities import requests
from .gateway import Gateway
from .http import Http

__all__ = ['ClientBuilder', 'Client']

logger = logging.getLogger(__name__)


class Client(QtCore.QObject):
    """Represents a client connection that connects to Twitch."""
    # Irc signals
    on_message = QtCore.Signal(object)
    """Emitted when the client receives a standard chat message in any connected
    channel.  The object emitted will be a variant of the PrivateMessage class."""
    on_user_join = QtCore.Signal(object)
    """Emitted when a user joins a channel the client is connected to.  Given
    the nature of Twitch's irc servers, this signal will be emitted once for
    every viewer that's new to the channel when the client checks a channel's
    current chatter list.  The object emitted will be a variant of the User
    class."""
    on_user_leave = QtCore.Signal(object)
    """Emitted when a user leaves a channel the client is connected to.  Given
    the nature of Twitch's irc servers, this signal will be emitted once for
    every viewer that's left the channel when the client checks a channel's
    current chatter list.  The object emitted will be a variant of the User
    class."""
    on_channel_join = QtCore.Signal(object)
    """Emitted when the client successfully connects to a channel's chat room.
    The object emitted will be a variant of the Channel class."""
    on_channel_leave = QtCore.Signal(object)
    """Emitted when the client successfully leaves a channel's chat room.  The
    object emitted will be a variant of the Channel class."""
    on_user_banned = QtCore.Signal(object, int)
    """Emitted when the client receives a ban notice in a channel.  The object
    emitted will be a variant of the User class, and the integer emitted will
    indicate how long the user will be banned for.  The integer emitted is
    classified as the `duration` of the ban, in seconds.

    A duration of -1 indicates the user was banned without a duration.
    A duration of above 0 indicates the user was banned with a duration."""
    on_user_unbanned = QtCore.Signal(object)
    """Emitted when the client receives an unban notice in a channel.  The
    object emitted will be a variant of the User class."""
    on_chat_clear = QtCore.Signal(object)
    """Emitted when the client receives a chat clear notice."""
    on_message_deleted: QtCore.Signal(object)
    """Emitted when the client receives a message deletion notice.  The object
    emitted will be a variant of the PrivateMessage class."""
    on_whisper = QtCore.Signal(object)
    """Emitted when the client receives a whisper message.  The object emitted
    will be a variant of the WhisperMessage class."""
    on_channel_host = QtCore.Signal(object)
    """Emitted when the client receives a host target message.  The object
    emitted will be a variant of the Channel class."""
    on_subscribe = QtCore.Signal(object, int)
    """Emitted when the client receives a subscribe notice.  The object emitted
    will be a variant of the User class."""

    # Api signals
    on_follow = QtCore.Signal(object)
    """Emitted when the client detects a new follower.  The object emitted will
    be a variant of the User class."""

    def __init__(self, parent: QtCore.QObject = None):
        """
        :param parent:    The QObject instance to act as this instance's parent
                          in Qt's parent-child relationship. system."""
        super().__init__(parent=parent)

        self.gateway: Optional[Gateway] = None
        self.http: Optional[Http] = None
        self.pubsub: Optional[object] = None


class ClientBuilder:
    """Represents a builder that eases constructing a new Client object."""

    def __init__(self, client_id: str):
        """
        :param client_id: The client id to use for api requests.
        """
        self._factory: Optional[requests.Factory] = None
        self._manager: Optional[QtNetwork.QNetworkAccessManager] = None
        self._token: Optional[str] = None
        self._parent: Optional[QtCore.QObject] = None

        self._client_id: str = client_id
        self._result: Client = Client.__new__(Client)

    def token(self, token: str) -> 'ClientBuilder':
        """The OAuth2 token to use for authentication purposes.

        :param token: The OAuth2 token to use for authentication.  If no token
                      is passed, the client will default to an unauthenticated
                      state.  While in this state, any connections to Twitch's
                      irc servers will be anonymous (justinfan), and any api
                      requests that require authentication will raise a
                      PermissionError."""
        self._token = token

        return self

    def factory(self, factory: requests.Factory = None, *,
                manager: QtNetwork.QNetworkAccessManager = None) -> 'ClientBuilder':
        """Sets the request factory the client will use for all requests.

        :param factory: The request factory the client will use for api requests.
                        If no factory is passed, the client will generate a new
                        instance.
        :param manager: The QNetworkAccessManger to pass to the factory instance
                        should the client generate a new instance."""
        self._factory = factory
        self._manager = manager
        return self

    def parent(self, parent: QtCore.QObject) -> 'ClientBuilder':
        """A QObject instance to serve as the client's parent in Qt's
        parent-child relationship.

        :param parent: The object instance to set as the client's parent."""
        self._parent = parent
        return self

    def build(self) -> Client:
        """Builds the client with the data passed to the builder."""
        if self._factory is None:
            self._factory = requests.Factory()

        self._result.__init__(parent=self._parent)
        self._result.http = Http()
        return self._result
