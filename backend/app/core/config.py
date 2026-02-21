
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "College Chatbot AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="insecure-static-secret-key-for-deployment", env="SECRET_KEY")
    KPGU_WEBSITE: str = "https://kpgu.ac.in"
    
    # CORS Origins (Allow all for development)
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://localhost:5175"] 

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # AI Configuration (To be filled by user)
    OPENAI_API_KEY: str = Field(default="sk-placeholder", env="OPENAI_API_KEY")
    GOOGLE_API_KEY: str = Field(default="AIza-placeholder", env="GOOGLE_API_KEY") # For Free Gemini API
    CHROMA_DB_DIR: str = "./chroma_db"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_file_encoding='utf-8')

settings = Settings()
