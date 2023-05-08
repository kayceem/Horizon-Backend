from database import get_db
from sqlalchemy.orm import Session
import schemas, models, oauth2
from fastapi import Depends, status, HTTPException, APIRouter
from typing import List

router = APIRouter(
    prefix='/products',
    tags=['Products']
)
@router.get('/', response_model=List[schemas.ProductResponse])
async def get_products(db:Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
def get_product(product: schemas.ProductCreate, db:Session = Depends(get_db),user_id : int =  Depends(oauth2.get_current_user)):
    product = product.dict()
    product['user_id'] = user_id.id
    new_product = models.Product(**product) #Unpcak dictionary
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product
    
    