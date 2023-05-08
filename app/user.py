from sqlalchemy.orm import Session
from database import get_db
import schemas,utils, models
from fastapi import Depends, status, HTTPException, APIRouter
from typing import List

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
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict()) #Unpcak dictionary
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id:int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    ##################################
    ####   Write code to delete   ####
    ##################################