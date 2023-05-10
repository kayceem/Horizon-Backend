import utils
import oauth2
from typing import List
from database import get_db
import schemas
import utils
import models
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, APIRouter

router = APIRouter(
    prefix='/wishlist',
    tags=['WishList']

)

@router.get('/', response_model=List[schemas.WishListItemResponse])
def get_wishlist(db:Session=Depends(get_db),
                 current_user=Depends(oauth2.get_current_user)
                 ):
    return current_user.wish_list_items

@router.post('/', status_code=status.HTTP_201_CREATED)
def add_to_wishlist(wish_list_item: schemas.WishListItem,
                    db:Session= Depends(get_db),
                    current_user=Depends(oauth2.get_current_user)):
    product = db.query(models.Product).filter(models.Product.id==wish_list_item.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product doesnot exists")

    existing_wish_list_item = db.query(models.WishListItem).filter_by(user_id=current_user.id, product_id=product.id).first()
    if existing_wish_list_item:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Already in wishlist")
    new_wish_list_item = models.WishListItem(user_id=current_user.id, product_id=product.id)
    db.add(new_wish_list_item)
    db.commit()
    return {"message": "Added to wishlist"}


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(wish_list_item: schemas.WishListItem,
                    db:Session= Depends(get_db),
                    current_user=Depends(oauth2.get_current_user)):

    item_to_remove = db.query(models.WishListItem).filter_by(user_id=current_user.id, product_id=wish_list_item.product_id).first()
    if not item_to_remove:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not in wishlist")
    db.delete(item_to_remove)
    db.commit()

