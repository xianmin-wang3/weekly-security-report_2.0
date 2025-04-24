import os
import time
from groq import Groq

# === 設定參數 ===
ARTICLE_DIR = "../data"
SUMMARY_DIR = "../data"
ARTICLE_PREFIX = "article_"
SUMMARY_PREFIX = "summary_"
NUM_ARTICLES = 7
WAIT_SECONDS = 10

# ✅ 取得 API 金鑰
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ 環境變數 GROQ_API_KEY 未設定！")

client = Groq(api_key=GROQ_API_KEY)

# ✅ 開始逐篇處理
for i in range(1, NUM_ARTICLES + 1):
    article_path = os.path.join(ARTICLE_DIR, f"{ARTICLE_PREFIX}{i}.md")
    summary_path = os.path.join(SUMMARY_DIR, f"{SUMMARY_PREFIX}{i}.md")

    print(f"\n📄 處理第 {i} 篇文章: {article_path}")

    if not os.path.exists(article_path):
        print(f"⚠️ 找不到檔案，跳過：{article_path}")
        continue

    with open(article_path, "r", encoding="utf-8") as f:
        article_text = f.read()

    # ✅ 建立 Prompt
    prompt = f"""
你是專業的資安新聞摘要助手，我手邊有一篇需整理的資安文章。
請依據以下面向(須符合定義的內容)，詳細彙整本次資安日報(只要彙整"近期資安日報"前面的內容):

1. 資安防護[定義：描述組織或系統所實施的防禦性措施]
2. 資安威脅態勢[定義：揭露本次資安新聞中出現的弱點(Vulnerability)、漏洞利用(Exploit)與整體攻擊技術趨勢。]
3. 資安事件[定義：實際發生的攻擊事件或資安事故，包含具體受害對象、影響範圍與時間點。]
4. 未來趨勢[定義：針對近期觀測到的威脅模式、防禦技術演進、產業動態與政策方向，提供預期中的發展與建議。]

請使用繁體中文回答。

輸出格式:
### 1. 資安防護
*(內容依序排列)
### 2. 資安威脅態勢
*(漏洞編號: 內容依序排列)
### 3. 資安事件
*(發生資安事件之西元年-月-日: 內容依序排列)
### 4. 未來趨勢
*(內容依序排列)

以下是文章內容：
{article_text}
    """

    try:
        print(f"🧠 正在摘要第 {i} 篇文章...")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "你是專業的資安新聞摘要助手。"},
                {"role": "user", "content": prompt}
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
        )

        summary = chat_completion.choices[0].message.content.strip()

        # ✅ 儲存摘要
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"✅ 摘要完成：{summary_path}")

        # ✅ 等待 10 秒再處理下一篇
        print(f"⏳ 等待 {WAIT_SECONDS} 秒後處理下一篇...")
        time.sleep(WAIT_SECONDS)

    except Exception as e:
        print(f"❌ 第 {i} 篇摘要失敗：{e}")
