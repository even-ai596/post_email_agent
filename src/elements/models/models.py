import asyncio
from langchain_core.messages import HumanMessage
from openai import OpenAI, AzureOpenAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.getcwd())


load_dotenv()
# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),
#     base_url=os.getenv("OPENAI_BASE_URL"),
    
# )
# completion = client.chat.completions.create(
#     model="gpt-5-2025-08-07",
#     messages=[
#         {
#             "role": "user",
#             "content": "你是谁？",
#         }
#     ],
# )
# print(completion.choices[0].message.content)
# exit()
# gpt4o = AzureChatOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY", ""),
#     azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT", ""),
#     api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION", ""),
#     azure_deployment="gpt-4o",
# )
# gpt4o.invoke("你好，你是谁？")

# gpt = AzureOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
#     api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION"),
#     azure_deployment="gpt-4o",
# )
# compeletion = gpt.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "你是谁？",
#         }
#     ],
#     model="gpt-4o",
# )
import os
# from openai import OpenAI
from langchain_anthropic import ChatAnthropic
# import litellm
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL")

# response = litellm.completion(
#     model="openai/kimi-k2-250711",               # add `openai/` prefix to model so litellm knows to route to OpenAI
    
#     messages=[
#                 {
#                     "role": "user",
#                     "content": "你是谁",
#                 }
#     ],
# )
# print(response)
# exit()
# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Openai客户端，从环境变量中读取您的API Key
openai_client = ChatOpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url=os.getenv("OPENAI_ASEURL", ""),
    # 从环境变量中获取您的 API Key
    api_key=os.getenv("OPENAI_API_KEY", ""),
    model=os.getenv("OPENAI_MODEL", ""),
)


# claude_sonnet_4 = ChatAnthropic(
#     api_key=os.getenv("OPENAI_API_KEY", ""),
#     base_url=os.getenv("OPENAI_BASE_URL", ""),
#     model="claude-sonnet-4@20250514",
#     temperature=0,
#     max_tokens=1024,
#     timeout=None,
#     max_retries=2,
#     # other params...
# )



# from google import genai
# from google.genai import types
 
# client = genai.Client(
#     api_key=os.getenv("OPENAI_API_KEY"),
#     http_options=types.HttpOptions(
#         api_version='v1',
#         base_url=os.getenv("OPENAI_BASE_URL"),
#     )
# )
 
# response = client.models.generate_content(
#     model="gemini-2.0-flash-001",
#     contents="How does AI work?",
# )
 
# print(response)
    
# exit()
# from langchain_google_genai import ChatGoogleGenerativeAI
# os.environ["GOOGLE_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


# gemini = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash-001",
#     # base_url=os.getenv("OPENAI_BASE_URL", ""),
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
#     # other params...
# )
if __name__ == "__main__":
    # print(compeletion.choices[0].message.content)
    # print(llm.invoke("你好吗？"))
    # print(claude_sonnet_4.invoke("你好,你是谁"))



    print(asyncio.run(openai_client.ainvoke("你好，你是谁？")))
    # print(openai_client.bind_tools(tools).invoke([HumanMessage(content="北京今天的天气怎么样？")]))