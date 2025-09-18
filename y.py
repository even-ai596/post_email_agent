import os
import openai
import requests

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

# 用 requests 模拟一次 Cursor 的调用
url = f"{base_url}/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
data = {
    "model": "gpt-5-2025-08-07",
    "messages": [{"role": "user", "content": "hello"}],
}

print(">>> 请求 URL:", url)
print(">>> 请求 Headers:", headers)

resp = requests.post(url, headers=headers, json=data)
print(">>> 返回状态:", resp.status_code)
print(">>> 返回内容:", resp.text[:200], "...")
