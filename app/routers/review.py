from typing import List
from app.database import get_db
from app import schemas
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app import utils, oauth2, utils, models
from fastapi import Depends, status, HTTPException, APIRouter, Response

router = APIRouter(
    prefix='/reviews',
    tags=['Reviews']
)

@router.get("/received", response_model=List[schemas.ReviewResponse])
def get_received_reviews(db: Session = Depends(get_db),
                         current_user=Depends(oauth2.get_current_user)
                         ):
    received_reviews = (db.query(models.Review)
                        .filter(models.Review.reviewee_id == current_user.id)
                        .order_by(desc(models.Review.created_at))
                        .all()
                        )
    return received_reviews

@router.get("/received/{user_id}", response_model=List[schemas.ReviewResponseProfile])
def get_received_reviews_user(user_id:int,
                              db: Session = Depends(get_db),
                              current_user=Depends(oauth2.get_current_user)
                              ):
    user = utils.check_user(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    received_reviews = (db.query(models.Review)
                        .filter(models.Review.reviewee_id == user_id)
                        .order_by(desc(models.Review.created_at))
                        .all()
                        )
    users = db.query(models.User).all()

    received_reviews = [
        schemas.ReviewResponseProfile(
            id = review.id,
            reviewer_id = review.reviewer_id,
            reviewee_id = review.reviewee_id,
            rating = review.rating,
            comment = review.comment,
            created_at = review.created_at,
             reviewer_username=(next(user.username for user in users if user.id == review.reviewer_id))
            ) 
            for review in received_reviews
    ]
    return received_reviews

@router.get("/given", response_model=List[schemas.ReviewResponse])
def get_given_reviews(db: Session = Depends(get_db),
                      current_user=Depends(oauth2.get_current_user)
                      ):
    given_reviews = (db.query(models.Review)
                     .filter(models.Review.reviewer_id == current_user.id)
                     .order_by(desc(models.Review.created_at))
                     .all()
                     )
    return given_reviews

@router.post("/", response_model=schemas.ReviewResponse)
def create_review(review: schemas.ReviewCreate,
                  db: Session = Depends(get_db),
                  current_user=Depends(oauth2.get_current_user)
                  ):
    reviewee = utils.check_user(db=db, id=review.reviewee_id)
    if not reviewee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_review = models.Review(reviewer_id=current_user.id,
                               reviewee_id=reviewee.id,
                               rating= review.rating,
                               comment=review.comment)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review
