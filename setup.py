"""
This file is part of QtTwitch.

QtTwitch is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

QtTwitch is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with QtTwitch.  If not, see <https://www.gnu.org/licenses/>.
"""
from setuptools import setup

setup(
    name='QtTwitch',
    version='0.1.0a',
    packages=[
        'QtTwitch',
        'QtTwitch.data',
        'QtTwitch.data.api',
    ],
    url='https://www.github.com/SirRandoo/QtTwitch',
    license='LGPLv3+',
    author='SirRandoo',
    author_email='',
    description='A PySide2 library for Twitch.', install_requires=['PySide6'],
    dependency_links=['http://github.com/sirrandoo/QtUtilities/tarball/master#egg=package-1.0']
)
