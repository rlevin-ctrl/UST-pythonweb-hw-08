import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.security import get_current_user
from app import models, schemas


router = APIRouter(prefix="/users", tags=["Users"])

cloudinary.config(
    cloud_name=settings.CLOUDINARY_URL.split("@")[1],
    api_key=settings.CLOUDINARY_URL.split("//")[1].split(":")[0],
    api_secret=settings.CLOUDINARY_URL.split(":")[2].split("@")[0]
)


@router.patch("/avatar", response_model=schemas.UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    upload_result = cloudinary.uploader.upload(
        file.file,
        folder="avatars",
        public_id=f"user_{current_user.id}",
        overwrite=True
    )

    avatar_url = upload_result.get("secure_url")

    current_user.avatar = avatar_url
    db.commit()
    db.refresh(current_user)

    return current_user
