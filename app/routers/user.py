import utils
import oauth2
from typing import List
from database import get_db
import schemas
import utils
import models
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, APIRouter, Response
from fastapi.responses import JSONResponse




router = APIRouter(
    prefix='/users',
    tags=['Users']

)

# Get all users
@router.get('/', response_model=List[schemas.UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

# Get user with id
@router.get('/{user_id}', response_model=schemas.UserResponse)
async def get_user_by_id(user_id: str,
                   db: Session = Depends(get_db), 
                   current_user: models.User = Depends(oauth2.get_current_user)):
    user = utils.check_user(db=db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = schemas.UserResponse.from_orm(user).dict()
    user['created_at'] =user['created_at'].isoformat()
    user['updated_at'] =user['updated_at'].isoformat()
    user['rating'] = utils.get_rating(user['id'], db)
    return user



# Create user
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_optional_current_user)
                      ):
    if current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Logout to create a new account")

    conflicts = utils.check_conflicts(db, current_user, **user.dict())

    if conflicts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=conflicts)
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())  # Unpcak dictionary
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Update Password
@router.put('/password', response_model=schemas.UserResponse)
def change_password(user_credentials:schemas.UserChangePassword = Depends(), 
                        db: Session = Depends(get_db),
                        current_user = Depends(oauth2.get_current_user)
                ):
    #  Not using schema for validating email, password
    # Instead using OAuth2PasswordRequestForm for validation
    user = db.query(models.User).filter(models.User.id==current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user.password = utils.hash(user_credentials.new_password)
    db.commit()
    db.refresh(user)
    # Creating a JWT Token
    token = oauth2.create_token(data={"user_id":user.id,"username":user.username})
    response = JSONResponse({'detail':'success'})
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

# Update User
@router.put('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponseLoggedIn)
async def update_user(update_user : schemas.UserUpdate,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)
                      ):
    conflicts = utils.check_conflicts(db, current_user, **update_user.dict())
    if conflicts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=conflicts)
    db.query(models.User).filter(models.User.id==current_user.id).update(update_user.dict(), synchronize_session=False)
    db.commit()
    db.refresh(current_user)
    user = schemas.UserResponseLoggedIn.from_orm(current_user).dict()
    user['rating'] = utils.get_rating(current_user.id, db)
    return user



# Delete User
@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(response:Response,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):
    response.delete_cookie(key="access_token")
    db.delete(current_user)
    db.commit()

