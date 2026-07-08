#!/usr/bin/env python3
"""
Guardian系统 - 商户准入初审复核自动化脚本

用法:
    python3 merchant_review_approval.py 6406
    python3 merchant_review_approval.py 6406 -u admin -p Secret123

参数:
    id: 审批任务ID（必填）
    --username, -u: 登录用户名（默认: liuchunen）
    --password, -p: 登录密码（默认: Abc@1234）
"""

import sys
import os
import argparse
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://guardian.weibopay.com/uni-login/login"
SYSTEM_NAME = "商户准入系统"

WAIT_TIME_SHORT = 300
WAIT_TIME_NORMAL = 1000
WAIT_TIME_LONG = 2000


def parse_args():
    parser = argparse.ArgumentParser(
        description='Guardian系统商户准入初审复核自动化脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 merchant_review_approval.py 6406
    python3 merchant_review_approval.py 6406 -u admin -p Secret123
        """
    )

    parser.add_argument(
        'id',
        type=str,
        help='审批任务ID（必填）'
    )

    parser.add_argument(
        '-u', '--username',
        type=str,
        default='liuchunen',
        help='登录用户名（默认: liuchunen）'
    )

    parser.add_argument(
        '-p', '--password',
        type=str,
        default='Abc@1234',
        help='登录密码（默认: Abc@1234）'
    )

    return parser.parse_args()


def get_screenshot_path(step_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots", "review", step_name)
    os.makedirs(screenshot_dir, exist_ok=True)
    return os.path.join(screenshot_dir, f"{timestamp}.png")


def main():
    args = parse_args()
    target_id = args.id
    username = args.username
    password = args.password

    print(f"🚀 启动商户准入初审复核脚本")
    print(f"📋 审批任务ID: {target_id}")
    print(f"👤 登录用户名: {username}")
    print("=" * 50)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])

        try:
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})

            print("\n步骤1-3: 登录Guardian系统")
            page.goto(LOGIN_URL, timeout=30000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(WAIT_TIME_NORMAL)

            username_input = page.locator('input[type="text"]').first
            username_input.fill(username)
            print(f"  ✅ 已输入用户名: {username}")

            password_input = page.locator('input[type="password"]').first
            password_input.fill(password)
            print("  ✅ 已输入密码")

            selected = False
            for retry in range(3):
                try:
                    system_element = page.locator(f"text={SYSTEM_NAME}").first
                    system_element.click(timeout=2000)
                    selected = True
                    print(f"  ✅ 已选择系统: {SYSTEM_NAME}")
                    break
                except:
                    pass
                try:
                    arrows = page.locator('.dijitArrowButtonInner')
                    if arrows.count() > 0:
                        arrows.last.click(timeout=2000)
                        page.wait_for_timeout(WAIT_TIME_NORMAL)
                        menu_item = page.locator(f".dijitMenuItem:text('{SYSTEM_NAME}')").first
                        menu_item.click(timeout=2000)
                        selected = True
                        print(f"  ✅ 已选择系统: {SYSTEM_NAME}")
                        break
                except:
                    pass

            if not selected:
                print(f"  ⚠️ 自动选择系统失败，请手动选择")

            login_button = page.locator('button:has-text("登录")').first
            login_button.click(timeout=5000)
            page.wait_for_load_state('networkidle', timeout=30000)
            page.wait_for_timeout(WAIT_TIME_LONG)
            print("  ✅ 登录成功")

            print("\n步骤4-6: 进入商户准入管理")
            try:
                merchant_manage = page.locator('text=商户准入管理').first
                merchant_manage.click(timeout=5000)
                page.wait_for_load_state('networkidle', timeout=30000)
                page.wait_for_timeout(WAIT_TIME_LONG)
                print("  ✅ 已进入商户准入管理")
            except Exception as e:
                print(f"  ⚠️ 进入商户准入管理失败，尝试其他方式: {e}")
                try:
                    merchant_link = page.locator('a:has-text("商户准入管理")').first
                    merchant_link.click(timeout=5000)
                    page.wait_for_load_state('networkidle', timeout=30000)
                    page.wait_for_timeout(WAIT_TIME_LONG)
                    print("  ✅ 通过链接进入商户准入管理")
                except:
                    print("  ⚠️ 请手动点击进入商户准入管理")

            print(f"\n步骤7: 查询审批任务ID {target_id}")
            try:
                search_input = page.locator('input[type="text"]').first
                search_input.fill(target_id)
                print(f"  ✅ 已输入审批任务ID: {target_id}")

                search_btn = page.locator('button:has-text("查询")').first
                search_btn.click(timeout=5000)
                page.wait_for_load_state('networkidle', timeout=15000)
                page.wait_for_timeout(WAIT_TIME_LONG)
                print("  ✅ 已点击查询按钮")
            except Exception as e:
                print(f"  ⚠️ 查询失败: {e}")

            print(f"\n步骤8: 找到审批任务 {target_id} 并点击查看")
            try:
                found = False
                max_retries = 3
                for retry in range(max_retries):
                    result = page.evaluate(f'''() => {{
                        const rows = document.querySelectorAll('tr, .list-row, .table-row');
                        for (let row of rows) {{
                            const text = row.textContent || '';
                            if (text.includes("{target_id}")) {{
                                const buttons = row.querySelectorAll('button, a');
                                for (let btn of buttons) {{
                                    const btnText = btn.textContent || btn.innerText || '';
                                    if (btnText.includes('查看') || btnText.includes('详情') || btnText.includes('审批')) {{
                                        btn.scrollIntoView({{ behavior: "instant", block: "center" }});
                                        btn.click();
                                        return true;
                                    }}
                                }}
                                row.click();
                                return true;
                            }}
                        }}
                        return false;
                    }}''')
                    if result:
                        found = True
                        print(f"  ✅ 已找到并点击审批任务 {target_id}")
                        page.wait_for_load_state('networkidle', timeout=30000)
                        page.wait_for_timeout(WAIT_TIME_LONG)
                        break
                    if retry < max_retries - 1:
                        print(f"  重试第 {retry + 1} 次...")
                        page.wait_for_timeout(WAIT_TIME_NORMAL)

                if not found:
                    print(f"  ⚠️ 未找到审批任务 {target_id}，请手动查找")
            except Exception as e:
                print(f"  ⚠️ 查找审批任务失败: {e}")

            print("\n步骤9: 选择审批意见 - 建议通过")
            try:
                result = page.evaluate('''() => {
                    const labels = document.querySelectorAll('label');
                    for (let label of labels) {
                        const text = label.textContent || '';
                        if (text.includes('建议通过')) {
                            const input = label.querySelector('input[type="radio"]');
                            if (input) {
                                input.click();
                                return true;
                            }
                        }
                    }
                    const radios = document.querySelectorAll('input[type="radio"]');
                    for (let radio of radios) {
                        if (radio.value && radio.value.includes('通过')) {
                            radio.click();
                            return true;
                        }
                    }
                    return false;
                }''')
                if result:
                    print("  ✅ 已选择审批意见：建议通过")
                else:
                    print("  ⚠️ 未找到审批意见选项")
            except Exception as e:
                print(f"  ⚠️ 选择审批意见失败: {e}")

            print("\n步骤10: 填写风险分析与结论")
            try:
                result = page.evaluate('''() => {
                    const textareas = document.querySelectorAll('textarea');
                    for (let ta of textareas) {
                        const placeholder = ta.placeholder || '';
                        const parentText = ta.parentElement ? ta.parentElement.textContent : '';
                        if (placeholder.includes('风险') || parentText.includes('风险分析')) {
                            ta.value = '123';
                            ta.dispatchEvent(new Event('input', { bubbles: true }));
                            return true;
                        }
                    }
                    const inputs = document.querySelectorAll('input[type="text"]');
                    for (let input of inputs) {
                        const placeholder = input.placeholder || '';
                        if (placeholder.includes('风险')) {
                            input.value = '123';
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            return true;
                        }
                    }
                    return false;
                }''')
                if result:
                    print("  ✅ 已填写风险分析与结论：123")
                else:
                    print("  ⚠️ 未找到风险分析与结论输入框")
            except Exception as e:
                print(f"  ⚠️ 填写风险分析与结论失败: {e}")

            print("\n步骤11: 填写经办初审意见")
            try:
                result = page.evaluate('''() => {
                    const textareas = document.querySelectorAll('textarea');
                    for (let ta of textareas) {
                        const placeholder = ta.placeholder || '';
                        const parentText = ta.parentElement ? ta.parentElement.textContent : '';
                        if (placeholder.includes('经办') || placeholder.includes('初审') || parentText.includes('经办初审')) {
                            ta.value = '123';
                            ta.dispatchEvent(new Event('input', { bubbles: true }));
                            return true;
                        }
                    }
                    const inputs = document.querySelectorAll('input[type="text"]');
                    for (let input of inputs) {
                        const placeholder = input.placeholder || '';
                        if (placeholder.includes('经办') || placeholder.includes('初审')) {
                            input.value = '123';
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            return true;
                        }
                    }
                    return false;
                }''')
                if result:
                    print("  ✅ 已填写经办初审意见：123")
                else:
                    print("  ⚠️ 未找到经办初审意见输入框")
            except Exception as e:
                print(f"  ⚠️ 填写经办初审意见失败: {e}")

            print("\n步骤12: 点击提交复核按钮")
            try:
                page.evaluate('window.scrollTo(0, 0)')
                page.wait_for_timeout(WAIT_TIME_SHORT)

                result = page.evaluate('''() => {
                    const allButtons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                    for (let btn of allButtons) {
                        const text = (btn.textContent || btn.innerText || btn.value || '').trim();
                        if (text.includes('提交复核')) {
                            btn.scrollIntoView({ behavior: 'instant', block: 'center' });
                            btn.click();
                            return { success: true, text: text };
                        }
                    }
                    return { success: false };
                }''')

                if result.get('success', False):
                    print(f"  ✅ 已点击提交复核按钮")
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_LONG)
                else:
                    print("  ⚠️ 未找到提交复核按钮")

                    try:
                        buttons = page.locator('button').all()
                        for btn in buttons:
                            text = btn.text_content()
                            if text and ('提交复核' in text):
                                btn.click()
                                print(f"  ✅ 通过备用方案点击按钮: {text}")
                                page.wait_for_load_state('networkidle', timeout=15000)
                                page.wait_for_timeout(WAIT_TIME_LONG)
                                break
                    except Exception as backup_error:
                        print(f"  ⚠️ 备用方案失败: {backup_error}")
            except Exception as e:
                print(f"  ❌ 步骤12执行异常: {e}")

            print("\n步骤13: 点击弹窗中的提交按钮")
            try:
                page.wait_for_timeout(3000)

                result = page.evaluate('''() => {
                    const popup = document.querySelector('.ant-modal-wrap');
                    if (popup) {
                        const buttons = popup.querySelectorAll('button');
                        for (let btn of buttons) {
                            const text = btn.textContent || '';
                            if (text.includes('提交')) {
                                btn.click();
                                return { success: true, message: '点击提交按钮' };
                            }
                        }
                    }
                    return { success: false, message: '未找到弹窗' };
                }''')

                if result.get('success', False):
                    print("  ✅ 已点击弹窗中的提交按钮")
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_LONG)
                else:
                    print(f"  ℹ️ {result.get('message', '无弹窗')}")

                    try:
                        submit_buttons = page.locator('button:has-text("提交")').all()
                        if submit_buttons:
                            for btn in submit_buttons:
                                btn.click()
                                print("  ✅ 通过备用方案点击提交按钮")
                                page.wait_for_load_state('networkidle', timeout=15000)
                                page.wait_for_timeout(WAIT_TIME_LONG)
                                break
                    except Exception as backup_error:
                        print(f"  ⚠️ 备用方案失败: {backup_error}")
            except Exception as e:
                print(f"  ❌ 步骤13执行异常: {e}")

            print("\n步骤14: 处理确认弹窗")
            try:
                page.wait_for_timeout(3000)

                result = page.evaluate('''() => {
                    const popup = document.querySelector('.ant-modal-wrap');
                    if (popup) {
                        const buttons = popup.querySelectorAll('button');
                        for (let btn of buttons) {
                            const text = btn.textContent || '';
                            if (text.includes('确定') || text.includes('确认')) {
                                btn.click();
                                return { success: true, message: '点击确认按钮' };
                            }
                        }
                    }
                    return { success: false, message: '未找到确认弹窗' };
                }''')

                if result.get('success', False):
                    print("  ✅ 已点击确认弹窗中的确定按钮")
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_LONG)
                else:
                    print(f"  ℹ️ {result.get('message', '无确认弹窗')}")
            except Exception as e:
                print(f"  ❌ 步骤14执行异常: {e}")

            print("\n" + "=" * 50)
            print("🎉 初审复核流程全部完成！")
            print(f"📋 审批任务ID: {target_id}")
            print("=" * 50)

            input("\n按回车键关闭浏览器...")

        except Exception as e:
            print(f"\n❌ 执行过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    main()
