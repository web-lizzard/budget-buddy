from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import find_dotenv


class Database(BaseModel):
    url: str


class Settings(BaseSettings):
    database: Database

    class Config:
        env_nested_delimiter = "__"
        extra = "ignore"
        env_file = find_dotenv()


settings = Settings()
