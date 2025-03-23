import os
import re

ARTICLE_DIR = "../data"
OUTPUT_PATH = "../data/merged_summary.md"
NUM_ARTICLES = 7

# 預設分類標題
sections = {
    "資安防護": [],
    "資安威脅態勢": [],
    "資安事件": [],
    "未來趨勢": []
}

# 正規表達式匹配段落標題
section_pattern = re.compile(r"^###\s*\d\.\s*(.+)$", re.MULTILINE)

# 逐篇處理
for i in range(1, NUM_ARTICLES + 1):
    path = os.path.join(ARTICLE_DIR, f"summary_{i}.md")
    if not os.path.exists(path):
        print(f"⚠️ 找不到檔案：{path}，跳過")
        continue

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 切分段落區塊
    matches = list(section_pattern.finditer(content))
    for idx, match in enumerate(matches):
        section_name = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        section_content = content[start:end].strip()

        if section_name in sections:
            sections[section_name].append(section_content)
        else:
            print(f"⚠️ 未知段落類別：{section_name}，略過")

# 組合並儲存
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for i, (section_name, contents) in enumerate(sections.items(), start=1):
        f.write(f"### {i}. {section_name}\n")
        for content in contents:
            f.write(content + "\n\n")

print(f"✅ 已完成彙整，儲存至：{OUTPUT_PATH}")
