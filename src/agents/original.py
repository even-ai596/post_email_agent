import os
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
import sys
sys.path.append(os.getcwd())
from src.agents.agent import memory
from src.elements.tools.tools import tools
from src.elements.models.models import openai_client


class AgentState(TypedDict):
    """The state of the agent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]

def agent(state: AgentState):

    SYSTEM_PROMPT = """你是一个天气、日期查询助手兼邮件助手，用户会提供天气、日期查询或邮件发送的需求，你需要根据用户的需求选择相应的工具进行处理。
要求如下：
1、如果用户的需求需要调用多个工具，你需要按照用户的需求顺序调用相应的工具，每次只给出一个工具的输入参数，观察这个工具返回的结果后，再决定是否继续调用其他工具，如果用户的需求被满足，则停止调用工具。
2、在邮件发送时，正文内容每行使用\\n\\n分割，**不要使用结束语和署名**，因为邮件发送工具会自动添加结束语和署名。
3、邮件工具的输入参数需要按照Email模型的定义进行输入，包括email_title、email_recipient、email_text，不要缺失参数
    """

    system_prompt = SystemMessage(content=SYSTEM_PROMPT)
    messages = [system_prompt] + state["messages"] 
    # print(messages)
    res = openai_client.bind_tools(tools).invoke(messages)
    return {"messages": res}


graph = StateGraph(AgentState) \
.add_node("agent", agent) \
.add_node("tools", ToolNode(tools)) \
.add_edge(START, "agent") \
.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": "__end__"}) \
.add_edge("tools", "agent") \
.compile(checkpointer=memory)

