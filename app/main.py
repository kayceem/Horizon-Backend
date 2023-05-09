import uvicorn
import models 
from database import engine
from fastapi import FastAPI, APIRouter
import user, auth, product

try:
    # Create all the tables
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(e)

app = FastAPI()
router = APIRouter(
    prefix='/api',
    tags=['Root']
    )

router.include_router(user.router)
router.include_router(auth.router)
router.include_router(product.router)

@router.get('/')    
async def home():
    return {"message":"OK"}
    
    
app.include_router(router)
if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        reload=True
    )