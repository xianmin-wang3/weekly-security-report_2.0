import requests

# 替換成你的 API 金鑰與模型名稱
api_key = "?"
model_name = "TAIDE-LX-7B-Chat"

url = "https://outer-medusa.genai.nchc.org.tw/v1/chat/completions"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "max_tokens": 1024,
    "messages": [
        {
            "content": "You are a helpful assistant. 你是一個樂於助人的助手。",
            "role": "system"
        },
        {
            "content": "你好",
            "role": "user"
        }
    ],
    "model": model_name,
    "temperature": 0.2,
    "top_p": 0.92
}

response = requests.post(url, headers=headers, json=payload)

# 提取模型生成的文字
if response.status_code == 200:
    result = response.json()
    generated_text = result["choices"][0]["message"]["content"]
    print(generated_text)
else:
    print("錯誤代碼:", response.status_code)
    print("錯誤訊息:", response.text)
