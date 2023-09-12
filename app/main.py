import uvicorn, models
from database import engine
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth, message, user, product, wish_list, review, image

# Create all the tables
models.Base.metadata.create_all(bind=engine)
#  Initialize FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static/Images"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
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
router.include_router(image.router)

@router.get('/')    
async def home():
    return {"message":"OK"}
    
    
app.include_router(router)
if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        reload=True
    )