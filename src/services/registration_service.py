#!/usr/bin/env python3
"""
注册服务模块
提供新浪支付会员注册的自动化流程
"""

import os
from datetime import datetime
from playwright.sync_api import sync_playwright

from src.config.business import *
from src.config.env import *
from src.utils.account_generator import generate_account, generate_random_email
from src.utils.screenshot_manager import create_screenshot_dir, get_screenshot_path

def show_registration_result(account, password, email, business_type, screenshot_dir):
    print("\n" + "=" * 60)
    print("新浪支付会员注册完成")
    print("=" * 60)
    print()
    print("┌" + "─" * 58 + "┐")
    print("│  注册信息概览")
    print("├" + "─" * 58 + "┤")
    print(f"│  登录账号:    {account}")
    print(f"│  登录密码:    {password}")
    print(f"│  注册邮箱:    {email}")
    print(f"│  业务类型:    {business_type}")
    print("└" + "─" * 58 + "┘")
    print()
    print("=" * 60)
    print("重要提示")
    print("=" * 60)
    print("  1. 请妥善保管您的登录账号和密码")
    print("  2. 登录密码为: " + password)
    print("  3. 注册邮箱用于接收重要通知和找回密码")
    print("  4. 邮箱验证码请查看: " + email)
    print("  5. 注册截图已保存至: " + screenshot_dir)
    print("=" * 60)
    print()
    print("注册流程已全部完成！")
    print()

def fill_page1(page, account, password):
    print("=" * 50)
    print("页面1：用户创建")
    print("=" * 50)
    
    page.wait_for_timeout(WAIT_TIME_MEDIUM)
    
    account_input = page.locator('input[placeholder*="登录账号"]').first
    account_input.fill(account)
    
    password_input = page.locator('#passwordEncrypt, input[placeholder*="请设置登录密码"]').first
    password_input.click()
    page.wait_for_timeout(500)
    password_input.type(LOGIN_PASSWORD, delay=50)
    
    confirm_input = page.locator('input[placeholder*="请再次确认密码"]').first
    confirm_input.click()
    page.wait_for_timeout(500)
    confirm_input.type(LOGIN_PASSWORD, delay=50)
    
    name_input = page.locator('input[placeholder*="经办人姓名"]').first
    if name_input.count() > 0:
        name_input.fill(OPERATOR_NAME)
    
    phone_input = page.locator('input[placeholder*="经办人手机号码"]').first
    if phone_input.count() > 0:
        phone_input.fill(OPERATOR_PHONE)
    
    sms_code_input = page.locator('input[placeholder*="短信验证码"]').first
    if sms_code_input.count() > 0:
        sms_code_input.fill(SMS_CODE)
    
    email_input = page.locator('input[placeholder*="经办人邮箱"]').first
    if email_input.count() > 0:
        email_input.fill(OPERATOR_EMAIL)
    
    email_code_inputs = page.locator('input[placeholder*="请输入验证码"], input[placeholder*="邮箱验证码"]').all()
    if len(email_code_inputs) >= 2:
        email_code_inputs[1].fill(EMAIL_CODE)
    elif len(email_code_inputs) == 1:
        email_code_inputs[0].fill(EMAIL_CODE)
    
    checkbox_wrapper = page.locator('.ant-checkbox-wrapper:has-text("我已经阅读并同意")').first
    if checkbox_wrapper.count() > 0:
        try:
            checkbox_wrapper.click()
        except Exception as e:
            page.evaluate('''() => {
                const checkbox = document.querySelector('input[type="checkbox"]');
                if (checkbox && !checkbox.checked) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }''')
    else:
        checkbox = page.locator('input[type="checkbox"]').first
        if checkbox.count() > 0:
            try:
                checkbox.check()
            except Exception as e:
                pass
    
    screenshot_path = get_screenshot_path(f"page1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"页面1截图保存到: {screenshot_path}")
    
    next_button = page.locator('button:has-text("下一步"), input[value="下一步"], a:has-text("下一步")').first
    if next_button.count() > 0:
        next_button.click()
        page.wait_for_timeout(WAIT_TIME_LONG)
        return True
    else:
        print("未找到下一步按钮")
        return False

def fill_page2(page, business_type=1):
    print("=" * 50)
    print("页面2：选择业务类型")
    print("=" * 50)
    
    page.wait_for_timeout(WAIT_TIME_MEDIUM)
    
    if business_type == 1:
        merchant_card = page.locator('text=新浪支付商户').first
        if merchant_card.count() > 0:
            merchant_card.click()
            page.wait_for_timeout(500)
        all_business = page.locator('text=综合业务').first
        if all_business.count() > 0:
            all_business.click()
            
    elif business_type == 2:
        merchant_card = page.locator('text=新浪支付商户').first
        if merchant_card.count() > 0:
            merchant_card.click()
            page.wait_for_timeout(1000)
        
        all_business = page.locator('text=综合业务').first
        if all_business.count() > 0:
            is_checked = page.evaluate('''() => {
                const checkbox = document.querySelector('input[type="checkbox"]:checked');
                return checkbox ? true : false;
            }''')
            if is_checked:
                all_business.click()
                page.wait_for_timeout(500)
        
        receive_business = page.locator('text=收款业务').first
        if receive_business.count() > 0:
            receive_business.click()
            page.wait_for_timeout(500)
            
    elif business_type == 3:
        partner_card = page.locator('text=商户的合作机构').first
        if partner_card.count() > 0:
            partner_card.click()
            page.wait_for_timeout(3000)
        
        page.evaluate('''() => {
            const wrappers = document.querySelectorAll('.ant-checkbox-wrapper');
            for (let wrapper of wrappers) {
                if (wrapper.textContent.includes('收款业务')) {
                    const input = wrapper.querySelector('input[type="checkbox"]');
                    const checkbox = wrapper.querySelector('.ant-checkbox');
                    if (input && checkbox && checkbox.classList.contains('ant-checkbox-checked')) {
                        input.style.display = 'block';
                        input.click();
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            }
        }''')
        page.wait_for_timeout(WAIT_TIME_MEDIUM)
        
        page.evaluate('''() => {
            const wrappers = document.querySelectorAll('.ant-checkbox-wrapper');
            for (let wrapper of wrappers) {
                if (wrapper.textContent.includes('综合业务')) {
                    const input = wrapper.querySelector('input[type="checkbox"]');
                    const checkbox = wrapper.querySelector('.ant-checkbox');
                    if (input && checkbox && !checkbox.classList.contains('ant-checkbox-checked')) {
                        input.style.display = 'block';
                        input.click();
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            }
        }''')
        page.wait_for_timeout(WAIT_TIME_MEDIUM)
        
        partner_name_input = page.locator('input[placeholder*="合作企业全称"]').first
        if partner_name_input.count() > 0:
            partner_name_input.fill(PARTNER_COMPANY_NAME)
        
        partner_merchant_input = page.locator('input[placeholder*="合作企业新浪支付商户号"]').first
        if partner_merchant_input.count() > 0:
            partner_merchant_input.fill(PARTNER_MERCHANT_ID)
            
    elif business_type == 4:
        partner_card = page.locator('text=商户的合作机构').first
        if partner_card.count() > 0:
            partner_card.click()
            page.wait_for_timeout(3000)
        
        partner_name_input = page.locator('input[placeholder*="合作企业全称"]').first
        if partner_name_input.count() > 0:
            partner_name_input.fill(PARTNER_COMPANY_NAME)
        
        partner_merchant_input = page.locator('input[placeholder*="合作企业新浪支付商户号"]').first
        if partner_merchant_input.count() > 0:
            partner_merchant_input.fill(PARTNER_MERCHANT_ID)
    
    page.wait_for_timeout(WAIT_TIME_SHORT)
    
    screenshot_path = get_screenshot_path(f"page2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    
    page.evaluate('''() => {
        const buttons = document.querySelectorAll('button');
        for (let btn of buttons) {
            if (btn.textContent.includes('下一步')) {
                btn.click();
                return true;
            }
        }
        return false;
    }''')
    page.wait_for_timeout(WAIT_TIME_LONG)
    
    dialog_screenshot = get_screenshot_path(f"page2_dialog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=dialog_screenshot, full_page=True)
    
    confirm_btn = page.locator('button:has-text("我已确认")').first
    if confirm_btn.count() > 0:
        confirm_btn.click()
    else:
        page.evaluate('''() => {
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                if (btn.textContent.includes('我已确认')) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }''')
    
    page.wait_for_timeout(10000)
    return True

def fill_page3(page, account, business_type=1):
    print("=" * 50)
    print("页面3：企业信息")
    print("=" * 50)
    
    page.wait_for_timeout(5000)
    current_url = page.url
    
    is_partner_page = business_type in [3, 4]
    
    license_path = f"{ATTACHMENT_DIR}/{FILE_BUSINESS_LICENSE}"
    if os.path.exists(license_path):
        file_input = page.locator('input[type="file"]').first
        if file_input.count() > 0:
            file_input.set_input_files(license_path)
            page.wait_for_timeout(WAIT_TIME_MEDIUM)
    
    company_name_input = page.locator('input[placeholder*="企业名称"], input[name*="companyName"]').first
    if company_name_input.count() > 0:
        company_name_input.fill(COMPANY_NAME_PREFIX)
    
    company_short_input = page.locator('input[placeholder*="企业简称"], input[name*="companyShortName"]').first
    if company_short_input.count() > 0:
        company_short_input.fill(COMPANY_SHORT_NAME_PREFIX)
    
    credit_code_input = page.locator('input[placeholder*="统一社会信用代码"], input[name*="creditCode"]').first
    if credit_code_input.count() > 0:
        credit_code_input.fill(CREDIT_CODE)
    
    industry_form_item = page.locator('.ant-form-item:has-text("所属行业")').first
    if industry_form_item.count() > 0:
        selects = industry_form_item.locator('.ant-select').all()
        if len(selects) >= 3:
            selects[0].click()
            page.wait_for_timeout(WAIT_TIME_MEDIUM)
            page.evaluate(f'''() => {{
                const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                for (let item of items) {{
                    if (item.textContent.trim() === '{INDUSTRY_LEVEL1}') {{
                        item.click();
                        return true;
                    }}
                }}
            }}''')
            page.wait_for_timeout(WAIT_TIME_LONG)
            
            selects[1].click()
            page.wait_for_timeout(WAIT_TIME_MEDIUM)
            page.evaluate(f'''() => {{
                const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                for (let item of items) {{
                    if (item.textContent.trim() === '{INDUSTRY_LEVEL2}') {{
                        item.click();
                        return true;
                    }}
                }}
            }}''')
            page.wait_for_timeout(WAIT_TIME_LONG)
            
            selects[2].click()
            page.wait_for_timeout(WAIT_TIME_LONG)
            page.evaluate(f'''() => {{
                const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                for (let item of items) {{
                    if (item.textContent.trim() === '{INDUSTRY_LEVEL3}') {{
                        item.click();
                        return true;
                    }}
                }}
            }}''')
            page.wait_for_timeout(WAIT_TIME_MEDIUM)
    
    if is_partner_page:
        agreement_file1 = f"{ATTACHMENT_DIR}/{FILE_COOPERATION_AGREEMENT_ZIP}"
        if os.path.exists(agreement_file1):
            file_inputs = page.locator('input[type="file"]').all()
            if len(file_inputs) >= 2:
                try:
                    file_inputs[1].set_input_files(agreement_file1)
                    page.wait_for_timeout(WAIT_TIME_LONG)
                except Exception as e:
                    pass
        
        agreement_file2 = f"{ATTACHMENT_DIR}/{FILE_COOPERATION_AGREEMENT_PDF}"
        if os.path.exists(agreement_file2):
            file_inputs = page.locator('input[type="file"]').all()
            if len(file_inputs) >= 3:
                try:
                    file_inputs[2].set_input_files(agreement_file2)
                    page.wait_for_timeout(WAIT_TIME_LONG)
                except Exception as e:
                    pass
        
        bank_account_name = page.locator('input[placeholder*="银行户名"], input[name*="bankAccountName"]').first
        if bank_account_name.count() > 0:
            bank_account_name.fill(BANK_ACCOUNT_NAME)
        
        bank_select = page.locator('.ant-form-item:has-text("开户银行") .ant-select').first
        if bank_select.count() > 0:
            bank_select.click()
            page.wait_for_timeout(2500)
            page.evaluate(f'''() => {{
                const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                for (let item of items) {{
                    if (item.textContent.includes('{BANK_NAME}')) {{
                        item.click();
                        return true;
                    }}
                }}
            }}''')
            page.wait_for_timeout(1500)
        
        bank_account = page.locator('input[placeholder*="企业银行账号"], input[name*="bankAccount"]').first
        if bank_account.count() > 0:
            bank_account.fill(BANK_ACCOUNT_NUMBER)
    else:
        product_select = page.locator('.ant-form-item:has(.ant-form-item-label:has-text("公司官网或产品")) .ant-select').first
        if product_select.count() > 0:
            product_select.click()
            page.wait_for_timeout(1500)
            
            app_option = page.locator('.ant-select-dropdown-menu-item:has-text("APP"), .ant-select-item:has-text("APP")').first
            if app_option.count() > 0:
                app_option.click()
                page.wait_for_timeout(1500)
        
        app_name_input = page.locator('.ant-form-item:has(.ant-form-item-label:has-text("公司官网或产品")) input[placeholder*="APP"]').first
        if app_name_input.count() > 0:
            app_name_input.fill(APP_NAME)
    
    page.evaluate(f'''() => {{
        const formItems = document.querySelectorAll('.ant-form-item');
        for (let item of formItems) {{
            if (item.textContent.includes('证件类型')) {{
                const select = item.querySelector('.ant-select');
                if (select) {{
                    select.click();
                    setTimeout(() => {{
                        const options = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                        for (let opt of options) {{
                            if (opt.textContent.includes('{LEGAL_ID_TYPE}')) {{
                                opt.click();
                            }}
                        }}
                    }}, 500);
                }}
            }}
        }}
    }}''')
    page.wait_for_timeout(WAIT_TIME_LONG)
    
    id_config = ID_CARD_TYPE_CONFIG.get(LEGAL_ID_TYPE, ID_CARD_TYPE_CONFIG["身份证"])
    
    if id_config["need_front"]:
        id_front_file = id_config["front_file"]
        id_front_path = f"{ATTACHMENT_DIR}/{id_front_file}"
        if os.path.exists(id_front_path):
            file_inputs = page.locator('input[type="file"]').all()
            id_front_index = 4 if is_partner_page else 1
            if len(file_inputs) > id_front_index:
                try:
                    file_inputs[id_front_index].set_input_files(id_front_path)
                    page.wait_for_timeout(5000)
                except Exception as e:
                    pass
    
    if id_config["need_back"] and id_config["back_file"]:
        id_back_file = id_config["back_file"]
        id_back_path = f"{ATTACHMENT_DIR}/{id_back_file}"
        if os.path.exists(id_back_path):
            file_inputs = page.locator('input[type="file"]').all()
            id_back_index = 5 if is_partner_page else 2
            if len(file_inputs) > id_back_index:
                try:
                    file_inputs[id_back_index].set_input_files(id_back_path)
                    page.wait_for_timeout(WAIT_TIME_LONG)
                except Exception as e:
                    pass
    
    page.wait_for_timeout(WAIT_TIME_OCR)
    
    id_screenshot = get_screenshot_path(f"page3_id_uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=id_screenshot, full_page=True)
    
    # 勾选证件有效期长期
    print("勾选证件有效期长期...")
    
    # 先截图查看当前状态
    expiry_screenshot = get_screenshot_path(f"page3_expiry_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=expiry_screenshot, full_page=True)
    
    # 尝试多种方法勾选"长期"
    # 方法1: 使用Playwright点击
    try:
        long_term_checkbox = page.locator('.ant-checkbox-wrapper:has-text("长期")').first
        if long_term_checkbox.count() > 0:
            long_term_checkbox.click()
            print(" 已使用Playwright点击'长期'复选框")
            page.wait_for_timeout(1000)
    except Exception as e:
        print(f" Playwright点击失败: {e}")
    
    # 方法2: 使用JavaScript强制勾选
    js_result = page.evaluate('''() => {
        // 找到包含"长期"文字的复选框wrapper
        const wrappers = document.querySelectorAll('.ant-checkbox-wrapper');
        for (let wrapper of wrappers) {
            if (wrapper.textContent.includes('长期')) {
                const input = wrapper.querySelector('input[type="checkbox"]');
                const checkbox = wrapper.querySelector('.ant-checkbox');
                if (input && checkbox) {
                    // 移除禁用状态
                    input.disabled = false;
                    checkbox.classList.remove('ant-checkbox-disabled');
                    // 勾选
                    input.checked = true;
                    checkbox.classList.add('ant-checkbox-checked');
                    // 触发事件
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    input.dispatchEvent(new Event('click', { bubbles: true }));
                    return '已使用JavaScript勾选证件有效期长期';
                }
            }
        }
        return '未找到长期复选框';
    }''')
    print(f" {js_result}")
    
    page.wait_for_timeout(1500)
    
    expiry_after_screenshot = get_screenshot_path(f"page3_expiry_after_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=expiry_after_screenshot, full_page=True)
    
    page.evaluate(f'''() => {{
        const inputs = document.querySelectorAll('input');
        for (let input of inputs) {{
            const placeholder = input.getAttribute('placeholder') || '';
            const name = input.getAttribute('name') || '';
            if (placeholder.includes('法人姓名') || name.includes('legalName')) {{
                input.disabled = false;
                input.readOnly = false;
                input.value = '';
                input.value = '{LEGAL_NAME}';
                input.dispatchEvent(new Event('focus', {{ bubbles: true }}));
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
            }}
        }}
    }}''')
    page.wait_for_timeout(1500)
    
    page.evaluate(f'''() => {{
        const inputs = document.querySelectorAll('input');
        for (let input of inputs) {{
            const placeholder = input.getAttribute('placeholder') || '';
            const name = input.getAttribute('name') || '';
            const parent = input.closest('.ant-form-item');
            const label = parent ? parent.textContent : '';
            if (placeholder.includes('证件号码') || name.includes('idNumber') || label.includes('法人证件号码')) {{
                input.disabled = false;
                input.readOnly = false;
                input.value = '';
                input.value = '{LEGAL_ID_NUMBER}';
                input.dispatchEvent(new Event('focus', {{ bubbles: true }}));
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
            }}
        }}
    }}''')
    page.wait_for_timeout(1500)
    
    return True

def run_registration(business_type="业务1"):
    account = generate_account(business_type=business_type)
    email = generate_random_email(account)
    password = LOGIN_PASSWORD
    
    screenshot_dir = create_screenshot_dir(account)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS_MODE,
            executable_path=get_browser_path(),
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
        )
        
        context = browser.new_context(
            viewport={'width': BROWSER_VIEWPORT_WIDTH, 'height': BROWSER_VIEWPORT_HEIGHT},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        page.set_default_timeout(TIMEOUT * 1000)
        
        try:
            page.goto(f"{get_api_url()}/web/register")
            page.wait_for_load_state("networkidle")
            
            fill_page1(page, account, password)
            fill_page2(page, int(business_type.replace("业务", "")))
            fill_page3(page, account, int(business_type.replace("业务", "")))
            
            show_registration_result(account, password, email, business_type, screenshot_dir)
            
        except Exception as e:
            print(f"注册过程中发生错误: {str(e)}")
            error_screenshot = get_screenshot_path(f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            page.screenshot(path=error_screenshot, full_page=True)
            raise
        finally:
            browser.close()
    
    return {
        'account': account,
        'password': password,
        'email': email,
        'business_type': business_type,
        'screenshot_dir': screenshot_dir
    }
