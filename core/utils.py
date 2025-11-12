import os
import base64
import math
from functools import lru_cache
from typing import Optional, Tuple
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


def upload_product_image(django_file, folder: str = "products") -> str:
    """
    Upload a product image to ImageKit.
    
    Args:
        django_file: Django UploadedFile object
        folder: Folder path in ImageKit storage
        
    Returns:
        str: URL of the uploaded image
        
    Raises:
        RuntimeError: If upload fails
    """
    client = get_imagekit()
    file_name = getattr(django_file, "name", "product-upload")
    
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


def parse_lat_lng(source) -> Optional[Tuple[float, float]]:
    """
    Parse latitude and longitude from various sources.
    
    Args:
        source: Can be a Campsite instance, "lat,lng" string, or (lat, lng) tuple
        
    Returns:
        Tuple of (latitude, longitude) or None if invalid
    """
    if source is None:
        return None
    
    # If it's a Campsite instance, try properties first
    lat = getattr(source, "latitude", None)
    lng = getattr(source, "longitude", None)
    if lat is not None and lng is not None:
        try:
            lat_float = float(lat)
            lng_float = float(lng)
            if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
                return lat_float, lng_float
        except (TypeError, ValueError):
            pass
    
    # Try map_location attribute
    map_location = getattr(source, "map_location", None)
    if isinstance(map_location, str):
        parts = map_location.split(",")
        if len(parts) == 2:
            try:
                lat_float = float(parts[0].strip())
                lng_float = float(parts[1].strip())
                if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
                    return lat_float, lng_float
            except ValueError:
                return None
    
    # If it's a tuple/list
    if isinstance(source, (tuple, list)) and len(source) == 2:
        try:
            lat_float = float(source[0])
            lng_float = float(source[1])
            if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
                return lat_float, lng_float
        except (TypeError, ValueError):
            return None
    
    # If it's a raw string "lat,lng"
    if isinstance(source, str):
        parts = source.split(",")
        if len(parts) == 2:
            try:
                lat_float = float(parts[0].strip())
                lng_float = float(parts[1].strip())
                if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
                    return lat_float, lng_float
            except ValueError:
                return None
    
    return None


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth using Haversine formula.
    
    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees
        
    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth's radius in kilometers
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def get_campsites_within_radius(center_campsite, radius_km: float, base_qs):
    """
    Get campsites within a specified radius of a center campsite.
    
    Args:
        center_campsite: Campsite instance to use as center point
        radius_km: Radius in kilometers
        base_qs: Base queryset to filter from
        
    Returns:
        Queryset of campsites within the radius
    """
    center = parse_lat_lng(center_campsite)
    if not center:
        return base_qs.none()
    
    lat0, lng0 = center
    
    # Bounding box approximation to reduce candidate set
    # 1 degree of latitude ≈ 111.32 km
    lat_delta = radius_km / 111.32
    # 1 degree of longitude varies by latitude
    cos_lat0 = max(math.cos(math.radians(lat0)), 1e-6)
    lng_delta = radius_km / (111.32 * cos_lat0)
    
    min_lat = lat0 - lat_delta
    max_lat = lat0 + lat_delta
    min_lng = lng0 - lng_delta
    max_lng = lng0 + lng_delta
    
    # Filter candidates within bounding box and check exact distance
    ids = []
    for cs in base_qs:
        coords = parse_lat_lng(cs)
        if not coords:
            continue
        
        lat, lng = coords
        
        # Quick bounding box check
        if lat < min_lat or lat > max_lat or lng < min_lng or lng > max_lng:
            continue
        
        # Exact distance check
        if calculate_distance(lat0, lng0, lat, lng) <= radius_km:
            ids.append(cs.pk)
    
    return base_qs.model.objects.filter(pk__in=ids)
