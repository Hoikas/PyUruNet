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
import re
import pprint
import secrets
import time
from typing import List, Optional, Sequence
import uuid

from . import _netio
from ._netio import authstructs as _msg

import _urunet

_account_sha0 = re.compile("@(?!gametap)(?!magiquest)")

_connection_data = (
    (_netio.fields.integer, "data_size", 4),
    (_netio.fields.uuid, "data_token", 1),
)

@dataclass
class Player:
    id: int
    name: str
    shape: str


@dataclass
class LoginResult:
    uuid: uuid.UUID
    flags: int
    encryption_key: Sequence[int]
    players: List[Player]


class AuthCli(_netio.NetClient):
    def __init__(self):
        super().__init__()
        self.incoming_lookup = {
            _msg.A2C.PingReply: _msg.ping_pong,
            _msg.A2C.ServerAddr: _msg.server_addr,
            _msg.A2C.ClientRegisterReply: _msg.client_register_reply,
            _msg.A2C.AcctLoginReply: _msg.login_reply,
            _msg.A2C.AcctPlayerInfo: _msg.player_info,
            _msg.A2C.KickedOff: _msg.kicked_off,
            _msg.A2C.VaultNodeFetched: _msg.vault_node_fetch_reply,
            _msg.A2C.VaultNodeFindReply: _msg.vault_node_find_reply,
        }
        self.incoming_handlers = {
            _msg.A2C.ServerAddr: self._handle_server_addr,
            _msg.A2C.ClientRegisterReply: self._handle_client_register,
            _msg.A2C.AcctPlayerInfo: self._handle_player_info,
            _msg.A2C.KickedOff: self._handle_kicked_off,
        }
        self._challenge = asyncio.get_running_loop().create_future()
        self._build = 918

    def _handle_server_addr(self, msg_id: int, netmsg: _netio.NetMessage) -> None:
        pass

    def _handle_client_register(self, msg_id: int, netmsg: _netio.NetMessage) -> None:
        self.log.debug("Got the server challenge!")
        self._challenge.set_result(netmsg.challenge)

    def _handle_player_info(self, msg_id: int, netmsg: _netio.NetMessage) -> None:
        self.log.debug(f"Got player ID {netmsg.player_id}: {netmsg.player_name}")
        if transaction := self._transactions.get(netmsg.trans_id):
            transaction.data.append(Player(netmsg.player_id, netmsg.player_name, netmsg.avatar_shape))
        else:
            self.log.warning("Player was not associated with a login transaction?")

    def _handle_kicked_off(self, msg_id: int, netmsg: _netio.NetMessage) -> None:
        reason = _netio.NetError(netmsg.reason)
        msg = f"Kicked off by server: {reason}"
        self.log.critical(msg)

        # Propagate this exception down to all pending transactions to improve error-handling
        # semantics. Nothing like getting a "Kicked by CCR" response to your PingRequest.
        if exc := _netio.error_lut.get(reason):
            exc = exc(msg)
            for i in self._transactions:
                i.future.set_exception(exc)
            self._transactions.clear()

        self.connection_reset(msg)

    async def _perform_handshake(self, build, product, nkey, xkey) -> None:
        self._build = build
        handshake_struct = _netio.msg.connection_header + _connection_data
        handshake = _netio.msg.NetMessage(handshake_struct,
                                          conn_type=_netio.NetProtocol.auth,
                                          size=31,
                                          build_id=build,
                                          build_type=50,
                                          branch_id=1,
                                          product=product,
                                          data_size=20)
        await self.send_netstruct(None, handshake)
        await self._establish_encryption_c2s(_netio.DiffieHellmanG.auth, nkey, xkey)

    async def login(self, account: str, password: str, build: Optional[int] = None) -> LoginResult:
        self.log.debug("Logging in...")

        if not self._challenge.done():
            self.log.debug("Need a server challenge...")
            if build is None:
                build = self._build
            register = _netio.msg.NetMessage(_msg.client_register_req, build_id=build)
            await self.send_netstruct(_msg.C2A.ClientRegisterRequest, register)
            await self._challenge

        if any(_account_sha0.finditer(account)):
            server_challenge: int = self._challenge.result()
            client_challenge = secrets.randbits(32)

            # Yes, a fencepost error.
            buf = io.BytesIO()
            buf.write(password[:-1].encode("utf-16-le"))
            buf.write(b"\x00\x00")
            buf.write(account[:-1].lower().encode("utf-16-le"))
            buf.write(b"\x00\x00")
            pass_hash = _urunet.sha0_buffer(buf.getvalue())

            buf = io.BytesIO()
            buf.write(client_challenge.to_bytes(length=4, byteorder="little"))
            buf.write(server_challenge.to_bytes(length=4, byteorder="little"))
            for i in pass_hash:
                buf.write(i.to_bytes(length=4, byteorder="little"))
            pass_hash = _urunet.sha0_buffer(buf.getvalue())
        else:
            client_challenge = 0
            pass_hash = _urunet.sha1_buffer(password.encode("utf-8"))

        players = []
        netmsg = _netio.NetMessage(
            _msg.login_request,
            challenge=client_challenge,
            account=account,
            hash=pass_hash,
            os="PyUruNet"
        )
        self.log.debug(f"Sending login for {account}")
        reply = await self.send_transaction(_msg.C2A.AcctLoginRequest, netmsg, players)
        self.log.info(f"Logged in as {account}")
        result = LoginResult(
            uuid=reply.uuid,
            flags=reply.flags,
            encryption_key=reply.encryption_key,
            players=players
        )
        self.log.debug(pprint.pformat(result))

    async def ping(self) -> None:
        ts = int(time.monotonic())
        ping = _netio.msg.NetMessage(_msg.ping_pong, ping_time=ts, payload=b"fart\0")
        self.log.debug(f"PING: {ts}?")
        pong = await self.send_transaction(_msg.C2A.PingRequest, ping)
        self.log.debug(f"PONG: {pong.ping_time}!")

    async def vault_fetch_node(self, node_id: int):
        req = _netio.msg.NetMessage(_msg.vault_node_fetch_request, node_id=node_id)
        self.log.debug(f"Requesting node {node_id}...")
        reply = await self.send_transaction(_msg.C2A.VaultNodeFetch, req)
        return reply.node_data

    async def vault_find_node(self, template: bytes) -> Sequence[int]:
        req = _netio.msg.NetMessage(_msg.vault_node_find_request, template_node=template)
        self.log.debug(f"Sending vault node find of length {len(template)}")
        reply = await self.send_transaction(_msg.C2A.VaultNodeFind, req)
        return reply.node_ids