import uvicorn
from app.core.config import get_settings

settings = get_settings()


def main():
    """
    Run the FastAPI application using uvicorn with configurable options
    """
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
        workers=settings.APP_WORKERS,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
