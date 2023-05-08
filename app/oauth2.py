import schemas
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "45sadsa4d4qw4e54gfsdf4asadgfhdtrvcertjdfhmfvcnbc"
ALGORITHM ="HS256"
TOKEN_EXPIRY_MINUTES = 30

oauth_schema = OAuth2PasswordBearer(tokenUrl='login')

def create_token(data:dict):
    to_encode= data.copy()
    expire = datetime.utcnow()+timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)
    return encoded_jwt

def verify_token(token:str, credentials_exceptions):
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        id = payload.get('user_id')
        if id is None:
            raise credentials_exceptions
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exceptions
    return token_data

def get_current_user(token=Depends(oauth_schema)):
        credentials_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                               detail="Could not verify credentials",
                                               headers={"WWW-Authenticate":"Bearer"})
        return verify_token(token, credentials_exceptions)