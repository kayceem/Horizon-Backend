from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
        
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    contact_number: int

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: datetime

    class Config:
        orm_mode = True
        
class UserLogin(BaseModel):
    email:EmailStr
    password:str
    
class Token(BaseModel):
    token:str
    token_type:str

class TokenData(BaseModel):
    id: str

class ProductBase(BaseModel):
    title: str
    price:float
    description: Optional[str]=None
    image_url: Optional[str]=None
    
    class Config:
        orm_mode = True
    
class ProductCreate(ProductBase):
    category_id: int

class ProductResponse(ProductBase):
    id:int
    user_id: int