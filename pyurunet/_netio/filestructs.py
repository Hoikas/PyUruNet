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
#    along with this program.  If not, see <http:#www.gnu.org/licenses/>.

import enum

from . import fields

class C2F(enum.IntEnum):
    # Global
    PingRequest = 0

    # File server-related
    BuildIdRequest = 10

    # Cache-related
    ManifestRequest = 20
    FileDownloadRequest  = 21
    ManifestEntryAck = 22
    FileDownloadChunkAck = 23


class F2C(enum.IntEnum):
    # Global
    PingReply = 0

    # File server-related
    BuildIdReply = 10
    BuildIdUpdate = 11

    # Cache-related
    ManifestReply = 20
    FileDownloadReply = 21

ping_pong = (
    (fields.integer, "ping_time", 4),
)

build_id_request = (
    (fields.integer, "trans_id", 4),
)
build_id_reply = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "result", 4),
    (fields.integer, "build_id", 4),
)

manifest_request = (
    (fields.integer, "trans_id", 4),
    (fields.char16_blob, "manifest_name", 260),
    (fields.integer, "build_id", 4),
)
manifest_reply = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "result", 4),
    (fields.integer, "reader_id", 4),
    (fields.integer, "file_count", 4),
    (fields.char16_buffer, "buffer", 4),
)
manifest_ack = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "reader_id", 4),
)
