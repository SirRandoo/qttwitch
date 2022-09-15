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
import datetime

from PySide6 import QtCore, QtGui

from .game import Game
from .user import User

__all__ = ['Stream']


class Stream(QtCore.QObject):
    """A channel on Twitch."""

    def __init__(self, **kwargs):
        super(Stream, self).__init__(parent=kwargs.get('parent'))

        self._id: str = kwargs.pop('id')
        self._game: Game = kwargs.get('game')
        self._language: str = kwargs.get('language')
        self._started_at: datetime.datetime = kwargs.get('started_at')
        self._thumbnail_url: str = kwargs.get('thumbnail_url')
        self._title: str = kwargs.get('title')
        self._type: str = kwargs.get('type')
        self._broadcaster: User = kwargs.get('broadcaster')
        self._viewer_count: int = kwargs.get('viewer_count')

    @property
    def game(self) -> Game:
        """The current game the streamer is playing."""
        return self._game

    @property
    def id(self) -> str:
        """The Twitch ID of the stream."""
        return self._id

    @property
    def language(self) -> str:
        """The primary language of the stream."""
        return self._language

    @property
    def started_at(self) -> datetime.datetime:
        """A datetime object representing when this stream was started."""
        return self._started_at

    @property
    def title(self) -> str:
        """The title of the stream."""
        return self._title

    @property
    def broadcaster(self) -> User:
        """The broadcaster of this stream."""
        return self._broadcaster

    @property
    def viewer_count(self) -> int:
        """The number of viewers watching the stream."""
        return self._viewer_count

    def thumbnail_url(self, width: int = None, height: int = None) -> QtCore.QUrl:
        """The url of the stream's thumbnail."""
        if width is None:
            width = 800

        if height is None:
            height = 600

        return QtCore.QUrl(self._thumbnail_url.format(width=width, height=height))

    def thumbnail(self, width: int = None, height: int = None) -> QtGui.QImage:
        """Returns a QImage of the stream's thumbnail."""
