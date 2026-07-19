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
from astrbot.api.message_components import File, Plain, Node, Image
from astrbot.api.star import Star
from astrbot.api.star import Context, register
from astrbot.api import AstrBotConfig
from astrbot.api.event import filter
from jmcomic import *
import astrbot.api.message_components as Comp



class JMdownloader(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.timeout = 10       # 命令最大执行超时
        self.max_output_len = 1800  # 输出文本长度限制

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.command("help")
    async def help(self, event: AstrMessageEvent):
        yield event.plain_result("使用格式: \n"
                                 "下载/jm download 车牌号\n"
                                 "搜索/jm search 关键词\n"
                                 "分页搜索/jm page 关键词 页码")

    """jmsearch插件，提供搜索和下载功能"""


    @filter.command_group("jm") 
    def jm():
        pass



    @jm.command("download")
    async def jmdownload(self, event: AstrMessageEvent, jmd: str = ""):
        if not jmd:
            yield event.plain_result("使用格式: /jm download 车牌号")
            return

        option = create_option_by_file("C:/Users/kkkkk/Desktop/option.yml")

        
        client = JmOption.default().new_jm_client()

        try:
            album: JmAlbumDetail = client.get_album_detail(jmd)
            """ 获得信息 """

        except MissingAlbumPhotoException as e:
            yield event.plain_result(f'id={e.error_jmid}的本子不存在')
            return
            """不存在"""

        except JsonResolveFailException as e:
            yield event.plain_result(f'解析json失败')
            resp = e.resp
            yield event.plain_result(f'resp.text: {resp.text}, resp.status_code: {resp.status_code}')
            return
            """解析json失败"""

        except RequestRetryAllFailException as e:
            yield event.plain_result(f'请求失败，重试次数耗尽')
            return
            """请求失败"""

        except JmcomicException as e:
            yield event.plain_result(f'jmcomic遇到异常: {e}')
            return
            """jmcomic遇到异常"""

        page = client.search_site(search_query=jmd)
        album: JmAlbumDetail = page.single_album
        yield event.plain_result(f'本子标题: 《{album.title}》正在下载，请等待')
        """获取信息并输出反馈""" 
        

        try:
            download_album(jmd,option)
            """下载本子"""
        except Exception as e:
            yield event.plain_result(f'下载失败，请稍后重试: {e}')
            return
            """下载失败"""

        user_name = event.get_sender_name()

        outphoto = f"{jmd}.pdf"

        chain = [
            
            Comp.Plain('下载成功，请等待文件上传'),
            Comp.File(file="D:/jmd/" + outphoto, name = outphoto),
            Comp.At(qq=event.get_sender_id()),
            Comp.Plain(f'下载成功')

        ]

        yield event.chain_result(chain)
        """上传文件并输出反馈"""


    @jm.command("search") #标题搜索
    async def jms(self, event: AstrMessageEvent, jms: str = ""):
        if not jms:
            yield event.plain_result("使用格式: /jm search 关键词")
            return

        option = create_option_by_file("C:/Users/kkkkk/Desktop/option.yml")
        """读取配置文件"""
        
        client = JmOption.default().new_jm_client()

        page: JmSearchPage = client.search_site(jms, page=1)
        """搜索本子"""

        yield event.plain_result(f'结果总数: {page.total}, 分页大小: {page.page_size}，页数: {page.page_count}, 页码: 1')
        
        output = ""

        for album_id, title in page:
            output= output + f'[{album_id}]: [{title}]\n'

        node = Node(
            uin=2706463790,
            name="KoNeko",
            content=[
                Plain(output)
            ]
        )
        yield event.chain_result([node])



    @jm.command("page")
    async def page_search(self, event: AstrMessageEvent, jms: str = "", page_input: int = 1):
        if not jms:
            yield event.plain_result("使用格式: /jm page 关键词 页码")
            return

        option = create_option_by_file("C:/Users/kkkkk/Desktop/option.yml")
        """读取配置文件"""
        
        client = JmOption.default().new_jm_client()

        page: JmSearchPage = client.search_site(jms, page=int(page_input))
        """搜索本子"""

        yield event.plain_result(f'结果总数: {page.total}, 分页大小: {page.page_size}，页数: {page.page_count}, 页码: {page_input}')
        
        output = ""

        for album_id, title in page:
            output= output + f'[{album_id}]: [{title}]\n'

        node = Node(
            uin=2706463790,
            name="KoNeko",
            content=[
                Plain(output)
            ]
        )
        yield event.chain_result([node])


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
