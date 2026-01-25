from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    alpha_vantage_api_key: str
    finnhub_api_key: str

    kakao_client_id: str
    kakao_client_secret: str
    kakao_redirect_uri: str

    jwt_secret: str
    database_url: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
