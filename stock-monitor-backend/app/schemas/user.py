from pydantic import BaseModel
from datetime import datetime

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    """用户创建请求模型"""
    username: str
    password: str
    email: str | None = None

class UserUpdatePassword(BaseModel):
    """修改密码请求模型"""
    new_password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
