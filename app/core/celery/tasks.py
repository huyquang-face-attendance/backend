from app.core.celery.celery_app import celery_app
from app.utils.helpers import save_base64_image_sync
from app.core.config import get_settings
import time

settings = get_settings()


@celery_app.task
def save_event_image(base64_image: str, path: str, filename: str) -> str:
    """
    Celery task to save event images asynchronously

    Args:
        base64_image: Base64 encoded image
        path: Directory path to save the image
        filename: Name of the image file

    Returns:
        str: Path to saved image or None if failed
    """
    try:
        result = save_base64_image_sync(base64_image, path, filename)
        return result
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return None
