from setuptools import setup, find_packages

setup(
    name="face_attendance",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "pydantic",
        "uvicorn",
        "pydantic-settings",
        "python-multipart",
        "sqlalchemy>=2.0.23",
        "PyYAML",
        "python-dotenv",
        "asyncpg>=0.29.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "alembic>=1.12.1",
    ],
)
