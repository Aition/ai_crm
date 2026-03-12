#!/usr/bin/env python3
"""
调试脚本：检查 Dify 页面结构
"""

import time
from playwright.sync_api import sync_playwright

STATE_FILE = "/Users/joey/ai_crm/dify_auth_state.json"
DIFY_DATASET_ID = "0584fa7b-d5b0-4bc4-a327-63e188aa2ca1"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        url = f"http://127.0.0.1/datasets/{DIFY_DATASET_ID}/documents"
        print(f"访问: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        time.sleep(5)  # 等待更长时间

        print(f"\nURL: {page.url}")
        print(f"标题: {page.title()}")

        # 截图
        page.screenshot(path="/Users/joey/ai_crm/debug_full.png", full_page=True)
        print("截图: debug_full.png")

        # 查找所有 input
        inputs = page.query_selector_all('input')
        print(f"\n找到 {len(inputs)} 个 input 元素:")
        for i, inp in enumerate(inputs):
            inp_type = inp.get_attribute('type') or 'unknown'
            inp_class = (inp.get_attribute('class') or '')[:50]
            print(f"  {i+1}. type={inp_type}, class={inp_class}")

        # 查找所有 checkbox（包括隐藏的）
        checkboxes = page.query_selector_all('[role="checkbox"], input[type="checkbox"], [class*="checkbox"], [class*="check"]')
        print(f"\n找到 {len(checkboxes)} 个可能的 checkbox:")
        for i, cb in enumerate(checkboxes):
            tag = cb.evaluate('el => el.tagName')
            cls = (cb.get_attribute('class') or '')[:50]
            print(f"  {i+1}. <{tag}> class={cls}")

        # 查找表格
        tables = page.query_selector_all('table')
        print(f"\n找到 {len(tables)} 个 table")

        rows = page.query_selector_all('tr')
        print(f"找到 {len(rows)} 个 tr")

        # 打印第一行的内容
        if rows:
            first_row = rows[0]
            print(f"\n第一行内容: {first_row.inner_text()[:100]}")

        # 查找可点击的元素
        clickables = page.query_selector_all('button, a, [role="button"], [class*="click"]')
        print(f"\n找到 {len(clickables)} 个可点击元素")
        for i, el in enumerate(clickables[:15]):
            text = el.inner_text()[:30].replace('\n', ' ')
            print(f"  {i+1}. {text}")

        # 保持浏览器打开
        print("\n浏览器将保持打开 30 秒...")
        time.sleep(30)
        browser.close()

if __name__ == "__main__":
    main()
