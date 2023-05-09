from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    email: EmailStr
    password: str
    contact_number: int


class UserResponse(UserBase):
    id: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime

        
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    token: str
    token_type: str


class TokenData(BaseModel):
    id: str


class ProductBase(BaseModel):
    title: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None

    class Config:
        orm_mode = True


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    user_id: int
    views:int
    user: UserBase

class ProductResponseNoUser(ProductBase):
    id: int
    views: int
