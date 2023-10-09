from app.database import get_db
from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, asc, desc, case
from app import schemas, models, oauth2, utils
from fastapi import Depends, status, HTTPException, APIRouter


from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy import literal

router = APIRouter(
    prefix='/category',
    tags=['Category']
)

# Get categories
@router.get('/', response_model=List[schemas.CategoryResponse])
async def get_categories(db: Session = Depends(get_db),
                       current_user = Depends(oauth2.get_optional_current_user)
                       ):

    categories = db.query(models.Category).all()
    return categories

# Get categories
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.CategoryResponse)
async def create_category(
                        category:schemas.CategoryCreate,
                        db: Session = Depends(get_db),
                        current_user = Depends(oauth2.get_current_user)
                       ):

    existing_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if existing_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Category already exists')
    new_category = models.Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


# Delete category
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(  id: int,
                        db: Session = Depends(get_db),
                        current_user = Depends(oauth2.get_current_user)):
    existing_category = db.query(models.Category).filter(models.Category.id == id).first()
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.delete(existing_category)
    db.commit()