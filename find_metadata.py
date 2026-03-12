#!/usr/bin/env python3
"""
Dify 元数据设置工具 - 简化版
"""

import time
import json
import os
import urllib.request
from playwright.sync_api import sync_playwright

DIFY_BASE_URL = "http://127.0.0.1"
DIFY_DATASET_ID = "0584fa7b-d5b0-4bc4-a327-63e188aa2ca1"
DIFY_API_KEY = "dataset-vl1q63xxkIV6VMUEe9qKHczg"
STATE_FILE = "/Users/joey/ai_crm/dify_auth_state.json"

def get_category_from_doc_name(doc_name):
    if doc_name.startswith("[") and "]" in doc_name:
        return doc_name[1:doc_name.index("]")]
    return "其他"

def get_documents():
    url = f"http://127.0.0.1/v1/datasets/{DIFY_DATASET_ID}/documents?page=1&limit=100"
    headers = {"Authorization": f"Bearer {DIFY_API_KEY}"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
    return data.get("data", [])

def main():
    print("=" * 60)
    print("Dify 元数据设置工具")
    print("=" * 60)

    if not os.path.exists(STATE_FILE):
        print("请先运行 dify_login.py")
        return

    documents = get_documents()
    print(f"\n找到 {len(documents)} 个文档")

    docs_by_category = {}
    for doc in documents:
        cat = get_category_from_doc_name(doc.get("name", ""))
        if cat not in docs_by_category:
            docs_by_category[cat] = []
        docs_by_category[cat].append(doc)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        try:
            url = f"{DIFY_BASE_URL}/datasets/{DIFY_DATASET_ID}/documents"
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            print(f"\n当前页面: {page.url}")

            # 关闭任何弹窗
            page.keyboard.press("Escape")
            time.sleep(1)

            # 截图当前状态
            page.screenshot(path="/Users/joey/ai_crm/page_state.png", full_page=True)
            print("截图: page_state.png")

            # ========== 方法1: 通过侧边栏导航 ==========
            print("\n尝试通过侧边栏找到 Metadata...")

            # 查找侧边栏中的所有链接
            sidebar = page.query_selector('nav, [class*="sidebar"], [class*="nav"]')
            if sidebar:
                links = sidebar.query_selector_all('a, button')
                print(f"侧边栏找到 {len(links)} 个元素")
                for link in links:
                    text = link.inner_text().strip()
                    if text:
                        print(f"  - {text}")
                    if 'metadata' in text.lower() or '元数据' in text:
                        print(f"  → 找到 Metadata: {text}")
                        link.click()
                        time.sleep(2)
                        break

            # ========== 方法2: 通过页面顶部工具栏 ==========
            print("\n尝试通过工具栏找到 Metadata...")

            # 查找顶部工具栏
            toolbar = page.query_selector('[class*="toolbar"], [class*="header"], header')
            if toolbar:
                btns = toolbar.query_selector_all('button')
                for btn in btns:
                    text = btn.inner_text().strip()
                    if 'metadata' in text.lower() or '元数据' in text:
                        print(f"  → 工具栏 Metadata: {text}")
                        btn.click()
                        time.sleep(2)
                        break

            # ========== 方法3: 查找页面所有 Metadata 元素 ==========
            print("\n搜索页面所有 Metadata 相关元素...")

            all_elements = page.query_selector_all('button, a, [role="button"]')
            for el in all_elements:
                try:
                    text = el.inner_text().strip().lower()
                    if 'metadata' in text or '元数据' in text:
                        print(f"  发现: {el.inner_text().strip()}")
                except:
                    pass

            # ========== 如果都没找到，打开设置页面 ==========
            print("\n尝试打开知识库设置...")

            # 点击设置图标（齿轮）
            settings_icons = page.query_selector_all('svg, [class*="setting"], [class*="gear"], [class*="cog"]')
            for icon in settings_icons[:5]:
                try:
                    parent = icon.evaluate_handle('el => el.closest("button, a, [role=\\"button\\"]")')
                    if parent:
                        parent.click()
                        time.sleep(1)
                        page.screenshot(path="/Users/joey/ai_crm/settings_page.png")
                        print("截图: settings_page.png")
                        break
                except:
                    continue

            # 保持浏览器打开让用户观察
            print("\n" + "=" * 60)
            print("浏览器将保持打开 60 秒")
            print("请观察页面并告诉我 Metadata 入口在哪里")
            print("=" * 60)
            time.sleep(60)

        except Exception as e:
            print(f"错误: {e}")
            page.screenshot(path="/Users/joey/ai_crm/error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    main()
