from pydantic import BaseModel


class RequestCodeRequest(BaseModel):
    phone_number: str


class RequestCodeResponse(BaseModel):
    message: str
    telegram_url: str


class VerifyCodeRequest(BaseModel):
    phone_number: str
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"