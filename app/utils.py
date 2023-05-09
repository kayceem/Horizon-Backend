import models
from sqlalchemy.sql.expression import or_
from passlib.context import CryptContext
from sqlalchemy.orm import Session

passwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def hash(passwd:str):
    return passwd_context.hash(passwd)

def verify(passwd, hashed_passwd):
    return passwd_context.verify(passwd,hashed_passwd)

def check_conflicts(db: Session,
                      username:str=None,
                      email:str=None,
                      contact_number:int=None,
                      ):
    existing_user = db.query(models.User).filter(or_(models.User.username == username,
                                                     models.User.email == email,
                                                     models.User.contact_number == contact_number)).first()
    if not existing_user:
        return None

    conflict = {}
    if existing_user.username == username:
        conflict['username'] = username
    if existing_user.email == email:
        conflict['email'] = email
    if existing_user.contact_number == contact_number:
        conflict['contact_number'] = contact_number
    return conflict

def check_user(db:Session, id:int):
    user = db.query(models.User).filter(models.User.id == id).first()
    return user
    