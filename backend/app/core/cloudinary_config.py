import cloudinary
import cloudinary.uploader
import cloudinary.api
from functools import lru_cache
from typing import Optional
from decouple import config


class CloudinaryConfig:
    def __init__(self):
        self.cloud_name = config("CLOUDINARY_CLOUD_NAME")
        self.api_key = config("CLOUDINARY_API_KEY")
        self.api_secret = config("CLOUDINARY_API_SECRET")
        
        self._configure()
    
    def _configure(self):
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True
        )
    
    def get_upload_preset(self) -> Optional[str]:
        return config("CLOUDINARY_UPLOAD_PRESET", default=None)


@lru_cache()
def get_cloudinary_config() -> CloudinaryConfig:
    return CloudinaryConfig()