#!/usr/bin/env python3
"""
快速探测 Dify 元数据界面
"""

import time
from playwright.sync_api import sync_playwright

DIFY_BASE_URL = "http://127.0.0.1"
DIFY_DATASET_ID = "0584fa7b-d5b0-4bc4-a327-63e188aa2ca1"
STATE_FILE = "/Users/joey/ai_crm/dify_auth_state.json"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        try:
            # 访问知识库
            url = f"{DIFY_BASE_URL}/datasets/{DIFY_DATASET_ID}/documents"
            print(f"访问: {url}")
            page.goto(url, timeout=30000)
            time.sleep(3)

            print(f"URL: {page.url}")
            print(f"标题: {page.title()}")

            # 截图
            page.screenshot(path="/Users/joey/ai_crm/current_page.png", full_page=True)
            print("截图: current_page.png")

            # 查找所有按钮
            print("\n查找所有按钮:")
            buttons = page.query_selector_all('button')
            for i, btn in enumerate(buttons):
                text = btn.inner_text()[:40].replace('\n', ' ')
                cls = (btn.get_attribute('class') or '')[:30]
                print(f"  {i+1}. [{cls}] {text}")

            # 查找包含 metadata 的元素
            print("\n查找 Metadata 相关:")
            all_text = page.content()
            if 'metadata' in all_text.lower():
                print("  ✓ 页面包含 'metadata'")
            if '元数据' in all_text:
                print("  ✓ 页面包含 '元数据'")

            # 查找表格行
            print("\n查找文档行:")
            rows = page.query_selector_all('tr')
            print(f"  找到 {len(rows)} 个表格行")

            for i, row in enumerate(rows[:5]):
                text = row.inner_text()[:60].replace('\n', ' ')
                print(f"  {i+1}. {text}")

        except Exception as e:
            print(f"错误: {e}")
            page.screenshot(path="/Users/joey/ai_crm/explore_error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    main()
