# 深度追踪 invoke 方法的具体执行代码

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Type
import json
from unittest.mock import patch
import inspect

# 1. 定义工具
class WeatherInput(BaseModel):
    city: str = Field(description="城市名称")

class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "获取天气信息"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, city: str):
        return f"{city}的天气是晴天，25度"

# 2. 创建模型和绑定工具
weather_tool = WeatherTool()
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([weather_tool])

print("=" * 100)
print("深度追踪：invoke 方法的具体执行代码")
print("=" * 100)

# 3. 拦截和展示关键方法的执行
original_invoke = llm_with_tools.__class__.invoke
original_bound_invoke = llm_with_tools.bound.__class__.invoke
original_generate_prompt = llm_with_tools.bound.__class__.generate_prompt
original_generate = llm_with_tools.bound.__class__.generate
original_get_request_payload = llm_with_tools.bound._get_request_payload

step_counter = 1

def traced_runnable_binding_invoke(self, input, config=None, **kwargs):
    global step_counter
    print(f"\n{'='*60}")
    print(f"步骤 {step_counter}: RunnableBinding.invoke() 执行")
    print(f"{'='*60}")
    step_counter += 1
    
    print(f"输入参数:")
    print(f"  - input: {input}")
    print(f"  - config: {config}")
    print(f"  - kwargs: {kwargs}")
    
    print(f"\nself.kwargs (绑定的工具信息):")
    for key, value in self.kwargs.items():
        if key == 'tools':
            print(f"  - {key}: {len(value)} 个工具")
        else:
            print(f"  - {key}: {value}")
    
    # 合并参数的逻辑
    merged_kwargs = {**self.kwargs, **kwargs}
    print(f"\n合并后的 kwargs:")
    for key, value in merged_kwargs.items():
        if key == 'tools':
            print(f"  - {key}: {len(value)} 个工具")
        else:
            print(f"  - {key}: {value}")
    
    print(f"\n即将调用: self.bound.invoke(input, merged_config, **merged_kwargs)")
    print(f"其中 self.bound 是: {type(self.bound)}")
    
    # 调用原始方法
    return original_invoke(self, input, config, **kwargs)

def traced_chat_openai_invoke(self, input, config=None, **kwargs):
    global step_counter
    print(f"\n{'='*60}")
    print(f"步骤 {step_counter}: ChatOpenAI.invoke() 执行")
    print(f"{'='*60}")
    step_counter += 1
    
    print(f"接收到的参数:")
    print(f"  - input: {input}")
    print(f"  - config: {config}")
    print(f"  - kwargs keys: {list(kwargs.keys())}")
    
    if 'tools' in kwargs:
        print(f"  - tools: {len(kwargs['tools'])} 个工具已传入")
        print(f"    工具名: {[tool['function']['name'] for tool in kwargs['tools']]}")
    
    print(f"\n即将调用: BaseChatModel.invoke() -> generate_prompt()")
    
    # 调用原始方法
    return original_bound_invoke(self, input, config, **kwargs)

def traced_generate_prompt(self, prompts, stop=None, callbacks=None, **kwargs):
    global step_counter
    print(f"\n{'='*60}")
    print(f"步骤 {step_counter}: generate_prompt() 执行")
    print(f"{'='*60}")
    step_counter += 1
    
    print(f"参数:")
    print(f"  - prompts: {len(prompts)} 个提示")
    print(f"  - kwargs keys: {list(kwargs.keys())}")
    
    if 'tools' in kwargs:
        print(f"  - tools: 工具信息继续传递")
    
    print(f"\n即将调用: self.generate() -> _generate()")
    
    # 调用原始方法
    return original_generate_prompt(self, prompts, stop, callbacks, **kwargs)

def traced_generate(self, messages, stop=None, callbacks=None, **kwargs):
    global step_counter
    print(f"\n{'='*60}")
    print(f"步骤 {step_counter}: generate() 执行")
    print(f"{'='*60}")
    step_counter += 1
    
    print(f"参数:")
    print(f"  - messages: {len(messages)} 批消息")
    print(f"  - kwargs keys: {list(kwargs.keys())}")
    
    if 'tools' in kwargs:
        print(f"  - tools: 工具信息继续传递到 _generate()")
    
    print(f"\n即将调用: self._generate()")
    
    # 调用原始方法
    return original_generate(self, messages, stop, callbacks, **kwargs)

def traced_get_request_payload(self, input_, *, stop=None, **kwargs):
    global step_counter
    print(f"\n{'='*60}")
    print(f"步骤 {step_counter}: _get_request_payload() 执行")
    print(f"{'='*60}")
    step_counter += 1
    
    print(f"参数:")
    print(f"  - input_: {input_}")
    print(f"  - stop: {stop}")
    print(f"  - kwargs keys: {list(kwargs.keys())}")
    
    if 'tools' in kwargs:
        print(f"  - tools: {len(kwargs['tools'])} 个工具")
        print(f"    即将添加到 API payload 中")
    
    # 调用原始方法获取 payload
    payload = original_get_request_payload(self, input_, stop=stop, **kwargs)
    
    print(f"\n构建的 payload:")
    print(f"  - model: {payload.get('model')}")
    print(f"  - messages: {len(payload.get('messages', []))} 条消息")
    
    if 'tools' in payload:
        print(f"  - tools: {len(payload['tools'])} 个工具 ✓")
        print(f"    工具名: {[tool['function']['name'] for tool in payload['tools']]}")
    else:
        print(f"  - tools: 未找到工具信息 ✗")
    
    print(f"\n这个 payload 将发送给 OpenAI API")
    
    return payload

# 4. 应用拦截器
llm_with_tools.__class__.invoke = traced_runnable_binding_invoke
llm_with_tools.bound.__class__.invoke = traced_chat_openai_invoke
llm_with_tools.bound.__class__.generate_prompt = traced_generate_prompt
llm_with_tools.bound.__class__.generate = traced_generate
llm_with_tools.bound._get_request_payload = traced_get_request_payload

print("开始追踪 invoke 调用...")

# 5. 执行调用
try:
    response = llm_with_tools.invoke("北京天气怎么样？")
    
    print(f"\n{'='*60}")
    print(f"最终结果")
    print(f"{'='*60}")
    
    print(f"响应类型: {type(response)}")
    print(f"内容: {response.content}")
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"工具调用: {len(response.tool_calls)} 个")
        for tool_call in response.tool_calls:
            print(f"  - {tool_call['name']}: {tool_call['args']}")
    
    print(f"\n🎉 工具信息成功从 bind_tools() 传递到 OpenAI API！")
    
except Exception as e:
    print(f"执行出错: {e}")

print(f"\n{'='*100}")
print("追踪完成：工具信息传递的完整路径")
print(f"{'='*100}")

print("""
工具信息传递路径总结:

1. bind_tools() 阶段:
   工具定义 → convert_to_openai_tool() → RunnableBinding.kwargs['tools']

2. invoke() 调用链:
   RunnableBinding.invoke()
   ↓ 合并 self.kwargs (包含 tools) 和传入的 kwargs
   ↓ 
   ChatOpenAI.invoke(**merged_kwargs)  # tools 在这里
   ↓
   BaseChatModel.invoke() → generate_prompt() → generate() → _generate()
   ↓ kwargs 中的 tools 一路传递
   ↓
   _get_request_payload(**kwargs)  # tools 最终到达这里
   ↓
   构建 API payload，将 tools 添加到请求中
   ↓
   发送给 OpenAI API

关键观察：
✓ 工具信息在每个步骤都成功传递
✓ RunnableBinding 起到了参数合并和透传的关键作用  
✓ 最终在 _get_request_payload() 中添加到 API 请求
""")
