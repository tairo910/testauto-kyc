#!/usr/bin/env python3
"""
Guardian系统统一登录平台 - 自动化登录脚本
登录地址: https://guardian.weibopay.com/uni-login/login
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://guardian.weibopay.com/uni-login/login"
USERNAME = "liuchunen"
PASSWORD = "Abc@1234"
SYSTEM_NAME = "商户准入系统"

WAIT_TIME_SHORT = 300
WAIT_TIME_NORMAL = 1000
WAIT_TIME_LONG = 2000

def get_screenshot_path(prefix):
    screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)
    return os.path.join(screenshot_dir, f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

def login_guardian():
    print("=== Guardian系统统一登录 ===")
    print(f"登录地址: {LOGIN_URL}")
    print(f"用户名: {USERNAME}")
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
            username_input.fill(USERNAME)
            print(f"  已输入用户名: {USERNAME}")
            page.wait_for_timeout(WAIT_TIME_SHORT)
            
            print("步骤3: 输入密码")
            password_input = page.locator('input[type="password"]').first
            password_input.fill(PASSWORD)
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
                
                # 步骤9: 查询申请ID为6337的申请
                target_id = "6337"
                print(f"\n步骤9: 查询申请ID为 {target_id} 的申请")
                
                try:
                    # 找到搜索框并输入申请ID
                    search_input = page.locator('input[type="text"]').first
                    search_input.fill(target_id)
                    print(f"  已在搜索框输入申请ID: {target_id}")
                    
                    # 点击查询按钮
                    search_btn = page.locator('text=查询').first
                    search_btn.click(timeout=3000)
                    print("  已点击查询按钮")
                    page.wait_for_load_state('networkidle', timeout=15000)
                    page.wait_for_timeout(WAIT_TIME_NORMAL)
                except Exception as e:
                    print(f"  ⚠️ 查询失败: {e}")
                
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
                                        const viewBtn = row.querySelector('a:contains("查看"), button:contains("查看"), [title*="查看"], [onclick*="查看"]');
                                        if (viewBtn) {
                                            viewBtn.click();
                                            return true;
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
                        # 方法1: 尝试通过label文本查找
                        result = page.evaluate('''() => {
                            const labels = document.querySelectorAll('label');
                            for (let label of labels) {
                                if (label.textContent && label.textContent.includes('建议通过')) {
                                    const radioId = label.getAttribute('for');
                                    if (radioId) {
                                        const radio = document.getElementById(radioId);
                                        if (radio && radio.type === 'radio') {
                                            radio.click();
                                            return true;
                                        }
                                    }
                                    // 尝试查找label旁边的radio
                                    const prevSibling = label.previousElementSibling;
                                    if (prevSibling && prevSibling.type === 'radio') {
                                        prevSibling.click();
                                        return true;
                                    }
                                }
                            }
                            return false;
                        }''')
                        if result:
                            print("  ✅ 已选择审批意见：建议通过")
                        else:
                            # 方法2: 尝试通过span或其他元素查找
                            result = page.evaluate('''() => {
                                const spans = document.querySelectorAll('span');
                                for (let span of spans) {
                                    if (span.textContent && span.textContent.includes('建议通过')) {
                                        // 查找父元素中的radio
                                        let parent = span.parentElement;
                                        while (parent) {
                                            const radio = parent.querySelector('input[type="radio"]');
                                            if (radio) {
                                                radio.click();
                                                return true;
                                            }
                                            parent = parent.parentElement;
                                        }
                                    }
                                }
                                return false;
                            }''')
                            if result:
                                print("  ✅ 已选择审批意见：建议通过")
                            else:
                                # 方法3: 查找所有radio并检查value或nextSibling
                                result = page.evaluate('''() => {
                                    const radios = document.querySelectorAll('input[type="radio"]');
                                    for (let radio of radios) {
                                        if (radio.value && (radio.value.includes('通过') || radio.value.includes('approve'))) {
                                            radio.click();
                                            return true;
                                        }
                                        const nextSibling = radio.nextSibling;
                                        if (nextSibling && nextSibling.textContent && nextSibling.textContent.includes('建议通过')) {
                                            radio.click();
                                            return true;
                                        }
                                    }
                                    return false;
                                }''')
                                if result:
                                    print("  ✅ 已选择审批意见：建议通过")
                                else:
                                    print("  ⚠️ 未找到建议通过单选按钮")
                    except Exception as e:
                        print(f"  ⚠️ 选择审批意见失败: {e}")
                    
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
                        
                        # 先滚动到页面底部
                        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                        page.wait_for_timeout(WAIT_TIME_SHORT)
                        
                        # 方法1: 尝试通过JavaScript查找并点击"提交复核"按钮
                        result = page.evaluate('''() => {
                            // 查找所有按钮和可点击元素
                            const clickableElements = document.querySelectorAll('button, input[type="button"], input[type="submit"], a, span[onclick], div[onclick], [role="button"]');
                            for (let el of clickableElements) {
                                const text = el.textContent || el.value || el.innerText || el.title || '';
                                if (text.includes('提交复核')) {
                                    el.click();
                                    return text;
                                }
                            }
                            return false;
                        }''')
                        if result:
                            print(f"  ✅ 已点击按钮: {result}")
                            clicked = True
                        
                        # 方法2: 尝试通过Playwright locator查找
                        if not clicked:
                            try:
                                submit_btn = page.locator('text=提交复核')
                                if submit_btn.count() > 0:
                                    submit_btn.first.click(timeout=3000)
                                    print("  ✅ 已点击提交复核按钮")
                                    clicked = True
                            except:
                                pass
                        
                        # 方法3: 尝试查找包含"提交"的按钮（排除其他按钮）
                        if not clicked:
                            result = page.evaluate('''() => {
                                const buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"], a');
                                for (let btn of buttons) {
                                    const text = btn.textContent || btn.value || '';
                                    // 只查找包含"提交"但不包含"更新"的按钮
                                    if (text.includes('提交') && !text.includes('更新') && !text.includes('备注')) {
                                        btn.click();
                                        return text;
                                    }
                                }
                                return false;
                            }''')
                            if result:
                                print(f"  ✅ 已点击按钮: {result}")
                                clicked = True
                        
                        # 方法4: 尝试查找页面底部的按钮
                        if not clicked:
                            result = page.evaluate('''() => {
                                // 查找页面底部区域的按钮
                                const bottomButtons = document.querySelectorAll('.footer button, .bottom button, .action-bar button, [class*="footer"] button, [class*="bottom"] button');
                                for (let btn of bottomButtons) {
                                    btn.click();
                                    return btn.textContent || btn.value || '底部按钮';
                                }
                                return false;
                            }''')
                            if result:
                                print(f"  ✅ 已点击底部按钮: {result}")
                                clicked = True
                        
                        if not clicked:
                            print("  ⚠️ 未找到提交复核按钮")
                        else:
                            page.wait_for_load_state('networkidle', timeout=15000)
                            page.wait_for_timeout(WAIT_TIME_NORMAL)
                            print(f"  提交复核后页面标题: {page.title()}")
                    
                    except Exception as e:
                        print(f"  ⚠️ 点击提交复核按钮失败: {e}")
                    
                    # 步骤14.5: 勾选弹窗中的复选框（提交复核后出现的弹窗）
                    print("\n步骤14.5: 勾选弹窗中的复选框")
                    try:
                        # 等待弹窗出现
                        page.wait_for_timeout(2000)
                        
                        result = page.evaluate('''() => {
                            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                            let count = 0;
                            for (let cb of checkboxes) {
                                cb.checked = true;
                                cb.dispatchEvent(new Event('change'));
                                count++;
                            }
                            return count;
                        }''')
                        print(f"  ✅ 已勾选 {result} 个复选框")
                    except Exception as e:
                        print(f"  ⚠️ 勾选复选框失败: {e}")
                    
                    # 步骤15: 检测弹窗并点击提交按钮
                    print("\n步骤15: 检测弹窗并点击提交按钮")
                    try:
                        popup_found = False
                        submit_success = False
                        
                        # 等待弹窗出现（最多等待5秒）
                        page.wait_for_timeout(3000)
                        
                        # 方法1: 检测是否存在弹窗（增强版）
                        popup_exists = page.evaluate('''() => {
                            // 检测常见弹窗特征
                            const selectors = [
                                '.modal', '.popup', '.dialog', '[role="dialog"]',
                                '.modal-dialog', '.ant-modal', '.el-dialog',
                                '.ui-dialog', '.modal-content', '.popup-content'
                            ];
                            
                            for (let selector of selectors) {
                                const elements = document.querySelectorAll(selector);
                                for (let el of elements) {
                                    if (el.style.display !== 'none' && el.offsetParent !== null) {
                                        return true;
                                    }
                                }
                            }
                            
                            // 检测有确认标题的弹窗
                            const titles = document.querySelectorAll('h1, h2, h3, .modal-title, .popup-title');
                            for (let title of titles) {
                                if (title.textContent && title.textContent.includes('确认')) {
                                    const parent = title.parentElement;
                                    if (parent && parent.classList) {
                                        return true;
                                    }
                                }
                            }
                            
                            // 检测遮罩层
                            const overlays = document.querySelectorAll('.modal-backdrop, .modal-mask, .mask, .overlay');
                            for (let overlay of overlays) {
                                if (overlay.style.display !== 'none' && overlay.offsetParent !== null) {
                                    return true;
                                }
                            }
                            
                            return false;
                        }''')
                        
                        if popup_exists:
                            popup_found = True
                            print("  ✅ 检测到弹窗存在")
                            
                            # 尝试点击弹窗中的提交按钮
                            result = page.evaluate('''() => {
                                const selectors = [
                                    '.modal', '.popup', '.dialog', '[role="dialog"]',
                                    '.modal-dialog', '.ant-modal', '.el-dialog',
                                    '.ui-dialog', '.modal-content', '.popup-content'
                                ];
                                
                                for (let selector of selectors) {
                                    const popups = document.querySelectorAll(selector);
                                    for (let popup of popups) {
                                        if (popup.style.display !== 'none' && popup.offsetParent !== null) {
                                            // 在弹窗内查找提交按钮
                                            const buttons = popup.querySelectorAll('button, input[type="button"], input[type="submit"]');
                                            for (let btn of buttons) {
                                                const text = btn.textContent || btn.value || '';
                                                if (text.includes('提交')) {
                                                    btn.click();
                                                    return true;
                                                }
                                            }
                                            // 尝试查找链接形式的提交
                                            const links = popup.querySelectorAll('a');
                                            for (let link of links) {
                                                const text = link.textContent || '';
                                                if (text.includes('提交')) {
                                                    link.click();
                                                    return true;
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                // 如果以上都没找到，直接查找页面上的提交按钮（可能弹窗没有特殊class）
                                const allButtons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                                for (let btn of allButtons) {
                                    const text = btn.textContent || btn.value || '';
                                    if (text.includes('提交')) {
                                        btn.click();
                                        return true;
                                    }
                                }
                                
                                return false;
                            }''')
                            
                            if result:
                                submit_success = True
                                print("  ✅ 已点击弹窗中的提交按钮")
                                page.wait_for_load_state('networkidle', timeout=15000)
                                page.wait_for_timeout(WAIT_TIME_NORMAL)
                            else:
                                print("  ⚠️ 弹窗存在，但未找到提交按钮")
                        else:
                            print("  ❌ 未检测到弹窗，报错")
                    
                    except Exception as e:
                        print(f"  ❌ 步骤15执行异常: {e}")
                    
                    # 步骤16: 检测确认弹窗并点击确定按钮
                    print("\n步骤16: 检测确认弹窗并点击确定按钮")
                    try:
                        confirm_popup_found = False
                        confirm_success = False
                        
                        # 等待确认弹窗出现（最多等待5秒）
                        page.wait_for_timeout(3000)
                        
                        # 检测是否存在确认弹窗（增强版）
                        confirm_exists = page.evaluate('''() => {
                            // 方法1: 检测包含确认标题的弹窗
                            const titles = document.querySelectorAll('h1, h2, h3, .modal-title, .title, [class*="title"]');
                            for (let title of titles) {
                                if (title.textContent && title.textContent.includes('确认')) {
                                    return true;
                                }
                            }
                            
                            // 方法2: 检测红色按钮（通常是提交/确定按钮）
                            const buttons = document.querySelectorAll('button');
                            for (let btn of buttons) {
                                const text = btn.textContent || '';
                                if (text.includes('确定')) {
                                    // 检查按钮样式是否为红色
                                    const style = window.getComputedStyle(btn);
                                    const bgColor = style.backgroundColor || style.background;
                                    if (bgColor && bgColor.includes('red')) {
                                        return true;
                                    }
                                    // 检查class是否包含红色相关
                                    if (btn.className && (btn.className.includes('red') || btn.className.includes('primary'))) {
                                        return true;
                                    }
                                }
                            }
                            
                            // 方法3: 检测包含"确认提交复核"文本的元素
                            const allElements = document.querySelectorAll('*');
                            for (let el of allElements) {
                                const text = el.textContent || '';
                                if (text.includes('确认提交复核')) {
                                    return true;
                                }
                            }
                            
                            return false;
                        }''')
                        
                        if confirm_exists:
                            confirm_popup_found = True
                            print("  ✅ 检测到确认弹窗存在")
                            
                            # 尝试点击确定按钮（优先找红色按钮）
                            result = page.evaluate('''() => {
                                // 方法1: 直接查找所有按钮并点击包含"确定"的
                                const allButtons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                                for (let btn of allButtons) {
                                    const text = btn.textContent || btn.value || '';
                                    if (text.includes('确定')) {
                                        btn.click();
                                        return true;
                                    }
                                }
                                
                                // 方法2: 查找所有元素中包含"确定"的按钮
                                const allElements = document.querySelectorAll('*');
                                for (let el of allElements) {
                                    if (el.tagName === 'BUTTON' || el.tagName === 'INPUT') {
                                        const text = el.textContent || el.value || '';
                                        if (text.includes('确定')) {
                                            el.click();
                                            return true;
                                        }
                                    }
                                }
                                
                                // 方法3: 查找红色按钮
                                const buttons = document.querySelectorAll('button');
                                for (let btn of buttons) {
                                    const style = window.getComputedStyle(btn);
                                    const bgColor = style.backgroundColor || style.background;
                                    if (bgColor && (bgColor.includes('255,') || bgColor.includes('red'))) {
                                        btn.click();
                                        return true;
                                    }
                                }
                                
                                return false;
                            }''')
                            
                            if result:
                                confirm_success = True
                                print("  ✅ 已点击确定按钮")
                                page.wait_for_load_state('networkidle', timeout=15000)
                                page.wait_for_timeout(WAIT_TIME_NORMAL)
                            else:
                                print("  ⚠️ 确认弹窗存在，但未找到确定按钮")
                        else:
                            print("  ❌ 未检测到确认弹窗，报错")
                    
                    except Exception as e:
                        print(f"  ❌ 步骤16执行异常: {e}")
                
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
    try:
        result = login_guardian()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ 执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()