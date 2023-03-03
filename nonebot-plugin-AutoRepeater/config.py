import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):
    # plugin custom config
    repeater_config_path: str = "./data/repeater_config/"
    repeat_interval: int = 300 # 5 * 60S
    class Config:
        extra = "ignore"








