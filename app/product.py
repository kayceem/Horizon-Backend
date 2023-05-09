from database import get_db
from sqlalchemy.orm import Session
import schemas, models, oauth2, utils
from fastapi import Depends, status, HTTPException, APIRouter
from typing import List, Optional

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

@router.get('/', response_model=List[schemas.ProductResponse])
async def get_products(user_id: Optional[int] = None, db:Session = Depends(get_db)):
    if not user_id:
        products = db.query(models.Product).all()
        return products
    user = utils.check_user(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    products = db.query(models.Product).filter(models.Product.user_id == user.id).all()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products not found")
    return products

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
def get_product(product: schemas.ProductCreate, 
                db:Session = Depends(get_db),
                user_id : int =  Depends(oauth2.get_current_user)
                ):
    product = product.dict()
    product['user_id'] = user_id.id
    new_product = models.Product(**product) #Unpcak dictionary
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# @router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(db: Session = Depends(get_db), user_id : int =  Depends(oauth2.get_current_user)):
#     user = utils.check_user(db=db, id=user_id.id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#     db.delete(user)
#     db.commit()  
    