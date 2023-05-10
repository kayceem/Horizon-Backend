from jose import jwt, JWTError
import schemas, database, models
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from config import settings
from typing import Optional
from fastapi import Request

# Secret Key used to hash info
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
TOKEN_EXPIRY_MINUTES = settings.token_expiry_minutes

oauth_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_token(data:dict):
    to_encode= data.copy()
    expire = datetime.utcnow()+timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    to_encode.update({"exp":expire})
    # Signing JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)
    return encoded_jwt

def verify_token(token:str, credentials_exceptions, expired_exceptions, required:bool):
    try:
        # Decoding JWT
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        id = payload.get('user_id')
        # Check is token has id
        if id is None:
            raise credentials_exceptions
        # Create a token_data class with TokenData Schema
        token_data = schemas.TokenData(id=id)
    # Checks expiry of token
    except jwt.ExpiredSignatureError:
        if required:
            raise expired_exceptions
        return None
    # Checks invalid credentials 
    except JWTError as e:
        raise credentials_exceptions
    return token_data

def get_current_user(request:Request, db: Session =Depends(database.get_db), required=True):
        credentials_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                               detail="Could not validate credentials",
                                               headers={"WWW-Authenticate":"Bearer"})
        expired_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Token has expired")
        login_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                               detail="User not logged in")

        token = request.cookies.get("access_token")
        
        # Handels if no token is provided and is not required to be logged in
        if not token and not required:
            return None
        
        # Handels if no token is provided but user must be logged in
        if not token:
            raise login_exception
            
        token = verify_token(token, credentials_exceptions, expired_exception, required)
        
        # Handels for token expiry
        if not token:
            return None

        user = db.query(models.User).filter(models.User.id == token.id).first()
        # Handels if user doesnot exists
        if not user:
            raise credentials_exceptions
        return user
    
def get_optional_current_user(request:Request, db: Session = Depends(database.get_db)):
    return get_current_user(request, db, required=False)
