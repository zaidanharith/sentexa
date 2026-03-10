from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    ALLOWED_ORIGINS: str = "*"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str

    @property
    def allowed_origins_list(self) -> List[str]:
        return self.ALLOWED_ORIGINS.split(",")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
