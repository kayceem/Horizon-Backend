import schemas
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

# Secret Key used to hash info
SECRET_KEY = "45sadsa4d4qw4e54gfsdf4asadgfhdtrvcertjdfhmfvcnbc"
ALGORITHM ="HS256"
TOKEN_EXPIRY_DAYS = 2
# TOKEN_EXPIRY_HOURS = 12
# TOKEN_EXPIRY_SECONDS = 30

oauth_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_token(data:dict):
    to_encode= data.copy()
    expire = datetime.utcnow()+timedelta(days=TOKEN_EXPIRY_DAYS)
    to_encode.update({"exp":expire})
    ########################################################################################
    ######## print(to_encode)   ############################################################
    ######## {'user_id': 103, 'exp': datetime.datetime(2023, 5, 9, 4, 21, 4, 294369)} ######
    ########################################################################################
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

def get_current_user(token=Depends(oauth_scheme)):
        credentials_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                               detail="Could not verify credentials",
                                               headers={"WWW-Authenticate":"Bearer"})
        return verify_token(token, credentials_exceptions)