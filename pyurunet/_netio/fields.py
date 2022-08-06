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

from __future__ import annotations

from collections import namedtuple
import struct
from typing import Optional, Sequence
from uuid import UUID

_net_field = namedtuple("_NetField", ["reader", "writer"])

async def _read_blob(fd, size: int) -> bytes:
    data = await fd.readexactly(size)
    return data

def _write_blob(fd, size: int, data: bytes):
    if data is None:
        data = bytes([0] * size)
    fd.write(data)

blob = _net_field(_read_blob, _write_blob)

async def _read_buffer(fd, size, maxsize):
    bufsz = await _read_integer(fd, 4)
    bufsz *= size
    if bufsz > maxsize:
        # somehow signal that the client needs to be booted
        pass
    data = await fd.readexactly(bufsz)
    return data

def _write_buffer(fd, size, value: Optional[bytes]):
    if value:
        _write_integer(fd, 4, len(value) // size)
        fd.write(value)
    else:
        _write_integer(fd, size, 0)

# buffer size hints to prevent clients from sending us a load of crap
# tiny = 1KB; medium = 1MB; big = 10MB
tiny_buffer = _net_field(lambda fd, size: _read_buffer(fd, size, 1024), _write_buffer)
medium_buffer = _net_field(lambda fd, size: _read_buffer(fd, size, 1024 * 1024), _write_buffer)
big_buffer = _net_field(lambda fd, size: _read_buffer(fd, size, 10 * 1024 * 1024), _write_buffer)

async def _read_char16_blob(fd, size: int) -> str:
    buf = await fd.readexactly(size * 2)
    decoded = buf.decode("utf-16-le", errors="replace")
    return decoded.rstrip('\0')

def _write_char16_blob(fd, size: int, value: Optional[str]) -> None:
    if value is None:
        value = ""
    buf = value[:size - 1].encode("utf-16-le", errors="replace")
    buf = buf + bytes((size * 2) - len(buf))
    fd.write(buf)

char16_blob = _net_field(_read_char16_blob, _write_char16_blob)

async def _read_integer(fd, size: int) -> int:
    if size == 1:
        p = "<B"
    elif size == 2:
        p = "<H"
    elif size == 4:
        p = "<I"
    else:
        raise RuntimeError(f"Invalid integer field size: {size}")

    data = await fd.readexactly(size)
    if data is not None:
        return struct.unpack(p, data)[0]
    return 0

def _write_integer(fd, size: int, value: int) -> None:
    if size == 1:
        p = "<B"
    elif size == 2:
        p = "<H"
    elif size == 4:
        p = "<I"
    else:
        raise RuntimeError(f"Invalid integer field size: {size}")
    fd.write(struct.pack(p, value if value is not None else 0))

integer = _net_field(_read_integer, _write_integer)

async def _read_dword_array(fd, size: Optional[int]) -> Sequence[int]:
    if size is None:
        size = await _read_integer(fd, 4)
    data = await fd.readexactly(size * 4)
    if data is not None:
        return struct.unpack(f"<{'I' * size}", data)
    return [0] * size

def _write_dword_array(fd, size: int, value: Sequence[int]) -> None:
    if size is None:
        size = 0 if value is None else len(value)
        _write_integer(fd, 4, size)
    if value is None:
        value = [0] * size
    fd.write(struct.pack(f"<{'I' * size}", *value))

dword_array = _net_field(_read_dword_array, _write_dword_array)

async def _read_string(fd, size: int) -> str:
    # It's official. The size in the NetStruct is a lie! :)
    actualSize = struct.unpack("<H", (await fd.readexactly(2)))[0]
    actualSize *= 2

    buf = await fd.readexactly(actualSize)
    decoded = buf.decode("utf-16-le", errors="replace")
    return decoded.rstrip('\0')

def _write_string(fd, size: int, value: Optional[str]) -> None:
    if value is None:
        value = ""
    buf = value[:size - 1].encode("utf-16-le", errors="replace")
    fd.write(struct.pack("<H", len(buf) // 2))
    fd.write(buf)

string = _net_field(_read_string, _write_string)

async def _read_uuid(fd, size: int) -> UUID:
    assert size == 1
    data = await fd.readexactly(16)
    return UUID(bytes_le=data)

def _write_uuid(fd, size: int, value: Optional[UUID]) -> None:
    assert size == 1
    if value is None:
        value = UUID(int=0)
    fd.write(value.bytes_le)

uuid = _net_field(_read_uuid, _write_uuid)
