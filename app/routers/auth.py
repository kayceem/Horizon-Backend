from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas,utils, models, oauth2
from fastapi import Depends, status, HTTPException, APIRouter, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.sql.expression import or_
from fastapi.responses import JSONResponse

router=APIRouter(
    tags=['Login']
)

# Login user 
@router.post('/login', response_model=schemas.UserResponseLoggedIn)
def login(user_credentials:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    #  Not using schema for validating email, password
    # Instead using OAuth2PasswordRequestForm for validation
    user = db.query(models.User).filter(
            or_(models.User.email==user_credentials.username, 
                models.User.username==user_credentials.username)
            ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Creating a JWT Token
    token = oauth2.create_token(data={"user_id":user.id,"username":user.username})
    response_data = schemas.UserResponseLoggedIn.from_orm(user).dict()
    response_data['created_at'] =user.created_at.isoformat()
    response_data['updated_at'] =user.updated_at.isoformat()
    response_data['rating'] = utils.get_rating(user.id, db)
    response = JSONResponse(response_data)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=False,
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