import uvicorn, models
from database import engine
from fastapi import FastAPI, APIRouter
from routers import auth, message, user, product, wish_list, review

# Create all the tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
router = APIRouter(
    prefix='/api',
    tags=['Root']
    )

router.include_router(user.router)
router.include_router(auth.router)
router.include_router(product.router)
router.include_router(wish_list.router)
router.include_router(message.router)
router.include_router(review.router)

@router.get('/')    
async def home():
    return {"message":"OK"}
    
    
app.include_router(router)
if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        reload=True
    )