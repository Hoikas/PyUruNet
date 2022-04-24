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

import asyncio
from dataclasses import dataclass
import io
from pathlib import PureWindowsPath
import struct
import time
from typing import List

from . import _netio
from ._netio import filestructs as _msg

import _urunet

_connection_data = (
    (_netio.fields.integer, "data_size", 4),
    (_netio.fields.integer, "data_build_id", 4),
    (_netio.fields.integer, "data_server_type", 4),
)

@dataclass(frozen=True)
class ManifestEntry:
    file_name: PureWindowsPath
    download_name: PureWindowsPath
    file_hash: str
    download_hash: str
    file_size: int
    download_size: int
    flags: int


class FileCli(_netio.NetClient):

    # The FileSrv sends all messages as buffer propagations. Fortunately, our NetCli will
    # kindly calculate this stuff for us.
    _msg_header = (
        (_netio.fields.integer, "msg_size", 4),
        (_netio.fields.integer, "msg_id", 4),
    )

    def __init__(self):
        super().__init__()
        self.incoming_lookup = {
            _msg.F2C.PingReply: _msg.ping_pong,
            _msg.F2C.BuildIdReply: _msg.build_id_reply,
            _msg.F2C.ManifestReply: _msg.manifest_reply,
        }
        self.incoming_handlers = {
            _msg.F2C.PingReply: self._handle_pong,
            _msg.F2C.ManifestReply: self._handle_manifest,
        }
        self._build = 0

    async def _handle_manifest(self, msg_id: int, netmsg: _netio.NetMessage) -> None:
        # Go ahead and send the response that we got it.
        response = _netio.NetMessage(
            _msg.manifest_ack,
            trans_id=netmsg.trans_id,
            reader_id=netmsg.reader_id
        )
        ack = self.send_netstruct(_msg.C2F.ManifestEntryAck, response)

        # We will potenially get this call multiple times, so we want to
        # keep firing until we have all of the files.
        if transaction := self._transactions.get(netmsg.trans_id):
            if transaction.data is None:
                transaction.data = []

            # Basic transaction handling ahoy.
            try:
                result = _netio.errors.NetError(netmsg.result)
            except ValueError:
                self.warning(f"Transaction {netmsg.trans_id} returned an invalid error code: {result}")
                exc = ValueError
            else:
                exc = _netio.errors.error_lut.get(result)
            if result != _netio.errors.NetError.success:
                self._transactions.pop(netmsg.trans_id)
                transaction.set_exception(exc)

            # Unpack the binary manifest into our working... thingy...
            s = io.BytesIO(netmsg.buffer)
            u16: int = lambda func: struct.unpack("<H", func(2))[0]

            def read_string(size=None) -> str:
                if size is None:
                    def _iter():
                        while True:
                            v = s.read(2)
                            if v != bytes(2):
                                yield from (i for i in v)
                            else:
                                break
                    value = bytes(list(_iter()))
                else:
                    value = bytes(list(s.read(size * 2)))
                    assert u16(s.read) == 0
                return value.decode("utf-16-le", errors="replace")

            def read_u32():
                value = u16(s.read) << 16 | u16(s.read)
                assert u16(s.read) == 0
                return value

            while True:
                file_name = read_string()
                if not file_name:
                    break
                download_name = read_string()
                file_hash = read_string(32).lower()
                download_hash = read_string(32).lower()
                file_size = read_u32()
                download_size = read_u32()
                flags = read_u32()

                entry = ManifestEntry(
                    PureWindowsPath(file_name), PureWindowsPath(download_name),
                    file_hash, download_hash, file_size, download_size, flags
                )
                transaction.data.append(entry)

            # Now that we've processed the buffer, see if life is good.
            if len(transaction.data) >= netmsg.file_count:
                self.log.debug("All file info received from manifest, firing coroutine!")
                transaction.future.set_result(transaction.data)
                self._transactions.pop(netmsg.trans_id)
            else:
                self.log.debug(f"Still waiting on {netmsg.file_count - len(transaction.data)} files before manifest completes...")
        else:
            self.log.warning(f"Manifest reply {netmsg.trans_id} was not associated with a transaction?")

        # Be sure the ack is sent before we exit.
        await ack

    def _handle_pong(self, msg_id: int, netmsg: _netio.NetMessage) -> None:
        self.log.debug(f"FILE PONG: {netmsg.ping_time}!")

    async def _perform_handshake(self, build, product, nkey, xkey) -> None:
        self._build = build
        handshake_struct = _netio.msg.connection_header + _connection_data
        handshake = _netio.msg.NetMessage(
            handshake_struct,
            conn_type=_netio.NetProtocol.file,
            size=31,
            build_id=build,
            build_type=50,
            branch_id=1,
            product=product,
            data_size=12,
            data_build_id=build,
            data_server_type=0
        )
        await self.send_netstruct(None, handshake)

    async def ping(self) -> None:
        ts = int(time.monotonic())
        ping = _netio.msg.NetMessage(_msg.ping_pong, ping_time=ts)
        self.log.debug(f"FILE PING: {ts}?")
        # FileSrv ping requests aren't transactions, so there's no result here.
        await self.send_netstruct(_msg.C2F.PingRequest, ping)

    async def request_build_id(self) -> int:
        req = _netio.NetMessage(_msg.build_id_request)
        self.log.debug("Requesting latest buildID")
        build = await self.send_transaction(_msg.C2F.BuildIdRequest, req)
        self.log.debug(f"Got {build.build_id=}")
        return build.build_id

    async def request_manifest(self, manifest: str) -> List[ManifestEntry]:
        req = _netio.NetMessage(
            _msg.manifest_request,
            manifest_name=manifest,
            build_id=0
        )
        self.log.debug(f"Requesting manifest '{manifest}'")
        files = await self.send_transaction(_msg.C2F.ManifestRequest, req)
        return files
