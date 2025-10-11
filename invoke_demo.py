# 演示 invoke 方法如何将工具信息传递给大语言模型

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Type
import json

# 1. 定义工具
class WeatherInput(BaseModel):
    city: str = Field(description="城市名称")
    country: str = Field(description="国家名称", default="中国")

class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "获取指定城市的天气信息"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, city: str, country: str = "中国"):
        return f"{country}{city}的天气是晴天，温度25度"

# 2. 创建模型和工具
weather_tool = WeatherTool()
llm = ChatOpenAI(model="gpt-4o-mini")

print("=" * 60)
print("1. invoke 方法的调用链分析")
print("=" * 60)

# 3. 使用 bind_tools 绑定工具
llm_with_tools = llm.bind_tools([weather_tool])

print("bind_tools 返回的对象类型:", type(llm_with_tools))
print("绑定的工具信息存储在:", hasattr(llm_with_tools, 'kwargs'))

# 检查绑定的工具信息
if hasattr(llm_with_tools, 'kwargs'):
    print("kwargs 内容:", llm_with_tools.kwargs.keys())
    if 'tools' in llm_with_tools.kwargs:
        print("工具数量:", len(llm_with_tools.kwargs['tools']))
        print("第一个工具结构:")
        print(json.dumps(llm_with_tools.kwargs['tools'][0], indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("2. invoke 方法的执行流程")
print("=" * 60)

print("""
invoke 方法的调用链:
1. llm_with_tools.invoke(input) 
   ↓
2. RunnableBinding.invoke(input, config, **kwargs)
   ↓ 
3. self.bound.invoke(input, merged_config, **{**self.kwargs, **kwargs})
   ↓
4. ChatOpenAI.invoke(input, config, **merged_kwargs)
   ↓
5. BaseChatModel.invoke() -> generate_prompt() -> generate() -> _generate()
   ↓
6. ChatOpenAI._generate() -> _get_request_payload()
   ↓
7. 在 payload 中添加 tools 信息，发送给 OpenAI API

关键点：
- bind_tools 创建 RunnableBinding 对象，将工具信息存储在 kwargs 中
- invoke 调用时，RunnableBinding 将 kwargs 合并传递给底层模型
- 底层模型在构建请求时，将 tools 信息添加到 API payload 中
""")

print("\n" + "=" * 60)
print("3. 实际调用演示")
print("=" * 60)

# 模拟调用过程
try:
    response = llm_with_tools.invoke("北京的天气怎么样？")
    print("模型响应类型:", type(response))
    print("是否包含工具调用:", hasattr(response, 'tool_calls') and len(response.tool_calls) > 0)
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print("工具调用信息:")
        for tool_call in response.tool_calls:
            print(f"  工具名: {tool_call['name']}")
            print(f"  参数: {tool_call['args']}")
            print(f"  ID: {tool_call['id']}")
    else:
        print("模型响应内容:", response.content)
        
except Exception as e:
    print(f"调用出错: {e}")

print("\n" + "=" * 60)
print("4. 关键数据结构")
print("=" * 60)

print("""
RunnableBinding 结构:
- bound: 原始的 ChatOpenAI 实例
- kwargs: {'tools': [converted_tool_schemas], ...}
- config: 运行配置

调用流程中的数据传递:
1. bind_tools() 阶段:
   tools -> convert_to_openai_tool() -> formatted_tools -> kwargs['tools']

2. invoke() 阶段:
   input + kwargs['tools'] -> merged_kwargs -> _get_request_payload() -> API payload

3. API payload 结构:
   {
     "model": "gpt-4o-mini",
     "messages": [...],
     "tools": [工具定义],
     "tool_choice": "auto"
   }
""")
