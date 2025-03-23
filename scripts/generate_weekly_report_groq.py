import os
from groq import Groq

MERGED_FILE = "../data/merged_summary.md"
REPORT_FILE = "../data/weekly_report.md"

# ✅ API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ 環境變數 GROQ_API_KEY 未設定！")

client = Groq(api_key=GROQ_API_KEY)

# ✅ 讀取合併後內容
if not os.path.exists(MERGED_FILE):
    raise FileNotFoundError(f"❌ 找不到合併檔案：{MERGED_FILE}")

with open(MERGED_FILE, "r", encoding="utf-8") as f:
    merged_content = f.read()

# ✅ Prompt 設定
prompt = f"""
你是專業的資安新聞摘要助手，以下是我彙整的一週資安新聞內容，已依照分類整理。
請你根據下列格式進行「更進一步的整合、統整與優化」，整理成一份專業的資安週報。

請使用繁體中文、條理清楚、避免重複。

輸出格式：
### 1. 資安防護
（請整合各篇防護措施，條列且不重複）

### 2. 資安威脅態勢
（整合 CVE 漏洞與利用方式，若有攻擊方式請一併摘要）

### 3. 資安事件
（彙整所有事件，請加上時間與影響範圍）

### 4. 未來趨勢
（統整趨勢觀察，若有政策、產業技術變化請補充）

--- 以下是彙整內容 ---
{merged_content}
"""

# ✅ 呼叫 Groq API
try:
    print("🧠 正在產生完整資安週報...")
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "你是專業的資安新聞分析師，請協助撰寫週報。"},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
    )

    weekly_report = chat_completion.choices[0].message.content.strip()

    # ✅ 儲存輸出
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(weekly_report)

    print(f"✅ 資安週報已儲存至：{REPORT_FILE}")

except Exception as e:
    print(f"❌ 週報產生失敗：{e}")
