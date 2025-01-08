from app.core.config import get_settings

settings = get_settings()


async def verify_client(
    client_id: str,
    client_secret: str
) -> bool:
    """Verify client credentials against config"""
    return (
        client_id == settings.CLIENT_ID and
        client_secret == settings.CLIENT_SECRET
    )
