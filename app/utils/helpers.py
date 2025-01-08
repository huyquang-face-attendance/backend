import base64
import os
from pathlib import Path
from typing import Optional
from uuid import uuid4
import aiofiles


async def save_base64_image(base64_string: str, save_path: str, filename: str = str(uuid4()) + ".jpg") -> Optional[str]:
    """Save base64 encoded image to file system

    Args:
        base64_string: Base64 encoded image string
        save_path: Directory path to save the image
        filename: Name of the file to save

    Returns:
        str: Path to saved image file, or None if save failed
    """
    try:
        # Create directory if it doesn't exist
        Path(save_path).mkdir(parents=True, exist_ok=True)

        # Remove base64 header if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        # Decode base64 to bytes
        image_data = base64.b64decode(base64_string)

        # Generate full file path
        file_path = os.path.join(save_path, filename)

        # Write bytes to file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_data)
        print(f"Save image success with fp: {file_path}")
        return filename

    except Exception:
        print(f"Error saving image: {e}")
        return None


def save_base64_image_sync(base64_image: str, path: str, filename: str = None) -> str:
    """
    Synchronous version of save_base64_image
    """
    try:
        # Create directory if not exists
        os.makedirs(path, exist_ok=True)

        # Remove header if exists
        if "base64," in base64_image:
            base64_image = base64_image.split("base64,")[1]

        # Decode base64 string
        image_data = base64.b64decode(base64_image)

        # Generate file path
        file_path = os.path.join(path, filename)

        # Save image
        with open(file_path, "wb") as f:
            f.write(image_data)

        return file_path
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return None
