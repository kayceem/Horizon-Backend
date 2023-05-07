from fastapi import FastAPI, Depends
import uvicorn
import models
from database import engine, get_db

try:
    # Create all the tables
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(e)
app = FastAPI()

@app.get('/')
def home():
    return "OK"

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        reload=True
    )