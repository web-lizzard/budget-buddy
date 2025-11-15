from datetime import datetime
from enum import Enum
from core import CoreError


class AlreadyRevokedError(CoreError):
    pass


class TokenStatus(Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    REVOKED = "REVOKED"


class RefreshToken:
    _id: str
    _user_id: str
    _session_id: str

    _token_hash: str
    _token_prefix: str
    _created_at: datetime
    _expires_at: datetime
    _status: TokenStatus
    _revoked_at: datetime | None

    def __init__(
        self,
        token_id: str,
        user_id: str,
        session_id: str,
        token_hash: str,
        token_prefix: str,
        created_at: datetime,
        expires_at: datetime,
        status: TokenStatus,
    ):
        self._id = token_id
        self._user_id = user_id
        self._session_id = session_id
        self._token_hash = token_hash
        self._token_prefix = token_prefix
        self._created_at = created_at
        self._expires_at = expires_at
        self._status = status
        self._revoked_at = None

    def set_status(self):
        match self._status:
            case TokenStatus.ACTIVE:
                self._status = TokenStatus.USED
            case TokenStatus.USED:
                self._status = TokenStatus.REVOKED
                self._revoked_at = datetime.now()
            case TokenStatus.REVOKED:
                raise AlreadyRevokedError("Token is already revoked")

    def is_revoked(self) -> bool:
        return self._status == TokenStatus.REVOKED
