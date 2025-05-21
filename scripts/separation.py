import os
import re

# === 設定參數 ===
INPUT_PATH = "../data/merged_summary.md"
OUTPUT_DIR = "../data"

# === 對應檔案名稱與標題 ===
section_info = {
    "資安防護": ("security.md", "### 1. 資安防護"),
    "資安威脅態勢": ("threat.md", "### 2. 資安威脅態勢"),
    "資安事件": ("incident.md", "### 3. 資安事件"),
    "未來趨勢": ("future.md", "### 4. 未來趨勢")
}

# === 正規表示式匹配標題 ===
section_pattern = re.compile(r"^###\s*\d\.\s*(.+)$", re.MULTILINE)

# === 讀取原始合併摘要 ===
if not os.path.exists(INPUT_PATH):
    print(f"❌ 找不到輸入檔案：{INPUT_PATH}")
    exit(1)

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# === 找出所有段落位置 ===
matches = list(section_pattern.finditer(content))
sections = {}

for idx, match in enumerate(matches):
    section_name = match.group(1).strip()
    start = match.end()
    end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
    section_content = content[start:end].strip()
    sections[section_name] = section_content

# === 儲存各段落為獨立檔案，含標題
for section_name, (file_name, header_title) in section_info.items():
    output_path = os.path.join(OUTPUT_DIR, file_name)
    if section_name in sections:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"{header_title}\n\n")
            f.write(sections[section_name])
        print(f"✅ 已儲存 {section_name} → {output_path}")
    else:
        print(f"⚠️ 找不到段落：{section_name}，未產生 {file_name}")
