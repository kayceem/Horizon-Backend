from sqlalchemy.orm import Session
from database import get_db
import schemas,utils, models
from fastapi import Depends, status, HTTPException, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
import oauth2
from sqlalchemy import or_

router=APIRouter()

@router.post('/login', response_model=schemas.Token)
def login(user_credentials:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    #  Not using schema fot validating email, password
    # Instead using OAuth2PasswordRequestForm for validation
    user = db.query(models.User).filter(
            or_(models.User.email==user_credentials.username, 
                models.User.username==user_credentials.username)
            ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    # Creating a JWT Token
    token = oauth2.create_token(data={"user_id":user.id,})
    return {"token": token, "token_type":"bearer"}