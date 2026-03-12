#!/usr/bin/env python3
"""
Dify 登录脚本 - 保存登录状态
运行此脚本后，在浏览器中登录，登录成功后脚本会自动保存状态
"""

import time
import json
import os
from playwright.sync_api import sync_playwright

DIFY_BASE_URL = "http://127.0.0.1"
STATE_FILE = "/Users/joey/ai_crm/dify_auth_state.json"

def main():
    print("=" * 60)
    print("Dify 登录状态保存工具")
    print("=" * 60)
    print("\n此脚本将打开浏览器，请手动登录 Dify")
    print("登录成功后会自动跳转到知识库页面")
    print("脚本会自动保存登录状态\n")

    with sync_playwright() as p:
        # 使用持久化上下文，这样可以保存登录状态
        browser = p.chromium.launch(headless=False)  # 非无头模式，可以看到浏览器

        # 尝试加载之前保存的状态
        if os.path.exists(STATE_FILE):
            print("发现之前保存的登录状态，尝试加载...")
            context = browser.new_context(storage_state=STATE_FILE)
        else:
            context = browser.new_context()

        page = context.new_page()

        try:
            # 访问知识库页面
            page.goto(f"{DIFY_BASE_URL}/datasets", timeout=30000)

            print("\n" + "-" * 60)
            print("请在浏览器中完成登录")
            print("登录成功后，页面会显示知识库列表")
            print("确认登录成功后，请在此终端按回车继续...")
            print("-" * 60)

            # 等待用户输入（在终端中运行时）
            import sys
            if sys.stdin.isatty():
                input()
            else:
                # 如果不是终端，等待用户手动操作
                print("\n等待登录... (请在新终端运行此脚本)")
                # 等待页面 URL 变化或出现知识库相关元素
                try:
                    page.wait_for_url("**/datasets**", timeout=120000)
                except:
                    pass
                time.sleep(5)

            # 检查是否登录成功
            current_url = page.url
            print(f"\n当前 URL: {current_url}")

            # 截图确认
            page.screenshot(path="/Users/joey/ai_crm/dify_after_login.png")
            print("截图已保存: dify_after_login.png")

            # 保存登录状态
            context.storage_state(path=STATE_FILE)
            print(f"\n✓ 登录状态已保存到: {STATE_FILE}")

            # 验证：尝试访问知识库文档页面
            print("\n验证登录状态...")
            test_url = f"{DIFY_BASE_URL}/datasets/0584fa7b-d5b0-4bc4-a327-63e188aa2ca1/documents"
            page.goto(test_url, timeout=30000)
            time.sleep(3)

            page.screenshot(path="/Users/joey/ai_crm/dify_documents_page.png")
            print(f"知识库文档页面截图: dify_documents_page.png")

            print("\n" + "=" * 60)
            print("登录状态保存成功！")
            print("现在可以运行 set_dify_metadata.py 来设置元数据")
            print("=" * 60)

        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            page.screenshot(path="/Users/joey/ai_crm/login_error.png")

        finally:
            # 不立即关闭浏览器，让用户确认
            print("\n按 Ctrl+C 退出...")
            try:
                time.sleep(300)  # 等待5分钟
            except KeyboardInterrupt:
                pass
            browser.close()

if __name__ == "__main__":
    main()
