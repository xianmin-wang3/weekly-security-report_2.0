import requests
import os

# 讀取環境變數中的 LINE Notify Token
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")

# 設定 Markdown 檔案路徑
MARKDOWN_FILE = "../data/weekly_report.md"

# LINE Notify API URL
LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"

def send_line_notify():
    if not LINE_NOTIFY_TOKEN:
        print("❌ 錯誤: 未設定 LINE_NOTIFY_TOKEN 環境變數")
        return

    if not os.path.exists(MARKDOWN_FILE):
        print(f"❌ 錯誤: 檔案不存在: {MARKDOWN_FILE}")
        return

    # 設定 HTTP 標頭
    headers = {
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
    }

    # 讀取 Markdown 內容
    with open(MARKDOWN_FILE, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    # LINE Notify 限制訊息長度最多 1000 個字元
    if len(markdown_content) > 1000:
        markdown_content = markdown_content[:1000] + "...\n(內容過長，請查看完整報告)"

    # 設定要發送的訊息
    data = {
        "message": f"{markdown_content}"
    }

    # 發送通知
    response = requests.post(LINE_NOTIFY_URL, headers=headers, data=data)

    # 檢查回應
    if response.status_code == 200:
        print("✅ 訊息已成功發送至 LINE！")
    else:
        print(f"❌ LINE Notify 發送失敗，錯誤碼: {response.status_code}, 錯誤訊息: {response.text}")

if __name__ == "__main__":
    send_line_notify()
