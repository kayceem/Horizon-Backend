import utils, oauth2
from typing import List
from database import get_db
import schemas,utils, models
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, APIRouter

router = APIRouter(
    prefix='/users',
    tags=['Users']
    
)

    
@router.get('/', response_model=List[schemas.UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users =db.query(models.User).all()
    return users

@router.get('/{id}', response_model=schemas.UserResponse)
async def get_user(id:int, db: Session = Depends(get_db)):
    user = utils.check_user(db=db, id=id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    conflicts = utils.check_conflicts(db=db,
                                   username=user.username,
                                   email=user.email,
                                   contact_number=user.contact_number)
    if conflicts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=conflicts)
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict()) #Unpcak dictionary
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: Session = Depends(get_db), user_id : int =  Depends(oauth2.get_current_user)):
    user = utils.check_user(db=db, id=user_id.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()