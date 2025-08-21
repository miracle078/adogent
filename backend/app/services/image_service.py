import cloudinary.uploader
from typing import Optional, Dict, Any, List
from fastapi import UploadFile, HTTPException
import uuid
from app.core.cloudinary_config import get_cloudinary_config
import logging

logger = logging.getLogger(__name__)


class ImageService:
    def __init__(self):
        self.config = get_cloudinary_config()
        self.allowed_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    async def upload_image(
        self, 
        file: UploadFile, 
        folder: str = "products",
        transformation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            if not self._validate_file(file):
                raise HTTPException(status_code=400, detail="Invalid file format or size")
            
            file_content = await file.read()
            
            public_id = f"{folder}/{uuid.uuid4()}"
            
            upload_options = {
                "public_id": public_id,
                "folder": folder,
                "resource_type": "image",
                "overwrite": True,
                "invalidate": True
            }
            
            if transformation:
                upload_options["transformation"] = transformation
            
            preset = self.config.get_upload_preset()
            if preset:
                upload_options["upload_preset"] = preset
            
            result = cloudinary.uploader.upload(file_content, **upload_options)
            
            return {
                "public_id": result.get("public_id"),
                "url": result.get("secure_url"),
                "thumbnail_url": self._get_thumbnail_url(result.get("public_id")),
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "size": result.get("bytes")
            }
            
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
    
    async def upload_multiple_images(
        self, 
        files: List[UploadFile], 
        folder: str = "products"
    ) -> List[Dict[str, Any]]:
        results = []
        for file in files:
            try:
                result = await self.upload_image(file, folder)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to upload {file.filename}: {str(e)}")
                results.append({"error": str(e), "filename": file.filename})
        return results
    
    def delete_image(self, public_id: str) -> bool:
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            logger.error(f"Error deleting image {public_id}: {str(e)}")
            return False
    
    def _validate_file(self, file: UploadFile) -> bool:
        if not file.filename:
            return False
        
        extension = file.filename.split('.')[-1].lower()
        if extension not in self.allowed_formats:
            return False
        
        if file.size and file.size > self.max_file_size:
            return False
        
        return True
    
    def _get_thumbnail_url(self, public_id: str) -> str:
        return cloudinary.CloudinaryImage(public_id).build_url(
            width=300,
            height=300,
            crop="fill",
            quality="auto",
            fetch_format="auto"
        )
    
    def get_optimized_url(
        self, 
        public_id: str, 
        width: Optional[int] = None,
        height: Optional[int] = None,
        crop: str = "fill"
    ) -> str:
        options = {
            "quality": "auto",
            "fetch_format": "auto",
            "crop": crop
        }
        
        if width:
            options["width"] = width
        if height:
            options["height"] = height
        
        return cloudinary.CloudinaryImage(public_id).build_url(**options)


def get_image_service() -> ImageService:
    return ImageService()