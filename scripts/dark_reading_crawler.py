import feedparser
import time
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os

# 設定 RSS 來源
RSS_URL = "https://www.darkreading.com/rss.xml"
CONTENT_SELECTOR = ("div", {"id": "article-main"})
URL_FILTER = "darkreading"

# 設定時間範圍（7 天內）
one_week_ago = datetime.now() - timedelta(days=7)

# 檢查資料夾是否存在，不存在則創建
output_folder = "../data/dark_reading"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 解析 RSS
feed = feedparser.parse(RSS_URL)
print(f"🔍 嘗試抓取過去 7 天內的資安新聞（來自 Dark Reading）\n")

# 過濾 7 天內的新聞
for entry in feed.entries:
    if hasattr(entry, "published_parsed"):  # 確保有發佈時間
        published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        
        if published_time >= one_week_ago and URL_FILTER in entry.link.lower():
            print(f"📌 {entry.title}")
            print(f"   🕒 發布時間: {published_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   🔗 連結: {entry.link}")

            # 嘗試抓取新聞內文
            try:
                scraper = cloudscraper.create_scraper()
                response = scraper.get(entry.link)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                article_body = soup.find(*CONTENT_SELECTOR)
                
                if article_body:
                    paragraphs = article_body.find_all("p")
                    content = "\n".join(p.get_text(strip=True) for p in paragraphs)

                    # 將內文保存為 JSON 檔案
                    article_data = {
                        "source": "Dark Reading",
                        "title": entry.title,
                        "published_time": published_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "link": entry.link,
                        "content": content
                    }

                    filename = f"{output_folder}/{published_time.strftime('%Y%m%d_%H%M%S')}_DarkReading.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(article_data, f, ensure_ascii=False, indent=4)

                    print(f"   ✅ 文章已儲存: {filename}\n")
                    break  # 成功抓取一篇後停止
                else:
                    print("   ❌ 無法擷取內文\n")
            
            except Exception as e:
                print(f"   ❌ 下載失敗: {e}\n")
