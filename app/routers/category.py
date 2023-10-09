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

# Search products
@router.get('/', response_model=List[schemas.CategoryResponse])
async def get_products(db: Session = Depends(get_db),
                       current_user = Depends(oauth2.get_optional_current_user)
                       ):

    categories = db.query(models.Category).all()
    return categories