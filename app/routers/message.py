import oauth2
from typing import List
from database import get_db
import schemas
import models
from sqlalchemy.orm import Session
from sqlalchemy import func, case, or_, desc
from fastapi import Depends, status, HTTPException, APIRouter, Response

router = APIRouter(
    prefix='/messages',
    tags=['Messages']
)

# Get latest messages for inbox
@router.get("/inbox", response_model=List[schemas.MessageResponse])
def get_inbox(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    subquery = db.query(
                        case(
                            (models.Message.sender_id == current_user.id, models.Message.receiver_id),
                            else_=models.Message.sender_id
                        ).label("user_id"),
                        func.max(models.Message.created_at).label("latest_created_at")
                    ).filter(
                        or_(models.Message.receiver_id == current_user.id, models.Message.sender_id == current_user.id)
                    ).group_by(
                        "user_id"
                    ).subquery()
    latest_messages = db.query(models.Message, models.User.username).join(
                    subquery,
                    or_(
                        (models.Message.sender_id == current_user.id) & (models.Message.receiver_id == subquery.c.user_id),
                        (models.Message.receiver_id == current_user.id) & (models.Message.sender_id == subquery.c.user_id)
                    ) &
                    (models.Message.created_at == subquery.c.latest_created_at)
                ).join(
                    models.User,
                     or_(
                        (models.Message.sender_id == models.User.id) & (models.Message.sender_id != current_user.id),
                        (models.Message.receiver_id == models.User.id) & (models.Message.receiver_id != current_user.id),
                    )
                ).order_by(desc(models.Message.created_at)).all()
    response_data = [
        schemas.MessageResponse(
            id=message.id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            sent=True if message.sender_id == current_user.id else False,
            content=message.content,
            created_at=message.created_at,
            read= message.read,
            username=username 
        )
        for message, username in latest_messages
    ]
    return response_data

# Get messages with user 
@router.get("/chat/{username}", response_model=List[schemas.MessageResponse])
def get_chat_with_user(username: str,
                       skip:int=0,
                       db: Session = Depends(get_db),
                       current_user=Depends(oauth2.get_current_user)
                       ):
    user= db.query(models.User).filter(models.User.username==username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_id= user.id
    messages = (db.query(models.Message, models.User.username)
        .join(
            models.User,
            or_(
                (models.Message.sender_id == models.User.id) & (models.Message.sender_id != current_user.id),
                (models.Message.receiver_id == models.User.id) & (models.Message.receiver_id != current_user.id),
            )
        )
        .filter(
            (models.Message.sender_id == current_user.id) & (models.Message.receiver_id == user_id) |
            (models.Message.sender_id == user_id) & (models.Message.receiver_id == current_user.id)
        )
        .order_by(desc(models.Message.created_at)).limit(20).offset(skip).all()
    )

    for message, username in messages:
        if message.sender_id == current_user.id: 
            break
        message.read = True
    db.commit()
    
    response_data = [
        schemas.MessageResponse(
            id=message.id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            sent=True if message.sender_id == current_user.id else False,
            content=message.content,
            created_at=message.created_at,
            read= message.read,
            username=username 
        )
        for message, username in messages
    ]

    return response_data



@router.post('/chat', response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(message: schemas.MessageCreate,
                 db: Session = Depends(get_db),
                 current_user = Depends(oauth2.get_current_user)
                 ):
    receiver = db.query(models.User).filter(models.User.username == message.receiver_username).first()
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")

    new_message = models.Message(sender_id=current_user.id, receiver_id=receiver.id, content=message.content)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    response_data = schemas.MessageResponse(
            id=new_message.id,
            sender_id=new_message.sender_id,
            receiver_id=new_message.receiver_id,
            sent=True if new_message.sender_id == current_user.id else False,
            content=new_message.content,
            created_at=new_message.created_at,
            username=receiver.username ,
            read=new_message.read
        )
    return response_data