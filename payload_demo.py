# 专门演示 _get_request_payload 方法如何处理工具信息

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Type
import json
from langchain_core.messages import HumanMessage

# 1. 定义工具
class WeatherInput(BaseModel):
    city: str = Field(description="城市名称")

class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "获取天气信息"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, city: str):
        return f"{city}的天气是晴天，25度"

print("🔍 深入分析：_get_request_payload 如何处理工具信息")
print("=" * 80)

# 2. 创建模型和绑定工具
weather_tool = WeatherTool()
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([weather_tool])

# 3. 准备输入数据
input_text = "北京天气怎么样？"
human_message = HumanMessage(content=input_text)

print(f"\n📝 准备调用 _get_request_payload")
print("-" * 50)
print(f"输入消息: {input_text}")

# 4. 获取工具信息
tools_info = llm_with_tools.kwargs.get('tools', [])
print(f"工具信息: {len(tools_info)} 个工具")

# 5. 模拟 _get_request_payload 的调用
print(f"\n🔧 调用 _get_request_payload 方法")
print("-" * 50)

# 直接调用 _get_request_payload 方法
try:
    # 准备参数 - 模拟实际调用时的参数
    kwargs = {
        'tools': tools_info,
        'temperature': 0.7
    }
    
    print(f"传入 _get_request_payload 的参数:")
    print(f"  - input_: {input_text}")
    print(f"  - stop: None")
    print(f"  - kwargs keys: {list(kwargs.keys())}")
    
    # 调用 _get_request_payload
    payload = llm_with_tools.bound._get_request_payload(
        input_=input_text,
        stop=None,
        **kwargs
    )
    
    print(f"\n✅ _get_request_payload 执行成功!")
    print(f"返回的 payload 结构:")
    
    # 分析 payload 内容
    for key, value in payload.items():
        if key == 'messages':
            print(f"  - {key}: {len(value)} 条消息")
            for i, msg in enumerate(value):
                print(f"    {i+1}. role: {msg.get('role')}, content: '{msg.get('content')}'")
        elif key == 'tools':
            print(f"  - {key}: {len(value)} 个工具")
            for i, tool in enumerate(value):
                tool_name = tool.get('function', {}).get('name', 'unknown')
                print(f"    {i+1}. {tool_name}")
        elif isinstance(value, (str, int, float, bool)):
            print(f"  - {key}: {value}")
        else:
            print(f"  - {key}: {type(value).__name__}")
    
    print(f"\n📋 完整的 payload 内容:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    print(f"\n🎯 关键观察:")
    print(f"  ✓ tools 信息成功添加到 payload")
    print(f"  ✓ messages 正确转换为 OpenAI 格式")
    print(f"  ✓ 其他参数 (temperature) 也包含在内")
    print(f"  ✓ 这个 payload 将直接发送给 OpenAI API")
    
except Exception as e:
    print(f"❌ 调用失败: {e}")
    import traceback
    traceback.print_exc()
    payload = {}

# 6. 验证工具信息的格式
print(f"\n🔍 验证工具信息格式")
print("-" * 50)

if payload and 'tools' in payload:
    tools = payload['tools']
    print(f"工具数量: {len(tools)}")
    
    for i, tool in enumerate(tools, 1):
        print(f"\n工具 {i}:")
        print(f"  - 类型: {tool.get('type')}")
        
        if 'function' in tool:
            func = tool['function']
            print(f"  - 函数名: {func.get('name')}")
            print(f"  - 描述: {func.get('description')}")
            
            if 'parameters' in func:
                params = func['parameters']
                print(f"  - 参数类型: {params.get('type')}")
                print(f"  - 必需参数: {params.get('required', [])}")
                
                if 'properties' in params:
                    props = params['properties']
                    print(f"  - 参数属性:")
                    for prop_name, prop_info in props.items():
                        print(f"    * {prop_name}: {prop_info.get('type')} - {prop_info.get('description')}")

# 7. 对比：没有工具时的 payload
print(f"\n🔄 对比：没有工具时的 payload")
print("-" * 50)

# 创建没有工具的模型
llm_no_tools = ChatOpenAI(model="gpt-4o-mini")

try:
    payload_no_tools = llm_no_tools._get_request_payload(
        input_=input_text,
        stop=None,
        temperature=0.7
    )
    
    print(f"没有工具的 payload 结构:")
    for key, value in payload_no_tools.items():
        if key == 'messages':
            print(f"  - {key}: {len(value)} 条消息")
        elif isinstance(value, (str, int, float, bool)):
            print(f"  - {key}: {value}")
        else:
            print(f"  - {key}: {type(value).__name__}")
    
    print(f"\n📊 对比结果:")
    has_tools_keys = set(payload.keys())
    no_tools_keys = set(payload_no_tools.keys())
    
    print(f"  - 有工具的 payload keys: {sorted(has_tools_keys)}")
    print(f"  - 无工具的 payload keys: {sorted(no_tools_keys)}")
    print(f"  - 差异: {sorted(has_tools_keys - no_tools_keys)}")
    
    if 'tools' in has_tools_keys - no_tools_keys:
        print(f"  ✅ 确认：工具信息是在 _get_request_payload 中添加的!")
    
except Exception as e:
    print(f"❌ 对比调用失败: {e}")

print(f"\n🎉 总结：_get_request_payload 的作用")
print("=" * 80)

print(f"""
_get_request_payload 方法的关键作用:

1️⃣ 接收参数:
   • input_: 用户输入文本
   • stop: 停止词 (可选)
   • **kwargs: 包含 tools、temperature 等参数

2️⃣ 处理流程:
   • 将输入转换为消息格式
   • 合并所有参数到 payload
   • 如果 kwargs 中有 'tools'，添加到 payload['tools']
   • 设置模型参数 (temperature, model 等)

3️⃣ 输出结果:
   • 返回完整的 API payload 字典
   • 包含 model, messages, tools, temperature 等
   • 这个 payload 直接发送给 OpenAI API

🎯 关键发现:
   • tools 信息在这一步被正式添加到 API 请求中
   • 这是工具信息传递链的最后一环
   • 从 bind_tools() → kwargs → _get_request_payload() → API
""")

print(f"\n🔚 这就是 _get_request_payload 处理工具信息的完整过程！")
