import uvicorn
import models 
from database import engine
from fastapi import FastAPI
import user, auth, product

try:
    # Create all the tables
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(e)

app = FastAPI()

app.include_router(user.router)
app.include_router(product.router)
app.include_router(auth.router)

@app.get('/')
async def home():
    return {"message":"OK"}
    
    
if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        reload=True
    )