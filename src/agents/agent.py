
import asyncio
import os
import sys
sys.path.append(os.getcwd())
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from src.elements.models.models import openai_client
from src.elements.tools.tools import tools
from langchain_core.tracers.langchain import wait_for_all_tracers

memory = MemorySaver()
from langchain_mcp_adapters.client import MultiServerMCPClient

    




system_prompt = f'''你是一个天气、日期查询助手兼邮件助手，用户会提供天气、日期查询或邮件发送的需求，你需要根据用户的需求选择相应的工具进行处理。
要求如下：
1、如果用户的需求需要调用多个工具，你需要按照用户的需求顺序调用相应的工具，每次只给出一个工具的输入参数，观察这个工具返回的结果后，再决定是否继续调用其他工具，如果用户的需求被满足，则停止调用工具。
2、在邮件发送时，正文内容每行使用\\n\\n分割，**不要使用结束语和署名**，因为邮件发送工具会自动添加结束语和署名。
3、邮件工具的输入参数需要按照Email模型的定义进行输入，包括email_title、email_recipient、email_text，不要缺失参数'''

email_agent = create_react_agent(model=openai_client, tools=tools,checkpointer=memory,prompt=system_prompt,
                                    debug=False)

from langchain.callbacks.tracers import LangChainTracer


tracer = LangChainTracer(project_name="email_agent")

config = {"configurable": {"thread_id": "123"}, "callbacks": [tracer]}
# config = {"configurable": {"thread_id": "123"}}


if __name__ == "__main__":
    
        # def get_answer_stream(generator):
        #     for chunk in generator:
        #         print(chunk["messages"])
        #         latest_chunk_info = chunk["messages"][-1]

        #         if latest_chunk_info.content and latest_chunk_info.type == "ai":
                    
        #             yield latest_chunk_info.content
        #         if latest_chunk_info.type == "ai" and latest_chunk_info.tool_calls:
        #             called_tool_zh_names = [a_tool for a_tool in latest_chunk_info.tool_calls]

        #             print("\n\n正在使用" + called_tool_zh_names[-1]["name"] + "\n\n参数为：" + str(latest_chunk_info.tool_calls[0]["args"]))
        #         if latest_chunk_info.type == "tool" and latest_chunk_info.content:
        #             print(
        #             "使用 " + latest_chunk_info.name + " 后获得了如下信息：\n\n" + latest_chunk_info.content)
        # state = email_agent.stream({"messages":[{"role":"user","content":"北京今天的天气怎么样？"}]}, config = config, stream_mode="values")

        # res = next(get_answer_stream(state))

        # print(res)
        # print(next(get_answer_stream(state)))


        async def get_answer_stream(async_generator):
            async for chunk in async_generator:
                print(chunk["messages"])
                latest_chunk_info = chunk["messages"][-1]

                if latest_chunk_info.content and latest_chunk_info.type == "ai":
                    
                    yield latest_chunk_info.content
                if latest_chunk_info.type == "ai" and latest_chunk_info.tool_calls:
                    called_tool_zh_names = [a_tool for a_tool in latest_chunk_info.tool_calls]

                    print("\n\n正在使用" + called_tool_zh_names[-1]["name"] + "\n\n参数为：" + str(latest_chunk_info.tool_calls[0]["args"]))
                if latest_chunk_info.type == "tool" and latest_chunk_info.content:
                    print(
                    "使用 " + latest_chunk_info.name + " 后获得了如下信息：\n\n" + latest_chunk_info.content)
        
        
        state = email_agent.astream({"messages":[{"role":"user","content":"查询2025/10/03北京到芜湖的火车票"}]}, config = config, stream_mode="values")
        async def main():
            res = await anext(get_answer_stream(state))
            print(res)
        asyncio.run(main())
        

        # async def main():
        #         state = email_agent.astream({"messages":{"role":"user","content":"今天是几号"}}, config = config, stream_mode="values")
        # #     async for chunk in state:
        # #         print(chunk)
        #         print(await anext(state))
        #         print(await anext(state))
        #         print(await anext(state))
        #         print(await anext(state))
              
        # asyncio.run(main())
        
