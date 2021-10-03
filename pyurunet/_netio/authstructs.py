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

class C2A(enum.IntEnum):
    # Global
    PingRequest = 0 # enum.auto() starts at 1

    # Client
    ClientRegisterRequest = enum.auto()
    ClientSetCCRLevel = enum.auto()

    # Account
    AcctLoginRequest = enum.auto()
    AcctSetEulaVersion = enum.auto()
    AcctSetDataRequest = enum.auto()
    AcctSetPlayerRequest = enum.auto()
    AcctCreateRequest = enum.auto()
    AcctChangePasswordRequest = enum.auto()
    AcctSetRolesRequest = enum.auto()
    AcctSetBillingTypeRequest = enum.auto()
    AcctActivateRequest = enum.auto()
    AcctCreateFromKeyRequest = enum.auto()

    # Player
    PlayerDeleteRequest = enum.auto()
    PlayerUndeleteRequest = enum.auto()
    PlayerSelectRequest = enum.auto()
    PlayerRenameRequest = enum.auto()
    PlayerCreateRequest = enum.auto()
    PlayerSetStatus = enum.auto()
    PlayerChat = enum.auto()
    UpgradeVisitorRequest = enum.auto()
    SetPlayerBanStatusRequest = enum.auto()
    KickPlayer = enum.auto()
    ChangePlayerNameRequest = enum.auto()
    SendFriendInviteRequest = enum.auto()

    # Vault
    VaultNodeCreate = enum.auto()
    VaultNodeFetch = enum.auto()
    VaultNodeSave = enum.auto()
    VaultNodeDelete = enum.auto()
    VaultNodeAdd = enum.auto()
    VaultNodeRemove = enum.auto()
    VaultFetchNodeRefs = enum.auto()
    VaultInitAgeRequest = enum.auto()
    VaultNodeFind = enum.auto()
    VaultSetSeen = enum.auto()
    VaultSendNode = enum.auto()

    # Ages
    AgeRequest = enum.auto()

    # File-related
    FileListRequest = enum.auto()
    FileDownloadRequest = enum.auto()
    FileDownloadChunkAck = enum.auto()

    # Game
    PropagateBuffer = enum.auto()

    # Public ages
    GetPublicAgeList = enum.auto()
    SetAgePublic = enum.auto()

    # Log Messages
    LogPythonTraceback = enum.auto()
    LogStackDump = enum.auto()
    LogClientDebuggerConnect = enum.auto()

    # Score
    ScoreCreate = enum.auto()
    ScoreDelete = enum.auto()
    ScoreGetScores = enum.auto()
    ScoreAddPoints = enum.auto()
    ScoreTransferPoints = enum.auto()
    ScoreSetPoints = enum.auto()
    ScoreGetRanks = enum.auto()

    AccountExistsRequest = enum.auto()

    # Extension messages
    AgeRequestEx = 0x1000
    ScoreGetHighScores = enum.auto()


class A2C(enum.IntEnum):
    # Global
    PingReply = 0 # enum.auto() starts at 1
    ServerAddr = enum.auto()
    NotifyNewBuild = enum.auto()

    # Client
    ClientRegisterReply = enum.auto()

    # Account
    AcctLoginReply = enum.auto()
    AcctData = enum.auto()
    AcctPlayerInfo = enum.auto()
    AcctSetPlayerReply = enum.auto()
    AcctCreateReply = enum.auto()
    AcctChangePasswordReply = enum.auto()
    AcctSetRolesReply = enum.auto()
    AcctSetBillingTypeReply = enum.auto()
    AcctActivateReply = enum.auto()
    AcctCreateFromKeyReply = enum.auto()

    # Player
    PlayerList = enum.auto()
    PlayerChat = enum.auto()
    PlayerCreateReply = enum.auto()
    PlayerDeleteReply = enum.auto()
    UpgradeVisitorReply = enum.auto()
    SetPlayerBanStatusReply = enum.auto()
    ChangePlayerNameReply = enum.auto()
    SendFriendInviteReply = enum.auto()

    # Friends
    FriendNotify = enum.auto()

    # Vault
    VaultNodeCreated = enum.auto()
    VaultNodeFetched = enum.auto()
    VaultNodeChanged = enum.auto()
    VaultNodeDeleted = enum.auto()
    VaultNodeAdded = enum.auto()
    VaultNodeRemoved = enum.auto()
    VaultNodeRefsFetched = enum.auto()
    VaultInitAgeReply = enum.auto()
    VaultNodeFindReply = enum.auto()
    VaultSaveNodeReply = enum.auto()
    VaultAddNodeReply = enum.auto()
    VaultRemoveNodeReply = enum.auto()

    # Ages
    AgeReply = enum.auto()

    # File-related
    FileListReply = enum.auto()
    FileDownloadChunk = enum.auto()

    # Game
    PropagateBuffer = enum.auto()
    
    # Admin
    KickedOff = enum.auto()

    # Public ages    
    PublicAgeList = enum.auto()

    # Score
    ScoreCreateReply = enum.auto()
    ScoreDeleteReply = enum.auto()
    ScoreGetScoresReply = enum.auto()
    ScoreAddPointsReply = enum.auto()
    ScoreTransferPointsReply = enum.auto()
    ScoreSetPointsReply = enum.auto()
    ScoreGetRanksReply = enum.auto()

    AccountExistsReply = enum.auto()

    # Extension messages
    AgeReplyEx = 0x1000,
    ScoreGetHighScoresReply = enum.auto()
    ServerCaps = enum.auto()


connection_header = (
    (fields.integer, "size", 4),
    (fields.uuid, "uuid", 1),
)

ping_pong = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "ping_time", 4),
    (fields.tiny_buffer, "payload", 4),
)

server_addr = (
    (fields.integer, "addr", 4),
    (fields.uuid, "token", 1)
)
kicked_off = (
    (fields.integer, "reason", 4),
)

client_register_req = (
    (fields.integer, "build_id", 4),
)
client_register_reply = (
    (fields.integer, "challenge", 4),
)

login_request = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "challenge", 4),
    (fields.string, "account", 64),
    (fields.dword_array, "hash", 5),
    (fields.string, "token", 64),
    (fields.string, "os", 8),
)
login_reply = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "result", 4),
    (fields.uuid, "uuid", 1),
    (fields.integer, "flags", 4),
    (fields.integer, "billing_type", 4),
    (fields.dword_array, "encryption_key", 4),
)
player_info = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "player_id", 4),
    (fields.string, "player_name", 40),
    (fields.string, "avatar_shape", 64),
    (fields.integer, "explorer", 4),
)

vault_node_fetch_request = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "node_id", 4),
)
vault_node_fetch_reply = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "result", 4),
    (fields.medium_buffer, "node_data", 4),
)

vault_node_find_request = (
    (fields.integer, "trans_id", 4),
    (fields.tiny_buffer, "template_node", 4),
)
vault_node_find_reply = (
    (fields.integer, "trans_id", 4),
    (fields.integer, "result", 4),
    (fields.dword_array, "node_ids", None),
)
