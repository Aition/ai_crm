#!/usr/bin/env python3
"""
探测 Dify 知识库界面结构
"""

import time
import re
from playwright.sync_api import sync_playwright

DIFY_BASE_URL = "http://127.0.0.1"
DIFY_DATASET_ID = "0584fa7b-d5b0-4bc4-a327-63e188aa2ca1"

def main():
    print("=" * 60)
    print("Dify 知识库界面探测")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. 访问知识库列表
            print("\n1. 访问知识库列表...")
            page.goto(f"{DIFY_BASE_URL}/datasets", timeout=30000)
            time.sleep(3)

            print(f"   URL: {page.url}")
            print(f"   标题: {page.title()}")

            # 截图
            page.screenshot(path="/Users/joey/ai_crm/dify_datasets_list.png", full_page=True)
            print("   截图: dify_datasets_list.png")

            # 查找知识库链接
            print("\n2. 查找知识库链接...")
            links = page.query_selector_all('a')
            print(f"   找到 {len(links)} 个链接")

            dataset_links = []
            for link in links:
                href = link.get_attribute('href') or ""
                text = link.inner_text()[:50] if link.inner_text() else ""
                if 'dataset' in href.lower() or 'knowledge' in href.lower():
                    dataset_links.append((href, text))
                    print(f"   - {text} -> {href}")

            # 查找包含 UUID 的链接（可能是知识库详情）
            print("\n3. 查找 UUID 链接...")
            all_hrefs = page.eval_on_selector_all('a', 'els => els.map(a => a.href)')
            uuid_pattern = re.compile(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}')

            for href in all_hrefs:
                if uuid_pattern.search(href):
                    print(f"   UUID 链接: {href}")

            # 2. 尝试直接访问知识库详情页的不同 URL 格式
            print("\n4. 尝试不同的知识库详情页 URL...")

            possible_urls = [
                f"{DIFY_BASE_URL}/datasets/{DIFY_DATASET_ID}",
                f"{DIFY_BASE_URL}/dataset/{DIFY_DATASET_ID}",
                f"{DIFY_BASE_URL}/knowledge/{DIFY_DATASET_ID}",
                f"{DIFY_BASE_URL}/datasets/{DIFY_DATASET_ID}/documents",
                f"{DIFY_BASE_URL}/app/datasets/{DIFY_DATASET_ID}",
            ]

            for url in possible_urls:
                try:
                    page.goto(url, timeout=10000)
                    time.sleep(2)
                    title = page.title()
                    if "404" not in title:
                        print(f"   ✓ 有效: {url}")
                        print(f"     标题: {title}")
                    else:
                        print(f"   ✗ 404: {url}")
                except Exception as e:
                    print(f"   ✗ 错误: {url} - {str(e)[:30]}")

            # 3. 分析页面 HTML 结构
            print("\n5. 分析页面结构...")
            html = page.content()

            # 保存 HTML
            with open("/Users/joey/ai_crm/dify_page_html.html", 'w', encoding='utf-8') as f:
                f.write(html)
            print("   HTML 已保存: dify_page_html.html")

            # 查找包含 dataset ID 的脚本或数据
            if DIFY_DATASET_ID in html:
                print(f"   ✓ 页面包含 Dataset ID: {DIFY_DATASET_ID}")
            else:
                print(f"   ✗ 页面不包含 Dataset ID")

            # 4. 尝试从列表页点击进入知识库
            print("\n6. 尝试点击知识库...")
            page.goto(f"{DIFY_BASE_URL}/datasets", timeout=30000)
            time.sleep(3)

            # 查找可点击的卡片或项目
            cards = page.query_selector_all('[class*="card"], [class*="item"], [class*="dataset"]')
            print(f"   找到 {len(cards)} 个可能的卡片元素")

            # 查找按钮
            buttons = page.query_selector_all('button')
            print(f"   找到 {len(buttons)} 个按钮")

            # 打印前 10 个按钮的文本
            for i, btn in enumerate(buttons[:10]):
                text = btn.inner_text()[:30] if btn.inner_text() else "(图标)"
                print(f"   按钮 {i+1}: {text}")

            print("\n" + "=" * 60)
            print("探测完成！")
            print("=" * 60)

        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            page.screenshot(path="/Users/joey/ai_crm/explore_error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    main()
