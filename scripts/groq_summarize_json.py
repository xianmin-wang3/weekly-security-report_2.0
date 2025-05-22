import os
import json
from groq import Groq

# === 設定參數 ===
ARTICLE_DIR = "../data"
SUMMARY_DIR = "../data"
EXCLUDE_FILE = "news_links.json"
SUMMARY_FILE = "summary_8.md"

# ✅ Groq API 設定
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ 環境變數 GROQ_API_KEY 未設定！")

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
client = Groq(api_key=GROQ_API_KEY)

# ✅ 掃描所有 JSON 檔案（排除特定）
all_files = os.listdir(ARTICLE_DIR)
json_files = [f for f in all_files if f.endswith(".json") and f != EXCLUDE_FILE]

if not json_files:
    print("⚠️ 沒有可處理的 JSON 檔案")
    exit(0)

# ✅ 合併所有內容
combined_content = ""
for file_name in sorted(json_files):
    article_path = os.path.join(ARTICLE_DIR, file_name)
    try:
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

if not combined_content.strip():
    print("⚠️ 所有 JSON 檔案皆無有效內容，結束。")
    exit(0)

# ✅ 建立統一摘要用 prompt
prompt = f"""
你是一位專業的資安新聞摘要助手，以下是我提供的三篇資安新聞文章，請根據以下四個明確面向，進行完整內容的彙整與條列式說明。

請務必：
1. 依據定義進行分類，不要重複、混淆。
2. 每一分類中，使用 `* ` 作為條列起始符號。
3. 避免冗長敘述，請條理清楚、簡潔扼要地摘要重點。
4. 僅彙整「近期資安日報」標題之前的內容，忽略後續補充段落。

### 面向與定義如下：

1. **資安防護**  
　　定義：組織或系統已實施的防禦性措施，例如多因子驗證、防火牆、入侵偵測系統等。

2. **資安威脅態勢**  
　　定義：本新聞中揭露的弱點（Vulnerability）、漏洞利用（Exploit）及整體攻擊技術趨勢，應包含漏洞編號與利用方式。

3. **資安事件**  
　　定義：新聞中提到的實際攻擊事件，請包含事件日期（西元年-月-日）、受害對象、攻擊方式與影響範圍。

4. **未來趨勢**  
　　定義：根據觀測資訊，提供對資安威脅演進、防禦技術發展、產業政策方向的預測與建議。

---

### 輸出格式（請嚴格遵守）：

### 1. 資安防護  
* 說明項目 1  
* 說明項目 2  

### 2. 資安威脅態勢  
* CVE-XXXX-XXXX：說明漏洞與利用情境  
* CVE-YYYY-YYYY：另一項漏洞說明  

### 3. 資安事件  
* 2025-05-14：攻擊對象為 XX 機構，攻擊手法為 YYY，影響為 ZZZ。  

### 4. 未來趨勢  
* 趨勢觀察項目 1  
* 趨勢觀察項目 2  

---

以下是三篇文章內容：
{combined_content}
"""

# ✅ 呼叫 Groq API
try:
    print("🧠 正在產生統合摘要...")
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "你是專業的資安新聞摘要助手。"},
            {"role": "user", "content": prompt}
        ],
        model=MODEL_NAME,
        temperature=0.2,
        top_p=0.92,
    )

    summary = chat_completion.choices[0].message.content.strip()

    os.makedirs(SUMMARY_DIR, exist_ok=True)
    summary_path = os.path.join(SUMMARY_DIR, SUMMARY_FILE)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n\n# 🧾 三篇新聞統合摘要\n\n")
        f.write(summary)
        f.write("\n\n" + "="*80 + "\n")

    print(f"✅ 統合摘要完成，已寫入：{summary_path}")

except Exception as e:
    print(f"❌ Groq API 呼叫失敗：{e}")
