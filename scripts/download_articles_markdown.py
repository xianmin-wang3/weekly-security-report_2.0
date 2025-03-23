import os
import json
import requests

# === 路徑設定 ===
input_json_path = "../data/news_links.json"
output_folder = "../data"
os.makedirs(output_folder, exist_ok=True)

# === 讀取 JSON ===
with open(input_json_path, "r", encoding="utf-8") as f:
    news_links = json.load(f)

# === 逐篇下載 ===
for item in news_links:
    article_id = item["id"]
    url = item["link"]
    print(f"📥 下載第 {article_id} 篇 Markdown：{url}")

    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            print(f"⚠️ 錯誤：HTTP {response.status_code}")
            continue

        # 儲存成 .md 檔
        output_path = os.path.join(output_folder, f"article_{article_id}.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"✅ 儲存完成：{output_path}")

    except Exception as e:
        print(f"❌ 第 {article_id} 篇下載失敗：{e}")
