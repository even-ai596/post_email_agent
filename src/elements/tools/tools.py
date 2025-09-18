
import asyncio
import os
from datetime import date
from pydantic import BaseModel
from typing import Type
import requests
from src.elements.pydantic_models.pydantic_models import Location, Email
from src.elements.utils.utils import sync_post_email
from langchain.tools import BaseTool
from langchain_core.tools import tool, InjectedToolArg
from langgraph.prebuilt import ToolNode
class GetTodayTool(BaseTool):
    name: str = "get_today_date"

    description: str = "拿到今天的日期。"
    args_schema: Type[BaseModel] = None

    def _run(self):
        return str(date.today())

    async def _arun(self):
        return self._run()

class PostEmailTool(BaseTool):
    name: str = "post_email"
    description: str = "发送邮件"
    args_schema: Type[BaseModel] = Email

    def _run(self, email_title: str, email_recipient: str, email_text: str):
        response = sync_post_email(email_title, email_recipient, email_text + "\n\n —— GPT EMAIL AGENT，勿念")
        return response

        
    async def _arun(self, email_title: str, email_recipient: str, email_text: str):
        return await self._run(email_title, email_recipient, email_text)

@tool(description="获取某个地区的天气")
def GetWeatherTool(loc: Location) -> str:
    response = requests.get(f"""https://api.open-meteo.com/v1/forecast?latitude={loc.latitude}&longitude={loc.longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m""")
        #     coroutine = asyncio.to_thread(
        #     requests.get,
        #     f"https://api.open-meteo.com/v1/forecast?"
        #     f"latitude={latitude}&longitude={longitude}&"
        #     "current=temperature_2m,wind_speed_10m&"
        #     "hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        # )
            # response = await asyncio.gather(coroutine)
    data = response.json()
    # print(data)
    return data['current']['temperature_2m']

from langchain_mcp_adapters.sessions import SSEConnection
from langchain_mcp_adapters.client import MultiServerMCPClient
print(os.getenv("12306_MCP_URL"))
client = MultiServerMCPClient(
    {
        "12306": SSEConnection(url=os.getenv("12306_MCP_URL"), transport="sse")
    }
)
# 同步化获取工具列表
def sync_get_12306_tools():
    return asyncio.run(client.get_tools())
    
tools = ([GetWeatherTool, PostEmailTool()] + sync_get_12306_tools())


# class GetWeatherTool(BaseTool):
#     name: str = "get_weather"
#     description: str = "获取天气。"
#     args_schema: Type[BaseModel] = Location

#     def _run(self,latitude: float, longitude: float):
#         try:
#             response = requests.get(f"""https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m""")
#         #     coroutine = asyncio.to_thread(
#         #     requests.get,
#         #     f"https://api.open-meteo.com/v1/forecast?"
#         #     f"latitude={latitude}&longitude={longitude}&"
#         #     "current=temperature_2m,wind_speed_10m&"
#         #     "hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
#         # )
#             # response = await asyncio.gather(coroutine)
#             data = response.json()
#             # print(data)
#             return data['current']['temperature_2m']
        
#         except requests.exceptions.RequestException as e:
#             raise ConnectionError(f"请求天气接口失败: {str(e)}")

#     async def _arun(self, latitude: float, longitude: float):
#         return self._run(latitude, longitude)
