import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "OutfitAura API"
    APP_DESCRIPTION: str = "Premium Fashion E-Commerce Backend API for OutfitAura"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # MongoDB Atlas
    MONGODB_USERNAME: str = os.getenv("MONGODB_USERNAME", "")
    MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD", "")
    MONGODB_URI: str = os.getenv(
        "MONGODB_URI", 
        "mongodb+srv://rkhusi879_db_user:46ENCgKt6cl1vpRp@cluster0.2nhurgf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
    DB_NAME: str = os.getenv("DB_NAME", "outfitaura")
    
    # Security / JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "outfitaura_super_secret_jwt_key_2024_luxury_fashion_minimalist")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings()
