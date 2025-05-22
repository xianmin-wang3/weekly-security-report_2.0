import os
import time
import requests

# === 設定參數 ===
ARTICLE_DIR = "../data"
SUMMARY_DIR = "../data"
ARTICLE_PREFIX = "article_"
SUMMARY_PREFIX = "summary_"
NUM_ARTICLES = 7
WAIT_SECONDS = 10


# ✅ NCHC API 設定
NCHC_API_KEY = os.getenv("NCHC_API_KEY")
if not NCHC_API_KEY:
    raise ValueError("❌ 環境變數 NCHC_API_KEY 未設定！")

MODEL_NAME = "Microsoft-Phi-4-multimodal-instruct"  # 或從 /v1/models 查詢其他可用模型
URL = "https://outer-medusa.genai.nchc.org.tw/v1/chat/completions"
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {NCHC_API_KEY}",
    "Content-Type": "application/json"
}

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
你是一位專業的資安新聞摘要助手，以下是我提供的一篇資安新聞文章，請根據以下四個明確面向，進行完整內容的彙整與條列式說明。

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

以下是文章內容：
{article_text}
"""

    try:
        print(f"🧠 正在摘要第 {i} 篇文章...")

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

        if response.status_code == 200:
            result = response.json()
            summary = result["choices"][0]["message"]["content"].strip()

            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary)

            print(f"✅ 摘要完成：{summary_path}")
            print(f"⏳ 等待 {WAIT_SECONDS} 秒後處理下一篇...")
            time.sleep(WAIT_SECONDS)

        else:
            print(f"❌ 第 {i} 篇摘要失敗（HTTP {response.status_code}）：")
            print(response.text)

    except Exception as e:
        print(f"❌ 第 {i} 篇摘要發生例外錯誤：{e}")
