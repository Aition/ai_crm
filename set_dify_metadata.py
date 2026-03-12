#!/usr/bin/env python3
"""
Dify 文档元数据批量设置工具 - 最终版
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
    print("Dify 文档元数据批量设置工具")
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

    print("\n分类统计:")
    for cat, docs in docs_by_category.items():
        print(f"  {cat}: {len(docs)} 个")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        try:
            url = f"{DIFY_BASE_URL}/datasets/{DIFY_DATASET_ID}/documents"
            print(f"\n访问: {url}")
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            success_total = 0
            fail_total = 0

            for category, docs in docs_by_category.items():
                if not docs:
                    continue

                print(f"\n{'='*40}")
                print(f"分类 [{category}]: {len(docs)} 个文档")
                print('='*40)

                try:
                    # 刷新页面
                    page.goto(url, timeout=60000)
                    page.wait_for_load_state("networkidle")
                    time.sleep(2)

                    # 点击全选框（表格左上角）
                    print("  点击全选框...")
                    # 根据截图，全选框在表头左侧
                    # 使用更精确的选择器
                    select_all = page.query_selector('th:first-child div[class*="cursor-pointer"]')
                    if not select_all:
                        # 备用选择器
                        checkboxes = page.query_selector_all('div[class*="cursor-pointer"][class*="justify-center"]')
                        if checkboxes:
                            select_all = checkboxes[0]

                    if select_all:
                        select_all.click()
                        time.sleep(2)
                        print("  ✓ 已全选")
                    else:
                        print("  ✗ 未找到全选框，尝试点击第一个文档...")
                        # 点击第一行的复选框
                        first_row_cb = page.query_selector('tr:nth-child(2) td:first-child div[class*="cursor-pointer"]')
                        if first_row_cb:
                            first_row_cb.click()
                            time.sleep(1)

                    # 等待底部操作栏出现
                    time.sleep(2)
                    page.screenshot(path=f"/Users/joey/ai_crm/selected_{category[:10]}.png")

                    # 点击底部元数据按钮
                    print("  查找底部元数据按钮...")

                    # 底部操作栏中的元数据按钮
                    batch_btn = None

                    # 方法1：查找底部固定栏
                    bottom_bar = page.query_selector('[class*="fixed"][class*="bottom"], [class*="sticky"][class*="bottom"]')
                    if bottom_bar:
                        batch_btn = bottom_bar.query_selector('button:has-text("元数据"), button:has-text("Metadata")')

                    # 方法2：直接查找元数据按钮
                    if not batch_btn:
                        batch_btn = page.query_selector('button:has-text("元数据")')

                    if not batch_btn:
                        batch_btn = page.query_selector('button:has-text("Metadata")')

                    if batch_btn:
                        print("  找到元数据按钮，点击...")
                        # 先关闭可能的弹窗
                        page.keyboard.press("Escape")
                        time.sleep(0.5)
                        # 使用 JavaScript 点击绕过遮挡
                        page.evaluate('(btn) => btn.click()', batch_btn)
                        time.sleep(3)

                        page.screenshot(path=f"/Users/joey/ai_crm/batch_panel_{category[:10]}.png")

                        # 在编辑器中添加 category 字段
                        print("  添加 category 字段...")

                        # 先关闭可能的弹窗
                        page.keyboard.press("Escape")
                        time.sleep(0.5)

                        add_btn = page.query_selector('button:has-text("添加"), button:has-text("Add")')
                        if add_btn:
                            # 使用 JavaScript 点击
                            page.evaluate('(btn) => btn.click()', add_btn)
                            time.sleep(1)

                            # 选择 category
                            cat_opt = page.query_selector('text="category"')
                            if cat_opt:
                                cat_opt.click()
                                time.sleep(0.5)

                        # 输入值
                        print(f"  输入值: {category}")
                        value_inputs = page.query_selector_all('input[type="text"], input:not([type])')
                        for inp in value_inputs:
                            try:
                                if inp.is_visible():
                                    inp.fill(category)
                                    print("  ✓ 已输入值")
                                    break
                            except:
                                continue

                        time.sleep(0.5)

                        # 保存
                        print("  保存...")
                        # 尝试多种保存按钮选择器
                        save_btn = page.query_selector('button:has-text("保存")')
                        if not save_btn:
                            save_btn = page.query_selector('button:has-text("Save")')
                        if not save_btn:
                            save_btn = page.query_selector('button:has-text("确定")')
                        if not save_btn:
                            save_btn = page.query_selector('button:has-text("确认")')
                        if not save_btn:
                            # 查找所有按钮，找最后一个（通常是保存）
                            all_btns = page.query_selector_all('button')
                            for btn in reversed(all_btns):
                                text = btn.inner_text()
                                if '保存' in text or 'Save' in text or '确定' in text or '确认' in text:
                                    save_btn = btn
                                    break

                        if save_btn:
                            page.evaluate('(btn) => btn.click()', save_btn)
                            time.sleep(2)
                            print(f"  ✓ 设置成功: {category}")
                            success_total += len(docs)
                        else:
                            print(f"  ✗ 未找到保存按钮")
                            # 截图调试
                            page.screenshot(path=f"/Users/joey/ai_crm/no_save_{category[:10]}.png")
                            fail_total += len(docs)

                        # 关闭编辑器
                        page.keyboard.press("Escape")
                        time.sleep(1)
                    else:
                        print("  ✗ 未找到元数据按钮")
                        fail_total += len(docs)
                        page.screenshot(path=f"/Users/joey/ai_crm/no_btn_{category[:10]}.png")

                except Exception as e:
                    print(f"  错误: {e}")
                    fail_total += len(docs)

            print("\n" + "=" * 60)
            print("完成!")
            print(f"成功: {success_total}")
            print(f"失败: {fail_total}")
            print("=" * 60)

            page.screenshot(path="/Users/joey/ai_crm/final_result.png")

        except Exception as e:
            print(f"\n错误: {e}")
            page.screenshot(path="/Users/joey/ai_crm/error.png")

        finally:
            print("\n10秒后关闭浏览器...")
            time.sleep(10)
            browser.close()

if __name__ == "__main__":
    main()
