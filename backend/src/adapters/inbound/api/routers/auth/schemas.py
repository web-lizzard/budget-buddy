from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    # Consider adding other fields returned by UserService.create_user if any


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class NewAccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# For login, we'd typically use OAuth2PasswordRequestForm = Depends()
# but for direct email/password in JSON body, we define a Pydantic model.
class UserLogin(BaseModel):
    email: EmailStr
    password: str
