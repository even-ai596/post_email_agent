from openai import OpenAI,AzureOpenAI
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)
llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION"),
    azure_deployment="gpt-4o",
)
gpt = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION"),
    azure_deployment="gpt-4o",
)
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
from openai import OpenAI
from langchain_anthropic import ChatAnthropic
import litellm
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
gpt_4_1 = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url=os.getenv("OPENAI_BASE_URL"),
    # 从环境变量中获取您的 API Key
    api_key=os.getenv("OPENAI_API_KEY"),
)


claude_sonnet_4 = ChatAnthropic(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    model="claude-sonnet-4@20250514",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    # other params...
)

    


if __name__ == "__main__":
    # print(compeletion.choices[0].message.content)
    # print(llm.invoke("你好吗？"))
    # print(claude_sonnet_4.invoke("你好,你是谁"))



    completion = gpt_4_1.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        model="gpt-4.1-2025-04-14",
        messages=[
            # {"role": "system", "content": "你是人工智能助手"},
            {"role": "user", "content": "你好，你是谁？"},
        ],
    )
    print(completion.choices[0].message.content)