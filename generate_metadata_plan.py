#!/usr/bin/env python3
"""
Generate a metadata labeling plan from existing Dify documents.
Outputs docs/metadata_plan.md for manual batch labeling.
"""

import json
import os
import urllib.request

DIFY_API_KEY = "dataset-vl1q63xxkIV6VMUEe9qKHczg"
DIFY_DATASET_ID = "0584fa7b-d5b0-4bc4-a327-63e188aa2ca1"
DIFY_API_BASE = "http://127.0.0.1/v1"
OUTPUT_PATH = "/Users/joey/ai_crm/docs/metadata_plan.md"

PREFIX_TO_CATEGORY = {
    "Android SDK": "Android SDK",
    "H5 SDK": "H5 SDK",
    "PC SDK": "PC SDK",
    "OpenAPI接口": "API接口",
    "常见问题": "常见问题",
    "产品介绍": "产品介绍",
    "解决方案": "解决方案",
    "端侧与云机通信": "端侧通信",
    "数据参考": "数据参考",
    "接口认证": "API认证",
    "参考文档": "数据参考",
    "使用指南": "API接口",
}


def _request(url: str) -> dict:
    headers = {"Authorization": f"Bearer {DIFY_API_KEY}"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def get_all_documents() -> list:
    docs = []
    page = 1
    while True:
        url = f"{DIFY_API_BASE}/datasets/{DIFY_DATASET_ID}/documents?page={page}&limit=100"
        data = _request(url)
        batch = data.get("data", [])
        if not batch:
            break
        docs.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return docs


def get_prefix(doc_name: str):
    if doc_name.startswith("[") and "]" in doc_name:
        return doc_name[1 : doc_name.index("]")]
    return None


def get_target_category(doc_name: str) -> str:
    prefix = get_prefix(doc_name)
    if not prefix:
        return "其他"
    return PREFIX_TO_CATEGORY.get(prefix, "其他")


def main() -> None:
    docs = get_all_documents()
    by_category = {}
    unknown = []

    for doc in docs:
        name = doc.get("name", "")
        doc_id = doc.get("id", "")
        category = get_target_category(name)
        entry = (name, doc_id)
        by_category.setdefault(category, []).append(entry)
        if category == "其他":
            unknown.append(entry)

    lines = []
    lines.append("# Dify 文档元数据标注清单")
    lines.append("")
    lines.append(f"- Dataset ID: {DIFY_DATASET_ID}")
    lines.append(f"- 文档总数: {len(docs)}")
    lines.append("")

    for category in sorted(by_category.keys()):
        lines.append(f"## {category}")
        lines.append("")
        for name, doc_id in sorted(by_category[category]):
            lines.append(f"- {name}  (id: {doc_id})")
        lines.append("")

    if unknown:
        lines.append("## 需要人工确认（未匹配分类）")
        lines.append("")
        for name, doc_id in sorted(unknown):
            lines.append(f"- {name}  (id: {doc_id})")
        lines.append("")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"已生成: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
