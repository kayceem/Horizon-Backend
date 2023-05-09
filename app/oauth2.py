from jose import jwt, JWTError
import schemas, database, models
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from config import settings

# Secret Key used to hash info
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
TOKEN_EXPIRY_MINUTES = settings.token_expiry_minutes

oauth_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_token(data:dict):
    to_encode= data.copy()
    expire = datetime.utcnow()+timedelta(days=TOKEN_EXPIRY_MINUTES)
    to_encode.update({"exp":expire})
    # Signing JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)
    return encoded_jwt

def verify_token(token:str, credentials_exceptions):
    try:
        # Decoding JWT
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        id = payload.get('user_id')
        # Check is token has id
        if id is None:
            raise credentials_exceptions
        # Create a token_data class with TokenData Schema
        token_data = schemas.TokenData(id=id)
    except JWTError as e:
        raise credentials_exceptions
    return token_data

def get_current_user(token=Depends(oauth_scheme), db: Session =Depends(database.get_db)):
        credentials_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                               detail="Could not validate credentials!",
                                               headers={"WWW-Authenticate":"Bearer"})
        token = verify_token(token, credentials_exceptions)
        user = db.query(models.User).filter(models.User.id == token.id).first()
        if user == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User doesnot exists")
        return user