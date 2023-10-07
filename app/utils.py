import models
from sqlalchemy.sql.expression import or_, desc
from passlib.context import CryptContext
from sqlalchemy.orm import Session

passwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def hash(passwd:str):
    return passwd_context.hash(passwd)

def verify(passwd, hashed_passwd):
    return passwd_context.verify(passwd,hashed_passwd)

def check_user(db:Session, id:str):
    user = db.query(models.User).filter(or_(models.User.id == id,
                                            models.User.username == id)).first()
    return user
        
def check_conflicts(db: Session,
                    current_user: models.User,
                    username:str=None,
                    email:str=None,
                    contact_number:int=None,
                    **kwargs):
    existing_user = db.query(models.User).filter(or_(models.User.username == username,
                                                     models.User.email == email,
                                                     models.User.contact_number == contact_number)).first()
    if not existing_user:
        return None

    conflict = {}
    if current_user:
        if existing_user.username == username and current_user.username != existing_user.username:
            conflict['username'] = username
        if existing_user.email == email and current_user.email != existing_user.email:
            conflict['email'] = email
        if existing_user.contact_number == contact_number and current_user.contact_number != existing_user.contact_number:
            conflict['contact_number'] = contact_number
        return conflict
    if existing_user.username == username:
        conflict['username'] = username
    if existing_user.email == email:
        conflict['email'] = email
    if existing_user.contact_number == contact_number:
        conflict['contact_number'] = contact_number
    return conflict

def get_rating(user_id, 
               db:Session
               ):
    received_reviews = (db.query(models.Review)
                        .filter(models.Review.reviewee_id == user_id)
                        .order_by(desc(models.Review.created_at))
                        .all()
                    )       
    average_rating = sum(review.rating for review in received_reviews) / len(received_reviews) if received_reviews else 0.0
    return round(average_rating,1)