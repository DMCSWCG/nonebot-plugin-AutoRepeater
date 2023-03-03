import os
import nonebot

try:
    import ujson as json
except ModuleNotFoundError as _:
    import json

from difflib import SequenceMatcher
import aiofiles,asyncio
import httpx
from pathlib import Path
import imghdr, random
from string import ascii_letters
from .config import Config
from typing import Union,Tuple



class Repeater:
    def __init__(self,setup_config:Config) -> None:
        self.logger_map()
        self.repeater_config_path = setup_config.repeater_config_path
        self.repeat_interval = abs(int(setup_config.repeat_interval))
        self.config_file_name = "config.json"
        self.config_save_path = Path(self.repeater_config_path,self.config_file_name)
        self.path_check()

    def logger_map(self):
        self.error = nonebot.logger.error
        self.warning = nonebot.logger.warning
        self.info = nonebot.logger.info
        self.debug = nonebot.logger.debug

    def path_check(self):
        if not os.path.exists(self.repeater_config_path):
            self.warning("未找到配置文件目录！将自动创建！")
            os.makedirs(self.repeater_config_path)
        if not os.path.exists(self.config_save_path):
            asyncio.run(self.WriteJson(self.config_save_path,{}))
        
    async def check_group_is_used(self,group_id):
        data = await self.ReadJson(self.config_save_path)
        if not str(group_id) in data:
            return False
        return data[f"{group_id}"]

    async def ReadJson(self, path:str)->dict:
        async with aiofiles.open(path, "r") as f:
            data = await f.readlines()
        return json.loads("".join(data))

    async def WriteJson(self, path, data)->None:
        async with aiofiles.open(path, "w+") as f:
            await f.write(json.dumps(data,indent=4))

    async def read_config(self):
        return await self.ReadJson(self.config_save_path)
    
    async def write_config(self,data):
        await self.WriteJson(self.config_save_path,data)
