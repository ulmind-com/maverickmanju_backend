"""Runtime configuration, loaded from environment variables / backend/.env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Mongo ---
    mongodb_uri: str
    mongodb_db: str = "maverickmanju"

    # --- Cloudinary ---
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    cloudinary_folder: str = "maverickmanju"

    # --- Admin auth ---
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    admin_email: str = "admin@maverickmanju.in"
    admin_password: str = "ChangeMe@123"
    admin_name: str = "Maverick Manju"

    # --- HTTP ---
    # Comma separated exact origins, plus a regex for preview deployments.
    cors_origins: str = (
        "http://localhost:3000,http://localhost:5173,http://localhost:8080,"
        "http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:8080"
    )
    cors_origin_regex: str = r"https://.*\.vercel\.app|https://([a-z0-9-]+\.)?maverickmanju\.in"

    max_upload_mb: int = 100

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
