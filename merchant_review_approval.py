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

    parser.add_argument(
        '--no-wait',
        action='store_true',
        help='非交互模式，执行完成后自动关闭浏览器（不等待用户输入）'
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
    no_wait = getattr(args, 'no_wait', False) or os.environ.get('NO_WAIT') == '1'

    print(f"🚀 启动商户准入初审复核脚本")
    print(f"📋 审批任务ID: {target_id}")
    print(f"👤 登录用户名: {username}")
    if no_wait:
        print("⚡ 非交互模式（执行完成后自动关闭）")
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

            login_button = page.locator('button:has-text("登录"), input[value="登录"], #loginBtn').first
            login_button.click(timeout=5000)
            if login_button.count() == 0:
                page.evaluate('''() => {
                    const btn = document.querySelector('#loginBtn, input[value="登录"]');
                    if (btn) { btn.click(); return true; }
                    return false;
                }''')
            page.wait_for_load_state('networkidle', timeout=30000)
            page.wait_for_timeout(WAIT_TIME_LONG)
            print("  ✅ 登录成功")

            # 步骤4-6: 进入商户准入管理（先展开父菜单，再点击子菜单）
            print("\n步骤4: 点击商户风险管理（父菜单）")
            menu_entered = False
            try:
                risk_menu = page.locator('text=商户风险管理').first
                risk_menu.click(timeout=3000)
                print("  ✅ 已点击商户风险管理菜单")
                page.wait_for_timeout(WAIT_TIME_NORMAL)
            except Exception as e:
                print(f"  ⚠️ 点击父菜单失败: {e}")

            print("\n步骤5: 点击商户准入管理（子菜单）")
            try:
                access_menu = page.locator('text=商户准入管理').first
                access_menu.click(timeout=5000)
                page.wait_for_load_state('networkidle', timeout=15000)
                page.wait_for_timeout(WAIT_TIME_LONG)
                print("  ✅ 已进入商户准入管理")
                menu_entered = True
            except Exception as e:
                print(f"  ⚠️ 点击子菜单失败，尝试备用方式: {e}")
                try:
                    merchant_link = page.locator('a:has-text("商户准入管理")').first
                    merchant_link.click(timeout=5000)
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_LONG)
                    print("  ✅ 通过链接进入商户准入管理")
                    menu_entered = True
                except:
                    print("  ⚠️ 请手动点击进入商户准入管理")

            if not menu_entered:
                if not no_wait:
                    input("  按回车键继续...")

            print(f"\n步骤6: 查询审批任务ID {target_id}")
            try:
                # 使用JavaScript精确查找搜索框（通过placeholder或位置）
                result = page.evaluate(f'''(targetId) => {{
                    // 方法1: 通过placeholder查找
                    const inputs = document.querySelectorAll('input');
                    for (const input of inputs) {{
                        const placeholder = input.placeholder || '';
                        if (placeholder.includes('申请') || placeholder.includes('编号') || placeholder.includes('ID')) {{
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeInputValueSetter.call(input, targetId);
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            return true;
                        }}
                    }}

                    // 方法2: 查找第一个可见的文本输入框（排除隐藏的）
                    const visibleInputs = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'))
                        .filter(input => input.offsetParent !== null && !input.disabled);
                    if (visibleInputs.length > 0) {{
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        nativeInputValueSetter.call(visibleInputs[0], targetId);
                        visibleInputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        return true;
                    }}
                    return false;
                }}''', target_id)
                if result:
                    print(f"  ✅ 已输入审批任务ID: {target_id}")
                else:
                    print(f"  ⚠️ 未找到搜索框")

                # 查询按钮可能有空格（如"查  询"），用JS查找更可靠
                result = page.evaluate(r'''() => {
                    const btns = document.querySelectorAll('button, .ant-btn, input[type="button"]');
                    for (const btn of btns) {
                        const text = (btn.textContent || btn.value || '').replace(/\s/g, '');
                        if (text === '查询') {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }''')
                if result:
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(3000)  # 等待表格数据渲染
                    print("  ✅ 已点击查询按钮")
                else:
                    # 备用：Playwright locator（处理空格）
                    try:
                        search_btn = page.locator('button:has-text("查询"), button:has-text("查")').first
                        search_btn.click(timeout=5000)
                        page.wait_for_load_state('networkidle', timeout=15000)
                        page.wait_for_timeout(WAIT_TIME_LONG)
                        print("  ✅ 已点击查询按钮（备用方案）")
                    except Exception as e:
                        print(f"  ⚠️ 未找到查询按钮: {e}")
            except Exception as e:
                print(f"  ⚠️ 查询失败: {e}")

            # 步骤7-9: 在准入管理列表中查找并进入审批详情页
            print(f"\n步骤7: 在列表中查找审批任务 {target_id}")
            detail_page_entered = False

            try:
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
                                        return {{ found: true, action: 'button' }};
                                    }}
                                }}
                                row.click();
                                return {{ found: true, action: 'row' }};
                            }}
                        }}
                        return {{ found: false }};
                    }}''')
                    if result.get('found'):
                        print(f"  ✅ 已找到并点击审批任务 {target_id}")
                        page.wait_for_load_state('networkidle', timeout=30000)
                        page.wait_for_timeout(WAIT_TIME_LONG)
                        detail_page_entered = True
                        break
                    if retry < max_retries - 1:
                        print(f"  重试第 {retry + 1} 次...")
                        page.wait_for_timeout(2000)

            except Exception as e:
                print(f"  ⚠️ 查找失败: {e}")

            # ========== 兜底逻辑：列表中没找到，去商户信息管理验证状态 ==========
            if not detail_page_entered:
                print(f"\nℹ️ 列表中未找到 {target_id}，执行兜底验证...")

                review_success = False

                try:
                    # ---- 第一步：去商户信息管理查看正序第一条记录 ----
                    print("\n  [兜底步骤1] 前往商户信息管理...")

                    # 点击父菜单「商户风险管理」
                    risk_menu = page.locator('text=商户风险管理').first
                    risk_menu.click(timeout=3000)
                    page.wait_for_timeout(WAIT_TIME_NORMAL)

                    # 点击子菜单「商户信息管理」
                    info_entered = False
                    for retry in range(3):
                        try:
                            info_menu = page.locator('text=商户信息管理').first
                            if info_menu.is_visible():
                                info_menu.click(timeout=5000)
                                info_entered = True
                                break
                        except:
                            pass
                        js_result = page.evaluate('''() => {
                            const els = document.querySelectorAll('a, span, div');
                            for (const el of els) {
                                if ((el.textContent || '').trim() === '商户信息管理') {
                                    el.click(); return true;
                                }
                            }
                            return false;
                        }''')
                        if js_result:
                            info_entered = True
                            break
                        page.wait_for_timeout(1000)

                    if not info_entered:
                        print("  ⚠️ 无法进入商户信息管理，跳过兜底验证")
                    else:
                        page.wait_for_load_state('networkidle', timeout=15000)
                        page.wait_for_timeout(2000)
                        print("  ✅ 已进入商户信息管理")

                        # 查看正序第一条记录是否包含目标申请ID
                        first_row_info = page.evaluate(f'''(targetId) => {{
                            // 获取表格所有行（排除表头）
                            const allRows = document.querySelectorAll('tbody tr, tr.ant-table-row, .ant-table-tbody > tr');
                            if (allRows.length === 0) {{ return {{ hasData: false }}; }}

                            // 取正序第一条数据行
                            const firstRow = allRows[0];
                            const rowText = firstRow.textContent || '';
                            const cells = firstRow.querySelectorAll('td');

                            // 提取该行的所有单元格文本（用于显示和判断状态）
                            const cellTexts = Array.from(cells).map(c => c.textContent.trim());

                            // 检查第一条记录的申请ID是否匹配
                            const idMatched = rowText.includes(targetId);

                            // 检查状态是否为【补充资料待提交】或【资料待提交】
                            let statusMatched = false;
                            let matchedStatus = '';
                            for (const text of cellTexts) {{
                                if (text === '补充资料待提交' || text === '资料待提交' ||
                                    text.includes('补充资料待提交') || text.includes('资料待提交')) {{
                                    statusMatched = true;
                                    matchedStatus = text;
                                    break;
                                }}
                            }}

                            return {{
                                hasData: true,
                                rowText: rowText.substring(0, 150),
                                cellTexts: cellTexts,
                                idMatched: idMatched,
                                statusMatched: statusMatched,
                                matchedStatus: matchedStatus
                            }};
                        }}''', target_id)

                        if first_row_info.get('hasData'):
                            print(f"    正序第1行内容: {first_row_info.get('rowText', '')[:80]}")
                            print(f"    ID匹配({target_id}): {'✅ 是' if first_row_info.get('idMatched') else '❌ 否'}")

                            # 判断1：ID一致 + 状态为补充资料待提交 → 复审成功
                            if first_row_info.get('idMatched') and first_row_info.get('statusMatched'):
                                status_val = first_row_info.get('matchedStatus', '')
                                print(f"\n{'='*50}")
                                print(f"✅ 复审成功！（商户信息管理验证通过）")
                                print(f"  申请ID: {target_id}")
                                print(f"  当前状态: 【{status_val}】")
                                print(f"{'='*50}")
                                review_success = True
                            elif first_row_info.get('idMatched'):
                                # ID一致但状态不对，需要回到准入管理继续审批
                                actual_status = first_row_info.get('cellTexts', [])
                                print(f"    ⚠️ ID一致但状态不是【补充资料待提交】，当前状态字段: {actual_status}")

                except Exception as e:
                    print(f"  ⚠️ 商户信息管理验证异常: {e}")

                # ---- 第二步：如果商户信息管理未确认成功，回到商户准入管理重新查找 ----
                if not review_success:
                    print("\n  [兜底步骤2] 回到商户准入管理重新查找...")

                    try:
                        # 点击父菜单展开
                        risk_menu2 = page.locator('text=商户风险管理').first
                        risk_menu2.click(timeout=3000)
                        page.wait_for_timeout(WAIT_TIME_NORMAL)

                        # 点击子菜单
                        access_menu2 = page.locator('text=商户准入管理').first
                        access_menu2.click(timeout=5000)
                        page.wait_for_load_state('networkidle', timeout=15000)
                        page.wait_for_timeout(2000)
                        print("  ✅ 已返回商户准入管理")

                        # 重新查询
                        page.evaluate(f'''(targetId) => {{
                            const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
                            for (const input of inputs) {{
                                if (input.offsetParent !== null && !input.disabled) {{
                                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                    setter.call(input, targetId);
                                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    return true;
                                }}
                            }}
                            return false;
                        }}''', target_id)
                        print(f"  ✅ 已输入申请ID: {target_id}")

                        page.evaluate(r'''() => {
                            const btns = document.querySelectorAll('button, .ant-btn, input[type="button"]');
                            for (const btn of btns) {
                                if ((btn.textContent || btn.value || '').replace(/\s/g, '') === '查询') {
                                    btn.click(); return true;
                                }
                            }
                            return false;
                        }''')
                        page.wait_for_load_state('networkidle', timeout=15000)
                        page.wait_for_timeout(3000)
                        print("  ✅ 已点击查询")

                        # 查找正序第一条记录
                        result = page.evaluate(f'''(targetId) => {{
                            const rows = document.querySelectorAll('tbody tr, tr.ant-table-row, .ant-table-tbody > tr');
                            if (rows.length === 0) {{ return {{ found: false }}; }}

                            const firstRow = rows[0];
                            const rowText = firstRow.textContent || '';

                            // 检查第一条是否为目标ID
                            if (rowText.includes(targetId)) {{
                                // 提取状态
                                const cells = firstRow.querySelectorAll('td');
                                const cellTexts = Array.from(cells).map(c => c.textContent.trim());
                                let statusVal = '';
                                for (const t of cellTexts) {{
                                    if (t.includes('补充资料待提交') || t.includes('资料待提交') ||
                                        t.includes('初审') || t.includes('终审')) {{
                                        statusVal = t; break;
                                    }}
                                }}
                                return {{ found: true, isFirstRow: true, status: statusVal, allCells: cellTexts }};
                            }}

                            // 第一条不是，遍历所有行找目标ID
                            for (let i = 0; i < rows.length; i++) {{
                                const rt = rows[i].textContent || '';
                                if (rt.includes(targetId)) {{
                                    const cs = rows[i].querySelectorAll('td');
                                    return {{ found: true, isFirstRow: false, rowIndex: i }};
                                }}
                            }}

                            return {{ found: false }};
                        }}''', target_id)

                        if result.get('found'):
                            is_first = result.get('isFirstRow', False)
                            status_val = result.get('status', '')
                            print(f"    在列表中找到 {target_id}（正序第{'1' if is_first else str(result.get('rowIndex', 0)+1)}条）")
                            print(f"    状态: [{status_val}]")

                            if '补充资料待提交' in status_val or '资料待提交' in status_val:
                                print(f"\n{'='*50}")
                                print(f"✅ 复审成功！")
                                print(f"  申请ID: {target_id}")
                                print(f"  当前状态: 【{status_val}】")
                                print(f"{'='*50}")
                                review_success = True
                            else:
                                print(f"\n  ⚠️ 找到 {target_id} 但状态为 [{status_val}]，可能需要继续操作")
                        else:
                            print(f"  ⚠️ 商户准入管理中也未找到 {target_id}")

                    except Exception as e:
                        print(f"  ⚠️ 回到准入管理失败: {e}")

                # 最终结果
                print("\n" + "=" * 50)
                if review_success:
                    print("✅ 复审流程完成！")
                else:
                    print("ℹ️ 复审流程结束（未能自动确认状态）")
                print(f"  审批任务ID: {target_id}")
                print("=" * 50)

                if not no_wait:
                    input("\n按回车键关闭浏览器...")
                return

            # ========== 以下为正常流程：进入了审批详情页 ==========
            print("\n步骤8: 选择审批意见 - 建议通过")
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

            # 步骤10: 填写复核意见相关字段（只填可编辑的字段）
            print("\n步骤10: 查找并填写可编辑字段")
            try:
                # 获取页面上所有textarea的状态
                ta_info = page.evaluate('''() => {
                    const tas = document.querySelectorAll('textarea');
                    return Array.from(tas).map(ta => ({
                        id: ta.id,
                        placeholder: ta.placeholder,
                        disabled: ta.disabled || ta.classList.contains('ant-input-disabled'),
                        visible: ta.offsetParent !== null,
                        value: ta.value ? ta.value.substring(0, 20) : ''
                    }));
                }''')

                editable_found = False
                for info in ta_info:
                    status = "禁用" if info['disabled'] else "可编辑"
                    print(f"    [{status}] id={info.get('id','')} placeholder={info.get('placeholder','')}")

                    # 只填写可编辑且可见的字段
                    if not info['disabled'] and info['visible']:
                        ta_id = info.get('id', '')
                        if ta_id:
                            ta_el = page.locator(f'#{ta_id}')
                            if ta_el.count() > 0:
                                ta_el.click(timeout=2000)
                                ta_el.fill('123')
                                ph = info.get('placeholder', '未知字段')
                                print(f"  ✅ 已填写 {ph}：123")
                                editable_found = True

                if not editable_found:
                    print("  ⚠️ 所有textarea均为禁用状态，无需填写（或需先执行其他操作）")
            except Exception as e:
                print(f"  ⚠️ 填写字段失败: {e}")

            # 步骤11: 经办初审意见已在步骤10中统一处理（只填可编辑字段）
            print("\n步骤11: 字段填写已在步骤10完成")

            # 步骤12: 点击提交按钮（可能是"提交复核"、"提交"、"复核通过"等）
            print("\n步骤12: 点击提交按钮")
            try:
                page.evaluate('window.scrollTo(0, 0)')
                page.wait_for_timeout(WAIT_TIME_SHORT)

                # 先打印页面上所有按钮文本，方便调试
                btn_texts = page.evaluate('''() => {
                    const allBtns = document.querySelectorAll('button, input[type="button"], input[type="submit"], .ant-btn');
                    return Array.from(allBtns).map(btn => (btn.textContent || btn.innerText || btn.value || '').trim())
                        .filter(t => t.length > 0 && t.length < 20);
                }''')
                print(f"  页面可用按钮: {btn_texts}")

                clicked = False

                # 方法1: JS 查找包含关键词的按钮（复审页面的按钮是"初审通过"）
                for keyword in ['初审通过', '提交复核', '提交', '复核通过', '复核', '确认']:
                    result = page.evaluate(f'''() => {{
                        const allButtons = document.querySelectorAll('button, input[type="button"], input[type="submit"], .ant-btn');
                        for (let btn of allButtons) {{
                            const text = (btn.textContent || btn.innerText || btn.value || '').trim().replace(/\\s/g, '');
                            if (text === '{keyword}' || text.includes('{keyword}')) {{
                                btn.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                                btn.click();
                                return {{ success: true, text: text }};
                            }}
                        }}
                        return {{ success: false }};
                    }}''')
                    if result.get('success'):
                        print(f"  ✅ 已点击按钮: {result.get('text')}")
                        clicked = True
                        break

                # 方法2: Playwright locator
                if not clicked:
                    for keyword in ['初审通过', '提交复核', '提交', '复核通过', '复核', '确认']:
                        try:
                            btn = page.locator(f'button:has-text("{keyword}"), input[value="{keyword}"]').first
                            if btn.count() > 0 and btn.is_visible():
                                btn.click(timeout=3000)
                                print(f"  ✅ 通过Playwright点击按钮: {keyword}")
                                clicked = True
                                break
                        except:
                            pass

                if clicked:
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_LONG)
                else:
                    print("  ⚠️ 未找到提交按钮")

            except Exception as e:
                print(f"  ❌ 步骤12执行异常: {e}")

            # 步骤13: 点击弹窗中的提交/确定按钮
            print("\n步骤13: 处理弹窗")
            try:
                page.wait_for_timeout(2000)

                # 多次尝试处理弹窗（可能有多个连续弹窗）
                for popup_attempt in range(3):
                    page.wait_for_timeout(1500)

                    # 方法1: JS 在弹窗容器内查找并点击按钮
                    result = page.evaluate('''() => {
                        const popups = document.querySelectorAll('.ant-modal-wrap');
                        for (const popup of popups) {
                            // 检查弹窗是否可见
                            if (popup.offsetParent === null) continue;

                            const buttons = popup.querySelectorAll('button, .ant-btn');
                            for (const btn of buttons) {
                                const text = (btn.textContent || btn.innerText || '').trim().replace(/\\s/g, '');
                                // 匹配：提交、确定、确认、通过 等
                                if (text === '提交' || text === '确定' || text === '确认' ||
                                    text === '通过' || text.includes('提交') || text.includes('确定')) {
                                    btn.click();
                                    return { success: true, buttonText: text };
                                }
                            }
                        }
                        return { success: false };
                    }''')

                    if result.get('success'):
                        btn_text = result.get('buttonText', '')
                        print(f"  ✅ 已点击弹窗按钮: [{btn_text}]")
                        page.wait_for_load_state('networkidle', timeout=10000)
                        page.wait_for_timeout(1000)
                    else:
                        # 方法2: Playwright force click（绕过遮罩层）
                        try:
                            modal = page.locator('.ant-modal-wrap').last
                            if modal.is_visible():
                                submit_btn = modal.locator('button').filter(has_text="提交").or_(
                                    modal.locator('button').filter(has_text="确定")
                                ).first
                                if submit_btn.count() > 0:
                                    submit_btn.click(force=True, timeout=3000)
                                    print("  ✅ 已强制点击弹窗按钮")
                                    page.wait_for_load_state('networkidle', timeout=10000)
                                    page.wait_for_timeout(1000)
                        except:
                            pass

                print("  ✅ 弹窗处理完成")
            except Exception as e:
                print(f"  ⚠️ 弹窗处理异常: {e}")

            print("\n" + "=" * 50)
            print("✅ 复审流程执行完成！")
            print(f"  审批任务ID: {target_id}")
            print("=" * 50)

            if not no_wait:
                input("\n按回车键关闭浏览器...")

        except Exception as e:
            print(f"\n❌ 执行过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    main()
