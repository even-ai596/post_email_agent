# 演示 bind_tools 如何将工具名和参数传递给大语言模型

from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import BaseModel, Field
from typing import Type
import json

# 1. 定义一个简单的工具
class WeatherInput(BaseModel):
    city: str = Field(description="城市名称")
    country: str = Field(description="国家名称", default="中国")

class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "获取指定城市的天气信息"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, city: str, country: str = "中国"):
        return f"{country}{city}的天气是晴天，温度25度"

# 2. 创建工具实例
weather_tool = WeatherTool()

# 3. 演示 convert_to_openai_tool 的转换过程
openai_tool = convert_to_openai_tool(weather_tool)

print("=" * 50)
print("1. 原始工具信息:")
print(f"工具名: {weather_tool.name}")
print(f"描述: {weather_tool.description}")
print(f"参数模式: {weather_tool.args_schema}")

print("\n" + "=" * 50)
print("2. 转换后的 OpenAI 工具格式:")
print(json.dumps(openai_tool, indent=2, ensure_ascii=False))

print("\n" + "=" * 50)
print("3. bind_tools 的工作流程:")
print("a) bind_tools 接收工具列表")
print("b) 对每个工具调用 convert_to_openai_tool 进行格式转换")
print("c) 将转换后的工具列表存储在模型的 kwargs 中")
print("d) 在调用模型时，将工具信息添加到请求 payload 的 'tools' 字段")

print("\n" + "=" * 50)
print("4. 发送给 OpenAI API 的 payload 结构示例:")
example_payload = {
    "model": "gpt-4",
    "messages": [
        {"role": "user", "content": "北京的天气怎么样？"}
    ],
    "tools": [openai_tool],
    "tool_choice": "auto"
}
import os
print(json.dumps(example_payload, indent=2, ensure_ascii=False))
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    **example_payload
)
print(response.choices[0].message.tool_calls)

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4.1")
response = llm.bind_tools([weather_tool]).invoke("北京的天气怎么样？")
print(response.tool_calls)
l = {1,2}
print(json.dumps(l, indent=2, ensure_ascii=False))
print("=" * 50)