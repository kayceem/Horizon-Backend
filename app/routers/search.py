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
    prefix='/search',
    tags=['Search']
)

# Search products
@router.get('/', response_model=List[Union[schemas.ProductResponse, schemas.ProductResponseNoUser]])
async def get_products(kwd: Optional[str] = None,
                       min_price: Optional[float]=None,
                       max_price: Optional[float]=None,
                       limit: int = 20,
                       skip:int = 0,
                       sortby: Optional[str] = None,
                       c_id: Optional[int]=None,
                       condition: Optional[str] = None,
                       db: Session = Depends(get_db),
                       current_user = Depends(oauth2.get_optional_current_user)
                       ):

    query_conditions=[models.Product.available==True]

    # Handle keyword search
    if kwd:
        keywords = kwd.split()
        keyword_name_filters = [models.Product.name.ilike(f"%{keyword}%") for keyword in keywords]
        keyword_desc_filters = [models.Product.description.contains(f"%{keyword}%") for keyword in keywords]
        query_conditions.append(or_(*keyword_name_filters, *keyword_desc_filters))

    if condition:
        query_conditions.append(models.Product.condition==condition)
    # Handle price range filtering
    if min_price is not None:
        query_conditions.append(models.Product.price >= min_price)

    if max_price is not None:
        query_conditions.append(models.Product.price <= max_price)

    if c_id is not None:
        query_conditions.append(models.Product.category_id == c_id)

    base_query = db.query(models.Product).filter(and_(*query_conditions))

    if sortby:
        if sortby == "price_asc":
            base_query = base_query.order_by(asc(models.Product.price))
        elif sortby == "price_desc":
            base_query = base_query.order_by(desc(models.Product.price))
        elif sortby == "date_asc":
            base_query = base_query.order_by(asc(models.Product.created_at))
        elif sortby == "date_desc":
            base_query = base_query.order_by(desc(models.Product.created_at))
        elif sortby == "views":
            base_query = base_query.order_by(desc(models.Product.views))

    products = (
        base_query
        .limit(limit)
        .offset(skip)   
        .all()
    )
                    
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No products not found")
    if current_user:
        wish_listed_items = (
            db.query(models.WishListItem)
            .filter(models.WishListItem.user_id==current_user.id)
            .all()
        ) 
        response = [
            schemas.ProductResponse(
                name=product.name,
                price=product.price,
                description=product.description,
                category_id=product.category_id,
                image_url=product.image_url,
                available=product.available,
                id= product.id,
                user_id= product.user_id,
                views=product.views,
                user= product.user,
                condition=product.condition,
                wishlisted= True if product.id in [item.product_id for item in wish_listed_items] else False
        ) for product in products]
    else:
        response = [schemas.ProductResponseNoUser.from_orm(product) for product in products]
    return response