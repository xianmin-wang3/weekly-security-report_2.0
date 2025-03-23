import os
import json
import requests
from bs4 import BeautifulSoup

ITHOME_URL = "https://www.ithome.com.tw/tags/資安日報"
NEWS_FILE = "../data/news_links.json"

def fetch_news_links():
    """抓取 iThome 最新 7 篇資安新聞的連結，並加上編號"""
    try:
        response = requests.get(ITHOME_URL, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        news_items = soup.find("div", class_="view-content").find_all("div", class_="views-row", limit=7)
        news_list = []

        for idx, item in enumerate(news_items, start=1):  # 從 1 開始編號
            a_tag = item.find("a")
            if not a_tag:
                continue

            link = a_tag["href"]
            if not link.startswith("http"):
                link = "https://r.jina.ai/https://www.ithome.com.tw" + link

            news_list.append({
                "id": idx,
                "link": link
            })

            print(f"✅ [{idx}] 已抓取連結: {link}")

        os.makedirs(os.path.dirname(NEWS_FILE), exist_ok=True)
        with open(NEWS_FILE, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=4)

        print(f"✅ 所有新聞連結已儲存至 {NEWS_FILE}")

    except Exception as e:
        print(f"⚠️ 抓取新聞連結錯誤: {e}")

if __name__ == "__main__":
    fetch_news_links()
