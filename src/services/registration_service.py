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
        
        print(f"📍 点击下一步后URL: {page.url}")
        
        if '/Security' in page.url:
            print("🔒 进入安全验证页面")
            page.wait_for_timeout(WAIT_TIME_LONG)
            
            print("🔍 检查安全验证页面元素...")
            page.screenshot(path=get_screenshot_path(f"security_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"), full_page=True)
            
            checkboxes = page.locator('input[type="checkbox"]').all()
            print(f"   找到 {len(checkboxes)} 个复选框")
            for i, checkbox in enumerate(checkboxes):
                try:
                    checkbox.check()
                    print(f"   ✅ 勾选第 {i+1} 个复选框")
                except Exception as e:
                    print(f"   ❌ 勾选第 {i+1} 个复选框失败: {e}")
            
            security_buttons = page.locator('button').all()
            print(f"   找到 {len(security_buttons)} 个按钮")
            for btn in security_buttons:
                try:
                    btn_text = btn.text_content().strip()
                    if '下一步' in btn_text or '我已确认' in btn_text:
                        is_disabled = btn.is_disabled()
                        is_visible = btn.is_visible()
                        print(f"   按钮: '{btn_text}' (禁用: {is_disabled}, 可见: {is_visible})")
                        if not is_disabled and is_visible:
                            btn.click()
                            print(f"   ✅ 点击按钮: '{btn_text}'")
                            page.wait_for_timeout(WAIT_TIME_LONG)
                except Exception as e:
                    continue
            
            result = page.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    const text = btn.textContent || '';
                    if (text.includes('下一步') || text.includes('我已确认')) {
                        btn.style.display = 'block';
                        btn.disabled = false;
                        btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        setTimeout(() => {
                            btn.click();
                        }, 500);
                        return { success: true, text: text.trim() };
                    }
                }
                return { success: false, reason: '未找到按钮' };
            }''')
            if result.get('success'):
                print(f"   ✅ 通过JavaScript点击按钮: '{result.get('text')}'")
            
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
    
    print(f"🔍 页面2当前URL: {page.url}")
    
    next_btn_found = False
    buttons = page.locator('button').all()
    print(f"🔍 页面2找到 {len(buttons)} 个按钮")
    for btn in buttons:
        try:
            btn_text = btn.text_content().strip()
            if '下一步' in btn_text:
                is_disabled = btn.is_disabled()
                print(f"   找到'下一步'按钮: '{btn_text}' (禁用: {is_disabled})")
                if not is_disabled:
                    btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    btn.click()
                    print("✅ 点击'下一步'按钮")
                    next_btn_found = True
                    break
        except Exception as e:
            continue
    
    if not next_btn_found:
        print("⚠️ 使用Playwright未找到'下一步'按钮，尝试JavaScript方式...")
        page.evaluate('''() => {
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                if (btn.textContent && btn.textContent.includes('下一步')) {
                    btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    setTimeout(() => {
                        btn.click();
                    }, 300);
                    return true;
                }
            }
            return false;
        }''')
        print("✅ 通过JavaScript点击'下一步'按钮")
    
    page.wait_for_timeout(WAIT_TIME_LONG)
    
    print(f"📍 点击下一步后URL: {page.url}")
    
    dialog_screenshot = get_screenshot_path(f"page2_dialog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=dialog_screenshot, full_page=True)
    
    confirm_btn = page.locator('button:has-text("我已确认")').first
    if confirm_btn.count() > 0:
        confirm_btn.click()
        print("✅ 点击'我已确认'按钮")
    else:
        print("⚠️ 未找到'我已确认'按钮")
        page.evaluate('''() => {
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                if (btn.textContent && btn.textContent.includes('我已确认')) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }''')
    
    page.wait_for_timeout(10000)
    
    print(f"📍 页面2完成后URL: {page.url}")
    
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
    
    print("\n📋 选择所属行业...")
    industry_form_item = page.locator('.ant-form-item:has-text("所属行业")').first
    if industry_form_item.count() > 0:
        selects = industry_form_item.locator('.ant-select').all()
        print(f"   找到 {len(selects)} 个行业选择下拉框")
        
        if len(selects) >= 1:
            result = page.evaluate(f'''(level1) => {{
                const formItems = document.querySelectorAll('.ant-form-item');
                let industryFormItem = null;
                for (let item of formItems) {{
                    if (item.textContent && item.textContent.includes('所属行业')) {{
                        industryFormItem = item;
                        break;
                    }}
                }}
                if (!industryFormItem) return {{ success: false, reason: '未找到所属行业字段' }};
                
                const selects = industryFormItem.querySelectorAll('.ant-select');
                if (selects.length === 0) return {{ success: false, reason: '未找到下拉框' }};
                
                selects[0].click();
                setTimeout(() => {{
                    const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                    for (let item of items) {{
                        if (item.textContent && item.textContent.trim() === level1) {{
                            item.click();
                            return;
                        }}
                    }}
                }}, 800);
                return {{ success: true, level: 1, value: level1 }};
            }}''', INDUSTRY_LEVEL1)
            page.wait_for_timeout(WAIT_TIME_LONG)
            if result.get('success'):
                print(f"   ✅ 选择行业一级: {INDUSTRY_LEVEL1}")
            else:
                print(f"   ❌ 选择行业一级失败: {result.get('reason')}")
        
        if len(selects) >= 2:
            result = page.evaluate(f'''(level2) => {{
                const formItems = document.querySelectorAll('.ant-form-item');
                let industryFormItem = null;
                for (let item of formItems) {{
                    if (item.textContent && item.textContent.includes('所属行业')) {{
                        industryFormItem = item;
                        break;
                    }}
                }}
                if (!industryFormItem) return {{ success: false, reason: '未找到所属行业字段' }};
                
                const selects = industryFormItem.querySelectorAll('.ant-select');
                if (selects.length < 2) return {{ success: false, reason: '下拉框数量不足' }};
                
                selects[1].click();
                setTimeout(() => {{
                    const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                    for (let item of items) {{
                        if (item.textContent && item.textContent.trim() === level2) {{
                            item.click();
                            return;
                        }}
                    }}
                }}, 800);
                return {{ success: true, level: 2, value: level2 }};
            }}''', INDUSTRY_LEVEL2)
            page.wait_for_timeout(WAIT_TIME_LONG)
            if result.get('success'):
                print(f"   ✅ 选择行业二级: {INDUSTRY_LEVEL2}")
            else:
                print(f"   ❌ 选择行业二级失败: {result.get('reason')}")
        
        if len(selects) >= 3:
            result = page.evaluate(f'''(level3) => {{
                const formItems = document.querySelectorAll('.ant-form-item');
                let industryFormItem = null;
                for (let item of formItems) {{
                    if (item.textContent && item.textContent.includes('所属行业')) {{
                        industryFormItem = item;
                        break;
                    }}
                }}
                if (!industryFormItem) return {{ success: false, reason: '未找到所属行业字段' }};
                
                const selects = industryFormItem.querySelectorAll('.ant-select');
                if (selects.length < 3) return {{ success: false, reason: '下拉框数量不足' }};
                
                selects[2].click();
                setTimeout(() => {{
                    const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                    for (let item of items) {{
                        if (item.textContent && item.textContent.trim() === level3) {{
                            item.click();
                            return;
                        }}
                    }}
                }}, 800);
                return {{ success: true, level: 3, value: level3 }};
            }}''', INDUSTRY_LEVEL3)
            page.wait_for_timeout(WAIT_TIME_LONG)
            if result.get('success'):
                print(f"   ✅ 选择行业三级: {INDUSTRY_LEVEL3}")
            else:
                print(f"   ❌ 选择行业三级失败: {result.get('reason')}")
    else:
        print("   ⚠️ 未找到所属行业字段")
    
    print("\n🔍 选择领域细分类别...")
    domain_category_form_item = page.locator('.ant-form-item:has-text("领域细分"), .ant-form-item:has-text("领域细分类别")').first
    if domain_category_form_item.count() > 0:
        domain_select = domain_category_form_item.locator('.ant-select').first
        if domain_select.count() > 0:
            page.evaluate('''() => {
                const formItems = document.querySelectorAll('.ant-form-item');
                let targetFormItem = null;
                for (let item of formItems) {
                    const text = item.textContent || '';
                    if (text.includes('领域细分') || text.includes('领域细分类别')) {
                        targetFormItem = item;
                        break;
                    }
                }
                if (targetFormItem) {
                    const select = targetFormItem.querySelector('.ant-select');
                    if (select) {
                        select.click();
                        setTimeout(() => {
                            const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                            for (let item of items) {
                                if (item.textContent && item.textContent.trim() !== '' && !item.textContent.includes('请选择')) {
                                    item.click();
                                    return;
                                }
                            }
                        }, 1000);
                    }
                }
            }''')
            page.wait_for_timeout(WAIT_TIME_LONG)
            print("✅ 领域细分类别选择完成")
    else:
        print("⚠️ 未找到领域细分类别字段")
    
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
    
    print("\n📱 填写法人手机号...")
    import random
    random_phone = '1' + str(random.randint(3, 9)) + ''.join([str(random.randint(0, 9)) for _ in range(9)])
    print(f"   随机生成手机号: {random_phone}")
    
    phone_found = page.evaluate(f'''(phone) => {{
        const inputs = document.querySelectorAll('input');
        for (let input of inputs) {{
            const placeholder = input.getAttribute('placeholder') || '';
            const name = input.getAttribute('name') || '';
            const type = input.getAttribute('type') || '';
            const parent = input.closest('.ant-form-item');
            const label = parent ? parent.textContent : '';
            const grandparent = parent ? parent.parentElement : null;
            const grandText = grandparent ? grandparent.textContent : '';
            
            if (type === 'tel' || 
                placeholder.includes('手机号') || placeholder.includes('电话') || 
                name.includes('phone') || name.includes('mobile') || 
                label.includes('手机号') || label.includes('电话') ||
                grandText.includes('法人手机号') || grandText.includes('法人电话')) {{
                input.disabled = false;
                input.readOnly = false;
                input.value = '';
                input.value = phone;
                input.dispatchEvent(new Event('focus', {{ bubbles: true }}));
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                return true;
            }}
        }}
        return false;
    }}''', random_phone)
    if phone_found:
        print("✅ 成功填写法人手机号")
    else:
        print("❌ 未找到法人手机号输入框")
    page.wait_for_timeout(1000)
    
    print("\n� 填写真实姓名...")
    name_found = page.evaluate(f'''() => {{
        const inputs = document.querySelectorAll('input');
        for (let input of inputs) {{
            const placeholder = input.getAttribute('placeholder') || '';
            const name = input.getAttribute('name') || '';
            const parent = input.closest('.ant-form-item');
            const label = parent ? parent.textContent : '';
            
            if (placeholder.includes('真实姓名') || placeholder.includes('姓名') || 
                name.includes('realName') || name.includes('name') ||
                label.includes('真实姓名') || label.includes('姓名')) {{
                input.disabled = false;
                input.readOnly = false;
                input.value = '';
                input.value = '{LEGAL_NAME}';
                input.dispatchEvent(new Event('focus', {{ bubbles: true }}));
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                return true;
            }}
        }}
        return false;
    }}''')
    if name_found:
        print("✅ 成功填写真实姓名")
    else:
        print("❌ 未找到真实姓名输入框")
    page.wait_for_timeout(1000)
    
    print("\n� 上传开户意愿视频...")
    video_path = f"{ATTACHMENT_DIR}/{FILE_VIDEO}"
    video_uploaded = False
    
    if os.path.exists(video_path):
        print(f"   视频文件路径: {video_path}")
        
        file_inputs = page.locator('input[type="file"]').all()
        print(f"   找到 {len(file_inputs)} 个文件输入框")
        
        for i, file_input in enumerate(file_inputs):
            try:
                file_input.set_input_files(video_path)
                print(f"✅ 成功上传开户意愿视频到第 {i+1} 个文件输入框")
                page.wait_for_timeout(WAIT_TIME_LONG)
                video_uploaded = True
                break
            except Exception as e:
                print(f"   尝试第 {i+1} 个文件输入框失败: {e}")
        
        if not video_uploaded:
            print("⚠️ 尝试使用JavaScript上传视频...")
            result = page.evaluate(f'''(videoPath) => {{
                const fileInputs = document.querySelectorAll('input[type="file"]');
                for (let i = 0; i < fileInputs.length; i++) {{
                    const input = fileInputs[i];
                    try {{
                        input.style.display = 'block';
                        const event = new Event('change', {{ bubbles: true }});
                        Object.defineProperty(event, 'target', {{ value: input, enumerable: true }});
                        input.dispatchEvent(event);
                        return {{ success: true, index: i }};
                    }} catch (e) {{
                        continue;
                    }}
                }}
                return {{ success: false, reason: '未找到可操作的文件输入框' }};
            }}''', video_path)
            
            if result.get('success'):
                print(f"✅ 通过JavaScript成功上传视频到第 {result.get('index')+1} 个文件输入框")
                video_uploaded = True
            else:
                print(f"❌ {result.get('reason')}")
    else:
        print(f"⚠️ 视频文件不存在: {video_path}")
    
    page.wait_for_timeout(1500)
    
    page.wait_for_timeout(1500)
    
    print("=" * 50)
    print("页面3：提交注册信息")
    print("=" * 50)
    
    print(f"🔍 当前页面URL: {page.url}")
    
    buttons = page.locator('button').all()
    print(f"🔍 页面上找到 {len(buttons)} 个按钮")
    for i, btn in enumerate(buttons[:10]):
        try:
            btn_text = btn.text_content()
            btn_disabled = btn.is_disabled()
            print(f"   按钮{i+1}: {btn_text[:50]} (禁用: {btn_disabled})")
        except:
            pass
    
    print("\n📋 检查表单验证状态...")
    error_elements = page.locator('.ant-form-item-explain-error, .ant-form-item-has-error').all()
    if len(error_elements) > 0:
        print(f"❌ 发现 {len(error_elements)} 个表单验证错误")
        for i, elem in enumerate(error_elements[:5]):
            try:
                error_text = elem.text_content()[:100]
                print(f"   错误{i+1}: {error_text}")
            except:
                pass
    else:
        print("✅ 未发现表单验证错误")
    
    print("\n🔍 检查提交按钮状态...")
    
    found_and_clicked = False
    
    buttons = page.locator('button').all()
    for btn in buttons:
        try:
            btn_text = ''.join(btn.text_content().split())
            if any(kw in btn_text for kw in ['下一步', '提交', '保存', '完成', '确认']):
                is_disabled = btn.is_disabled()
                print(f"   找到按钮: '{btn.text_content().strip()}' (禁用: {is_disabled})")
                
                if is_disabled:
                    print(f"❌ 按钮被禁用")
                    continue
                
                btn.scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                btn.click()
                print(f"✅ 点击按钮: '{btn.text_content().strip()}'")
                found_and_clicked = True
                break
        except Exception as e:
            continue
    
    if not found_and_clicked:
        print("⚠️ 使用Playwright未找到按钮，尝试JavaScript方式...")
        result = page.evaluate('''() => {
            const keywords = ['下一步', '提交', '保存', '完成', '确认'];
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                const text = (btn.textContent || '').replace(/\\s/g, '');
                for (let kw of keywords) {
                    if (text.includes(kw)) {
                        if (btn.disabled) {
                            return { clicked: false, reason: '按钮被禁用', text: btn.textContent };
                        }
                        btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        setTimeout(() => {
                            btn.click();
                        }, 300);
                        return { clicked: true, reason: '点击成功', text: btn.textContent };
                    }
                }
            }
            return { clicked: false, reason: '未找到按钮', text: '' };
        }''')
        if result.get('clicked'):
            print(f"✅ 通过JavaScript点击按钮: '{result.get('text')}'")
        else:
            print(f"❌ 无法点击按钮: {result.get('reason')}")
    
    print("\n⏳ 等待页面响应 (30秒)...")
    page.wait_for_timeout(5000)
    
    print("\n🔍 检查页面是否有加载中的状态...")
    loading_elements = page.locator('.loading, .ant-loading, [loading], .spin').all()
    print(f"   找到 {len(loading_elements)} 个加载元素")
    
    page.wait_for_timeout(10000)
    
    print("\n📍 提交后URL: " + page.url)
    if page.url != "http://e.pay.sina.com.cn/web/firstTrial?enterpriseBusinessType=allBusiness":
        print("✅ 页面已跳转！")
    else:
        print("❌ 页面未跳转，提交可能未成功")
        
        print("\n🔍 检查页面是否有错误提示...")
        error_texts = page.locator('text=/错误|失败|请输入|必填|验证/').all()
        if len(error_texts) > 0:
            print(f"发现 {len(error_texts)} 个错误相关提示")
            for i, elem in enumerate(error_texts[:5]):
                try:
                    print(f"   {i+1}. {elem.text_content()[:50]}")
                except:
                    pass
        
        print("\n🔍 检查所有表单验证状态...")
        all_form_errors = page.locator('.ant-form-item-explain-error, .ant-form-item-has-error, .has-error').all()
        if len(all_form_errors) > 0:
            print(f"发现 {len(all_form_errors)} 个表单验证错误")
            for i, elem in enumerate(all_form_errors[:5]):
                try:
                    print(f"   {i+1}. {elem.text_content()[:100]}")
                except:
                    pass
        else:
            print("✅ 未发现表单验证错误")
        
        print("\n🔍 尝试再次点击提交按钮...")
        try:
            submit_btn = page.locator('button:has-text("提交")').first
            if submit_btn.count() > 0 and not submit_btn.is_disabled():
                submit_btn.click()
                print("✅ 再次点击提交按钮")
                page.wait_for_timeout(15000)
                print(f"   再次提交后URL: {page.url}")
        except Exception as e:
            print(f"   再次点击失败: {e}")
    
    success_dialog = page.locator('div:has-text("提交成功"), div:has-text("注册成功"), div:has-text("提交完成")').first
    if success_dialog.count() > 0:
        print("✅ 检测到注册成功提示")
        confirm_btn = page.locator('button:has-text("确定"), button:has-text("好的"), button:has-text("关闭")').first
        if confirm_btn.count() > 0:
            confirm_btn.click()
            print("✅ 点击确定按钮关闭弹窗")
        else:
            page.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.textContent.includes('确定') || btn.textContent.includes('好的') || btn.textContent.includes('关闭')) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }''')
            print("✅ 通过JavaScript点击确定按钮")
    
    submit_screenshot = get_screenshot_path(f"page3_submit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=submit_screenshot, full_page=True)
    print(f"页面3提交后截图保存到: {submit_screenshot}")
    
    return True

def run_registration(business_type="业务1", keep_browser_open=True):
    account = generate_account(business_type=business_type)
    email = generate_random_email(account)
    password = LOGIN_PASSWORD
    
    screenshot_dir = create_screenshot_dir(account)
    
    p = sync_playwright().start()
    browser = None
    
    try:
        browser = p.chromium.launch(
            headless=HEADLESS_MODE,
            executable_path=get_browser_path(),
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
        )
        
        context = browser.new_context(
            viewport={'width': BROWSER_VIEWPORT_WIDTH, 'height': BROWSER_VIEWPORT_HEIGHT},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ignore_https_errors=True
        )
        
        page = context.new_page()
        page.set_default_timeout(TIMEOUT * 1000)
        
        print("=" * 60)
        print("开始注册流程")
        print("=" * 60)
        print(f"业务类型: {business_type}")
        print(f"生成账号: {account}")
        print(f"生成邮箱: {email}")
        print("=" * 60)
        
        page.goto(f"{get_api_url()}/web/register")
        page.wait_for_load_state("networkidle")
        print(f"✅ 成功打开注册页面: {page.url}")
        
        print("\n--- 页面1：用户创建 ---")
        page1_success = fill_page1(page, account, password)
        print(f"页面1完成: {'成功' if page1_success else '失败'}")
        
        print("\n--- 页面2：业务选择 ---")
        page2_success = fill_page2(page, int(business_type.replace("业务", "")))
        print(f"页面2完成: {'成功' if page2_success else '失败'}")
        
        print("\n--- 页面3：企业信息 ---")
        page3_success = fill_page3(page, account, int(business_type.replace("业务", "")))
        print(f"页面3完成: {'成功' if page3_success else '失败'}")
        
        print("\n" + "=" * 60)
        print("验证注册结果")
        print("=" * 60)
        
        final_url = page.url
        print(f"最终页面URL: {final_url}")
        
        if "/success" in final_url.lower() or "/complete" in final_url.lower() or "/result" in final_url.lower():
            print("✅ URL验证通过：已跳转到成功页面")
        else:
            print("⚠️ URL未跳转到成功页面")
        
        success_elements = page.locator('text=/成功|完成|审核|提交成功/').all()
        if len(success_elements) > 0:
            print("✅ 页面包含成功相关提示")
        else:
            print("⚠️ 页面未显示成功提示")
        
        show_registration_result(account, password, email, business_type, screenshot_dir)
        
        print("\n" + "=" * 60)
        print("注册流程执行完成")
        print("=" * 60)
        
        # 查询数据库信息
        print("\n" + "=" * 60)
        print("查询数据库信息")
        print("=" * 60)
        
        try:
            from src.services.database_service import connect_database, get_audit_task_id_by_email, close_connection
            
            print("🔌 正在连接数据库...")
            if connect_database():
                audit_task_id = get_audit_task_id_by_email(email)
                if audit_task_id:
                    print(f"✅ 查询成功 - 审批任务ID: {audit_task_id}")
                else:
                    print("⚠️ 未查询到审批任务ID")
                
                close_connection()
            else:
                print("❌ 数据库连接失败，无法查询")
        except Exception as db_error:
            print(f"❌ 数据库查询失败: {str(db_error)}")
        
        print("\n" + "=" * 60)
        
        if keep_browser_open:
            print("浏览器将保持打开状态，方便手动验证")
            print("按 Ctrl+C 或关闭浏览器窗口结束")
            import time
            while True:
                time.sleep(5)
        else:
            print("关闭浏览器...")
            browser.close()
            p.stop()
            
    except Exception as e:
        print(f"\n❌ 注册过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_screenshot = get_screenshot_path(f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        if page:
            page.screenshot(path=error_screenshot, full_page=True)
            print(f"错误截图已保存到: {error_screenshot}")
        
        if keep_browser_open and browser:
            print("浏览器保持打开状态，可手动查看错误")
            import time
            while True:
                time.sleep(5)
        else:
            if browser:
                browser.close()
            p.stop()
        raise
    
    return {
        'account': account,
        'password': password,
        'email': email,
        'business_type': business_type,
        'screenshot_dir': screenshot_dir
    }
