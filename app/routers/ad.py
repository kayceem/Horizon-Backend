from app.database import get_db
from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app import schemas, models, oauth2
from fastapi import Depends, status, HTTPException, APIRouter

router = APIRouter(
    prefix='/ad',
    tags=['Ads']
)



# Get ads
@router.get('/', response_model=List[schemas.AdResponse])
async def get_ads(
                    db: Session = Depends(get_db),
                    current_user= Depends(oauth2.get_optional_current_user)
                       ):
    ads = (
                db.query(models.Ad)
                .order_by(desc(models.Ad.created_at))
                .all()
            )
    if not ads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No ads found")
    return ads

# Create ad listing
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.AdResponse)
async def create_ad(ad: schemas.AdCreate,
                         db: Session = Depends(get_db),
                         current_user = Depends(oauth2.get_current_user)
                ):
    new_ad = models.Ad(**ad.dict())
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad

# Delete ad listing
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(id: int,
                      db: Session = Depends(get_db),
                      current_user = Depends(oauth2.get_current_user)
                      ):

    ad_query = db.query(models.Ad).filter(
        (models.Ad.id == id))
    ad = ad_query.first()
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    ad_query.delete(synchronize_session=False)
    db.commit()
