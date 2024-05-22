from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SLACK_SIGNING_SECRET: str
    NGROK_AUTHTOKEN: str
    SLACK_BOT_TOKEN: str
    SLACK_VERIFICATION_TOKEN: str
    
    class Config():
        env_file = ".env"
    
settings = Settings()