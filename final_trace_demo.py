# 最终追踪演示：完整展示 invoke 调用链的参数传递

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Type
import json

# 1. 定义工具
class WeatherInput(BaseModel):
    city: str = Field(description="城市名称")

class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "获取天气信息"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, city: str):
        return f"{city}的天气是晴天，25度"

print("🔍 完整追踪：invoke 方法如何传递工具信息")
print("=" * 80)

# 2. 创建模型和工具
weather_tool = WeatherTool()
llm = ChatOpenAI(model="gpt-4o-mini")

print("\n📝 步骤 1: 原始状态")
print("-" * 40)
print(f"原始模型类型: {type(llm).__name__}")
print(f"原始模型是否有 kwargs 属性: {hasattr(llm, 'kwargs')}")

# 3. 绑定工具
print("\n📝 步骤 2: bind_tools() 执行")
print("-" * 40)
llm_with_tools = llm.bind_tools([weather_tool])

print(f"绑定后对象类型: {type(llm_with_tools).__name__}")
print(f"是否为 RunnableBinding: {'RunnableBinding' in str(type(llm_with_tools))}")

# 检查 RunnableBinding 的内部结构
print(f"\nRunnableBinding 内部结构:")
print(f"  - bound (原始模型): {type(llm_with_tools.bound).__name__}")
print(f"  - kwargs 键: {list(llm_with_tools.kwargs.keys())}")
print(f"  - config: {llm_with_tools.config}")

# 工具信息详情
if 'tools' in llm_with_tools.kwargs:
    tools = llm_with_tools.kwargs['tools']
    print(f"\n工具信息:")
    print(f"  - 工具数量: {len(tools)}")
    print(f"  - 工具名: {tools[0]['function']['name']}")
    print(f"  - 工具描述: {tools[0]['function']['description']}")

# 4. 模拟 RunnableBinding.invoke() 的参数合并
print("\n📝 步骤 3: RunnableBinding.invoke() 参数合并")
print("-" * 40)

input_text = "北京天气怎么样？"
invoke_kwargs = {"temperature": 0.7}  # 模拟额外参数

print(f"调用参数:")
print(f"  - input: '{input_text}'")
print(f"  - 额外 kwargs: {invoke_kwargs}")

# 模拟参数合并逻辑 (RunnableBinding.invoke 中的关键代码)
binding_kwargs = llm_with_tools.kwargs  # 来自 bind_tools
merged_kwargs = {**binding_kwargs, **invoke_kwargs}
print(merged_kwargs)
print(f"\n参数合并过程:")
print(f"  - binding_kwargs (来自 bind_tools): {list(binding_kwargs.keys())}")
print(f"  - invoke_kwargs (调用时传入): {list(invoke_kwargs.keys())}")
print(f"  - merged_kwargs: {list(merged_kwargs.keys())}")

print(f"\n关键代码逻辑:")
print(f"  self.bound.invoke(input, config, **{{**self.kwargs, **kwargs}})")
print(f"  其中 self.kwargs 包含工具信息")

# 5. 展示实际的方法调用
print("\n📝 步骤 4: 实际调用链执行")
print("-" * 40)

# 创建一个简单的监控装饰器
def monitor_call(func_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\n🔄 调用 {func_name}")
            if kwargs:
                key_info = []
                for key, value in kwargs.items():
                    if key == 'tools':
                        key_info.append(f"{key}: {len(value)} 个工具")
                    elif isinstance(value, (str, int, float, bool)):
                        key_info.append(f"{key}: {value}")
                    else:
                        key_info.append(f"{key}: {type(value).__name__}")
                if key_info:
                    print(f"   参数: {', '.join(key_info)}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 6. 实际执行调用
print(f"\n开始实际调用...")
try:
    response = llm_with_tools.invoke(input_text)
    
    print(f"\n✅ 调用成功!")
    print(f"响应类型: {type(response).__name__}")
    
    if hasattr(response, 'content'):
        content = response.content or "无文本内容"
        print(f"响应内容: {content}")
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"\n🔧 工具调用信息:")
        for i, tool_call in enumerate(response.tool_calls, 1):
            print(f"  {i}. 工具: {tool_call['name']}")
            print(f"     参数: {tool_call['args']}")
            print(f"     ID: {tool_call['id']}")
        
        print(f"\n🎉 成功！工具信息已从 bind_tools() 传递到模型并触发工具调用")
    else:
        print(f"⚠️  未检测到工具调用")
    
except Exception as e:
    print(f"❌ 调用失败: {e}")

# 7. 总结
print(f"\n📋 完整调用链总结")
print("=" * 80)

print(f"""
🔄 工具信息传递的完整流程:

1️⃣ bind_tools([weather_tool])
   └── 创建 RunnableBinding 对象
   └── 工具信息存储在 self.kwargs['tools']

2️⃣ llm_with_tools.invoke(input)
   └── RunnableBinding.invoke() 执行
   └── 参数合并: {{**self.kwargs, **invoke_kwargs}}
   └── self.kwargs 包含 tools 信息

3️⃣ self.bound.invoke(input, config, **merged_kwargs)
   └── 调用原始 ChatOpenAI.invoke()
   └── tools 信息通过 kwargs 传递

4️⃣ ChatOpenAI 内部调用链
   └── invoke() → generate_prompt() → generate() → _generate()
   └── tools 信息在每一步都通过 kwargs 传递

5️⃣ _get_request_payload()
   └── 构建发送给 OpenAI API 的 payload
   └── 将 kwargs['tools'] 添加到 payload['tools']

6️⃣ 发送 API 请求
   └── payload 包含工具定义
   └── OpenAI 返回包含工具调用的响应

🎯 关键设计模式:
   • 装饰器模式: RunnableBinding 装饰原始模型
   • 参数透传: kwargs 在整个调用链中传递
   • 延迟绑定: 工具信息在最后阶段添加到 API 请求

✅ 结果: 工具信息成功从绑定阶段传递到 API 调用阶段！
""")

# 8. 验证参数传递机制
print(f"\n🧪 验证: 参数传递机制")
print("-" * 40)

# 展示 RunnableBinding 的核心逻辑
print(f"RunnableBinding 的核心逻辑 (简化版):")
print(f"""
class RunnableBinding:
    def __init__(self, bound, kwargs):
        self.bound = bound          # 原始模型
        self.kwargs = kwargs        # 绑定的参数 (包含 tools)
    
    def invoke(self, input, **kwargs):
        merged = {{**self.kwargs, **kwargs}}  # 参数合并
        return self.bound.invoke(input, **merged)  # 传递给原始模型
""")

print(f"\n在我们的例子中:")
print(f"  - self.bound = ChatOpenAI 实例")
print(f"  - self.kwargs = {{'tools': [工具定义]}}")
print(f"  - merged = {{'tools': [工具定义], ...其他参数}}")
print(f"  - ChatOpenAI.invoke() 接收到 tools 参数")

print(f"\n🔚 这就是 invoke 方法传递工具信息的完整机制！")
