import feedparser
import time
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os

# 設定 RSS 來源
rss_url = "https://feeds.feedburner.com/TheHackersNews"

# 解析 RSS
feed = feedparser.parse(rss_url)

# 設定時間範圍（7 天內）
one_week_ago = datetime.now() - timedelta(days=8)

# 檢查資料夾是否存在，不存在則創建
output_folder = "../data"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

print(f"🔍 嘗試抓取過去 7 天內的資安新聞（來自 {feed.feed.title}）\n")

# 過濾 7 天內的新聞
for entry in feed.entries:
    if hasattr(entry, "published_parsed"):  # 確保有發佈時間
        published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        
        # 只儲存網址包含 "weekly" 的文章
        if published_time >= one_week_ago and "weekly" in entry.link.lower():
            print(f"📌 {entry.title}")
            print(f"   🕒 發布時間: {published_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   🔗 連結: {entry.link}")

            # 嘗試抓取新聞內文
            try:
                scraper = cloudscraper.create_scraper()  # 使用 cloudscraper 繞過 Cloudflare
                response = scraper.get(entry.link)
                response.raise_for_status()  # 確保請求成功
                
                soup = BeautifulSoup(response.text, "html.parser")

                # 嘗試提取主要內容
                article_body = soup.find("div", class_="articlebody clear cf")
                if article_body:
                    paragraphs = article_body.find_all("p")  # 取出所有 <p> 標籤
                    content = "\n".join(p.get_text(strip=True) for p in paragraphs)  # 連接段落

                    # 將內文保存為 JSON 檔案
                    article_data = {
                        "source": "TheHackersNews",
                        "title": entry.title,
                        "published_time": published_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "link": entry.link,
                        "content": content
                    }

                    # 創建文章文件，保存為 JSON
                    filename = f"{output_folder}/{published_time.strftime('%Y%m%d_%H%M%S')}_TheHackersNews.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(article_data, f, ensure_ascii=False, indent=4)

                    print(f"   ✅ 文章已儲存: {filename}\n")
                    
                    # 找到符合條件的文章後，立刻停止抓取
                    break

                else:
                    print("   ❌ 無法擷取內文\n")
            
            except Exception as e:
                print(f"   ❌ 下載失敗: {e}\n")
