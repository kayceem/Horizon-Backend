from sqlalchemy.orm import Session
from database import get_db
import schemas,utils, models
from fastapi import Depends, status, HTTPException, APIRouter, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
import oauth2
from sqlalchemy.sql.expression import or_
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
router=APIRouter(
    tags=['Login']
)

# Login user 
@router.post('/login', response_model=schemas.Token)
def login(user_credentials:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    #  Not using schema for validating email, password
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
    token = oauth2.create_token(data={"user_id":user.id,"username":user.username})
    
    response = JSONResponse(content={"access_token": token, "token_type": "bearer"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=oauth2.TOKEN_EXPIRY_MINUTES * 60,  # Token expiration in seconds
        # expires=datetime.now(timezone.utc)+ timedelta(minutes=oauth2.TOKEN_EXPIRY_MINUTES),
        samesite="none",
        secure=True,  # Uncomment this line for HTTPS only
    )
    return response

@router.post("/logout")
async def logout(response: Response, current_user: models.User = Depends(oauth2.get_current_user)):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}