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
from typing import List

from PySide6 import QtCore, QtGui


class Cheermote:
    """A cheermote."""

    def __init__(self, state, **kwargs):
        self._state = state

        self._prefix: str = kwargs.get('prefix')
        self._minimum_amount: int = kwargs.get('min_amount')
        self._scales: List[str] = []
        self._color: QtGui.QColor = kwargs.get('color')
        self._id: str = kwargs.get('id')
        self._images: dict = kwargs.get('images')
        self._amount: int = kwargs.get('amount', self._minimum_amount)
        self._can_cheer: bool = kwargs.get('can_cheer')
        self._priority: int = kwargs.get('priority')
        self._backgrounds: List[str] = kwargs.get('backgrounds')
        self._states: List[str] = kwargs.get('states')
        self._type: str = kwargs.get('type')
        self._updated_at: datetime.datetime = kwargs.get('updated_at')

        self._static_cheermotes_unsupported = 'Does not support static cheermotes!'
        self._animated_cheermotes_unsupported = 'Does not support animated cheermotes!'

    @property
    def amount(self) -> int:
        """The amount of bits this cheermote was cheered with."""
        return self._amount

    @amount.setter
    def amount(self, value: int):
        self._amount = value

    @property
    def prefix(self) -> str:
        """The prefix of this cheermote."""
        return self._prefix

    @property
    def id(self) -> str:
        """The Twitch ID of this cheermote."""
        return self._id

    @property
    def scales(self) -> List[str]:
        """The scales this cheermote supports."""
        return self._scales.copy()

    @property
    def color(self) -> QtGui.QColor:
        """The hex color of this cheermote."""
        return self._color

    @property
    def min_amount(self) -> int:
        """The minimum amount of bits that must be cheered before this
        cheermote should be displayed."""
        return self._minimum_amount

    @property
    def can_cheer(self) -> bool:
        """Whether or not this cheermote can be cheered."""
        return self._can_cheer

    @property
    def priority(self) -> int:
        """The priority this cheermote has compared to other cheermotes."""
        return self._priority

    @property
    def backgrounds(self) -> List[str]:
        """The different backgrounds this cheermote supports."""
        return self._backgrounds

    @property
    def states(self) -> List[str]:
        """The different states this cheermote supports."""
        return self._states

    @property
    def type(self) -> str:
        """The type of cheermote this is."""
        return self._type

    @property
    def updated_at(self) -> datetime.datetime:
        """The last time this cheermote was updated at."""
        return self._updated_at

    def static_url(self, theme: str, scale: str) -> QtCore.QUrl:
        """Returns a QUrl of the static cheermote at `scale` in `theme`."""
        if theme not in self._images:
            raise KeyError(f'Cheermote does not support specified theme "{theme}"!')

        themed: dict = self._images.get(theme)

        if 'static' not in themed:
            raise KeyError(self._static_cheermotes_unsupported)

        static_themed: dict = themed.get('static')

        if scale not in static_themed:
            raise KeyError(f'Cheermote does not support specified scale "{scale}"!')

        return QtCore.QUrl(static_themed['scale'])

    def animated_url(self, theme: str, scale: str) -> QtCore.QUrl:
        """Returns a QUrl of the animated cheermote at `scale` in `theme`."""
        if theme not in self._images:
            raise KeyError(f'Cheermote does not support specified theme "{theme}"!')

        themed: dict = self._images.get(theme)

        if 'animated' not in themed:
            raise KeyError(self._animated_cheermotes_unsupported)

        animated_themed: dict = themed.get('animated')

        if scale not in animated_themed:
            raise KeyError(f'Cheermote does not support specified scale "{scale}"!')

        return QtCore.QUrl(animated_themed.get(scale))

    def static(self, theme: str, scale: str) -> QtGui.QImage:
        """Returns a QImage of the cheermote with `theme` at `scale`."""
        if theme not in self._images:
            raise KeyError(f'Cheermote does not support specified theme "{theme}"!')

        themed: dict = self._images.get(theme)

        if 'static' not in themed:
            raise KeyError(self._static_cheermotes_unsupported)

        static_themed: dict = themed.get('static')

        if scale not in static_themed:
            raise KeyError(f'Cheermote does not support specified scale "{scale}"')

        else:
            pass  # TODO: Fetch the image

    def animated(self, theme: str, scale: str) -> QtGui.QImage:
        """Returns a QImage of the cheermote with `theme` at `scale`."""
        if theme not in self._images:
            raise KeyError(f'Cheermote does not support specified theme "{theme}"!')

        themed: dict = self._images.get(theme)

        if 'animated' not in themed:
            raise KeyError(self._animated_cheermotes_unsupported)

        animated_themed: dict = themed.get('animated')

        if scale not in animated_themed:
            raise KeyError(f'Cheermote does not support specified scale "{scale}"')

        else:
            pass  # TODO: Fetch GIF

    def __str__(self):
        return f'{self._prefix}{self.amount}'
