from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str


class UserRead(BaseModel):
    id: int
    email: str
    role: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
