#    PyUruNet
#    Copyright (C) 2016  Adam 'Hoikas' Johnson <AdamJohnso AT gmail DOT com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import _urunet

class RC4(_urunet.rc4):
    def __init__(self, base, key, logger=None):
        super().__init__(key)
        self.log = logger

        # Now we map the base to us
        for i in dir(base):
            if not hasattr(self, i):
                setattr(self, i, getattr(base, i))
        self._base = base

    async def read(self, size) -> bytes:
        return self.transform(await self._base.read(size))

    async def readexactly(self, size) -> bytes:
        return self.transform(await self._base.readexactly(size))

    def write(self, data: bytes):
        self._base.write(self.transform(data))
