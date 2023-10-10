from pydantic import BaseSettings

class Settings(BaseSettings):
    db_hostname:str
    db_password:str
    db_username:str
    db_name:str
    db_port:str
    secret_key:str
    algorithm:str
    token_expiry_minutes:int
    ALLOWED_ORIGINS:str
    
    class Config:
        env_file = ".env"
        

settings=Settings()