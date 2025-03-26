import requests
import feedparser
import json
import os
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# 設定 RSS 來源
RSS_URL = "https://www.twcert.org.tw/tw/rss-104-1.xml"
URL_FILTER = "twcert.org.tw"

# 設定時間範圍（過去 7 天）
one_week_ago = datetime.now() - timedelta(days=8)

# 檢查資料夾是否存在，不存在則創建
output_folder = "../data"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 使用 requests 下載 RSS XML，禁用 SSL 驗證
print(f"🔍 嘗試下載 RSS: {RSS_URL}")
try:
    response = requests.get(RSS_URL, verify=False)  # 禁用 SSL 驗證
    response.raise_for_status()  # 檢查請求是否成功
    print("✅ RSS XML 下載成功")
except requests.exceptions.RequestException as e:
    print(f"❌ RSS 下載失敗: {e}")
    exit()

# 將下載的 XML 內容傳給 feedparser 解析
feed = feedparser.parse(response.content)

# 檢查 RSS 是否成功解析
if not feed.entries:
    print(f"❌ RSS 解析失敗，條目數量: {len(feed.entries)}")
    print(f"錯誤訊息: {feed.get('bozo_exception', '無錯誤訊息')}")
    exit()

print(f"✅ RSS 解析成功，總共有 {len(feed.entries)} 篇條目")
print(f"嘗試抓取過去 7 天（{one_week_ago.strftime('%Y-%m-%d')} 至今）的資安新聞（來自 TWCERT/CC）\n")

# 計數器
article_count = 0

# 抓取過去 7 天的新聞
for entry in feed.entries:
    if URL_FILTER in entry.link.lower():  # 確保是 TWCERT 的文章
        # 解析發布時間
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                published_time_str = published_time.strftime('%Y-%m-%d %H:%M:%S')
            else:
                print("   ⚠️ 無法解析時間，使用當前時間作為備用")
                published_time = datetime.now()
                published_time_str = published_time.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"   ❌ 時間解析失敗: {e}")
            published_time = datetime.now()  # 備用時間
            published_time_str = published_time.strftime('%Y-%m-%d %H:%M:%S')

        # 檢查是否在過去 7 天內
        if published_time >= one_week_ago:
            print(f"📌 {entry.title}")
            print(f"   🕒 發布時間: {published_time_str}")
            print(f"   🔗 連結: {entry.link}")

            # 提取 <description> 內容並移除 HTML 標籤
            raw_content = entry.get('description', '').strip()
            if raw_content:
                # 使用 BeautifulSoup 移除 HTML 標籤
                soup = BeautifulSoup(raw_content, 'html.parser')
                clean_content = soup.get_text(strip=True)  # 移除標籤，連續文字
                
                # 額外移除文字中的換行符
                clean_content = clean_content.replace('\n', ' ')

                
                # 儲存資料
                article_data = {
                    "source": "TWCERT/CC",
                    "title": entry.title,
                    "published_time": published_time_str,
                    "link": entry.link,
                    "content": clean_content  # 儲存移除標籤並調整後的純文字
                }

                filename = f"{output_folder}/{published_time.strftime('%Y%m%d_%H%M%S')}_TWCERT.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(article_data, f, ensure_ascii=False, indent=4)

                print(f"   ✅ 文章已儲存: {filename}\n")
                article_count += 1
            else:
                print("   ❌ <description> 內容為空\n")

print(f"🎉 已完成抓取 {article_count} 篇新聞（過去 7 天）")

