#!/usr/bin/env python3
"""
Guardian系统统一登录平台 - 自动化登录脚本
登录地址: https://guardian.weibopay.com/uni-login/login

用法:
    python merchant_access_approval.py --id 6337
    python merchant_access_approval.py -i 1234

参数:
    --id, -i:  申请ID（必填）
    --username, -u:  登录用户名（默认: liuchunen）
    --password, -p:  登录密码（默认: Abc@1234）
    --help, -h:  显示帮助信息
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
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Guardian系统商户准入审批自动化脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 merchant_access_approval.py 6337
    python3 merchant_access_approval.py 1234 -u admin -p Secret123
        """
    )
    
    parser.add_argument(
        'id',
        type=str,
        help='申请ID（必填）'
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

def get_screenshot_path(prefix):
    screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)
    return os.path.join(screenshot_dir, f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

def login_guardian(username, password, target_id):
    print("=== Guardian系统统一登录 ===")
    print(f"登录地址: {LOGIN_URL}")
    print(f"用户名: {username}")
    print(f"申请ID: {target_id}")
    print(f"选择系统: {SYSTEM_NAME}")
    print("=" * 50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            args=["--start-maximized", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        
        try:
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            print("\n步骤1: 访问登录页面")
            page.goto(LOGIN_URL, timeout=30000)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(WAIT_TIME_NORMAL)
            
            print("步骤2: 输入用户名")
            username_input = page.locator('input[type="text"]').first
            username_input.fill(username)
            print(f"  已输入用户名: {username}")
            page.wait_for_timeout(WAIT_TIME_SHORT)
            
            print("步骤3: 输入密码")
            password_input = page.locator('input[type="password"]').first
            password_input.fill(password)
            print("  已输入密码")
            page.wait_for_timeout(WAIT_TIME_SHORT)
            
            print("步骤4: 选择系统 - 商户准入系统")
            
            selected = False
            max_retries = 3
            
            for retry in range(max_retries):
                try:
                    # 方法1: 尝试直接点击包含系统名称的元素
                    system_element = page.locator(f"text={SYSTEM_NAME}").first
                    system_element.click(timeout=2000)
                    page.wait_for_timeout(WAIT_TIME_SHORT)
                    selected = True
                    print(f"  已选择系统: {SYSTEM_NAME}")
                    break
                except:
                    pass
                
                try:
                    # 方法2: 查找下拉框箭头并点击展开
                    arrows = page.locator('.dijitArrowButtonInner')
                    if arrows.count() > 0:
                        arrows.last.click(timeout=2000)
                        page.wait_for_timeout(WAIT_TIME_NORMAL)
                        
                        # 等待菜单展开后点击系统选项
                        menu_item = page.locator(f".dijitMenuItem:text('{SYSTEM_NAME}')").first
                        menu_item.click(timeout=2000)
                        page.wait_for_timeout(WAIT_TIME_SHORT)
                        selected = True
                        print(f"  已选择系统: {SYSTEM_NAME}")
                        break
                except:
                    pass
                
                try:
                    # 方法3: 使用role选择器查找下拉框
                    combobox = page.locator('role=combobox').last
                    combobox.click(timeout=2000)
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                    
                    option = page.locator(f'role=option:text("{SYSTEM_NAME}")').first
                    option.click(timeout=2000)
                    page.wait_for_timeout(WAIT_TIME_SHORT)
                    selected = True
                    print(f"  已选择系统: {SYSTEM_NAME}")
                    break
                except:
                    pass
                
                if retry < max_retries - 1:
                    print(f"  重试第 {retry + 1} 次...")
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
            
            if not selected:
                print(f"  ⚠️ 自动选择系统失败，请手动选择")
            
            page.wait_for_timeout(WAIT_TIME_SHORT)
            
            print("步骤5: 点击登录")
            
            # 先获取页面信息进行调试
            page_info = page.evaluate('''() => {
                const forms = document.querySelectorAll('form');
                const allButtons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                const links = document.querySelectorAll('a');
                const loginElements = [];
                
                allButtons.forEach(btn => {
                    const text = btn.textContent ? btn.textContent.trim() : '';
                    const value = btn.value ? btn.value.trim() : '';
                    if (text.includes('登录') || value.includes('登录')) {
                        loginElements.push({
                            type: 'button',
                            tagName: btn.tagName,
                            btnType: btn.type,
                            className: btn.className,
                            id: btn.id,
                            textContent: text,
                            value: value
                        });
                    }
                });
                
                links.forEach(link => {
                    const text = link.textContent ? link.textContent.trim() : '';
                    if (text.includes('登录')) {
                        loginElements.push({
                            type: 'link',
                            tagName: link.tagName,
                            className: link.className,
                            id: link.id,
                            textContent: text,
                            href: link.href
                        });
                    }
                });
                
                return {
                    formCount: forms.length,
                    loginElements: loginElements,
                    currentUrl: window.location.href,
                    forms: forms.length > 0 ? {
                        action: forms[0].action,
                        method: forms[0].method
                    } : null
                };
            }''')
            print(f"  页面信息: 表单数={page_info['formCount']}")
            print(f"  表单信息: {page_info['forms']}")
            print(f"  登录元素数: {len(page_info['loginElements'])}")
            for i, elem in enumerate(page_info['loginElements']):
                print(f"    [{i}] {elem['type']} {elem['tagName']} id={elem['id']} class={elem['className']}")
                print(f"         text='{elem['textContent']}' value='{elem['value']}'")
            
            login_success = False
            
            # 尝试多种方式提交登录
            methods_tried = 0
            
            # 方法1: 查找并点击登录按钮(通过value属性)
            if not login_success:
                methods_tried += 1
                try:
                    login_btn = page.locator('input[value="登录"]').first
                    login_btn.click(timeout=3000)
                    print(f"  [{methods_tried}] 点击登录按钮(input[value=登录])")
                    print("  等待登录响应...")
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                    if page.url != LOGIN_URL:
                        login_success = True
                except Exception as e:
                    print(f"  [{methods_tried}] 点击登录按钮失败: {e}")
            
            # 方法2: 使用JavaScript提交表单
            if not login_success:
                methods_tried += 1
                try:
                    page.evaluate('''() => {
                        const forms = document.querySelectorAll('form');
                        if (forms.length > 0) {
                            forms[0].submit();
                        }
                    }''')
                    print(f"  [{methods_tried}] JavaScript提交表单")
                    print("  等待登录响应...")
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                    if page.url != LOGIN_URL:
                        login_success = True
                except Exception as e:
                    print(f"  [{methods_tried}] JavaScript提交表单失败: {e}")
            
            # 方法3: 查找带特定class的按钮
            if not login_success:
                methods_tried += 1
                try:
                    login_btn = page.locator('.btn.btn-primary#loginBtn').first
                    login_btn.click(timeout=3000)
                    print(f"  [{methods_tried}] 点击登录按钮(.btn.btn-primary#loginBtn)")
                    print("  等待登录响应...")
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                    if page.url != LOGIN_URL:
                        login_success = True
                except Exception as e:
                    print(f"  [{methods_tried}] 点击带class的按钮失败: {e}")
            
            print("\n步骤6: 确认登录结果")
            print(f"  当前URL: {page.url}")
            print(f"  当前标题: {page.title()}")
            
            if login_success:
                print("\n✅ 登录成功！")
                
                # 步骤7: 点击商户风险管理菜单
                print("\n步骤7: 点击商户风险管理菜单")
                try:
                    # 查找商户风险管理菜单
                    risk_menu = page.locator('text=商户风险管理').first
                    risk_menu.click(timeout=3000)
                    print("  已点击商户风险管理菜单")
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                except Exception as e:
                    print(f"  ⚠️ 点击商户风险管理菜单失败: {e}")
                
                # 步骤8: 点击商户准入管理子菜单
                print("\n步骤8: 点击商户准入管理子菜单")
                try:
                    # 查找商户准入管理子菜单
                    access_menu = page.locator('text=商户准入管理').first
                    access_menu.click(timeout=3000)
                    print("  已点击商户准入管理子菜单")
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                except Exception as e:
                    print(f"  ⚠️ 点击商户准入管理子菜单失败: {e}")
                
                # 步骤9: 查询申请ID
                print(f"\n步骤9: 查询申请ID为 {target_id} 的申请")
                
                try:
                    # 先截图查看页面状态
                    page.screenshot(path=get_screenshot_path("step9_search_page"), full_page=True)
                    
                    # 使用JavaScript精确查找搜索框（通过placeholder或位置）
                    result = page.evaluate('''(targetId) => {
                        const inputs = document.querySelectorAll('input[type="text"]');
                        let searchInput = null;
                        
                        // 方法1: 通过placeholder查找
                        for (let input of inputs) {
                            const placeholder = (input.placeholder || '').toLowerCase();
                            if (placeholder.includes('申请') || placeholder.includes('id') || placeholder.includes('搜索') || placeholder.includes('查询')) {
                                searchInput = input;
                                break;
                            }
                        }
                        
                        // 方法2: 如果没找到，找第一个可见的输入框
                        if (!searchInput) {
                            for (let input of inputs) {
                                if (input.offsetParent !== null) { // 可见元素
                                    searchInput = input;
                                    break;
                                }
                            }
                        }
                        
                        if (searchInput) {
                            searchInput.value = '';
                            searchInput.value = targetId;
                            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                            searchInput.dispatchEvent(new Event('change', { bubbles: true }));
                            return { success: true, placeholder: searchInput.placeholder || 'none' };
                        }
                        return { success: false };
                    }''', target_id)
                    
                    if result and result.get('success'):
                        print(f"  ✅ 已在搜索框输入申请ID: {target_id} (placeholder: {result.get('placeholder')})")
                    else:
                        # 备用：Playwright方式
                        search_input = page.locator('input[type="text"]').first
                        search_input.fill(target_id)
                        print(f"  ✅ 通过Playwright输入申请ID: {target_id}")
                    
                    page.wait_for_timeout(WAIT_TIME_SHORT)
                    
                    # 点击查询按钮
                    search_clicked = page.evaluate('''() => {
                        const buttons = document.querySelectorAll('button, input[type="button"]');
                        for (let btn of buttons) {
                            const text = (btn.textContent || btn.value || '').trim();
                            if (text.includes('查询')) {
                                btn.click();
                                return text;
                            }
                        }
                        return false;
                    }''')
                    
                    if search_clicked:
                        print(f"  ✅ 已点击查询按钮: {search_clicked}")
                    else:
                        search_btn = page.locator('button:has-text("查询")').first
                        if search_btn.count() > 0:
                            search_btn.click()
                            print("  ✅ 通过Playwright点击查询按钮")
                    
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                    
                    # 截图确认搜索结果
                    page.screenshot(path=get_screenshot_path("step9_search_result"), full_page=True)
                    print("  📸 已截图搜索结果")
                    
                except Exception as e:
                    print(f"  ⚠️ 查询失败: {e}")
                    page.screenshot(path=get_screenshot_path("step9_error"), full_page=True)
                    print("  继续尝试直接查找申请记录...")
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                
                # 步骤10: 找到对应申请并点击查看按钮
                print(f"\n步骤10: 找到申请ID {target_id} 并点击查看")
                
                found = False
                try:
                    # 方法1: 查找包含该ID的行，然后找到对应的查看按钮
                    result = page.evaluate('''(targetId) => {
                        const tables = document.querySelectorAll('table');
                        for (let table of tables) {
                            const rows = table.querySelectorAll('tr');
                            for (let row of rows) {
                                const cells = row.querySelectorAll('td');
                                for (let cell of cells) {
                                    if (cell.textContent && cell.textContent.trim() === targetId) {
                                        // 找到该行，然后查找查看按钮
                                        const allLinks = row.querySelectorAll('a, button');
                                        for (let btn of allLinks) {
                                            if (btn.textContent && btn.textContent.includes('查看')) {
                                                btn.click();
                                                return true;
                                            }
                                        }
                                        // 如果没找到，尝试找操作列
                                        const actionCells = row.querySelectorAll('td:last-child, td:last-of-type');
                                        for (let ac of actionCells) {
                                            const links = ac.querySelectorAll('a');
                                            for (let link of links) {
                                                if (link.textContent && link.textContent.includes('查看')) {
                                                    link.click();
                                                    return true;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        return false;
                    }''', target_id)
                    
                    if result:
                        print(f"  ✅ 已找到申请ID {target_id} 并点击查看按钮")
                        found = True
                    else:
                        # 方法2: 直接查找查看按钮
                        print("  [方法1] 通过行查找失败，尝试方法2")
                        view_buttons = page.locator('a:text("查看")')
                        if view_buttons.count() > 0:
                            view_buttons.first.click(timeout=3000)
                            print(f"  ✅ 已点击查看按钮")
                            found = True
                except Exception as e:
                    print(f"  ⚠️ 点击查看按钮失败: {e}")
                
                if found:
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                    print(f"\n  当前页面标题: {page.title()}")
                    
                    # 步骤11: 填写审批意见 - 选择"建议通过"
                    print("\n步骤11: 填写审批意见 - 选择建议通过")
                    try:
                        # 先截图查看审批意见区域
                        page.screenshot(path=get_screenshot_path("step11_before_approval"), full_page=True)
                        
                        selected = False
                        
                        # 方法1: 通过label查找并点击（支持自定义radio组件）
                        result = page.evaluate('''() => {
                            const labels = document.querySelectorAll('label');
                            for (let label of labels) {
                                if (label.textContent && label.textContent.includes('建议通过')) {
                                    // 先尝试点击label本身（对于自定义radio组件，label可触发radio）
                                    label.click();
                                    
                                    // 再尝试找到对应的radio并设置checked
                                    const radioId = label.getAttribute('for');
                                    if (radioId) {
                                        const radio = document.getElementById(radioId);
                                        if (radio) {
                                            radio.checked = true;
                                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                                        }
                                    }
                                    
                                    // 检查父元素中的radio
                                    const parent = label.closest('.ant-radio-wrapper, .radio-wrapper, [class*="radio"]');
                                    if (parent) {
                                        const radio = parent.querySelector('input[type="radio"]');
                                        if (radio) {
                                            radio.checked = true;
                                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                                        }
                                    }
                                    
                                    return true;
                                }
                            }
                            return false;
                        }''')
                        
                        if result:
                            print("  ✅ 已选择审批意见：建议通过")
                            selected = True
                        else:
                            # 方法2: 查找所有radio，检查value或相邻文本
                            result = page.evaluate('''() => {
                                const radios = document.querySelectorAll('input[type="radio"]');
                                for (let radio of radios) {
                                    if (radio.value && radio.value.includes('通过')) {
                                        radio.checked = true;
                                        radio.dispatchEvent(new Event('change', { bubbles: true }));
                                        radio.click();
                                        return true;
                                    }
                                    // 检查相邻兄弟元素
                                    let sibling = radio.nextElementSibling;
                                    while (sibling) {
                                        if (sibling.textContent && sibling.textContent.includes('建议通过')) {
                                            radio.checked = true;
                                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                                            radio.click();
                                            return true;
                                        }
                                        sibling = sibling.nextElementSibling;
                                    }
                                }
                                return false;
                            }''')
                            if result:
                                print("  ✅ 通过value找到并选择审批意见：建议通过")
                                selected = True
                        
                        if not selected:
                            print("  ⚠️ 未找到建议通过单选按钮")
                            
                        page.wait_for_timeout(WAIT_TIME_SHORT)
                        
                        # 截图确认审批意见状态
                        page.screenshot(path=get_screenshot_path("step11_after_approval"), full_page=True)
                        print("  📸 已截图审批意见状态")
                        
                    except Exception as e:
                        print(f"  ⚠️ 选择审批意见失败: {e}")
                        page.screenshot(path=get_screenshot_path("step11_error"), full_page=True)
                    
                    # 步骤11.5: 勾选初审环节需要补充的材料复选框（启用输入框）
                    print("\n步骤11.5: 勾选初审环节需要补充的材料复选框")
                    try:
                        # 等待页面加载
                        page.wait_for_timeout(1000)
                        
                        # 勾选所有复选框
                        result = page.evaluate('''() => {
                            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                            let count = 0;
                            for (let cb of checkboxes) {
                                if (!cb.checked) {
                                    cb.click();
                                    count++;
                                }
                            }
                            return count;
                        }''')
                        print(f"  ✅ 已勾选 {result} 个复选框")
                        page.wait_for_timeout(WAIT_TIME_SHORT)
                    except Exception as e:
                        print(f"  ⚠️ 勾选复选框失败: {e}")
                    
                    # 步骤12: 填写风险分析与结论（如果输入框可用）
                    print("\n步骤12: 填写风险分析与结论")
                    try:
                        # 检查输入框是否可用
                        result = page.evaluate('''() => {
                            const textarea = document.getElementById('firstCheck_riskAnalysisConclusion');
                            if (textarea && !textarea.disabled) {
                                textarea.value = '123';
                                textarea.dispatchEvent(new Event('input'));
                                return true;
                            }
                            return false;
                        }''')
                        if result:
                            print("  ✅ 已填写风险分析与结论：123")
                        else:
                            print("  ⚠️ 风险分析与结论输入框禁用，跳过")
                    except Exception as e:
                        print(f"  ⚠️ 填写风险分析与结论失败: {e}")
                    
                    # 步骤13: 填写经办初审意见
                    print("\n步骤13: 填写经办初审意见")
                    try:
                        filled = False
                        
                        # 方法1: 尝试通过label文本查找
                        result = page.evaluate('''() => {
                            const labels = document.querySelectorAll('label');
                            for (let label of labels) {
                                if (label.textContent && label.textContent.includes('经办初审')) {
                                    const inputId = label.getAttribute('for');
                                    if (inputId) {
                                        const input = document.getElementById(inputId);
                                        if (input) {
                                            input.value = '123';
                                            return true;
                                        }
                                    }
                                }
                            }
                            return false;
                        }''')
                        if result:
                            print("  ✅ [方法1] 通过label找到并填写经办初审意见：123")
                            filled = True
                        
                        # 方法2: 尝试通过textarea的class或id查找
                        if not filled:
                            result = page.evaluate('''() => {
                                const textareas = document.querySelectorAll('textarea');
                                for (let ta of textareas) {
                                    if (ta.id && ta.id.includes('opinion')) {
                                        ta.value = '123';
                                        return true;
                                    }
                                    if (ta.className && ta.className.includes('opinion')) {
                                        ta.value = '123';
                                        return true;
                                    }
                                    if (ta.id && ta.id.includes('comment')) {
                                        ta.value = '123';
                                        return true;
                                    }
                                    if (ta.className && ta.className.includes('comment')) {
                                        ta.value = '123';
                                        return true;
                                    }
                                }
                                return false;
                            }''')
                            if result:
                                print("  ✅ [方法2] 通过class/id找到并填写经办初审意见：123")
                                filled = True
                        
                        # 方法3: 尝试通过placeholder查找
                        if not filled:
                            result = page.evaluate('''() => {
                                const textareas = document.querySelectorAll('textarea');
                                for (let ta of textareas) {
                                    if (ta.placeholder) {
                                        if (ta.placeholder.includes('经办') || ta.placeholder.includes('初审') || ta.placeholder.includes('意见')) {
                                            ta.value = '123';
                                            return true;
                                        }
                                    }
                                }
                                return false;
                            }''')
                            if result:
                                print("  ✅ [方法3] 通过placeholder找到并填写经办初审意见：123")
                                filled = True
                        
                        # 方法4: 查找第二个textarea（通常风险分析是第一个，经办初审是第二个）
                        if not filled:
                            result = page.evaluate('''() => {
                                const textareas = document.querySelectorAll('textarea');
                                if (textareas.length >= 2) {
                                    textareas[1].value = '123';
                                    return true;
                                }
                                return false;
                            }''')
                            if result:
                                print("  ✅ [方法4] 通过位置找到并填写经办初审意见：123")
                                filled = True
                        
                        if not filled:
                            print("  ⚠️ 未找到经办初审意见输入框")
                    except Exception as e:
                        print(f"  ⚠️ 填写经办初审意见失败: {e}")
                    
                    # 步骤14: 点击提交复核按钮
                    print("\n步骤14: 点击提交复核按钮")
                    try:
                        clicked = False
                        
                        # 先截图记录当前状态
                        page.screenshot(path=get_screenshot_path("step14_before_submit"), full_page=True)
                        print("  📸 已截图：提交前页面状态")
                        
                        # 先滚动到页面顶部（按钮可能在顶部）
                        page.evaluate('window.scrollTo(0, 0)')
                        page.wait_for_timeout(WAIT_TIME_SHORT)
                        
                        # 方法1: 查找包含"提交复核"文字的按钮（使用 includes，更灵活）
                        result = page.evaluate('''() => {
                            const allButtons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                            for (let btn of allButtons) {
                                const text = (btn.textContent || btn.innerText || btn.value || '').trim();
                                if (text.includes('提交复核')) {
                                    btn.scrollIntoView({ behavior: 'instant', block: 'center' });
                                    btn.click();
                                    return { success: true, text: text, tag: btn.tagName };
                                }
                            }
                            return { success: false };
                        }''')
                        
                        if result and result.get('success'):
                            print(f"  ✅ 已点击按钮: [{result['tag']}] {result['text']}")
                            clicked = True
                        else:
                            print("  ⚠️ 方法1未找到提交复核按钮，尝试备用方案...")
                        
                        # 方法2: 通过Playwright原生 locator 查找
                        if not clicked:
                            submit_btn = page.locator('button:has-text("提交复核")').first
                            if submit_btn.count() > 0:
                                submit_btn.scroll_into_view_if_needed()
                                submit_btn.click()
                                print("  ✅ 通过Playwright locator点击提交复核")
                                clicked = True
                        
                        # 方法3: 滚动到底部再查找
                        if not clicked:
                            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                            page.wait_for_timeout(WAIT_TIME_SHORT)
                            
                            result = page.evaluate('''() => {
                                const buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                                for (let btn of buttons) {
                                    const text = (btn.textContent || btn.innerText || btn.value || '').trim();
                                    if (text.includes('提交复核')) {
                                        btn.scrollIntoView({ behavior: 'instant', block: 'center' });
                                        btn.click();
                                        return { success: true, text: text };
                                    }
                                }
                                return { success: false };
                            }''')
                            if result and result.get('success'):
                                print(f"  ✅ 滚动到底部找到并点击: {result['text']}")
                                clicked = True
                        
                        if not clicked:
                            print("  ❌ 所有方法均未找到提交复核按钮，截图保存...")
                            page.screenshot(path=get_screenshot_path("step14_submit_not_found"), full_page=True)
                        else:
                            # 点击后等待弹窗出现（关键修复！）
                            print("  ⏳ 等待弹窗出现...")
                            page.wait_for_timeout(2000)
                            
                            # 截图确认点击后状态
                            page.screenshot(path=get_screenshot_path("step14_after_submit"), full_page=True)
                            print("  📸 已截图：点击提交后页面状态")
                            
                            # 等待弹窗渲染（尝试多种弹窗class）
                            try:
                                page.wait_for_selector('.ant-modal-wrap, .ant-modal-root, .modal, [role="dialog"]', 
                                                      timeout=5000, state='visible')
                                print("  ✅ 弹窗已出现")
                            except:
                                print("  ⚠️ 未检测到标准弹窗，继续执行...")
                    
                    except Exception as e:
                        print(f"  ❌ 点击提交复核按钮失败: {e}")
                        page.screenshot(path=get_screenshot_path("step14_error"), full_page=True)
                    
                    # 步骤14.5: 处理弹窗中的复选框和提交
                    print("\n步骤14.5: 处理审批弹窗")
                    try:
                        page.wait_for_timeout(2000)
                        
                        # 尝试多种弹窗选择器
                        popup_selectors = [
                            '.ant-modal-wrap',
                            '.ant-modal-root',
                            '.modal',
                            '[role="dialog"]',
                            '.dialog'
                        ]
                        
                        popup_found = False
                        for selector in popup_selectors:
                            popup = page.locator(selector).first
                            if popup.count() > 0 and popup.is_visible():
                                popup_found = True
                                print(f"  ✅ 找到弹窗: {selector}")
                                
                                # 勾选所有复选框
                                checkboxes = popup.locator('input[type="checkbox"]').all()
                                checked_count = 0
                                for cb in checkboxes:
                                    if not cb.is_checked():
                                        cb.check()
                                        checked_count += 1
                                print(f"  ✅ 已勾选 {checked_count} 个复选框")
                                
                                # 填写附加信息（如果有textarea）
                                textarea = popup.locator('textarea').first
                                if textarea.count() > 0:
                                    textarea.fill('无')
                                    print("  ✅ 已填写附加信息")
                                
                                # 截图弹窗状态
                                popup.screenshot(path=get_screenshot_path("step14_5_popup"))
                                print("  📸 已截图弹窗状态")
                                
                                # 点击弹窗中的提交按钮
                                submit_btn = popup.locator('button:has-text("提交")').first
                                if submit_btn.count() > 0:
                                    submit_btn.click()
                                    print("  ✅ 已点击弹窗提交按钮")
                                    page.wait_for_timeout(2000)
                                else:
                                    # 备用：查找所有包含"确定"或"提交"的按钮
                                    buttons = popup.locator('button').all()
                                    for btn in buttons:
                                        btn_text = btn.inner_text().strip()
                                        if '提交' in btn_text or '确定' in btn_text or '确认' in btn_text:
                                            btn.click()
                                            print(f"  ✅ 已点击弹窗按钮: {btn_text}")
                                            page.wait_for_timeout(2000)
                                            break
                                
                                break
                        
                        if not popup_found:
                            print("  ⚠️ 未找到弹窗，检查是否已直接提交...")
                            page.screenshot(path=get_screenshot_path("step14_5_no_popup"), full_page=True)
                    
                    except Exception as e:
                        print(f"  ❌ 弹窗处理异常: {e}")
                        page.screenshot(path=get_screenshot_path("step14_5_error"), full_page=True)
                    
                    # 步骤15: 检测确认弹窗
                    print("\n步骤15: 检测确认弹窗")
                    try:
                        page.wait_for_timeout(2000)
                        
                        # 截图确认当前状态
                        page.screenshot(path=get_screenshot_path("step15_confirm_check"), full_page=True)
                        
                        # 查找确认弹窗
                        confirm_popup = page.locator('.ant-modal-wrap:has-text("确认"), .ant-modal-wrap:has-text("提示"), .ant-modal-wrap:has-text("提交复核")').first
                        if confirm_popup.count() > 0 and confirm_popup.is_visible():
                            print("  ✅ 检测到确认弹窗")
                            
                            # 查找确定按钮（优先红色/primary）
                            ok_btn = confirm_popup.locator('button:has-text("确定"), button:has-text("确认"), button.ant-btn-primary').first
                            if ok_btn.count() > 0:
                                ok_btn.click()
                                print("  ✅ 已点击确定按钮")
                                page.wait_for_timeout(2000)
                            else:
                                # JavaScript 备用
                                page.evaluate('''() => {
                                    const btns = document.querySelectorAll('button');
                                    for (let b of btns) {
                                        if (b.textContent.includes('确定') || b.textContent.includes('确认')) {
                                            b.click();
                                            return true;
                                        }
                                    }
                                    return false;
                                }''')
                                print("  ✅ 通过JS点击确定按钮")
                        else:
                            # 也尝试通过JS检测
                            confirm_exists = page.evaluate('''() => {
                                const allText = document.body.innerText || '';
                                return allText.includes('确认提交复核') || allText.includes('确认提交');
                            }''')
                            if confirm_exists:
                                print("  ✅ 页面包含确认文本，通过JS点击确定...")
                                page.evaluate('''() => {
                                    const btns = document.querySelectorAll('button');
                                    for (let b of btns) {
                                        if (b.textContent.includes('确定') || b.textContent.includes('确认')) {
                                            b.click();
                                            return true;
                                        }
                                    }
                                    return false;
                                }''')
                            else:
                                print("  未检测到确认弹窗，流程可能已完成")
                    
                    except Exception as e:
                        print(f"  ❌ 确认弹窗处理异常: {e}")
                    
                    # 最终状态截图
                    print("\n📸 最终页面状态截图")
                    page.screenshot(path=get_screenshot_path("final_state"), full_page=True)
                    print(f"  当前页面标题: {page.title()}")
                    print(f"  当前页面URL: {page.url}")
                
                else:
                    print(f"  ⚠️ 未找到申请ID {target_id} 的查看按钮")
                
                return True
            else:
                print("\n❌ 登录失败，页面未跳转")
                return False
                
        except Exception as e:
            print(f"\n❌ 登录异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            print("\n登录流程已完成，浏览器将保持打开状态...")
            while True:
                try:
                    page.wait_for_timeout(5000)
                except:
                    break

def main():
    args = parse_args()
    
    try:
        result = login_guardian(args.username, args.password, args.id)
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ 执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()