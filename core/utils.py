import os
import base64
from functools import lru_cache
from typing import Optional
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions


@lru_cache(maxsize=1)
def get_imagekit() -> ImageKit:
    """Get cached ImageKit client instance."""
    public_key = os.environ.get("IMAGEKIT_PUBLIC_KEY")
    private_key = os.environ.get("IMAGEKIT_PRIVATE_KEY")
    url_endpoint = os.environ.get("IMAGEKIT_URL_ENDPOINT")
    
    if not all([public_key, private_key, url_endpoint]):
        raise RuntimeError(
            "Missing ImageKit env vars. Set IMAGEKIT_PUBLIC_KEY, "
            "IMAGEKIT_PRIVATE_KEY, IMAGEKIT_URL_ENDPOINT."
        )
    
    return ImageKit(
        public_key=public_key,
        private_key=private_key,
        url_endpoint=url_endpoint
    )


def upload_campsite_image(django_file, folder: str = "campsites") -> str:
    """
    Upload a campsite image to ImageKit.
    
    Args:
        django_file: Django UploadedFile object
        folder: Folder path in ImageKit storage
        
    Returns:
        str: URL of the uploaded image
        
    Raises:
        RuntimeError: If upload fails
    """
    client = get_imagekit()
    file_name = getattr(django_file, "name", "campsite-upload")
    
    try:
        # Read file content as bytes
        if hasattr(django_file, "seek"):
            try:
                django_file.seek(0)
            except Exception:
                pass
        
        file_content = django_file.read()
        
        # Convert to base64 string (required by ImageKit SDK)
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Create options object
        options = UploadFileRequestOptions(
            folder=f"/{folder}",
            use_unique_file_name=True,
        )
        
        # Upload file to ImageKit
        res = client.upload_file(
            file=file_base64,
            file_name=file_name,
            options=options,
        )
        
        # Extract URL from response (handle both dict and object)
        if isinstance(res, dict):
            url = res.get("url")
        else:
            url = getattr(res, "url", None)
        
        if not url:
            raise RuntimeError("Upload succeeded but no URL returned.")
        
        return url
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise RuntimeError(f"ImageKit upload failed: {e}\nDetails: {error_details}")


def imagekit_transformed_url(
    original_url: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: int = 75,
    auto_format: bool = True,
    smart_focus: bool = True
) -> str:
    """
    Build an ImageKit transformation URL.
    
    Args:
        original_url: Original ImageKit URL
        width: Target width in pixels
        height: Target height in pixels
        quality: Image quality (1-100)
        auto_format: Enable automatic format selection
        smart_focus: Enable smart cropping/focus
        
    Returns:
        str: Transformed ImageKit URL
    """
    if not original_url:
        return ""
    
    parts = []
    
    if width:
        parts.append(f"w-{int(width)}")
    if height:
        parts.append(f"h-{int(height)}")
    if smart_focus:
        parts.append("fo-auto")
    if auto_format:
        parts.append("f-auto")
    if quality:
        parts.append(f"q-{int(quality)}")
    
    if not parts:
        return original_url
    
    sep = "&" if "?" in original_url else "?"
    return f"{original_url}{sep}tr={','.join(parts)}"
