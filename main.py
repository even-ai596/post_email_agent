from io import BytesIO
from httpx import get
import streamlit as st
import ast
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from src.agents.agent import email_agent  
from random import randint
from langchain.callbacks.tracers import LangChainTracer


tracer = LangChainTracer()
if __name__ == "__main__":
    thread_id = randint(1,999999)
    config = {"configurable": {"thread_id": thread_id}, "callbacks": [tracer]}
    st.set_page_config(page_title="AgentDemo", page_icon="", layout="centered", initial_sidebar_state="auto",
                       menu_items=None)
    st.title("AgentDemo")
    if "config" not in st.session_state.keys():
        st.session_state.config = config
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{
            "role": "assistant",
            "content": "我是gpt，请问有什么可以帮助你的吗？"
        }]
        with st.chat_message("assistant"):
            st.markdown(st.session_state.messages[-1]["content"])
    else:
        for i,message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    if user_input := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        statu_container = st.container(border=True)

        def get_answer_stream():
            last_human_message = HumanMessage(content=user_input)
            stream = email_agent.stream({"messages": [last_human_message]}, stream_mode="values", config=st.session_state.config)
            
            for chunk in stream:
                latest_chunk_info = chunk["messages"][-1]
                print(chunk)
                if latest_chunk_info.content and latest_chunk_info.type == "ai":
                    
                    yield latest_chunk_info.content
                if latest_chunk_info.type == "ai" and latest_chunk_info.tool_calls:
                    called_tool_zh_names = [a_tool for a_tool in latest_chunk_info.tool_calls]

                    statu_container.markdown(str(latest_chunk_info.additional_kwargs["tool_calls"][0]["function"])+"\n\n正在使用" + called_tool_zh_names[-1]["name"])
                if latest_chunk_info.type == "tool" and latest_chunk_info.content:
                    statu_container.markdown(
                    "使用 " + latest_chunk_info.name + " 后获得了如下信息：\n\n" + latest_chunk_info.content)
        
        answer = next(get_answer_stream())
        with st.chat_message("assistant"):
            st.markdown(answer)
        # answer = st.write_stream(get_answer_stream())
        an_answer_message = {"role": "assistant", "content": answer, "image": None}
        st.session_state.messages.append(an_answer_message)
