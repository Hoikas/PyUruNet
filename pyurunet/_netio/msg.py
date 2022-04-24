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

import abc
import asyncio
from asyncio.exceptions import CancelledError
import codecs
from dataclasses import dataclass
import io
import inspect
import logging
import secrets
import sys
from typing import *
import uuid

from . import cryptio, errors, fields
from .constants import Product

# FIXME: don't hardwire this?
_logger = logging.getLogger("PyUruNet")
_logger.setLevel(logging.DEBUG)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(peer)s %(message)s"))
_logger.addHandler(_handler)

_kablooey = (asyncio.CancelledError, ConnectionError, EOFError)

connection_header = (
    (fields.integer, "conn_type", 1),
    (fields.integer, "size", 2),
    (fields.integer, "build_id", 4),
    (fields.integer, "build_type", 4),
    (fields.integer, "branch_id", 4),
    (fields.uuid, "product", 1),
)

_c2s_connect = 0
_s2c_encrypt = 1

_connect_struct = (
    (fields.integer, "msg_id", 1),
    (fields.integer, "msg_size", 1),
    (fields.blob, "y_data", 64),
)

_encrypt_struct = (
    (fields.integer, "msg_id", 1),
    (fields.integer, "msg_size", 1),
    (fields.blob, "server_seed", 7),
)

class NetMessage:
    def __init__(self, struct, **kwargs):
        self._struct = struct
        self.__dict__.update(kwargs)

    def __str__(self):
        detail = "NetMessage\n"
        for i in filter(lambda x: not x.startswith("_"), dir(self)):
            detail += f"    '{i}': \"{getattr(self, i)}\"\n"
        return detail


async def read_netstruct(fd: asyncio.StreamReader, struct: Sequence) -> NetMessage:
    """Reads a message off the wire defined by the given struct"""

    msg = NetMessage(struct)
    for rw, name, size in struct:
        data = await rw.reader(fd, size)
        setattr(msg, name, data)
    return msg

def write_netstruct(fd: Optional[asyncio.StreamWriter], msg: NetMessage) -> Union[bytes, int]:
    """Writes a NetStruct to a given fd and returns the number of bytes written. If fd is None, then
       the buffered data is returned instead"""
    def _debug(msg, data):
        hex = codecs.encode(data, "hex")
        print(f"{msg._struct}\n{str(msg)}\n{hex}\n")

    # Unfortunately, the client arseplodes if we send the buffer bit-by-bit in some cases...
    # So, we're going to have to buffer it locally.
    bio = io.BytesIO()
    for rw, name, size in msg._struct:
        data = getattr(msg, name, None)
        rw.writer(bio, size, data)

    data = bio.getvalue()
    if fd is not None:
        #_debug(msg, data)
        fd.write(data)
        return len(data)
    else:
        return data

class NetStructDispatcher(abc.ABC):
    """Dispatches NetStructs read off the wire to callables"""

    # This is the most common message header...
    _msg_header = (
        (fields.integer, "msg_id", 2),
    )

    def __init__(self, reader=None, writer=None):
        self._msg_header_size = sum(list(zip(*self._msg_header))[2])
        self.reader = reader
        self.writer = writer

        # TODO: use multiple loggers?
        self.log = logging.LoggerAdapter(_logger, extra=dict(peer=""))

    async def _establish_encryption_c2s(self, gValue: int, nKey: int, xKey: int) -> None:
        b = secrets.randbits(512)
        cliSeed = pow(xKey, b, nKey).to_bytes(64, byteorder="little")
        srvSeed = pow(gValue, b, nKey).to_bytes(64, byteorder="little")

        # Send our junk to the server
        self.log.debug("Sending NetCliConnect packet...")
        ncc = NetMessage(_connect_struct,
                         msg_id=_c2s_connect,
                         msg_size=66,
                         y_data=srvSeed)
        write_netstruct(self.writer, ncc)
        await self.writer.drain()

        # Now, we get the seed from the server and make the key...
        self.log.debug("Waiting for NetCliEncrypt packet...")
        nce = await read_netstruct(self.reader, _encrypt_struct)
        assert nce.msg_id == _s2c_encrypt
        assert nce.msg_size == 9

        key = bytearray(7)
        cliLen = len(cliSeed)
        for i in range(7):
            if i >= cliLen:
                key[i] = nce.server_seed[i]
            else:
                key[i] = cliSeed[i] ^ nce.server_seed[i]
        key = bytes(key)

        self.reader = cryptio.RC4(self.reader, key, self.log)
        self.writer = cryptio.RC4(self.writer, key, self.log)
        self.log.debug("Encryption established!")

    async def _establish_encryption_s2c(self, kKey: int, nKey: int) -> None:
        # Reference implementation - current servers are not supported.
        msgId = await fields.integer.reader(self.reader, 1)
        msgSize = await fields.integer.reader(self.reader, 1)

        # Cyan sends the TOTAL message size.
        msgSize -= 2

        # Sanity...
        assert msgId == _c2s_connect
        assert msgSize <= 64 or msgSize == 0

        # Okay, so, now here's our cleverness. If the message is empty, this is a decrypted connection.
        if msgSize:
            y_data = int.from_bytes((await self.reader.readexactly(msgSize)), byteorder="little")
            cliSeed = pow(y_data, kKey, nKey).to_bytes(64, byteorder="little")
            srvSeed = secrets.randbits(56).to_bytes(length=7, byteorder=sys.byteorder)

            key = bytearray(7)
            cliLen = len(cliSeed)
            for i in range(7):
                if i >= cliLen:
                    key[i] = srvSeed[i]
                else:
                    key[i] = cliSeed[i] ^ srvSeed[i]
            key = bytes(key)

            nce = NetMessage(_encrypt_struct, msg_id=_s2c_encrypt, msg_size=9, server_seed=srvSeed)
            write_netstruct(self.writer, nce)
            await self.writer.drain()

            # Now set up our encrypted reader/writer
            self.reader = cryptio.RC4(self.reader, key, self.log)
            self.writer = cryptio.RC4(self.writer, key, self.log)
        else:
            # NetCliEncrypt... but not really
            fields.integer.writer(self.writer, 1, _s2c_encrypt)
            fields.integer.writer(self.writer, 1, 2)
            await self.writer.drain()

    async def dispatch_netstructs(self):
        while True:
            try:
                header = await read_netstruct(self.reader, self._msg_header)
            except _kablooey as e:
                self.connection_reset(str(e))
                break

            try:
                msg_struct = self.incoming_lookup[header.msg_id]
            except LookupError:
                msg = f"Invalid incoming messageID {header.msg_id}"
                self.log.error(msg)
                self.connection_reset(msg)
                return

            try:
                actual_netmsg = await read_netstruct(self.reader, msg_struct)
            except _kablooey as e:
                self.connection_reset(str(e))
                break

            handler = self.incoming_handlers.get(header.msg_id, self.handle_incoming)
            try:
                self.log.debug(f"Dispatching {header.msg_id:02X} to {handler}")
                dispatch_result = handler(header.msg_id, actual_netmsg)
                if asyncio.iscoroutine(dispatch_result):
                    # Be very careful about doing this, or you may deadlock the loop.
                    await dispatch_result
            except CancelledError:
                raise
            except Exception as e:
                self.log.exception(e)

    def connection_reset(self):
        if self.writer is not None:
            self.writer.close()

    @abc.abstractmethod
    def handle_incoming(self, netmsg: NetMessage) -> None:
        ...

    @property
    def peername(self) -> str:
        return "/".join((str(i) for i in self.writer.get_extra_info("peername")))

    async def send_netstruct(self, msg_id: Optional[int], netmsg: NetMessage) -> None:
        msgBuf = write_netstruct(None, netmsg)

        if msg_id is None:
            sendBuf = msgBuf
        else:
            header = NetMessage(self._msg_header,
                                msg_id=msg_id,
                                msg_size=self._msg_header_size+len(msgBuf))
            headerBuf = write_netstruct(None, header)
            sendBuf = headerBuf + msgBuf

        self.writer.write(sendBuf)
        try:
            await self.writer.drain()
        except _kablooey as e:
            self.log.exception(e)
            self.connection_reset(str(e))


@dataclass
class _Transaction:
    future: asyncio.Future
    data: Any


class NetClient(NetStructDispatcher):
    def __init__(self):
        super().__init__()
        self._next_trans_id = 1
        self._transactions: Dict[int, _Transaction] = {}
        self._read_task: Optional[asyncio.Task] = None

    @abc.abstractmethod
    async def _perform_handshake(self, build: int, uuid: uuid.UUID) -> None:
        ...

    def handle_incoming(self, msg_id: int, netmsg: NetMessage):
        if trans_id := getattr(netmsg, "trans_id", None):
            if transaction := self._transactions.pop(trans_id, None):
                result = getattr(netmsg, "result", int(errors.NetError.success))
                try:
                    result = errors.NetError(result)
                except ValueError:
                    self.warning(f"Transaction {trans_id} returned an invalid error code: {result}")
                    exc = ValueError
                else:
                    exc = errors.error_lut.get(result)

                if exc is not None:
                    self.log.error(f"Transaction {trans_id} failed: {exc.__name__}")
                    transaction.future.set_exception(exc)
                else:
                    transaction.future.set_result(netmsg)
            else:
                self.log.warning(f"Unexpected transaction reply from server: {trans_id}")
        else:
            self.log.warning(f"Unhandled {msg_id:X}: Expected a transaction, but it's not a transaction.")

    async def start(self, *, host: str = Product.host, port: int = Product.port,
                    build: int = Product.build_id, product: uuid.UUID = Product.uuid,
                    nkey: int = 0, xkey: int = 0):
        self.log.info(f"Connecting to {host}/{port}...")
        self.reader, self.writer = await asyncio.open_connection(host, port)
        self.log.extra["peer"] = self.peername
        self.log.debug("Connection established, performing handshake...")
        try:
            await self._perform_handshake(build=build, product=product, nkey=nkey, xkey=xkey)
            #await self.dispatch_netstructs()
        except _kablooey:
            self.connection_reset()
        else:
            self._read_task = asyncio.create_task(self.dispatch_netstructs())

    async def send_transaction(self, msg_id: int, netmsg: NetMessage, data=None):
        trans_id = self._trans_id
        trans = _Transaction(future=asyncio.get_running_loop().create_future(), data=data)
        self._transactions[trans_id] = trans
        netmsg.trans_id = trans_id
        await self.send_netstruct(msg_id, netmsg)
        await trans.future
        return trans.future.result()

    def connection_reset(self, msg: str = "Connection reset"):
        if self._read_task is not None:
            self._read_task.cancel(msg)
        for transaction in self._transactions.values():
            transaction.future.cancel(msg)
        return super().connection_reset()

    @property
    def _trans_id(self):
        """Gets and increments the next transaction ID"""
        trans_id = self._next_trans_id
        self._next_trans_id = 1 if self._next_trans_id == 0xFFFFFFFF else self._next_trans_id + 1
        return trans_id

    @abc.abstractmethod
    async def ping(self) -> None:
        ...

    async def keep_alive(self) -> None:
        while not self._read_task.cancelled():
            await self.ping()
            await asyncio.sleep(20)
