import uuid


class AccessToken:
    _sub: str
    _iat: int
    _exp: int
    _iss: str
    _jti: str

    def __init__(self, sub: str, iat: int, exp: int, iss: str, jti: str | None = None):
        self._sub = sub
        self._iat = iat
        self._exp = exp
        self._iss = iss
        self._jti = jti or str(uuid.uuid4())

    def __str__(self):
        return f"AccessToken(sub={self._sub}, iat={self._iat}, exp={self._exp}, iss={self._iss}, jti={self._jti})"
