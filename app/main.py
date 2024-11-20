import uvicorn
from app import models
from app.database import engine
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import auth, message, user, product, wish_list, review, image, search, category, ad
from app.config import settings

# Create all the tables
models.Base.metadata.create_all(bind=engine)

#  Initialize FastAPI
app = FastAPI()
origins = settings.ALLOWED_ORIGINS.split(",")
app.mount("/api/static", StaticFiles(directory="app/static/images"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
router.include_router(search.router)
router.include_router(category.router)
router.include_router(ad.router)

@router.get('/')    
async def home():
    return {"message":"OK"}
    
    
app.include_router(router)
# if __name__ == '__main__':
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",  # Listen on all network interfaces inside the container
#         port=8000,       # Expose the port that you have configured in Docker
#         reload=settings.DEBUG  # Enable auto-reload in development
#    