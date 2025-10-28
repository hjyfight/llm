from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # SiliconFlow配置
    siliconflow_api_key: str = ""
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    siliconflow_model: str = "Qwen/Qwen2.5-7B-Instruct"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库配置
    database_url: str = "sqlite:///./sentiment_analysis.db"
    
    # ChromaDB配置
    chroma_persist_directory: str = "./chroma_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
