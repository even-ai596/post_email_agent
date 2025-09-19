# -*- coding: utf-8 -*-
# =====================
#
#
# Author: lizilong
# Date: 2025/9/19
# Source Code: https://github.com/langchain-ai/langgraph/
# =====================


import os
import sys

from langchain_core.language_models import BaseChatModel
sys.path.append(os.getcwd())

from src.elements.tools.tools import tools
from src.elements.models.models import openai_client

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing_extensions import TypedDict

class AgentState(TypedDict):
    """The state of the agent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]


class Agent:
    def __init__(self, model: BaseChatModel, tools: list, memory: MemorySaver, system_prompt: str = ""):
        self.system_prompt = system_prompt
        graph = StateGraph(AgentState)
        graph.add_node("agent", self.agent_node)
        graph.add_node("tools", self.tools_node)
        graph.add_conditional_edges("agent", self.exists_action, {True: "tools", False: END})
        graph.add_edge("tools", "agent")
        graph.set_entry_point("agent")
        self.graph = graph.compile(checkpointer=memory)
        self.tools_map = {t.name: t for t in tools}
        self.model_with_tools = model.bind_tools(tools)

    def exists_action(self, state: AgentState):
        """
        判断是否需要调用工具
        """
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def agent_node(self, state: AgentState):
        """
        调用模型
        """

        system_prompt = SystemMessage(content=self.system_prompt)
        messages = [system_prompt] + state["messages"] 
        # print(messages)
        res = self.model_with_tools.invoke(messages)
        return {"messages": res}


    def tools_node(self, state: AgentState):
        """
        调用工具
        """
        tool_calls = state['messages'][-1].tool_calls
        results = []

        for t in tool_calls:
            result = self.tools_map[t['name']].invoke(t['args'])
            
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        
        print("Back to the model!")
        return {'messages': results}

    



memory = MemorySaver()


system_prompt = f'''你是一个天气、日期查询助手兼邮件助手，用户会提供天气、日期查询或邮件发送的需求，你需要根据用户的需求选择相应的工具进行处理。
要求如下：
1、如果用户的需求需要调用多个工具，你需要按照用户的需求顺序调用相应的工具，每次只给出一个工具的输入参数，观察这个工具返回的结果后，再决定是否继续调用其他工具，如果用户的需求被满足，则停止调用工具。
2、在邮件发送时，正文内容每行使用\\n\\n分割，**不要使用结束语和署名**，因为邮件发送工具会自动添加结束语和署名。
3、邮件工具的输入参数需要按照Email模型的定义进行输入，包括email_title、email_recipient、email_text，不要缺失参数'''

graph = Agent(openai_client, tools, memory, system_prompt).graph
if __name__ == "__main__":
    state = graph.invoke({"messages": [HumanMessage(content="今天是几号？")]}, config={"configurable": {"thread_id": "123"}})
    print(state)