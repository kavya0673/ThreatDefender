from pydantic_settings import BaseSettings
from typing import List, Optional
import logging

class Settings(BaseSettings):
    PROJECT_NAME: str = "ARES - Security Assessment Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./ares.db"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None

    @property
    def get_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # AI API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Scanner Settings
    MAX_CRAWL_DEPTH: int = 5
    MAX_CONCURRENT_REQUESTS: int = 10
    USER_AGENT: str = "ARES-Scanner/1.0.0 (Enterprise-Security)"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Setup logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(settings.PROJECT_NAME)
