from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, BigInteger, Text
from sqlalchemy.sql.expression import  text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
# from database import engine


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    contact_number = Column(BigInteger, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),nullable=False)
    last_login = Column(TIMESTAMP(timezone=True), server_default=text('CURRENT_TIMESTAMP'), nullable=False)

class Category(Base):
    __tablename__ = 'category'  
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),nullable=False)

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    title = Column(String(255))
    description = Column(Text)
    price = Column(Numeric(10,2))
    image_url = Column(String(255))
    views = Column(Integer, default=0)
    user = relationship('User', backref='product')
    category = relationship('Category', backref='product')
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),nullable=False)

class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('user.id'))
    receiver_id = Column(Integer, ForeignKey('user.id'))
    content = Column(Text)
    sender = relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('CURRENT_TIMESTAMP'), nullable=False)

class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_id = Column(Integer, ForeignKey('user.id'))
    reviewee_id = Column(Integer, ForeignKey('user.id'))
    rating = Column(Integer)
    comment = Column(Text)
    reviewer = relationship('User', foreign_keys=[reviewer_id])
    reviewee = relationship('User', foreign_keys=[reviewee_id])
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('CURRENT_TIMESTAMP'), nullable=False)

class WishListItem(Base):
    __tablename__ = 'wish_list_item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    user = relationship('User', backref='wish_list_item')
    product = relationship('Product', backref='wish_list_item')
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    
# Base.metadata.create_all(bind=engine)

