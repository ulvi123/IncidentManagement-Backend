from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SLACK_SIGNING_SECRET: str
    NGROK_AUTHTOKEN: str
    SLACK_BOT_TOKEN: str
    SLACK_VERIFICATION_TOKEN: str
    SLACK_GENERAL_OUTAGES_CHANNEL:str
    database_hostname: str
    database_port: str
    database_password: str
    database_name : str
    database_username : str
    secret_key : str
    algorithm : str
    access_token_expire_minutes : int
    opsgenie_api_key: str
    jira_api_key: str
    jira_email: str
    jira_server: str
    
    
    
    
    class Config():
        env_file = ".env"
    
settings = Settings()