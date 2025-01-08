from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
from typing import List
import dotenv
import yaml
from pydantic import BaseModel
from datetime import datetime, timedelta

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent.parent.parent

# Check if env file exists
ENV_FILE = ROOT_DIR / "resources" / "configs" / ".env"
if not ENV_FILE.exists():
    raise FileNotFoundError(
        f"Environment file not found at {ENV_FILE}. Please create .env file based on .env.example"
    )

# Load environment variables
dotenv.load_dotenv(ENV_FILE)


class ResourcePrivilege(BaseModel):
    view: str
    manage: str


class PrivilegeConfig(BaseModel):
    user: ResourcePrivilege
    role: ResourcePrivilege
    unit: ResourcePrivilege
    privilege: ResourcePrivilege


class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str
    VERSION: str
    API_V1_STR: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    ALLOWED_ORIGINS: List[str]

    # App Settings
    APP_HOST: str
    APP_PORT: int = 8000
    APP_WORKERS: int = 1
    APP_RELOAD: bool = False

    # Token Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # AI Configuration
    AI_SERVICE_BASE_URL: str = "http://192.168.83.12:62070"
    DETECT_FACE_URI: str = "/api/v1/analyze/detect"
    DETECT_FACE_METHOD: str = "POST"
    DETECT_FACE_HEADERS: str = "Content-Type: application/json"
    DETECT_FACE_BODY: str = "{\"base64_image\": \"\"}"
    MASK_THRESHOLD_SUB: float = 0.05

    # Database Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    # Timezone
    GMT_TIMEZONE: int = 7

    # Storage
    STORAGE_PATH: str
    PERSON_PATH: str
    EVENT_PATH: str

  # Add privilege config
    _privilege_config: PrivilegeConfig | None = None

    # Face Detection Configuration
    REGISTER_MIN_QUALITY: float = 0.6  # Minimum quality threshold for registration

    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_privileges()

    def _load_privileges(self):
        """Load privileges from YAML file"""
        privilege_file = ROOT_DIR / "resources" / "configs" / "privileges.yaml"
        if not privilege_file.exists():
            raise FileNotFoundError(
                f"Privileges file not found at {privilege_file}. Please create privileges.yaml"
            )

        with open(privilege_file, 'r') as f:
            config_data = yaml.safe_load(f)
            self._privilege_config = PrivilegeConfig.model_validate(
                config_data)

    def get_privilege(self, key: str) -> str:
        """Get privilege value by key
        Example: get_privilege("user.view") returns "ViewUser"
        """
        if not self._privilege_config:
            return key

        try:
            resource, action = key.split(".")
            resource_config = getattr(self._privilege_config, resource)
            return getattr(resource_config, action)
        except (AttributeError, ValueError):
            return key

    @property
    def privileges(self) -> PrivilegeConfig:
        """Get privilege configuration"""
        if not self._privilege_config:
            self._load_privileges()
        return self._privilege_config

    @property
    def get_person_path(self) -> str:
        return f"{self.STORAGE_PATH}/{self.PERSON_PATH}"

    @property
    def get_event_path(self) -> str:
        return f"{self.STORAGE_PATH}/{self.EVENT_PATH}"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def datetime_now(self) -> datetime:
        return datetime.utcnow() + timedelta(hours=self.GMT_TIMEZONE)

    class Config:
        env_file = ENV_FILE
        env_file_encoding = 'utf-8'


@lru_cache()
def get_settings() -> Settings:
    return Settings()
