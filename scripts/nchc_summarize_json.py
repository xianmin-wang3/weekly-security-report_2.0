import os
import json
import requests

# === 設定參數 ===
ARTICLE_DIR = "../data"
SUMMARY_DIR = "../data"
EXCLUDE_FILE = "news_links.json"
SUMMARY_FILE = "summary_8.md"

# ✅ NCHC GenAI API 設定
NCHC_API_KEY = os.getenv("NCHC_API_KEY")
if not NCHC_API_KEY:
    raise ValueError("❌ 環境變數 NCHC_API_KEY 未設定！")

MODEL_NAME = "Microsoft-Phi-4-multimodal-instruct"
URL = "https://outer-medusa.genai.nchc.org.tw/v1/chat/completions"
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {NCHC_API_KEY}",
    "Content-Type": "application/json"
}

# ✅ 掃描所有 JSON 檔案（排除特定）
all_files = os.listdir(ARTICLE_DIR)
json_files = [f for f in all_files if f.endswith(".json") and f != EXCLUDE_FILE]

if not json_files:
    print("⚠️ 沒有可處理的 JSON 檔案")
    exit(0)

# ✅ 合併所有內容
combined_content = ""
for file_name in sorted(json_files):  # 可依字母順序一致化
    article_path = os.path.join(ARTICLE_DIR, file_name)

    try:
        print(f"🧠 正在統合摘要文章...")
        with open(article_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            title = data.get("title", "（無標題）")
            content = data.get("content", "").strip()

        if not content:
            print(f"⚠️ 檔案 {file_name} 缺少 content，跳過。")
            continue

        combined_content += f"【標題】：{title}\n【內容】：{content}\n\n"

    except Exception as e:
        print(f"❌ 無法處理 {file_name}：{e}")

# ✅ 如果沒有有效內容就退出
if not combined_content.strip():
    print("⚠️ 所有 JSON 檔案皆無有效內容，結束。")
    exit(0)

# ✅ 建立統一摘要用 prompt
prompt = f"""
你是專業的資安新聞摘要助手，以下是三篇資安新聞的原始內容，請依據以下四個面向進行**統合摘要**：

1. 資安防護：描述組織或系統所實施的防禦性措施
2. 資安威脅態勢：揭露弱點(Vulnerability)、漏洞利用(Exploit)、攻擊技術趨勢
3. 資安事件：實際發生的攻擊事件、影響範圍、受害對象與時間
4. 未來趨勢：針對威脅模式、防禦技術、產業與政策趨勢進行預測與建議

請使用繁體中文撰寫摘要，並依以下格式輸出：

### 1. 資安防護
（依序列出要點）

### 2. 資安威脅態勢
（漏洞編號: 要點）

### 3. 資安事件
（發生時間: 事件要點）

### 4. 未來趨勢
（依序列出要點）

以下是三篇文章內容：
{combined_content}
"""

# ✅ 呼叫 NCHC 模型 API
payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "system", "content": "你是專業的資安新聞摘要助手。"},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.2,
    "top_p": 0.92,
}

response = requests.post(URL, headers=HEADERS, json=payload)

# ✅ 寫入 summary_8.md
os.makedirs(SUMMARY_DIR, exist_ok=True)
summary_path = os.path.join(SUMMARY_DIR, SUMMARY_FILE)

if response.status_code == 200:
    result = response.json()
    summary = result["choices"][0]["message"]["content"].strip()

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n\n# 🧾 三篇新聞統合摘要\n\n")
        f.write(summary)
        f.write("\n\n" + "="*80 + "\n")

    print(f"✅ 統合摘要完成，已寫入：{summary_path}")

else:
    print(f"❌ 模型 API 失敗（HTTP {response.status_code}）：")
    print(response.text)
