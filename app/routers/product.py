from database import get_db
from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_
import schemas, models, oauth2, utils
from fastapi import Depends, status, HTTPException, APIRouter, UploadFile, File

router = APIRouter(
    prefix='/products',
    tags=['Products']
)

# Get products
@router.get('/', response_model=List[Union[schemas.ProductResponse, schemas.ProductResponseNoUser]])
async def get_products(user_id: Optional[int] = None,
                       limit: int = 20,
                       skip:int = 0,
                       search:Optional[str]="", 
                       db: Session = Depends(get_db),
                       current_user:Optional[dict] = Depends(oauth2.get_optional_current_user)
                       ):

    query_conditions=[models.Product.name.contains(search)]
    if user_id:
        user = utils.check_user(db=db, id=user_id)
        query_conditions.append(models.Product.user_id == user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    products = (
                db.query(models.Product)
                .filter(and_(*query_conditions))
                .limit(limit=limit)
                .offset(skip)
                .all()
                )
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No products not found")
    if current_user:
        response = [schemas.ProductResponse.from_orm(product) for product in products]
    else:
        response = [schemas.ProductResponseNoUser.from_orm(product) for product in products]
    return response

# Get product
@router.get('/{id}', response_model=Union[schemas.ProductResponse, schemas.ProductResponseNoUser])
async def get_product(id,
                       db: Session = Depends(get_db),
                       current_user = Depends(oauth2.get_optional_current_user)
                       ):
    product = db.query(models.Product).filter(models.Product.id == id).first()

        
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No product not found")
    if current_user:
        response = schemas.ProductResponse.from_orm(product)
    else:
        response = schemas.ProductResponseNoUser.from_orm(product)
        
    if current_user:
        product.views+=1
        db.commit()
        db.refresh(product)
    return response


# Create product listing
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate,
                         db: Session = Depends(get_db),
                         current_user = Depends(oauth2.get_current_user)
                ):
    new_product = models.Product(
        user_id=current_user.id, **product.dict())  # Unpcak dictionary
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# Update product listing
@router.put('/{id}', status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
async def update_product(id: int,
                         updated_product: schemas.ProductCreate,
                         db: Session = Depends(get_db),
                         current_user = Depends(oauth2.get_current_user)
                   ):
    product_query = db.query(models.Product).filter(models.Product.id == id)
    product = product_query.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product doesnot exixts")
    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
    product_query.update(updated_product.dict(), synchronize_session=False)
    db.commit()
    db.refresh(product)
    return product


# Delete product listing
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id: int,
                      db: Session = Depends(get_db),
                      current_user = Depends(oauth2.get_current_user)
                      ):

    product_query = db.query(models.Product).filter(
        (models.Product.id == id))
    product = product_query.first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")

    product_query.delete(synchronize_session=False)
    db.commit()
