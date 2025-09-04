

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from src.elements.models.models import llm
from src.elements.tools.tools import  GetTodayTool, GetWeatherTool, PostEmailTool

memory = MemorySaver()

tools = [GetTodayTool(), GetWeatherTool(), PostEmailTool()]

system_prompt = f'''你是一个天气、日期查询助手兼邮件助手，用户会提供天气、日期查询或邮件发送的需求，你需要根据用户的需求选择相应的工具进行处理。
要求如下：
1、如果用户的需求需要调用多个工具，你需要按照用户的需求顺序调用相应的工具，每次只给出一个工具的输入参数，观察这个工具返回的结果后，再决定是否继续调用其他工具，如果用户的需求被满足，则停止调用工具。
2、在邮件发送时，正文内容每行使用\\n\\n分割，**不要使用结束语和署名**，因为邮件发送工具会自动添加结束语和署名。'''

email_agent = create_react_agent(model=llm, tools=tools,checkpointer=memory,prompt=system_prompt,
                                    debug=False)
