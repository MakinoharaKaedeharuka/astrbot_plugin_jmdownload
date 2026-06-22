import asyncio
import os
import shlex
import re
import time
import json
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass, field
import aiohttp
import uuid
import tempfile
import subprocess

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageChain, MessageEventResult, EventResultType
from astrbot.api.platform import MessageType
from astrbot.api.message_components import File, Plain
from astrbot.api.star import Star
from astrbot.api.star import Context, register
from astrbot.api import AstrBotConfig
from astrbot.api.event import filter
from jmcomic import *
import astrbot.api.message_components as Comp



@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.timeout = 10       # 命令最大执行超时
        self.max_output_len = 1800  # 输出文本长度限制

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.command("jm")
    async def jm(self, event: AstrMessageEvent, jmd: str = ""):
        if not jmd:
            yield event.plain_result("使用格式: /jm <车牌号>")
            return
        
        option = create_option_by_file("C:/Users/kkkkk/Desktop/option.yml")
        option.download_album(jmd)

        try:

            outphoto: str = jmd + ".pdf"

            chain = [

                Comp.File(file="D:/jmd/" + outphoto, name = outphoto),
                Comp.Plain("密码114514")

            ]
            yield event.chain_result(chain)
        except subprocess.TimeoutExpired:
            yield event.plain_result("执行超时（10s），命令已终止")
        except Exception as e:
            logger.error(f"cmd执行异常: {e}")
            yield event.plain_result(f"执行失败：{str(e)}")


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
