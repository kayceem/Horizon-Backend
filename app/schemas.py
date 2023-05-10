from pydantic import BaseModel, EmailStr, validator, Field, constr, conint
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    username:str = Field(min_length=4, max_length=15)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode = True
        
    @validator('username')
    def validate_username(cls, v):
        if ' ' in v:    
            raise ValueError('Cannot contain a spaces')
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()

class UserCreate(UserBase):
    email: EmailStr
    password:str = Field(min_length=8,max_length=32)
    contact_number: int
    
    @validator('contact_number')
    def validate_contact_number(cls, v):
        if len(str(v)) != 10:
            raise ValueError('Contact number must be a 10-digit integer')
        return v
    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]', v):
            raise ValueError('Password must contain at least one uppercase letter, one digit, and one special character')
        return v

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
    title: str = Field(min_length=4, max_length=255)
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


class WishListItem(BaseModel):
    product_id:int
        
class WishListItemResponse(BaseModel):
    product:ProductResponseNoUser
    class Config:
        orm_mode = True 