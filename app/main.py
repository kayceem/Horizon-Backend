from fastapi import FastAPI, Depends, status, HTTPException
from typing import Optional
import uvicorn
import models as models
from database import engine, get_db
from pydantic import BaseModel
import pymysql
from pymysql.cursors import DictCursor


try:
    # Create all the tables
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(e)
    
class User(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    contact_number: int

try:
    conn = pymysql.connect(host='localhost', 
                           database='webuy',
                           user='wbuser',
                           password='webuyuser',
                           cursorclass=DictCursor)
    cursor = conn.cursor()
    print("Connection Success!")
except Exception as e:
    print(e)


app = FastAPI()

@app.get('/')
async def home():
    return {"message":"OK"}

@app.get('/users')
async def get_users():
    cursor.execute("""SELECT * FROM user LIMIT 10""")
    users = cursor.fetchall()
    return {"data":users}


@app.get('/users/{id}')
async def get_user(id:int):
    cursor.execute("""SELECT * FROM user WHERE id = %s""",(id))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message":user}

@app.post('/users', status_code=status.HTTP_201_CREATED)
async def create_users(user: User):
    cursor.execute("""INSERT INTO user (username,email,password_hash,contact_number) VALUES (%s, %s, %s, %s)""",
                   (user.username, user.email, user.password, user.contact_number))
    user = cursor.fetchone()
    conn.commit()
    return {"message":user}

@app.delete('/users/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id:int):
    cursor.execute("""DELETE FROM user WHERE id = %s""",(id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = cursor.fetchone()
    conn.commit()



if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        reload=True
    )