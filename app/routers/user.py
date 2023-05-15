import utils
import oauth2
from typing import List
from database import get_db
import schemas
import utils
import models
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, APIRouter, Response

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
async def get_user_by_id(user_id: int,
                   db: Session = Depends(get_db), 
                   current_user: models.User = Depends(oauth2.get_current_user)):
    user = utils.check_user(db=db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# Create user
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_optional_current_user)
                      ):
    if current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Logout to create a new account")

    conflicts = utils.check_conflicts(db, **user.dict())

    if conflicts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=conflicts)
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())  # Unpcak dictionary
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Update User
@router.put('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def update_user(update_user : schemas.UserCreate,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)
                      ):
    conflicts = utils.check_conflicts(db, **update_user.dict())
    if conflicts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=conflicts)
    update_user.password = utils.hash(update_user.password)
    db.query(models.User).filter(models.User.id==current_user.id).update(update_user.dict(), synchronize_session=False)
    db.commit()
    db.refresh(current_user)
    return current_user
    
# Delete User
@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(response:Response,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):
    response.delete_cookie(key="access_token")
    db.delete(current_user)
    db.commit()

