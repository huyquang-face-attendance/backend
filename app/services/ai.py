from fastapi import HTTPException, status
import httpx
from app.core.config import get_settings
from app.schemas.person import FaceDetectResponse

settings = get_settings()


async def detect_face(base64_image: str, timeout: float = 10.0) -> FaceDetectResponse:
    """
    Call AI service to detect face and get embedding

    Args:
        base64_image: Base64 encoded image
        timeout: Request timeout in seconds

    Returns:
        FaceDetectResponse object containing detection results

    Raises:
        HTTPException: If face detection fails or no face detected
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.AI_SERVICE_BASE_URL}{settings.DETECT_FACE_URI}",
                json={"base64_image": base64_image},
                timeout=timeout
            )
            response.raise_for_status()
            response_data = response.json()

            # Check if response indicates no face detected
            if response_data.get("data") is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No face detected in image"
                )

            detect_result = FaceDetectResponse(**response_data)

            # Validate if face is detected
            if not detect_result.data.feature:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No face detected"
                )

            return detect_result

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Face detection service error: {str(e)}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid response from face detection service: {str(e)}"
            )
