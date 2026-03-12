#!/usr/bin/env python3
"""
批量上传 ARMCloud 文档到 Dify 知识库
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path

# Dify 配置
DIFY_API_KEY = "dataset-vl1q63xxkIV6VMUEe9qKHczg"
DIFY_DATASET_ID = "0584fa7b-d5b0-4bc4-a327-63e188aa2ca1"
DIFY_API_BASE = "http://127.0.0.1/v1"

# 文档根目录
DOCS_ROOT = "/Users/joey/ai_crm/docs"

# 文档分类映射
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
    """根据文件路径获取分类名称"""
    rel_path = os.path.relpath(file_path, DOCS_ROOT)

    # 按最长路径匹配分类
    for path_prefix, category in sorted(CATEGORY_MAPPING.items(), key=lambda x: -len(x[0])):
        if rel_path.startswith(path_prefix):
            return category

    return "其他"

def build_process_rule(category: str) -> dict:
    """构建分段规则：除常见问题外，其它文档分段大小为1000"""
    if category == "常见问题":
        return {"mode": "automatic"}
    return {
        "mode": "custom",
        "rules": {
            "pre_processing_rules": [],
            "segmentation": {"max_tokens": 1000}
        },
    }

def build_process_rule(file_path: str) -> dict:
    """根据文档类型选择更合理的切片规则"""
    rel_path = os.path.relpath(file_path, DOCS_ROOT).replace("\\", "/")

    # 常见问题：按空行切分，每段较短
    if rel_path.startswith("guides/faq/"):
        return {
            "mode": "custom",
            "rules": {
                "pre_processing_rules": [],
                "segmentation": {"separator": "\n\n", "max_tokens": 400},
            },
        }

    # OpenAPI：按接口标题切分
    if rel_path == "reference/openapi/openapi-ai.md":
        return {
            "mode": "custom",
            "rules": {
                "pre_processing_rules": [],
                "segmentation": {"separator": "#### ", "max_tokens": 800},
            },
        }

    # 数据参考：按小节切分
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

    # SDK/解决方案/产品/使用指南：按二级标题切分
    if rel_path.startswith(("sdk/", "guides/solutions/", "guides/usage-guide.md", "product/")):
        return {
            "mode": "custom",
            "rules": {
                "pre_processing_rules": [],
                "segmentation": {"separator": "## ", "max_tokens": 800},
            },
        }

    # 兜底
    return {"mode": "automatic"}


def upload_document(file_path: str, category: str) -> dict:
    """上传单个文档到 Dify"""
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 构建文档名称（包含分类）
    file_name = os.path.basename(file_path)
    doc_name = f"[{category}] {file_name.replace('.md', '').replace('.txt', '')}"

    # 调用 Dify API
    url = f"{DIFY_API_BASE}/datasets/{DIFY_DATASET_ID}/document/create-by-text"

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": doc_name,
        "text": content,
        "indexing_technique": "high_quality",
        "process_rule": build_process_rule(file_path),
        # 添加元数据，用于分类过滤
        "doc_metadata": {
            "category": category
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status == 200:
                return {"success": True, "data": json.loads(response.read().decode('utf-8'))}
            else:
                return {"success": False, "error": response.read().decode('utf-8'), "status_code": response.status}
    except urllib.error.HTTPError as e:
        return {"success": False, "error": e.read().decode('utf-8'), "status_code": e.code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """主函数"""
    print("=" * 60)
    print("ARMCloud 文档上传到 Dify 知识库")
    print("=" * 60)
    print(f"知识库 ID: {DIFY_DATASET_ID}")
    print(f"文档目录: {DOCS_ROOT}")
    print("=" * 60)

    # 收集所有 markdown 文件
    md_files = []
    for root, dirs, files in os.walk(DOCS_ROOT):
        for file in files:
            if file.endswith('.md') or file.endswith('.txt'):
                md_files.append(os.path.join(root, file))

    # 排除 Dify 相关的文档
    md_files = [f for f in md_files if not os.path.basename(f).startswith('dify-')]

    md_files.sort()

    print(f"\n找到 {len(md_files)} 个文档文件\n")

    # 上传文档
    success_count = 0
    fail_count = 0

    for i, file_path in enumerate(md_files, 1):
        category = get_category(file_path)
        file_name = os.path.basename(file_path)

        print(f"[{i}/{len(md_files)}] 上传: [{category}] {file_name}")

        result = upload_document(file_path, category)

        if result["success"]:
            success_count += 1
            doc_id = result["data"].get("document", {}).get("id", "unknown")
            print(f"    ✓ 成功 (ID: {doc_id})")
        else:
            fail_count += 1
            print(f"    ✗ 失败: {result['error']}")

    # 输出统计
    print("\n" + "=" * 60)
    print("上传完成")
    print("=" * 60)
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"总计: {len(md_files)}")

if __name__ == "__main__":
    main()
