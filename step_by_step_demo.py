# 逐步执行 invoke 调用链的每个步骤

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Type
import json
import inspect

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

# 2. 创建模型和工具实例
weather_tool = WeatherTool()
llm = ChatOpenAI(model="gpt-4o-mini")

print("=" * 80)
print("步骤 1: 创建原始模型")
print("=" * 80)
print(f"原始模型类型: {type(llm)}")
print(f"原始模型类: {llm.__class__.__name__}")

print("\n" + "=" * 80)
print("步骤 2: bind_tools() - 创建 RunnableBinding")
print("=" * 80)

# 执行 bind_tools
llm_with_tools = llm.bind_tools([weather_tool])

print(f"bind_tools 后的对象类型: {type(llm_with_tools)}")
print(f"是否为 RunnableBinding: {llm_with_tools.__class__.__name__}")
print(f"bound 属性 (原始模型): {type(llm_with_tools.bound)}")
print(f"kwargs 键: {list(llm_with_tools.kwargs.keys())}")
print(f"工具数量: {len(llm_with_tools.kwargs.get('tools', []))}")

print("\n" + "=" * 80)
print("步骤 3: 调用 llm_with_tools.invoke()")
print("=" * 80)

input_text = "北京的天气怎么样？"
print(f"输入: {input_text}")

# 这里我们会模拟调用，但实际调用会触发真正的API
print("\n开始执行调用链...")

print("\n--- 3.1: RunnableBinding.invoke() ---")
print("代码逻辑:")
print("""
def invoke(self, input, config=None, **kwargs):
    return self.bound.invoke(
        input,
        self._merge_configs(config),
        **{**self.kwargs, **kwargs}  # 工具信息在这里合并
    )
""")

print("参数合并:")
print(f"self.kwargs: {list(llm_with_tools.kwargs.keys())}")
print("合并后传递给底层模型的参数包含: tools")

print("\n--- 3.2: ChatOpenAI.invoke() ---")
print("调用 BaseChatModel.invoke() -> generate_prompt()")

print("\n--- 3.3: generate_prompt() -> generate() -> _generate() ---")
print("最终调用 ChatOpenAI._generate() 方法")

print("\n--- 3.4: _generate() -> _get_request_payload() ---")
print("构建发送给 OpenAI API 的 payload")

# 模拟 _get_request_payload 的逻辑
print("\n模拟 payload 构建过程:")
from langchain_core.messages import HumanMessage

# 模拟消息转换
messages = [HumanMessage(content=input_text)]
print(f"消息对象: {messages}")

# 模拟 payload 构建
mock_payload = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": input_text}],
    "tools": llm_with_tools.kwargs['tools'],  # 工具信息被添加到这里
    "tool_choice": "auto"
}

print("构建的 payload 结构:")
print(f"- model: {mock_payload['model']}")
print(f"- messages: {len(mock_payload['messages'])} 条消息")
print(f"- tools: {len(mock_payload['tools'])} 个工具")
print(f"- tool_choice: {mock_payload['tool_choice']}")

print("\n工具定义详情:")
print(json.dumps(mock_payload['tools'][0], indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
print("步骤 4: 实际执行完整调用")
print("=" * 80)

try:
    # 实际调用
    response = llm_with_tools.invoke(input_text)
    
    print("调用成功！")
    print(f"响应类型: {type(response)}")
    print(f"响应类: {response.__class__.__name__}")
    
    # 检查响应内容
    if hasattr(response, 'content'):
        print(f"内容: {response.content}")
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"工具调用数量: {len(response.tool_calls)}")
        for i, tool_call in enumerate(response.tool_calls):
            print(f"工具调用 {i+1}:")
            print(f"  - 名称: {tool_call['name']}")
            print(f"  - 参数: {tool_call['args']}")
            print(f"  - ID: {tool_call['id']}")
    
    if hasattr(response, 'response_metadata'):
        print(f"响应元数据: {list(response.response_metadata.keys())}")
        
except Exception as e:
    print(f"调用失败: {e}")

print("\n" + "=" * 80)
print("步骤 5: 调用链总结")
print("=" * 80)

print("""
完整的调用链执行过程：

1. llm.bind_tools([weather_tool])
   → 创建 RunnableBinding 对象
   → 工具信息存储在 kwargs['tools'] 中

2. llm_with_tools.invoke(input)
   → RunnableBinding.invoke()
   → 合并 kwargs (包含工具信息)

3. self.bound.invoke(input, config, **merged_kwargs)
   → 调用原始 ChatOpenAI.invoke()
   → 工具信息通过 kwargs 传递

4. BaseChatModel.invoke() → generate_prompt() → generate() → _generate()
   → ChatOpenAI._generate()
   → _get_request_payload()

5. _get_request_payload()
   → 将工具信息添加到 API payload
   → 发送给 OpenAI API

6. API 返回响应
   → 包含工具调用信息
   → 转换为 AIMessage 对象

关键点：
- 工具信息通过 kwargs 在整个调用链中传递
- RunnableBinding 起到参数合并和透传的作用
- 最终在构建 API payload 时添加工具定义
""")

print("\n" + "=" * 80)
print("步骤 6: 验证参数传递")
print("=" * 80)

# 验证参数传递机制
print("验证 RunnableBinding 的参数合并机制:")

# 模拟额外的 kwargs
extra_kwargs = {"temperature": 0.7}

# 展示参数合并逻辑
binding_kwargs = llm_with_tools.kwargs  # {'tools': [...]}
merged = {**binding_kwargs, **extra_kwargs}

print(f"RunnableBinding.kwargs: {list(binding_kwargs.keys())}")
print(f"额外的 kwargs: {list(extra_kwargs.keys())}")
print(f"合并后的 kwargs: {list(merged.keys())}")

print("\n这就是工具信息如何通过 invoke 传递给模型的完整机制！")
