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
import time
from typing import Optional, Callable

__all__ = ['CachedMethod']


class CachedMethod:
    """A descriptor class mostly used for ratelimiting Twitch API calls.
    Callables decorated with this class allow the callable to be called once
    every 5 minutes (configurable).  If the callable is called again during this
    cooldown period, the last returned value(s) will be returned again."""

    def __init__(self, cooldown: float = 300):
        """
        :param cooldown: The amount in seconds a callable cannot be used for.
                         During this period, the last valid request will be
                         returned.
        """

        self._last_use: float = 0
        self._cooldown: float = cooldown
        self._last_result: Optional[dict] = None

    def freeze(self):
        self._last_use = time.time()

    def thaw(self):
        self._last_use = 0

    def is_frozen(self) -> bool:
        return (self._last_use - time.time()) < self._cooldown

    def __call__(self, f: Callable):
        def wrapper(*args, **kwargs):
            if not self.is_frozen():
                result = f(*args, **kwargs)
                self._last_result = result
                self.freeze()

                return result

            else:
                return self._last_result

        return wrapper
