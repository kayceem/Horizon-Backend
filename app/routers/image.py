from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter, UploadFile, File
from app import oauth2
from fastapi.responses import JSONResponse
from typing import Optional
from PIL import Image
from io import BytesIO
from uuid import uuid4

router=APIRouter(
    prefix='/images',
    tags=['Images']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def upload_image(image: Optional[UploadFile] = File(None), 
                       current_user=Depends(oauth2.get_current_user)
                       ):
    if image is None:
        return {"success": False, "detail": "No file uploaded."}

    try:
        img=Image.open(BytesIO(await image.read()))
    except Exception:
        return {"success": False, "detail": "Invalid image file."}

    file_name = f"{str(uuid4())}.webp"
    file_location = f"./app/static/images/{file_name}"
    img_webp = img.convert("RGB")
    img_webp.save(file_location, "WebP")
    return {"success": True, "image_url":f"api/static/{file_name}"}
