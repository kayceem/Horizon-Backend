from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from datetime import datetime
import re
from fastapi.param_functions import Form
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


class UserChangePassword(OAuth2PasswordRequestForm):
        username: str = Form(),
        password: str = Form(),
        new_password: str = Form(),
        def __init__(
            self,
            username: str = Form(),
            password: str = Form(),
            new_password: str = Form(),
    ):
            self.username = username
            self.password = password
            self.new_password = new_password

        @validator('new_password')
        def validate_password(cls, v):
            if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]', v):
                raise ValueError('Password must contain at least one uppercase letter, one digit, and one special character')
            return v

class UserBase(BaseModel):
    username:str = Field(min_length=4, max_length=25)
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
    rating: Optional[str]

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    contact_number: int
    @validator('contact_number')
    def validate_contact_number(cls, v):
        if len(str(v)) != 10:
            raise ValueError('Contact number must be a 10-digit integer')
        return v

class UserResponseLoggedIn(UserResponse):
    contact_number: int

        
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    token: str
    token_type: str


class TokenData(BaseModel):
    id: str


class ProductBase(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    price: float
    description: Optional[str] = None
    category_id: Optional[int] = None
    image_url:Optional[str]=None
    available:Optional[bool]=True
    condition:Optional[str]=None


class ProductCreate(ProductBase):
    pass

class AdCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    provider: str
    sub_title: Optional[str] = None
    image_url:str
class AdResponse(AdCreate):
    id :int
    created_at : datetime
    class Config:
        orm_mode = True

class ProductCreateResponse(ProductBase):
    id: int
    user_id: int
    views:int
    user: UserResponse
    
    class Config:
        orm_mode = True

class ProductResponse(ProductCreateResponse):
    wishlisted: bool


class ProductResponseNoUser(ProductBase):
    id: int
    views: int
    
    class Config:
        orm_mode = True

class WishListItem(BaseModel):
    product_id:int
        
class WishListItemResponse(ProductResponse):
    created_at: datetime

        
class MessageCreate(BaseModel):
    receiver_username: str
    content: str

class MessageResponse(BaseModel):
    id: int
    first_name:str
    last_name:str
    username:str
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime
    sent:bool
    read:bool

    class Config:
        orm_mode = True

class ReviewCreate(BaseModel):
    reviewee_id: int
    rating: int
    comment: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v>5 or v<0:
            raise ValueError('Rating must be 1 to 5')
        return v

class ReviewResponse(BaseModel):
    id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
class ReviewResponseProfile(ReviewResponse):
    reviewer_username: str

class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(CategoryCreate):
    id: int
    class Config:
        orm_mode = True