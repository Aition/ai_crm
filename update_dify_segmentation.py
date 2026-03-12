#!/usr/bin/env python3
"""
Recreate Dify documents to apply latest segmentation rules.

- Uses local docs in /Users/joey/ai_crm/docs
- Keeps doc name format: "[{category}] {basename}"
- Deletes existing doc by name (if found), then re-creates
"""

import json
import os
import time
import urllib.error
import urllib.request

# Dify config
DIFY_API_KEY = "dataset-vl1q63xxkIV6VMUEe9qKHczg"
DIFY_DATASET_ID = "0584fa7b-d5b0-4bc4-a327-63e188aa2ca1"
DIFY_API_BASE = "http://127.0.0.1/v1"

# Docs root
DOCS_ROOT = "/Users/joey/ai_crm/docs"
ALLOWED_PREFIXES = (
    "product/",
    "reference/",
    "guides/",
    "sdk/",
)

# Category mapping (same as upload_to_dify.py)
CATEGORY_MAPPING = {
    "product": "产品介绍",
    "reference/openapi": "API接口",
    "reference/data": "数据参考",
    "reference/auth": "API认证",
    "reference": "数据参考",
    "guides/solutions": "解决方案",
    "guides/faq": "常见问题",
    "guides": "API接口",
    "sdk/android": "Android SDK",
    "sdk/h5": "H5 SDK",
    "sdk/pc": "PC SDK",
    "sdk/system": "端侧通信",
}


def get_category(file_path: str) -> str:
    rel_path = os.path.relpath(file_path, DOCS_ROOT)
    for path_prefix, category in sorted(CATEGORY_MAPPING.items(), key=lambda x: -len(x[0])):
        if rel_path.startswith(path_prefix):
            return category
    return "其他"


def build_process_rule(file_path: str, category: str) -> dict:
    rel_path = os.path.relpath(file_path, DOCS_ROOT).replace("\\", "/")

    if rel_path.startswith("guides/faq/"):
        return {
            "mode": "custom",
            "rules": {
                "pre_processing_rules": [],
                "segmentation": {"separator": "\n\n", "max_tokens": 400},
            },
        }

    if rel_path == "reference/openapi/openapi-ai.md":
        return {
            "mode": "custom",
            "rules": {
                "pre_processing_rules": [],
                "segmentation": {"separator": "#### ", "max_tokens": 800},
            },
        }

    if rel_path.startswith("reference/data/") or rel_path in {
        "reference/error-codes.md",
        "reference/callback-codes.md",
        "reference/changelog.md",
    }:
        return {
            "mode": "custom",
            "rules": {
                "pre_processing_rules": [],
                "segmentation": {"separator": "### ", "max_tokens": 1000},
            },
        }

    if rel_path.startswith(("sdk/", "guides/solutions/", "guides/usage-guide.md", "product/")):
        return {
            "mode": "custom",
            "rules": {
                "pre_processing_rules": [],
                "segmentation": {"separator": "## ", "max_tokens": 800},
            },
        }

    return {"mode": "automatic"}


def _headers():
    return {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }


def list_documents(limit=100):
    docs = []
    page = 1
    while True:
        url = f"{DIFY_API_BASE}/datasets/{DIFY_DATASET_ID}/documents?page={page}&limit={limit}"
        req = urllib.request.Request(url, headers=_headers())
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        batch = data.get("data", [])
        docs.extend(batch)
        has_more = data.get("has_more")
        if not has_more and len(batch) < limit:
            break
        page += 1
    return docs


def delete_document(doc_id: str) -> None:
    url = f"{DIFY_API_BASE}/datasets/{DIFY_DATASET_ID}/documents/{doc_id}"
    req = urllib.request.Request(url, headers=_headers(), method="DELETE")
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def create_document(name: str, text: str, category: str, file_path: str) -> dict:
    url = f"{DIFY_API_BASE}/datasets/{DIFY_DATASET_ID}/document/create-by-text"
    payload = {
        "name": name,
        "text": text,
        "indexing_technique": "high_quality",
        "process_rule": build_process_rule(file_path, category),
        "doc_metadata": {"category": category},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=_headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {e.code}: {detail}") from e


def main():
    print("=" * 60)
    print("更新 Dify 知识库分段规则（重建文档）")
    print("=" * 60)

    # Build local doc list
    md_files = []
    for root, _, files in os.walk(DOCS_ROOT):
        for file in files:
            if file.endswith(".md") or file.endswith(".txt"):
                rel_path = os.path.relpath(os.path.join(root, file), DOCS_ROOT)
                if not rel_path.startswith(ALLOWED_PREFIXES):
                    continue
                md_files.append(os.path.join(root, file))
    md_files = [f for f in md_files if not os.path.basename(f).startswith("dify-")]
    md_files.sort()

    print(f"本地文档数: {len(md_files)}")

    # Map existing docs by name
    existing = {d.get("name"): d for d in list_documents()}

    success = 0
    failed = 0

    for i, file_path in enumerate(md_files, 1):
        category = get_category(file_path)
        file_name = os.path.basename(file_path)
        doc_name = f"[{category}] {file_name.replace('.md', '').replace('.txt', '')}"

        print(f"[{i}/{len(md_files)}] 重建: {doc_name}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if doc_name in existing:
                delete_document(existing[doc_name]["id"])
                time.sleep(0.2)

            create_document(doc_name, content, category, file_path)
            success += 1
        except Exception as e:
            failed += 1
            print(f"  ✗ 失败: {e}")

    print("=" * 60)
    print(f"完成。成功: {success} 失败: {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
