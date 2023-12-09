from pydantic_settings import BaseSettings
from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    url: str


class Setting(BaseSettings):
    database: DatabaseSettings

    class Config:
        env_nested_delimiter = "__"


settings = Setting()
