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

import enum

class NetError(enum.IntEnum):
    pending = -1
    success = 0

    internal_error = 1
    timeout = 2
    bad_server_data = 3
    age_not_found = 4
    connect_failed = 5
    disconnected = 6
    # Unfortunately, there is no TriStateBoolean here...
    file_not_found = 7
    old_build_id = 8
    remote_shutdown = 9
    timeout_odbc = 10
    account_already_exists = 11
    player_already_exists = 12
    account_not_found = 13
    player_not_found = 14
    invalid_parameter = 15
    name_lookup_failed = 16
    logged_in_elsewhere = 17
    vault_node_not_found = 18
    max_players_on_account = 19
    authentication_failed = 20
    state_object_not_found = 21
    login_denied = 22
    circular_reference = 23
    account_not_activated = 24
    key_already_used = 25
    key_not_found = 26
    activation_code_not_found = 27
    player_name_invalid = 28
    not_supported = 29
    service_forbidden = 30
    auth_token_too_old = 31
    must_use_gametap_client = 32
    too_many_failed_logins = 33
    gametap_connection_failed = 34
    gametap_too_many_auth_options = 35
    gametap_missing_parameter = 36
    gametap_server_error = 37
    account_banned = 38
    kicked_by_ccr = 39
    score_wrong_type = 40
    score_not_enough_points = 41
    score_already_exists = 42
    score_no_data_found = 43
    invite_no_matching_player = 44
    invite_too_many_hoods = 45
    need_to_pay = 46
    server_busy = 47
    vault_node_access_violation = 48


class UruNetError(Exception): pass
class UruNetAccountAlreadyExistsError(UruNetError): pass
class UruNetAccountBannedError(UruNetError): pass
class UruNetAccountNotActivatedError(UruNetError): pass
class UruNetAccountNotFoundError(UruNetError): pass
class UruNetActivationCodeNotFoundError(UruNetError): pass
class UruNetAgeNotFoundError(UruNetError): pass
class UruNetAuthTokenTooOldError(UruNetError): pass
class UruNetAuthenticationFailedError(UruNetError): pass
class UruNetBadServerDataError(UruNetError): pass
class UruNetCircularReferenceError(UruNetError): pass
class UruNetConnectFailedError(UruNetError): pass
class UruNetDisconnectedError(UruNetError): pass
class UruNetFileNotFoundError(UruNetError): pass
class UruNetGametapConnectionFailedError(UruNetError): pass
class UruNetGametapMissingParameterError(UruNetError): pass
class UruNetGametapServerError(UruNetError): pass
class UruNetGametapTooManyAuthOptionsError(UruNetError): pass
class UruNetInternalError(UruNetError): pass
class UruNetInvalidParameterError(UruNetError): pass
class UruNetInviteNoMatchingPlayerError(UruNetError): pass
class UruNetInviteTooManyHoodsError(UruNetError): pass
class UruNetKeyAlreadyUsedError(UruNetError): pass
class UruNetKeyNotFoundError(UruNetError): pass
class UruNetKickedByCcrError(UruNetError): pass
class UruNetLoggedInElsewhereError(UruNetError): pass
class UruNetLoginDeniedError(UruNetError): pass
class UruNetMaxPlayersOnAccountError(UruNetError): pass
class UruNetMustUseGametapClientError(UruNetError): pass
class UruNetNameLookupFailedError(UruNetError): pass
class UruNetNeedToPayError(UruNetError): pass
class UruNetNotSupportedError(UruNetError): pass
class UruNetOldBuildIdError(UruNetError): pass
class UruNetPlayerAlreadyExistsError(UruNetError): pass
class UruNetPlayerNameInvalidError(UruNetError): pass
class UruNetPlayerNotFoundError(UruNetError): pass
class UruNetRemoteShutdownError(UruNetError): pass
class UruNetScoreAlreadyExistsError(UruNetError): pass
class UruNetScoreNoDataFoundError(UruNetError): pass
class UruNetScoreNotEnoughPointsError(UruNetError): pass
class UruNetScoreWrongTypeError(UruNetError): pass
class UruNetServerBusyError(UruNetError): pass
class UruNetServiceForbiddenError(UruNetError): pass
class UruNetStateObjectNotFoundError(UruNetError): pass
class UruNetTimeoutError(UruNetError): pass
class UruNetTimeoutOdbcError(UruNetError): pass
class UruNetTooManyFailedLoginsError(UruNetError): pass
class UruNetVaultNodeAccessViolationError(UruNetError): pass
class UruNetVaultNodeNotFoundError(UruNetError): pass

error_lut = {
    NetError.account_already_exists: UruNetAccountAlreadyExistsError,
    NetError.account_banned: UruNetAccountBannedError,
    NetError.account_not_activated: UruNetAccountNotActivatedError,
    NetError.account_not_found: UruNetAccountNotFoundError,
    NetError.activation_code_not_found: UruNetActivationCodeNotFoundError,
    NetError.age_not_found: UruNetAgeNotFoundError,
    NetError.auth_token_too_old: UruNetAuthTokenTooOldError,
    NetError.authentication_failed: UruNetAuthenticationFailedError,
    NetError.bad_server_data: UruNetBadServerDataError,
    NetError.circular_reference: UruNetCircularReferenceError,
    NetError.connect_failed: UruNetConnectFailedError,
    NetError.disconnected: UruNetDisconnectedError,
    NetError.file_not_found: UruNetFileNotFoundError,
    NetError.gametap_connection_failed: UruNetGametapConnectionFailedError,
    NetError.gametap_missing_parameter: UruNetGametapMissingParameterError,
    NetError.gametap_server_error: UruNetGametapServerError,
    NetError.gametap_too_many_auth_options: UruNetGametapTooManyAuthOptionsError,
    NetError.internal_error: UruNetInternalError,
    NetError.invalid_parameter: UruNetInvalidParameterError,
    NetError.invite_no_matching_player: UruNetInviteNoMatchingPlayerError,
    NetError.invite_too_many_hoods: UruNetInviteTooManyHoodsError,
    NetError.key_already_used: UruNetKeyAlreadyUsedError,
    NetError.key_not_found: UruNetKeyNotFoundError,
    NetError.kicked_by_ccr: UruNetKickedByCcrError,
    NetError.logged_in_elsewhere: UruNetLoggedInElsewhereError,
    NetError.login_denied: UruNetLoginDeniedError,
    NetError.max_players_on_account: UruNetMaxPlayersOnAccountError,
    NetError.must_use_gametap_client: UruNetMustUseGametapClientError,
    NetError.name_lookup_failed: UruNetNameLookupFailedError,
    NetError.need_to_pay: UruNetNeedToPayError,
    NetError.not_supported: UruNetNotSupportedError,
    NetError.old_build_id: UruNetOldBuildIdError,
    NetError.player_already_exists: UruNetPlayerAlreadyExistsError,
    NetError.player_name_invalid: UruNetPlayerNameInvalidError,
    NetError.player_not_found: UruNetPlayerNotFoundError,
    NetError.remote_shutdown: UruNetRemoteShutdownError,
    NetError.score_already_exists: UruNetScoreAlreadyExistsError,
    NetError.score_no_data_found: UruNetScoreNoDataFoundError,
    NetError.score_not_enough_points: UruNetScoreNotEnoughPointsError,
    NetError.score_wrong_type: UruNetScoreWrongTypeError,
    NetError.server_busy: UruNetServerBusyError,
    NetError.service_forbidden: UruNetServiceForbiddenError,
    NetError.state_object_not_found: UruNetStateObjectNotFoundError,
    NetError.timeout: UruNetTimeoutError,
    NetError.timeout_odbc: UruNetTimeoutOdbcError,
    NetError.too_many_failed_logins: UruNetTooManyFailedLoginsError,
    NetError.vault_node_access_violation: UruNetVaultNodeAccessViolationError,
    NetError.vault_node_not_found: UruNetVaultNodeNotFoundError,
}
