from sqlalchemy.orm import Session
from database import get_db
import schemas,utils, models
from fastapi import Depends, status, APIRouter, UploadFile, File
import oauth2
from fastapi.responses import JSONResponse
from typing import Optional
from PIL import Image
from io import BytesIO

router=APIRouter(
    prefix='/images',
    tags=['Images']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def upload_image(image: Optional[UploadFile] = File(None), 
                       current_user=Depends(oauth2.get_current_user)
                       ):
    if image is None:
        return JSONResponse(content={"success": False, "detail": "No file uploaded."})

    try:
        img=Image.open(BytesIO(await image.read()))
    except Exception:
        return JSONResponse(content={"success": False, "detail": "Invalid image file."})

    file_location = f"./{image.filename}"
    img.save(file_location)
    return JSONResponse(content={"success": True})
