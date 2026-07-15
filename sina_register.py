#!/usr/bin/env python3
"""
新浪支付会员注册自动化脚本
使用 Playwright 自动填写注册表单 - 完整三页面流程
"""

import random
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# 导入配置文件
import config

# 全局变量：当前用户的截图文件夹路径
CURRENT_SCREENSHOT_DIR = None


def generate_account(prefix="babweb", business_type="业务1", id_type="身份证"):
    """
    生成登录账号
    新命名规则:
    - 业务1 + 身份证: yw11
    - 业务1 + 护照: yw12
    - 业务1 + 港澳通行证: yw13
    - 业务1 + 居住证: yw14
    - 业务2 + 身份证: yw21
    - 业务2 + 护照: yw22
    - ...以此类推
    
    格式: prefix + yw + 业务数字 + 证件类型数字 + 年月日时分
    例如: babwebyw11202606142028 (业务1+身份证)
          babwebyw22202606142029 (业务2+护照)
    """
    # 提取业务数字
    business_num = business_type.replace("业务", "").strip()
    
    # 证件类型映射到数字
    ID_TYPE_NUMBER_MAP = {
        "身份证": "1",
        "护照": "2",
        "港澳居民来往内地通行证": "3",
        "港澳居民居住证": "4",
    }
    
    # 获取证件类型数字，默认为1（身份证）
    id_type_num = ID_TYPE_NUMBER_MAP.get(id_type, "1")
    
    # 获取当前时间，精确到分
    time_str = datetime.now().strftime("%Y%m%d%H%M")
    
    # 组合账号: prefix + yw + 业务数字 + 证件类型数字 + 时间
    return f"{prefix}yw{business_num}{id_type_num}{time_str}"


def create_screenshot_dir(account, business_type="业务1"):
    """
    创建用户专属的截图文件夹
    截图保存到当前项目目录下的 screenshots/业务类型/账号/ 目录下
    """
    global CURRENT_SCREENSHOT_DIR
    # 使用当前项目目录作为截图基础路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 截图保存到 screenshots/业务类型/账号/ 目录下
    screenshot_dir = os.path.join(base_dir, "screenshots", business_type, account)
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
        print(f"创建截图文件夹: {screenshot_dir}")
    CURRENT_SCREENSHOT_DIR = screenshot_dir
    return screenshot_dir


def get_screenshot_path(filename):
    """获取截图的完整路径"""
    global CURRENT_SCREENSHOT_DIR
    if CURRENT_SCREENSHOT_DIR is None:
        CURRENT_SCREENSHOT_DIR = "/Users/xl-shuke_1/Documents/trae_projects"
    return os.path.join(CURRENT_SCREENSHOT_DIR, filename)


def fill_page1(page, account, password, email=None):
    """填写页面1：用户创建"""
    print("=" * 50)
    print("页面1：用户创建")
    print("=" * 50)
    
    # 等待页面加载完成
    page.wait_for_timeout(2000)
    
    # 1. 填写登录账号
    print("填写登录账号...")
    account_input = page.locator('input[placeholder*="登录账号"]').first
    account_input.fill(account)
    
    # 2. 填写登录密码
    print("填写登录密码...")
    password_input = page.locator('#passwordEncrypt, input[placeholder*="请设置登录密码"]').first
    password_input.click()
    page.wait_for_timeout(500)
    password_input.type(config.LOGIN_PASSWORD, delay=50)
    
    # 3. 填写确认密码
    print("填写确认密码...")
    confirm_input = page.locator('input[placeholder*="请再次确认密码"]').first
    confirm_input.click()
    page.wait_for_timeout(500)
    confirm_input.type(config.LOGIN_PASSWORD, delay=50)
    
    # 4. 填写经办人信息
    print("填写经办人信息...")
    
    # 姓名
    name_input = page.locator('input[placeholder*="经办人姓名"]').first
    if name_input.count() > 0:
        name_input.fill(config.OPERATOR_NAME)
    
    # 手机号
    phone_input = page.locator('input[placeholder*="经办人手机号码"]').first
    if phone_input.count() > 0:
        phone_input.fill(config.OPERATOR_PHONE)
    
    # 短信验证码
    sms_code_input = page.locator('input[placeholder*="短信验证码"]').first
    if sms_code_input.count() > 0:
        sms_code_input.fill(config.SMS_CODE)
    
    # 邮箱
    email_input = page.locator('input[placeholder*="经办人邮箱"]').first
    if email_input.count() > 0:
        email_to_use = email or config.OPERATOR_EMAIL
        email_input.fill(email_to_use)
        print(f"  已填写经办人邮箱: {email_to_use}")
    
    # 邮箱验证码
    email_code_inputs = page.locator('input[placeholder*="请输入验证码"], input[placeholder*="邮箱验证码"]').all()
    print(f"找到 {len(email_code_inputs)} 个验证码输入框")
    if len(email_code_inputs) >= 2:
        email_code_inputs[1].fill(config.EMAIL_CODE)
    elif len(email_code_inputs) == 1:
        email_code_inputs[0].fill(config.EMAIL_CODE)
    
    # 5. 勾选协议复选框
    print("勾选协议复选框...")
    # 方法1: 尝试点击复选框的label/wrapper
    checkbox_wrapper = page.locator('.ant-checkbox-wrapper:has-text("我已经阅读并同意")').first
    if checkbox_wrapper.count() > 0:
        try:
            checkbox_wrapper.click()
            print("  已点击协议复选框wrapper")
        except Exception as e:
            print(f"  点击wrapper失败: {e}")
            # 方法2: 直接操作input
            checkbox = page.locator('input[type="checkbox"]').first
            if checkbox.count() > 0:
                page.evaluate('''() => {
                    const checkbox = document.querySelector('input[type="checkbox"]');
                    if (checkbox && !checkbox.checked) {
                        checkbox.checked = true;
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                        return '已勾选';
                    }
                    return '无需勾选或已勾选';
                }''')
    else:
        # 备选：直接找checkbox input
        checkbox = page.locator('input[type="checkbox"]').first
        if checkbox.count() > 0:
            try:
                checkbox.check()
                print("  已勾选协议复选框")
            except Exception as e:
                print(f"  勾选失败: {e}")
    
    # 截图保存
    screenshot_path = get_screenshot_path(f"page1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"页面1截图保存到: {screenshot_path}")
    
    # 6. 点击下一步
    print("点击下一步按钮...")
    next_button = page.locator('button:has-text("下一步"), input[value="下一步"], a:has-text("下一步")').first
    if next_button.count() > 0:
        next_button.click()
        page.wait_for_timeout(3000)
        
        # 验证页面是否跳转成功
        current_url = page.url
        print(f"  点击后URL: {current_url}")
        
        # 如果还在register页面，等待更长时间
        max_retries = 3
        retry_count = 0
        while "register" in current_url and retry_count < max_retries:
            print(f"  页面未跳转，等待... (尝试 {retry_count + 1}/{max_retries})")
            page.wait_for_timeout(3000)
            current_url = page.url
            retry_count += 1
        
        if "Security" in current_url or "firstTrial" in current_url:
            print("页面1完成，成功进入页面2")
            return True
        else:
            print(f"  警告：页面可能未正确跳转，当前URL: {current_url}")
            # 再尝试点击一次
            next_button = page.locator('button:has-text("下一步"), input[value="下一步"], a:has-text("下一步")').first
            if next_button.count() > 0:
                print("  再次点击下一步...")
                next_button.click()
                page.wait_for_timeout(5000)
            # 二次检查
            current_url = page.url
            if "Security" in current_url or "firstTrial" in current_url or "register" not in current_url:
                print("  重试后成功进入页面2")
                return True
            else:
                print(f"  错误：页面1无法跳转到页面2，当前URL: {current_url}")
                return False
    else:
        print("未找到下一步按钮")
        return False


def fill_page2(page, business_type=1):
    """填写页面2：选择业务类型
    business_type: 1=新浪支付商户-综合业务, 2=新浪支付商户-收款业务, 
                   3=新浪合作机构-综合业务, 4=新浪合作机构-收款业务
    """
    print("=" * 50)
    print("页面2：选择业务类型")
    print("=" * 50)
    
    # 等待页面加载
    page.wait_for_timeout(2000)
    
    print(f"选择业务类型: {business_type}")
    
    # 根据业务类型选择
    if business_type == 1:
        # 业务1：新浪支付商户 - 综合业务
        print("选择：新浪支付商户 - 综合业务")
        # 点击新浪支付商户
        merchant_card = page.locator('text=新浪支付商户').first
        if merchant_card.count() > 0:
            merchant_card.click()
            page.wait_for_timeout(500)
        # 勾选综合业务
        all_business = page.locator('text=综合业务').first
        if all_business.count() > 0:
            all_business.click()
            
    elif business_type == 2:
        # 业务2：新浪支付商户 - 收款业务
        print("选择：新浪支付商户 - 收款业务")
        merchant_card = page.locator('text=新浪支付商户').first
        if merchant_card.count() > 0:
            merchant_card.click()
            page.wait_for_timeout(1000)
        
        # 先取消"综合业务"的勾选（如果已勾选）
        print("  取消综合业务勾选...")
        all_business = page.locator('text=综合业务').first
        if all_business.count() > 0:
            # 检查是否已选中
            is_checked = page.evaluate('''() => {
                const checkbox = document.querySelector('input[type="checkbox"]:checked');
                return checkbox ? true : false;
            }''')
            if is_checked:
                all_business.click()
                page.wait_for_timeout(500)
        
        # 勾选收款业务
        print("  勾选收款业务...")
        receive_business = page.locator('text=收款业务').first
        if receive_business.count() > 0:
            receive_business.click()
            page.wait_for_timeout(500)
            
    elif business_type == 3:
        # 业务3：新浪合作机构 - 综合业务
        print("选择：新浪合作机构 - 综合业务")
        partner_card = page.locator('text=商户的合作机构').first
        if partner_card.count() > 0:
            partner_card.click()
            page.wait_for_timeout(3000)  # 增加等待时间，让复选框显示
        
        # 等待复选框出现（综合业务/收款业务）
        print("  等待复选框加载...")
        page.wait_for_timeout(2000)
        
        # 截图查看当前选择状态
        debug_screenshot = get_screenshot_path(f"page2_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        page.screenshot(path=debug_screenshot, full_page=True)
        print(f"  调试截图: {debug_screenshot}")
        
        # 商户的合作机构默认选中"收款业务"，需要先取消，再勾选"综合业务"
        
        # 第一步：取消"收款业务"的勾选
        print("  取消收款业务勾选...")
        try:
            receive_checkbox = page.get_by_role("checkbox", name="收款业务")
            if receive_checkbox.count() > 0:
                receive_checkbox.uncheck(timeout=10000)
                print("    已用 get_by_role 取消收款业务")
            else:
                print("    未找到收款业务checkbox role，尝试locator...")
                wrapper = page.locator(".ant-checkbox-wrapper").filter(has_text="收款业务").first
                if wrapper.count() > 0:
                    wrapper.click(timeout=5000)
                    print("    已用locator点击取消收款业务")
        except Exception as e:
            print(f"    取消收款业务失败: {e}")
        page.wait_for_timeout(1500)
        
        # 第二步：勾选"综合业务"
        print("  勾选综合业务...")
        try:
            all_checkbox = page.get_by_role("checkbox", name="综合业务")
            if all_checkbox.count() > 0:
                all_checkbox.check(timeout=10000)
                print("    已用 get_by_role 勾选综合业务")
            else:
                print("    未找到综合业务checkbox role，尝试locator...")
                wrapper = page.locator(".ant-checkbox-wrapper").filter(has_text="综合业务").first
                if wrapper.count() > 0:
                    wrapper.click(timeout=5000)
                    print("    已用locator点击勾选综合业务")
        except Exception as e:
            print(f"    勾选综合业务失败: {e}")
        page.wait_for_timeout(1500)
        
        # 第三步：再次验证，如果还没勾选上就重试
        print("  验证勾选结果...")
        all_business_wrapper2 = page.locator('.ant-checkbox-wrapper:has-text("综合业务")').first
        if all_business_wrapper2.count() > 0:
            is_checked = all_business_wrapper2.locator('.ant-checkbox-checked').count() > 0
            if not is_checked:
                print("    综合业务仍未勾选，强制点击...")
                page.evaluate('''() => {
                    const wrappers = document.querySelectorAll('.ant-checkbox-wrapper');
                    for (let wrapper of wrappers) {
                        if (wrapper.textContent.includes('综合业务')) {
                            wrapper.click();
                            return '已强制点击综合业务wrapper';
                        }
                    }
                }''')
                page.wait_for_timeout(1500)
            else:
                print("    综合业务确认已勾选")
        
        # 验证选择结果
        verify_result = page.evaluate('''() => {
            let result = {};
            const wrappers = document.querySelectorAll('.ant-checkbox-wrapper');
            for (let wrapper of wrappers) {
                const text = wrapper.textContent.trim();
                const checkbox = wrapper.querySelector('.ant-checkbox');
                if (text.includes('综合业务')) {
                    result['综合业务'] = checkbox && checkbox.classList.contains('ant-checkbox-checked') ? '已勾选' : '未勾选';
                }
                if (text.includes('收款业务')) {
                    result['收款业务'] = checkbox && checkbox.classList.contains('ant-checkbox-checked') ? '已勾选' : '未勾选';
                }
            }
            return result;
        }''')
        print(f"  选择状态验证: {verify_result}")
        
        # 截图验证选择结果
        verify_screenshot = get_screenshot_path(f"page2_verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        page.screenshot(path=verify_screenshot, full_page=True)
        print(f"  选择验证截图: {verify_screenshot}")
        
        # 填写合作企业信息
        print("  填写合作企业信息...")
        # 合作企业全称
        partner_name_input = page.locator('input[placeholder*="合作企业全称"]').first
        if partner_name_input.count() > 0:
            partner_name_input.fill(config.PARTNER_COMPANY_NAME)
            print(f"    已填写合作企业全称: {config.PARTNER_COMPANY_NAME}")
        
        # 合作企业新浪支付商户号
        partner_merchant_input = page.locator('input[placeholder*="合作企业新浪支付商户号"]').first
        if partner_merchant_input.count() > 0:
            partner_merchant_input.fill(config.PARTNER_MERCHANT_ID)
            print(f"    已填写合作企业新浪支付商户号: {config.PARTNER_MERCHANT_ID}")
            
    elif business_type == 4:
        # 业务4：新浪合作机构 - 收款业务
        print("选择：新浪合作机构 - 收款业务")
        partner_card = page.locator('text=商户的合作机构').first
        if partner_card.count() > 0:
            partner_card.click()
            page.wait_for_timeout(3000)  # 增加等待时间
        # 商户的合作机构默认就是"收款业务"，不需要额外操作
        print("  保持默认收款业务勾选")
        
        # 填写合作企业信息
        print("  填写合作企业信息...")
        # 合作企业全称
        partner_name_input = page.locator('input[placeholder*="合作企业全称"]').first
        if partner_name_input.count() > 0:
            partner_name_input.fill(config.PARTNER_COMPANY_NAME)
            print(f"    已填写合作企业全称: {config.PARTNER_COMPANY_NAME}")
        
        # 合作企业新浪支付商户号
        partner_merchant_input = page.locator('input[placeholder*="合作企业新浪支付商户号"]').first
        if partner_merchant_input.count() > 0:
            partner_merchant_input.fill(config.PARTNER_MERCHANT_ID)
            print(f"    已填写合作企业新浪支付商户号: {config.PARTNER_MERCHANT_ID}")
    
    page.wait_for_timeout(1000)
    
    # 截图保存
    screenshot_path = get_screenshot_path(f"page2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"页面2截图保存到: {screenshot_path}")
    
    # 点击下一步
    print("点击【下一步】按钮...")
    
    # 使用 JavaScript 点击下一步按钮
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
    page.wait_for_timeout(3000)
    print("已点击下一步，等待确认对话框...")
    
    # 截图查看确认对话框
    dialog_screenshot = get_screenshot_path(f"page2_dialog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=dialog_screenshot, full_page=True)
    print(f"确认对话框截图保存到: {dialog_screenshot}")
    
    # 点击【我已确认】按钮
    print("点击【我已确认】按钮...")
    
    # 使用Playwright方式点击（更可靠）
    confirm_btn = page.locator('button:has-text("我已确认")').first
    if confirm_btn.count() > 0:
        confirm_btn.click()
        print("  已点击【我已确认】按钮")
    else:
        # 备选：使用JavaScript
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
    
    # 等待页面跳转（增加等待时间）
    print("  等待页面跳转...")
    page.wait_for_timeout(10000)
    
    # 检查当前URL
    current_url = page.url
    print(f"  当前页面URL: {current_url}")
    
    if "firstTrial" in current_url:
        print("页面2完成，成功进入页面3")
        return True
    else:
        print("  页面未正确跳转，尝试重新点击...")
        # 再次尝试点击
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
        page.wait_for_timeout(5000)
        return True


def fill_page3(page, account, business_type=1):
    """填写页面3：企业信息
    business_type: 1,2=业务1/2的页面3, 3,4=业务3/4的页面3(合作机构页面)
    """
    print("=" * 50)
    print("页面3：企业信息")
    print("=" * 50)
    
    # 等待页面加载，并检查URL
    page.wait_for_timeout(5000)
    current_url = page.url
    print(f"当前页面URL: {current_url}")
    
    # 如果还在页面1或页面2，等待更长时间或刷新
    max_retries = 3
    retry_count = 0
    while ("register" in current_url or "Security" in current_url) and retry_count < max_retries:
        print(f"页面未正确跳转，等待... (尝试 {retry_count + 1}/{max_retries})")
        page.wait_for_timeout(5000)
        current_url = page.url
        retry_count += 1
    
    if "firstTrial" not in current_url:
        print("警告：当前不在页面3，尝试导航到页面3...")
        # 尝试直接导航到页面3
        page.goto("https://e.pay.sina.com.cn/web/firstTrial?enterpriseBusinessType=allBusiness", timeout=60000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
    
    # 判断是哪种页面类型
    is_partner_page = business_type in [3, 4]
    
    # 企业信息
    print("填写企业信息...")
    
    # 1. 上传营业执照
    print("上传营业执照...")
    license_path = f"{config.ATTACHMENT_DIR}/{config.FILE_BUSINESS_LICENSE}"
    if os.path.exists(license_path):
        # 找到文件上传input
        file_input = page.locator('input[type="file"]').first
        if file_input.count() > 0:
            file_input.set_input_files(license_path)
            print(f"已上传: {license_path}")
            page.wait_for_timeout(2000)
    else:
        print(f"营业执照文件不存在: {license_path}")
    
    # 2. 企业名称（直接使用配置文件中的值，不添加后缀）
    print("填写企业名称...")
    company_name = config.COMPANY_NAME_PREFIX
    company_name_input = page.locator('input[placeholder*="企业名称"], input[name*="companyName"]').first
    if company_name_input.count() > 0:
        company_name_input.fill(company_name)
    
    # 3. 企业简称（直接使用配置文件中的值，不添加后缀）
    print("填写企业简称...")
    company_short_name = config.COMPANY_SHORT_NAME_PREFIX
    company_short_input = page.locator('input[placeholder*="企业简称"], input[name*="companyShortName"]').first
    if company_short_input.count() > 0:
        company_short_input.fill(company_short_name)
    
    # 4. 统一社会信用代码
    print("填写统一社会信用代码...")
    credit_code_input = page.locator('input[placeholder*="统一社会信用代码"], input[name*="creditCode"]').first
    if credit_code_input.count() > 0:
        credit_code_input.fill(config.CREDIT_CODE)
    
    # 5. 所属行业（三级级联选择：采矿业 -> 其他采矿业 -> 其他采矿业）
    print("选择所属行业（从左到右一层一层选择）...")
    
    # 找到所属行业表单项下的所有下拉选择框
    industry_form_item = page.locator('.ant-form-item:has-text("所属行业")').first
    if industry_form_item.count() > 0:
        # 获取该表单项下的所有ant-select（应该有三个）
        selects = industry_form_item.locator('.ant-select').all()
        print(f"  找到 {len(selects)} 个下拉选择框")
        
        if len(selects) >= 3:
            # 第一层：选择行业
            print(f"  选择第一层：{config.INDUSTRY_LEVEL1}...")
            selects[0].click()
            page.wait_for_timeout(2000)
            
            # 在弹出的下拉菜单中选择第一层行业
            level1_option = page.locator(f'.ant-select-dropdown-menu-item:has-text("{config.INDUSTRY_LEVEL1}"), .ant-select-item:has-text("{config.INDUSTRY_LEVEL1}")').first
            if level1_option.count() > 0:
                level1_option.click()
                print(f"    已选择{config.INDUSTRY_LEVEL1}")
            else:
                # 使用JavaScript选择
                page.evaluate(f'''() => {{
                    const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                    for (let item of items) {{
                        if (item.textContent.trim() === '{config.INDUSTRY_LEVEL1}') {{
                            item.click();
                            return true;
                        }}
                    }}
                }}''')
            page.wait_for_timeout(3000)
            
            # 第二层：选择行业
            print(f"  选择第二层：{config.INDUSTRY_LEVEL2}...")
            selects[1].click()
            page.wait_for_timeout(2000)
            
            level2_option = page.locator(f'.ant-select-dropdown-menu-item:has-text("{config.INDUSTRY_LEVEL2}"), .ant-select-item:has-text("{config.INDUSTRY_LEVEL2}")').first
            if level2_option.count() > 0:
                level2_option.click()
                print(f"    已选择{config.INDUSTRY_LEVEL2}（第二层）")
            else:
                page.evaluate(f'''() => {{
                    const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                    for (let item of items) {{
                        if (item.textContent.trim() === '{config.INDUSTRY_LEVEL2}') {{
                            item.click();
                            return true;
                        }}
                    }}
                }}''')
            page.wait_for_timeout(3000)
            
            # 第三层：选择行业
            print(f"  选择第三层：{config.INDUSTRY_LEVEL3}...")
            selects[2].click()
            page.wait_for_timeout(3000)
            
            # 先检查第三个下拉框是否已经选中了目标值（在所属行业表单项内查找）
            selected_text = page.evaluate('''() => {
                let industryItem = null;
                const formItems = document.querySelectorAll('.ant-form-item');
                for (let item of formItems) {
                    if (item.textContent && item.textContent.includes('所属行业')) {
                        industryItem = item;
                        break;
                    }
                }
                if (!industryItem) return '';
                const selects = industryItem.querySelectorAll('.ant-select');
                if (selects.length < 3) return '';
                const selected = selects[2].querySelector('.ant-select-selection-selected-value, .ant-select-selection-item');
                return selected ? selected.textContent.trim() : '';
            }''')
            
            if selected_text and config.INDUSTRY_LEVEL3 in selected_text:
                print(f"    第三层已经选中{config.INDUSTRY_LEVEL3}")
            else:
                # 使用JavaScript强制点击（更可靠）
                js_result = page.evaluate(f'''() => {{
                    // 找到所有下拉菜单项
                    const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                    for (let item of items) {{
                        if (item.textContent.trim() === '{config.INDUSTRY_LEVEL3}' && !item.classList.contains('ant-select-dropdown-menu-item-selected') && !item.classList.contains('ant-select-item-option-selected')) {{
                            item.click();
                            return '已点击{config.INDUSTRY_LEVEL3}（第三层）';
                        }}
                    }}
                    // 如果都选中了，就返回已选中
                    return '{config.INDUSTRY_LEVEL3}可能已选中或不可见';
                }}''')
                print(f"    {js_result}")
            page.wait_for_timeout(2000)
        else:
            print(f"  警告：只找到 {len(selects)} 个下拉选择框，预期是3个")
    else:
        print("  未找到所属行业表单项，尝试使用级联选择器方式")
        # 备选：使用级联选择器方式
        cascader = page.locator('.ant-cascader-picker').first
        if cascader.count() > 0:
            cascader.click()
            page.wait_for_timeout(3000)
    
    # 根据页面类型填写不同内容
    if is_partner_page:
        # 业务3/4：合作机构页面
        print("填写合作机构特有信息...")
        
        # 上传与商户的业务合作协议
        print("  上传与商户的业务合作协议...")
        # 上传1: 视频压缩包.zip (第一个上传框)
        agreement_file1 = f"{config.ATTACHMENT_DIR}/{config.FILE_COOPERATION_AGREEMENT_ZIP}"
        if os.path.exists(agreement_file1):
            # 使用JavaScript找到第一个合作协议上传框
            page.evaluate(f'''() => {{
                const fileInputs = document.querySelectorAll('input[type="file"]');
                // 找到包含合作协议相关文本的上传框
                for (let i = 0; i < fileInputs.length; i++) {{
                    const parent = fileInputs[i].closest('.ant-form-item, .upload-item, div');
                    if (parent && (parent.textContent.includes('合作协议') || parent.textContent.includes('业务合作'))) {{
                        // 创建DataTransfer对象来模拟文件上传
                        const dt = new DataTransfer();
                        // 注意：这里只是标记，实际文件上传需要通过Playwright的set_input_files
                        return '找到合作协议上传框1，索引: ' + i;
                    }}
                }}
                return '未找到合作协议上传框1';
            }}''')
            # 使用Playwright上传
            file_inputs = page.locator('input[type="file"]').all()
            if len(file_inputs) >= 2:
                try:
                    file_inputs[1].set_input_files(agreement_file1)
                    print(f"    已上传合作协议1 (zip): {agreement_file1}")
                    page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"    上传合作协议1失败: {e}")
        
        # 上传2: aaaa.pdf (第二个上传框 - 新浪支付账户业务申请表)
        agreement_file2 = f"{config.ATTACHMENT_DIR}/{config.FILE_COOPERATION_AGREEMENT_PDF}"
        if os.path.exists(agreement_file2):
            print("    上传PDF申请表...")
            # 使用Playwright上传第二个文件
            file_inputs = page.locator('input[type="file"]').all()
            if len(file_inputs) >= 3:
                try:
                    file_inputs[2].set_input_files(agreement_file2)
                    print(f"    已上传合作协议2 (pdf): {agreement_file2}")
                    page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"    上传合作协议2失败: {e}")
        
        # 结算账户
        print("  填写结算账户...")
        # 银行户名
        bank_account_name = page.locator('input[placeholder*="银行户名"], input[name*="bankAccountName"]').first
        if bank_account_name.count() > 0:
            bank_account_name.fill(config.BANK_ACCOUNT_NAME)
            print(f"    已填写银行户名: {config.BANK_ACCOUNT_NAME}")
        
        # 开户银行
        print(f"    选择开户银行：{config.BANK_NAME}...")
        bank_select = page.locator('.ant-form-item:has-text("开户银行") .ant-select').first
        if bank_select.count() > 0:
            bank_select.click()
            page.wait_for_timeout(2500)
            # 使用JavaScript选择银行
            js_result = page.evaluate(f'''() => {{
                const items = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                for (let item of items) {{
                    if (item.textContent.includes('{config.BANK_NAME}')) {{
                        item.click();
                        return '已选择银行: {config.BANK_NAME}';
                    }}
                }}
                return '未找到{config.BANK_NAME}选项';
            }}''')
            print(f"    {js_result}")
            page.wait_for_timeout(1500)
        
        # 企业银行账号
        bank_account = page.locator('input[placeholder*="企业银行账号"], input[name*="bankAccount"]').first
        if bank_account.count() > 0:
            bank_account.fill(config.BANK_ACCOUNT_NUMBER)
            print(f"    已填写企业银行账号: {config.BANK_ACCOUNT_NUMBER}")
        
        # 开户证明材料
        print("    上传开户证明材料...")
        bank_cert_file = f"{config.ATTACHMENT_DIR}/{config.FILE_BANK_CERTIFICATE}"
        if os.path.exists(bank_cert_file):
            # 找到"开户证明材料"文字旁边的上传按钮
            upload_cert = page.locator('text=开户证明材料').first
            if upload_cert.count() > 0:
                file_input = upload_cert.locator('xpath=ancestor::div[contains(@class,"ant-form-item")]//input[@type="file"]').first
                if file_input.count() == 0:
                    # 尝试点击上传按钮
                    cert_btn = page.locator('button:has-text("点击上传"), .ant-upload:has-text("开户证明材料")').first
                    if cert_btn.count() > 0:
                        cert_btn.click()
                        page.wait_for_timeout(500)
                    file_input = page.locator('input[type="file"]').first
                if file_input.count() > 0:
                    file_input.set_input_files(bank_cert_file)
                    print(f"    已上传开户证明材料: {bank_cert_file}")
                    page.wait_for_timeout(2000)
    else:
        # 业务1/2：普通商户页面
        # 6. 公司官网或产品
        print("填写公司官网或产品...")
        
        # 使用Playwright方式选择APP
        # 找到"公司官网或产品"后面的下拉选择框
        product_select = page.locator('.ant-form-item:has(.ant-form-item-label:has-text("公司官网或产品")) .ant-select').first
        if product_select.count() > 0:
            product_select.click()
            page.wait_for_timeout(1500)
            
            # 选择 APP
            app_option = page.locator('.ant-select-dropdown-menu-item:has-text("APP"), .ant-select-item:has-text("APP")').first
            if app_option.count() > 0:
                app_option.click()
                page.wait_for_timeout(1500)
        
        # 填写 APP 名称
        print("  填写APP名称...")
        app_name_input = page.locator('.ant-form-item:has(.ant-form-item-label:has-text("公司官网或产品")) input[placeholder*="APP"]').first
        if app_name_input.count() > 0:
            app_name_input.fill(config.APP_NAME)
            print(f"  已填写APP名称: {config.APP_NAME}")
        else:
            # 备选：查找所有输入框，找到placeholder包含APP的
            inputs = page.locator('input').all()
            for input_field in inputs:
                placeholder = input_field.get_attribute('placeholder') or ''
                if 'APP' in placeholder:
                    input_field.fill(config.APP_NAME)
                    print(f"  已填写APP名称: {config.APP_NAME}")
                    break
    
    # 法人信息
    print("填写法人信息...")

    # 7. 先选择证件类型（这样页面会切换为对应的证件上传区域）
    print(f"选择证件类型: {config.LEGAL_ID_TYPE}...")
    # 先点击下拉框，等待下拉菜单出现，再同步查找选项
    js_click = page.evaluate(f'''() => {{
        const formItems = document.querySelectorAll('.ant-form-item');
        for (let item of formItems) {{
            if (item.textContent.includes('证件类型')) {{
                const select = item.querySelector('.ant-select');
                if (select) {{
                    select.click();
                    return 'clicked';
                }}
            }}
        }}
        return 'not_found';
    }}''')
    print(f"  证件类型下拉框: {js_click}")
    
    if js_click == 'clicked':
        # 等待下拉菜单渲染
        page.wait_for_timeout(800)
        # 同步查找并点击选项
        js_result = page.evaluate(f'''() => {{
            const dropdown = document.querySelector('.ant-select-dropdown');
            if (!dropdown) return 'dropdown_not_found';
            const options = dropdown.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
            for (let opt of options) {{
                if (opt.textContent.includes('{config.LEGAL_ID_TYPE}')) {{
                    opt.click();
                    return '已选择证件类型: {config.LEGAL_ID_TYPE}';
                }}
            }}
            return '选项未找到';
        }}''')
        print(f"  {js_result}")
    else:
        print(f"  未找到证件类型下拉框")
    page.wait_for_timeout(3000)  # 等待证件类型切换完成，页面重新渲染

    # 8-9. 根据证件类型上传对应的证件图片
    id_config = config.ID_CARD_TYPE_CONFIG.get(config.LEGAL_ID_TYPE, config.ID_CARD_TYPE_CONFIG["身份证"])
    display_name = id_config["display_name"]

    # 上传证件正面
    if id_config["need_front"]:
        front_label = id_config["front_label"]
        print(f"上传{display_name} - {front_label}...")
        id_front_file = id_config["front_file"]
        id_front_path = f"{config.ATTACHMENT_DIR}/{id_front_file}"

        if os.path.exists(id_front_path):
            # 方法1: 通过查找包含文字的区域来定位上传框
            try:
                # 根据证件类型使用不同的定位文字
                if config.LEGAL_ID_TYPE == "身份证":
                    id_card_section = page.locator('text=请上传人像面, text=上传人像面').first
                elif config.LEGAL_ID_TYPE == "护照":
                    id_card_section = page.locator('text=上传护照, text=请上传护照').first
                elif config.LEGAL_ID_TYPE == "港澳居民来往内地通行证":
                    id_card_section = page.locator('text=上传港澳居民来往内地通行证正面, text=请上传港澳居民来往内地通行证正面').first
                elif config.LEGAL_ID_TYPE == "港澳居民居住证":
                    id_card_section = page.locator('text=上传港澳居民居住证正面, text=请上传港澳居民居住证正面').first
                else:
                    id_card_section = page.locator('text=请上传正面, text=上传正面').first

                if id_card_section.count() > 0:
                    # 在该区域内查找文件上传input
                    file_input = id_card_section.locator('xpath=ancestor::div[contains(@class,"ant-form-item") or contains(@class,"upload")]//input[@type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(id_front_path)
                        print(f"  已通过文字定位上传{display_name} - {front_label}")
                        page.wait_for_timeout(5000)
                    else:
                        raise Exception("在区域内未找到文件上传框")
                else:
                    raise Exception(f"未找到{display_name} - {front_label}区域")
            except Exception as e:
                print(f"  文字定位失败: {e}，尝试使用索引方式")
                # 方法2: 使用索引方式（根据页面类型调整索引）
                file_inputs = page.locator('input[type="file"]').all()
                print(f"  找到 {len(file_inputs)} 个文件上传框")

                # 根据页面类型确定索引
                if is_partner_page:
                    # 合作机构页面：营业执照(0), 合作协议1(1), 合作协议2(2), 开户证明(3), 证件正面(4), 证件背面(5)
                    id_front_index = 4
                else:
                    # 普通商户页面：营业执照(0), 证件正面(1), 证件背面(2), 附件(3)
                    id_front_index = 1

                if len(file_inputs) > id_front_index:
                    try:
                        file_inputs[id_front_index].set_input_files(id_front_path)
                        print(f"  已上传{display_name} - {front_label}到第 {id_front_index + 1} 个上传框")
                        page.wait_for_timeout(5000)
                    except Exception as e2:
                        print(f"  上传{display_name} - {front_label}失败: {e2}")
                else:
                    print(f"  警告：未找到足够的文件上传框，需要索引{id_front_index}，但只有{len(file_inputs)}个")
        else:
            print(f"  {display_name} - {front_label}文件不存在: {id_front_path}")

    # 上传证件背面（如果需要）
    if id_config["need_back"] and id_config["back_file"]:
        back_label = id_config["back_label"]
        print(f"上传{display_name} - {back_label}...")
        id_back_file = id_config["back_file"]
        id_back_path = f"{config.ATTACHMENT_DIR}/{id_back_file}"

        if os.path.exists(id_back_path):
            # 方法1: 通过查找包含文字的区域来定位上传框
            try:
                # 根据证件类型使用不同的定位文字
                if config.LEGAL_ID_TYPE == "身份证":
                    id_card_back_section = page.locator('text=请上传国徽面, text=上传国徽面').first
                elif config.LEGAL_ID_TYPE == "港澳居民来往内地通行证":
                    id_card_back_section = page.locator('text=上传港澳居民来往内地通行证反面, text=请上传港澳居民来往内地通行证反面').first
                elif config.LEGAL_ID_TYPE == "港澳居民居住证":
                    id_card_back_section = page.locator('text=上传港澳居民居住证反面, text=请上传港澳居民居住证反面').first
                else:
                    id_card_back_section = page.locator('text=请上传背面, text=上传背面').first

                if id_card_back_section.count() > 0:
                    file_input = id_card_back_section.locator('xpath=ancestor::div[contains(@class,"ant-form-item") or contains(@class,"upload")]//input[@type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(id_back_path)
                        print(f"  已通过文字定位上传{display_name} - {back_label}")
                        page.wait_for_timeout(3000)
                    else:
                        raise Exception("在区域内未找到文件上传框")
                else:
                    raise Exception(f"未找到{display_name} - {back_label}区域")
            except Exception as e:
                print(f"  文字定位失败: {e}，尝试使用索引方式")
                # 方法2: 使用索引方式
                file_inputs = page.locator('input[type="file"]').all()

                if is_partner_page:
                    id_back_index = 5
                else:
                    id_back_index = 2

                if len(file_inputs) > id_back_index:
                    try:
                        file_inputs[id_back_index].set_input_files(id_back_path)
                        print(f"  已上传{display_name} - {back_label}到第 {id_back_index + 1} 个上传框")
                        page.wait_for_timeout(3000)
                    except Exception as e2:
                        print(f"  上传{display_name} - {back_label}失败: {e2}")
                else:
                    print(f"  警告：未找到足够的文件上传框，需要索引{id_back_index}，但只有{len(file_inputs)}个")
        else:
            print(f"  {display_name} - {back_label}文件不存在: {id_back_path}")
    else:
        print(f"  {display_name}不需要上传背面/反面")

    # 等待OCR识别完成
    print("等待OCR识别完成...")
    page.wait_for_timeout(5000)

    # 截图查看身份证上传后的状态
    id_screenshot = get_screenshot_path(f"page3_id_uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=id_screenshot, full_page=True)
    print(f"证件上传后截图: {id_screenshot}")

    # 10. 法人姓名（上传证件后修改，使用JavaScript强制修改）
    print("填写法人姓名（上传证件后）...")
    js_result = page.evaluate(f'''() => {{
        // 查找法人姓名输入框
        const inputs = document.querySelectorAll('input');
        for (let input of inputs) {{
            const placeholder = input.getAttribute('placeholder') || '';
            const name = input.getAttribute('name') || '';
            if (placeholder.includes('法人姓名') || name.includes('legalName')) {{
                // 保存原始状态
                const wasDisabled = input.disabled;
                const wasReadOnly = input.readOnly;
                // 移除disabled和readOnly属性
                input.disabled = false;
                input.readOnly = false;
                // 清空原有值
                input.value = '';
                // 设置新值
                input.value = '{config.LEGAL_NAME}';
                // 触发事件
                input.dispatchEvent(new Event('focus', {{ bubbles: true }}));
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                return '已填写法人姓名: {config.LEGAL_NAME} (原disabled=' + wasDisabled + ', readOnly=' + wasReadOnly + ')';
            }}
        }}
        return '未找到法人姓名输入框';
    }}''')
    print(f"  {js_result}")
    page.wait_for_timeout(1500)
    
    # 11. 法人证件号码（上传身份证后必须重新填写指定号码）
    print("填写法人证件号码（上传身份证后重新填写）...")

    # 使用JavaScript强制修改证件号码（即使字段被禁用）
    js_result = page.evaluate(f'''() => {{
        // 查找法人证件号码输入框
        const inputs = document.querySelectorAll('input');
        for (let input of inputs) {{
            const placeholder = input.getAttribute('placeholder') || '';
            const name = input.getAttribute('name') || '';
            const parent = input.closest('.ant-form-item');
            const label = parent ? parent.textContent : '';
            if (placeholder.includes('证件号码') || name.includes('idNumber') || label.includes('法人证件号码')) {{
                // 保存原始状态
                const wasDisabled = input.disabled;
                const wasReadOnly = input.readOnly;
                // 移除disabled和readOnly属性
                input.disabled = false;
                input.readOnly = false;
                // 清空原有值
                input.value = '';
                // 设置新值
                input.value = '{config.LEGAL_ID_NUMBER}';
                // 触发事件
                input.dispatchEvent(new Event('focus', {{ bubbles: true }}));
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                return '已填写法人证件号码: {config.LEGAL_ID_NUMBER} (原disabled=' + wasDisabled + ', readOnly=' + wasReadOnly + ')';
            }}
        }}
        return '未找到法人证件号码输入框';
    }}''')
    print(f"  {js_result}")
    page.wait_for_timeout(1500)
    
    # 12. 法人证件有效期（勾选长期）- 使用JavaScript因为元素可能被禁用
    print("勾选证件有效期长期...")
    
    # 先截图查看当前状态
    expiry_screenshot = get_screenshot_path(f"page3_expiry_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=expiry_screenshot, full_page=True)
    
    # 尝试多种方法勾选"长期"
    # 方法1: 使用Playwright点击
    try:
        long_term_checkbox = page.locator('.ant-checkbox-wrapper:has-text("长期"), label:has-text("长期")').first
        if long_term_checkbox.count() > 0:
            long_term_checkbox.click()
            print("  已使用Playwright点击'长期'复选框")
            page.wait_for_timeout(1000)
    except Exception as e:
        print(f"  Playwright点击失败: {e}")
    
    # 方法2: 使用JavaScript强制勾选
    js_result = page.evaluate('''() => {
        // 找到包含"长期"文字的复选框wrapper
        const wrappers = document.querySelectorAll('.ant-checkbox-wrapper, label');
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
        return '未找到证件有效期长期复选框';
    }''')
    print(f"  {js_result}")
    page.wait_for_timeout(1500)
    
    # 再次截图查看勾选后的状态
    expiry_after_screenshot = get_screenshot_path(f"page3_expiry_after_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=expiry_after_screenshot, full_page=True)
    
    # 13. 法人手机号
    print("填写法人手机号...")
    js_result = page.evaluate(f'''() => {{
        const inputs = document.querySelectorAll('input');
        for (let input of inputs) {{
            const placeholder = input.getAttribute('placeholder') || '';
            if (placeholder.includes('法人手机号') || placeholder.includes('法人手机号码')) {{
                input.value = '{config.LEGAL_PHONE}';
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return '已填写法人手机号: {config.LEGAL_PHONE}';
            }}
        }}
        return '未找到法人手机号输入框';
    }}''')
    print(f"  {js_result}")
    page.wait_for_timeout(1000)
    
    # 如果是合作机构页面，填写开户意愿核实方式
    if is_partner_page:
        print("填写开户意愿核实方式...")
        
        # 先滚动到页面底部，确保开户意愿核实方式部分可见
        page.evaluate('''() => {
            window.scrollTo(0, document.body.scrollHeight);
        }''')
        page.wait_for_timeout(2000)
        
        # 截图查看当前页面状态
        verify_screenshot = get_screenshot_path(f"page3_verify_method_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        page.screenshot(path=verify_screenshot, full_page=True)
        print(f"  开户意愿核实方式区域截图: {verify_screenshot}")
        
        # 先勾选"上传开户意愿视频" - 使用更可靠的方式
        print("  勾选'上传开户意愿视频'...")
        
        # 方法1: 使用Playwright点击包含文字的元素
        try:
            # 查找包含"上传开户意愿视频"文本的元素并点击
            upload_video_option = page.locator('label:has-text("上传开户意愿视频"), .ant-radio-wrapper:has-text("上传开户意愿视频"), .ant-checkbox-wrapper:has-text("上传开户意愿视频")').first
            if upload_video_option.count() > 0:
                upload_video_option.click()
                print("    已点击'上传开户意愿视频'选项")
            else:
                # 方法2: 使用JavaScript查找并点击
                js_result = page.evaluate('''() => {
                    // 查找所有label或radio元素
                    const elements = document.querySelectorAll('label, .ant-radio-wrapper, .ant-checkbox-wrapper, span');
                    for (let el of elements) {
                        if (el.textContent && el.textContent.trim() === '上传开户意愿视频') {
                            // 查找radio或checkbox input
                            const input = el.querySelector('input[type="radio"], input[type="checkbox"]');
                            const radio = el.querySelector('.ant-radio, .ant-checkbox');
                            if (input && radio) {
                                input.checked = true;
                                radio.classList.add('ant-radio-checked', 'ant-checkbox-checked');
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                return '已勾选上传开户意愿视频';
                            }
                            // 如果没有找到input，尝试点击元素本身
                            el.click();
                            return '已点击上传开户意愿视频元素';
                        }
                    }
                    return '未找到上传开户意愿视频选项';
                }''')
                print(f"    {js_result}")
        except Exception as e:
            print(f"    点击上传开户意愿视频失败: {e}")
        
        page.wait_for_timeout(2000)
        
        # 再勾选"由法人本人认证"
        print("  勾选'由法人本人认证'...")
        
        try:
            # 查找包含"由法人本人认证"文本的元素并点击
            legal_person_option = page.locator('label:has-text("由法人本人认证"), .ant-radio-wrapper:has-text("由法人本人认证"), .ant-checkbox-wrapper:has-text("由法人本人认证")').first
            if legal_person_option.count() > 0:
                legal_person_option.click()
                print("    已点击'由法人本人认证'选项")
            else:
                # 方法2: 使用JavaScript查找并点击
                js_result = page.evaluate('''() => {
                    const elements = document.querySelectorAll('label, .ant-radio-wrapper, .ant-checkbox-wrapper, span');
                    for (let el of elements) {
                        if (el.textContent && el.textContent.trim() === '由法人本人认证') {
                            const input = el.querySelector('input[type="radio"], input[type="checkbox"]');
                            const radio = el.querySelector('.ant-radio, .ant-checkbox');
                            if (input && radio) {
                                input.checked = true;
                                radio.classList.add('ant-radio-checked', 'ant-checkbox-checked');
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                return '已勾选由法人本人认证';
                            }
                            el.click();
                            return '已点击由法人本人认证元素';
                        }
                    }
                    return '未找到由法人本人认证选项';
                }''')
                print(f"    {js_result}")
        except Exception as e:
            print(f"    点击由法人本人认证失败: {e}")
        
        page.wait_for_timeout(2000)
        
        # 上传开户意愿视频附件
        print("  上传开户意愿视频...")
        video_file = f"{config.ATTACHMENT_DIR}/{config.FILE_VIDEO}"
        if os.path.exists(video_file):
            # 方法1: 通过查找包含"请上传法人开户意愿视频"或"点击上传"文字的区域来定位
            try:
                # 先等待一下，让上传区域显示出来
                page.wait_for_timeout(2000)
                
                # 查找开户意愿视频上传区域（在"由法人本人认证"下方）
                upload_section = page.locator('text=请上传法人开户意愿视频').first
                if upload_section.count() > 0:
                    # 在该区域内查找文件上传input
                    file_input = upload_section.locator('xpath=ancestor::div[contains(@class,"ant-form-item") or contains(@class,"upload")]//input[@type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(video_file)
                        print(f"    已通过文字定位上传开户意愿视频")
                        page.wait_for_timeout(3000)
                    else:
                        raise Exception("在开户意愿视频区域内未找到文件上传框")
                else:
                    raise Exception("未找到开户意愿视频上传区域")
            except Exception as e:
                print(f"    文字定位失败: {e}，尝试使用索引方式")
                # 方法2: 使用索引方式（开户意愿视频是最后一个上传框）
                file_inputs = page.locator('input[type="file"]').all()
                print(f"    找到 {len(file_inputs)} 个文件上传框")
                
                # 开户意愿视频应该是最后一个上传框
                if len(file_inputs) > 0:
                    last_index = len(file_inputs) - 1
                    try:
                        file_inputs[last_index].set_input_files(video_file)
                        print(f"    已上传开户意愿视频到最后一个上传框（第 {last_index + 1} 个）")
                        page.wait_for_timeout(3000)
                    except Exception as e2:
                        print(f"    上传开户意愿视频失败: {e2}")
                else:
                    print("    警告：未找到文件上传框")
    else:
        # 业务1/2：上传普通附件
        print("上传附件...")
        attachment_path = f"{config.ATTACHMENT_DIR}/{config.FILE_VIDEO}"
        if os.path.exists(attachment_path):
            file_inputs = page.locator('input[type="file"]').all()
            print(f"  找到 {len(file_inputs)} 个文件上传框")
            # 附件上传框的索引取决于证件类型上传了几个文件
            # 身份证/港澳通行证/居住证：上传2张，附件在索引3
            # 护照：上传1张，附件在索引2
            id_config = config.ID_CARD_TYPE_CONFIG.get(config.LEGAL_ID_TYPE, config.ID_CARD_TYPE_CONFIG["身份证"])
            if id_config["need_back"]:
                # 需要上传2张证件图片，附件在第4个上传框（索引3）
                attachment_index = 3
            else:
                # 只需要上传1张证件图片，附件在第3个上传框（索引2）
                attachment_index = 2
            
            if len(file_inputs) > attachment_index:
                file_inputs[attachment_index].set_input_files(attachment_path)
                print(f"  已上传附件到第 {attachment_index + 1} 个上传框: {attachment_path}")
                page.wait_for_timeout(2000)
            else:
                print(f"  警告：未找到足够的文件上传框，需要索引{attachment_index}，但只有{len(file_inputs)}个")
        else:
            print(f"  附件文件不存在: {attachment_path}")
    
    # 截图保存
    screenshot_path = get_screenshot_path(f"page3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"页面3截图保存到: {screenshot_path}")
    
    # 14. 点击提交
    print("点击【提交】按钮...")
    
    # 先滚动到页面底部，确保提交按钮可见
    page.evaluate('''() => {
        window.scrollTo(0, document.body.scrollHeight);
    }''')
    page.wait_for_timeout(2000)
    
    # 调试：打印所有按钮的信息
    print("  调试：查找所有按钮...")
    buttons_info = page.evaluate('''() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        return buttons.map((btn, index) => ({
            index: index,
            text: btn.textContent.trim(),
            class: btn.className,
            type: btn.type,
            id: btn.id
        }));
    }''')
    print(f"  找到 {len(buttons_info)} 个按钮:")
    for btn_info in buttons_info:
        print(f"    按钮{btn_info['index']}: 文字='{btn_info['text']}', class='{btn_info['class']}', type='{btn_info['type']}'")
    
    # 使用多种方式尝试点击提交按钮
    submit_success = False
    
    # 方式1：通过ant-btn-primary和文字查找（处理"提 交"带空格的情况）
    try:
        primary_btns = page.locator('.ant-btn-primary').all()
        for btn in primary_btns:
            text = btn.text_content() or ''
            if '提' in text and '交' in text:  # 处理"提 交"带空格的情况
                btn.click()
                print("  已点击提交按钮（通过ant-btn-primary查找）")
                submit_success = True
                break
    except Exception as e:
        print(f"  方式1失败: {e}")
    
    # 方式2：查找所有按钮，找到包含"提"和"交"文字的
    if not submit_success:
        try:
            all_btns = page.locator('button').all()
            for btn in all_btns:
                text = btn.text_content() or ''
                if '提' in text and '交' in text:
                    btn.click()
                    print("  已点击提交按钮（通过遍历所有按钮查找）")
                    submit_success = True
                    break
        except Exception as e:
            print(f"  方式2失败: {e}")
    
    # 方式3：使用JavaScript强制点击（最可靠）
    if not submit_success:
        js_result = page.evaluate('''() => {
            // 查找所有按钮
            const buttons = Array.from(document.querySelectorAll('button'));
            
            // 查找包含"提"和"交"文字的按钮（处理带空格的情况）
            for (let btn of buttons) {
                const text = btn.textContent.trim();
                if (text.includes('提') && text.includes('交')) {
                    btn.click();
                    return 'JavaScript点击提交按钮成功';
                }
            }
            
            // 查找红色主按钮
            const primaryBtns = document.querySelectorAll('.ant-btn-primary');
            for (let btn of primaryBtns) {
                const text = btn.textContent.trim();
                if (text.includes('提') && text.includes('交')) {
                    btn.click();
                    return 'JavaScript点击红色主按钮成功';
                }
            }
            
            return '未找到提交按钮';
        }''')
        print(f"  {js_result}")
        if '成功' in js_result:
            submit_success = True
    
    if submit_success:
        page.wait_for_timeout(5000)
        print("页面3提交完成！")
        
        # 截图保存最终结果
        final_screenshot = get_screenshot_path(f"page3_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        page.screenshot(path=final_screenshot, full_page=True)
        print(f"最终结果截图保存到: {final_screenshot}")
        return True
    else:
        print("未找到提交按钮，但页面3信息已填写完成")
        return True


def fill_page4(page, account, business_type=1):
    """
    填写补充资料页面（页面4）- 仅业务1、业务2审核通过后进入
    URL: https://e.pay.sina.com.cn/web/reviewCheck
    
    参数:
        page: Playwright页面对象
        account: 登录账号
        business_type: 业务类型（1或2）
    """
    print("\n" + "="*50)
    print("页面4：补充资料审核")
    print("="*50)
    
    # 等待页面加载
    page.wait_for_timeout(3000)
    
    # 截图保存
    screenshot_path = get_screenshot_path(f"page4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"页面4截图保存到: {screenshot_path}")
    
    # 1. 填写结算账户（与业务3/4页面3类似）
    print("\n填写结算账户...")
    
    # 银行账户名（通常是企业名称）
    bank_account_name_input = page.locator('input[placeholder*="银行账户名"], input[name*="bankAccountName"]').first
    if bank_account_name_input.count() > 0:
        bank_account_name_input.fill(config.BANK_ACCOUNT_NAME)
        print(f"  已填写银行账户名: {config.BANK_ACCOUNT_NAME}")
    
    # 开户银行
    print("  选择开户银行...")
    bank_select = page.locator('.ant-form-item:has-text("开户银行") .ant-select').first
    if bank_select.count() > 0:
        bank_select.click()
        page.wait_for_timeout(2000)
        # 选择银行
        bank_option = page.locator(f'.ant-select-dropdown-menu-item:has-text("{config.BANK_NAME}"), .ant-select-item:has-text("{config.BANK_NAME}")').first
        if bank_option.count() > 0:
            bank_option.click()
            print(f"    已选择开户银行: {config.BANK_NAME}")
        page.wait_for_timeout(2000)
    
    # 企业银行账号
    bank_account_input = page.locator('input[placeholder*="企业银行账号"], input[name*="bankAccount"]').first
    if bank_account_input.count() > 0:
        bank_account_input.fill(config.BANK_ACCOUNT)
        print(f"  已填写企业银行账号: {config.BANK_ACCOUNT}")
    
    # 上传开户证明材料
    print("  上传开户证明材料...")
    cert_path = os.path.join(config.ATTACHMENT_DIR, config.FILE_BANK_CERTIFICATE)
    if os.path.exists(cert_path):
        # 找到开户证明材料上传框
        cert_upload = page.locator('.ant-form-item:has-text("开户证明材料") .ant-btn').first
        if cert_upload.count() > 0:
            cert_upload.click()
            page.wait_for_timeout(2000)
            
            # 查找文件输入框
            file_input = page.locator('input[type="file"]').last
            if file_input.count() > 0:
                file_input.set_input_files(cert_path)
                print(f"    已上传开户证明材料: {cert_path}")
                page.wait_for_timeout(3000)
    
    # 2. 填写受益人信息
    print("\n填写受益人信息...")
    
    for index, beneficiary in enumerate(config.BENEFICIARIES):
        print(f"  填写受益人 {index + 1}: {beneficiary['name']}")
        
        # 如果是第二个及以上的受益人，需要先点击"添加受益人"按钮
        if index > 0:
            add_btn = page.locator('button:has-text("添加受益人")').first
            if add_btn.count() > 0:
                add_btn.click()
                print(f"    点击添加受益人按钮")
                page.wait_for_timeout(2000)
        
        # 展开受益人卡片（如果是折叠状态）
        beneficiary_card = page.locator(f'.ant-card:has-text("受益人{index + 1}"), .beneficiary-item:has-text("受益人{index + 1}")').first
        if beneficiary_card.count() > 0:
            beneficiary_card.click()
            page.wait_for_timeout(1000)
        
        # 填写姓名
        name_input = page.locator(f'input[placeholder*="姓名"]').nth(index)
        if name_input.count() > 0:
            name_input.fill(beneficiary['name'])
            print(f"    已填写姓名: {beneficiary['name']}")
        
        # 选择证件类型
        id_type_select = page.locator('.ant-form-item:has-text("证件类型") .ant-select').nth(index)
        if id_type_select.count() > 0:
            id_type_select.click()
            page.wait_for_timeout(1000)
            id_type_option = page.locator(f'.ant-select-dropdown-menu-item:has-text("{beneficiary['id_type']}"), .ant-select-item:has-text("{beneficiary['id_type']}")').first
            if id_type_option.count() > 0:
                id_type_option.click()
                print(f"    已选择证件类型: {beneficiary['id_type']}")
            page.wait_for_timeout(1000)
        
        # 填写证件号码
        id_number_input = page.locator(f'input[placeholder*="证件号码"], input[placeholder*="身份证号"]').nth(index)
        if id_number_input.count() > 0:
            id_number_input.fill(beneficiary['id_number'])
            print(f"    已填写证件号码: {beneficiary['id_number']}")
        
        # 填写有效期
        valid_start_input = page.locator(f'input[placeholder*="开始时间"]').nth(index * 2)
        valid_end_input = page.locator(f'input[placeholder*="截止时间"]').nth(index * 2 + 1)
        if valid_start_input.count() > 0 and valid_end_input.count() > 0:
            valid_start_input.fill(beneficiary['valid_start'])
            valid_end_input.fill(beneficiary['valid_end'])
            print(f"    已填写有效期: {beneficiary['valid_start']} 至 {beneficiary['valid_end']}")
        
        # 填写居住地址
        address_input = page.locator(f'input[placeholder*="居住地址"]').nth(index)
        if address_input.count() > 0:
            address_input.fill(beneficiary['address'])
            print(f"    已填写居住地址: {beneficiary['address']}")
    
    # 3. 开户意愿核实方式（与业务3/4页面3相同）
    print("\n填写开户意愿核实方式...")
    
    # 选择"上传开户意愿视频"
    video_radio = page.locator('label:has-text("上传开户意愿视频"), .ant-radio-wrapper:has-text("上传开户意愿视频")').first
    if video_radio.count() > 0:
        video_radio.click()
        print("  已选择: 上传开户意愿视频")
        page.wait_for_timeout(2000)
    
    # 选择"由法人本人认证"
    legal_person_radio = page.locator('label:has-text("由法人本人认证"), .ant-radio-wrapper:has-text("由法人本人认证")').first
    if legal_person_radio.count() > 0:
        legal_person_radio.click()
        print("  已选择: 由法人本人认证")
        page.wait_for_timeout(2000)
    
    # 上传开户意愿视频
    print("  上传开户意愿视频...")
    video_path = os.path.join(config.ATTACHMENT_DIR, config.FILE_VIDEO)
    if os.path.exists(video_path):
        # 查找视频上传框
        video_upload = page.locator('.ant-form-item:has-text("开户意愿视频") .ant-btn, .ant-form-item:has-text("上传") .ant-btn').last
        if video_upload.count() > 0:
            video_upload.click()
            page.wait_for_timeout(2000)
            
            # 查找文件输入框
            file_input = page.locator('input[type="file"]').last
            if file_input.count() > 0:
                file_input.set_input_files(video_path)
                print(f"    已上传开户意愿视频: {video_path}")
                page.wait_for_timeout(3000)
    
    # 4. 截图保存
    screenshot_path = get_screenshot_path(f"page4_filled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"\n页面4填写完成截图保存到: {screenshot_path}")
    
    # 5. 点击提交
    print("\n点击【提交】按钮...")
    
    # 滚动到页面底部
    page.evaluate('''() => {
        window.scrollTo(0, document.body.scrollHeight);
    }''')
    page.wait_for_timeout(2000)
    
    # 查找提交按钮
    submit_btn = page.locator('button:has-text("提交"), .ant-btn-primary:has-text("提交")').first
    if submit_btn.count() > 0:
        submit_btn.click()
        print("  已点击提交按钮")
        page.wait_for_timeout(5000)
        
        # 截图保存最终结果
        final_screenshot = get_screenshot_path(f"page4_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        page.screenshot(path=final_screenshot, full_page=True)
        print(f"页面4最终截图保存到: {final_screenshot}")
        print("\n页面4提交完成！")
        return True
    else:
        print("  未找到提交按钮")
        return False


def register_sina_member(input_param='babweb 业务1', id_type=None):
    """
    执行新浪支付会员注册完整流程

    参数:
        input_param: 输入参数，格式为 "前缀 业务类型"
            例如: "babweb 业务1" - 生成账号 babwebyw1_202606142028
                  "babbxb 业务2" - 生成账号 babbxbyw2_202606142029
        id_type: 法人证件类型，可选值：身份证、港澳通行证、护照、台胞证
            如果为None，则使用配置文件中的 LEGAL_ID_TYPE
    """
    # 解析输入参数
    parts = input_param.split()
    if len(parts) >= 2:
        prefix = parts[0]
        business_type = parts[1]
    else:
        # 默认参数
        prefix = "babweb"
        business_type = input_param if input_param in ['业务1', '业务2', '业务3', '业务4'] else '业务1'

    # 验证业务类型参数
    valid_types = ['业务1', '业务2', '业务3', '业务4']
    if business_type not in valid_types:
        print(f"错误: 无效的业务类型 '{business_type}'")
        print(f"有效的业务类型: {', '.join(valid_types)}")
        return

    # 如果指定了证件类型，更新配置
    if id_type and id_type in config.ID_CARD_TYPE_CONFIG:
        config.LEGAL_ID_TYPE = id_type
        print(f"使用指定的法人证件类型: {id_type}")
    else:
        print(f"使用配置文件的法人证件类型: {config.LEGAL_ID_TYPE}")

    # 生成账号（传入证件类型）
    account = generate_account(prefix=prefix, business_type=business_type, id_type=config.LEGAL_ID_TYPE)
    password = config.LOGIN_PASSWORD

    print(f"生成的登录账号: {account}")
    print(f"登录密码: {password}")
    print(f"业务类型: {business_type}")
    print(f"法人证件类型: {config.LEGAL_ID_TYPE}")
    
    # 创建用户专属的截图文件夹
    screenshot_dir = create_screenshot_dir(account, business_type=business_type)
    print(f"截图文件夹: {screenshot_dir}")
    
    # 将业务类型映射为数字
    business_type_map = {
        '业务1': 1,
        '业务2': 2,
        '业务3': 3,
        '业务4': 4
    }
    business_type_num = business_type_map[business_type]
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--ignore-certificate-errors',
                '--ignore-ssl-errors',
                '--ignore-certificate-errors-spki-list'
            ]
        )
        
        # 创建新页面
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        try:
            # 打开注册页面
            print("正在打开注册页面...")
            page.goto("https://e.pay.sina.com.cn/web/register", timeout=60000)
            page.wait_for_load_state("networkidle")
            
            # 生成随机邮箱：登录账号 + 随机邮箱域名
            email_domains = ["@qq.com", "@163.com", "@gmail.com", "@outlook.com", "@sina.com", "@sina.cn"]
            random_domain = random.choice(email_domains)
            operator_email = f"{account}{random_domain}"
            print(f"生成经办人邮箱: {operator_email}")
            
            # 页面1：用户创建
            if not fill_page1(page, account, password, email=operator_email):
                print("页面1执行失败")
                return
            
            # 页面2：选择业务类型
            if not fill_page2(page, business_type=business_type_num):
                print("页面2执行失败")
                return
            
            # 页面3：企业信息
            if not fill_page3(page, account, business_type_num):
                print("页面3执行失败")
                return
            
            print("=" * 50)
            print("注册流程全部完成！")
            print("=" * 50)
            
            # 查询数据库获取审批任务ID
            print("\n" + "=" * 50)
            print("查询数据库 - 获取审批任务ID")
            print("=" * 50)
            print(f"登录账号: {account}")
            
            audit_task_id = None
            try:
                from src.services.database_service import get_audit_task_id_by_email
                audit_task_id = get_audit_task_id_by_email(account)
                if audit_task_id:
                    print(f"\n✅ 查询成功！")
                    print(f"   审批任务ID: {audit_task_id}")
                else:
                    print("\n⚠️ 未查询到审批任务ID")
                    print("   可能的原因：")
                    print("   1. 数据库同步延迟，请稍后重试")
                    print("   2. 注册数据尚未写入数据库")
            except Exception as db_error:
                print(f"\n❌ 数据库查询失败: {str(db_error)}")
            
            print("\n" + "=" * 50)
            print("【注册结果汇总】")
            print("=" * 50)
            print(f"登录账号: {account}")
            print(f"登录密码: {config.LOGIN_PASSWORD}")
            print(f"邮箱: {operator_email}")
            print(f"审批任务ID: {audit_task_id if audit_task_id else '未查询到'}")
            
            print("\n" + "=" * 50)
            print("【注册信息汇总】")
            print("=" * 50)
            print(f"登录账号: {account}")
            print(f"登录密码: {config.LOGIN_PASSWORD}")
            print(f"邮箱: {operator_email}")
            print(f"审批任务ID: {audit_task_id if audit_task_id else '未查询到'}")
            
            # 提示：业务1、业务2审核通过后会进入补充资料页面
            if business_type_num in [1, 2]:
                print("\n【重要提示】")
                print("业务1、业务2在审核通过后，刷新页面会进入补充资料页面。")
                print("如需自动填写补充资料页面，请：")
                print("1. 等待审核通过（通常1-3个工作日）")
                print("2. 登录后刷新页面进入补充资料页面")
                print("3. 运行脚本：python3 sina_register.py <前缀> <业务类型> 补充资料")
                print("   例如：python3 sina_register.py babweb 业务1 补充资料")
                print("\n或者手动填写补充资料页面（URL: /web/reviewCheck）")
            
            # 等待用户查看
            if os.environ.get('NO_WAIT') == '1':
                print("非交互模式，跳过等待，5秒后关闭浏览器...")
                page.wait_for_timeout(5000)
            else:
                input("按回车键关闭浏览器...")
            
        except Exception as e:
            print(f"执行出错: {e}")
            error_screenshot = get_screenshot_path(f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            page.screenshot(path=error_screenshot, full_page=True)
            print(f"错误截图保存到: {error_screenshot}")
            
        finally:
            browser.close()


def register_supplement(input_param='babweb 业务1', login_account=None):
    """
    执行业务1、业务2审核通过后的补充资料页面填写
    页面URL: https://e.pay.sina.com.cn/web/reviewCheck
    
    参数:
        input_param: 输入参数，格式为 "前缀 业务类型"
            例如: "babweb 业务1" 或 "babweb 业务2"
        login_account: 登录账号（如果为None，则使用input_param生成账号）
            例如: "babwebyw11202606161348"（之前注册并审核通过的账号）
    """
    # 解析输入参数
    parts = input_param.split()
    if len(parts) >= 2:
        prefix = parts[0]
        business_type = parts[1]
    else:
        prefix = "babweb"
        business_type = input_param if input_param in ['业务1', '业务2'] else '业务1'
    
    # 验证业务类型参数（仅支持业务1和业务2）
    valid_types = ['业务1', '业务2']
    if business_type not in valid_types:
        print(f"错误: 补充资料页面仅支持业务1和业务2")
        print(f"有效的业务类型: {', '.join(valid_types)}")
        return
    
    # 将业务类型映射为数字
    business_type_map = {
        '业务1': 1,
        '业务2': 2,
    }
    business_type_num = business_type_map[business_type]
    
    # 确定登录账号
    if login_account is None:
        # 如果没有指定登录账号，生成一个新账号（用于首次注册）
        account = generate_account(prefix=prefix, business_type=business_type, id_type=config.LEGAL_ID_TYPE)
        print(f"警告: 未指定登录账号，将使用生成的账号: {account}")
        print(f"注意: 此账号可能尚未注册或审核通过")
    else:
        # 使用指定的登录账号（已注册并审核通过的账号）
        account = login_account
        # 从账号中提取前缀和业务类型信息用于截图文件夹命名
        # 账号格式: prefix + yw + 业务数字 + 证件类型数字 + 时间
        # 例如: babwebyw11202606161348
        if 'yw' in account:
            # 尝试提取前缀（yw之前的部分）
            prefix_part = account.split('yw')[0]
            if prefix_part:
                prefix = prefix_part
    
    print(f"补充资料页面填写")
    print(f"业务类型: {business_type}")
    print(f"账号前缀: {prefix}")
    print(f"登录账号: {account}")
    
    # 创建截图文件夹
    screenshot_dir = create_screenshot_dir(account, business_type=business_type)
    print(f"截图文件夹: {screenshot_dir}")
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--ignore-certificate-errors',
                '--ignore-ssl-errors',
                '--ignore-certificate-errors-spki-list'
            ]
        )
        
        # 创建浏览器上下文
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 打开新页面
        page = context.new_page()
        
        try:
            # 先导航到控制台页面
            console_url = "https://e.pay.sina.com.cn/console/index"
            print(f"\n正在打开控制台页面: {console_url}")
            
            page.goto(console_url, timeout=60000)
            page.wait_for_timeout(5000)
            
            # 检查当前URL
            current_url = page.url
            print(f"当前页面URL: {current_url}")
            
            # 如果被重定向到登录页面，提示用户手动登录
            if "login" in current_url or "site/login" in current_url:
                print("\n" + "="*50)
                print("检测到需要登录，请手动登录")
                print("="*50)
                print(f"建议登录账号: {account}")
                print(f"密码: {config.LOGIN_PASSWORD}")
                print("\n请在浏览器中完成登录，登录成功后按回车键继续...")
                print("="*50)
                if os.environ.get('NO_WAIT') == '1':
                    print("非交互模式，等待30秒后自动继续...")
                    page.wait_for_timeout(30000)
                else:
                    input()  # 等待用户手动登录
                
                # 用户登录后，再次检查当前URL
                page.wait_for_timeout(3000)
                current_url = page.url
                print(f"\n登录后页面URL: {current_url}")
                
                # 如果登录后仍不在控制台页面，再次导航
                if "console" not in current_url:
                    print("登录成功，正在导航到控制台页面...")
                    page.goto(console_url, timeout=60000)
                    page.wait_for_timeout(5000)
                    current_url = page.url
                    print(f"导航后页面URL: {current_url}")
            
            # 检查是否在控制台页面
            if "console" not in current_url:
                print("\n警告: 当前不在控制台页面")
                print("可能的原因:")
                print("1. 登录失败，请检查账号密码")
                print("2. 页面加载异常")
                
                # 截图保存当前状态
                error_screenshot = get_screenshot_path(f"supplement_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                page.screenshot(path=error_screenshot, full_page=True)
                print(f"\n当前页面截图保存到: {error_screenshot}")
                
                if os.environ.get('NO_WAIT') == '1':
                    print("非交互模式，跳过等待...")
                else:
                    input("\n按回车键关闭浏览器...")
                return
            
            # 在控制台页面，查找并点击"提交资料"按钮
            print("\n在控制台页面查找'提交资料'按钮...")
            submit_data_btn = page.locator('button:has-text("提交资料"), .ant-btn:has-text("提交资料"), a:has-text("提交资料")').first
            if submit_data_btn.count() > 0:
                print("找到'提交资料'按钮，正在点击...")
                submit_data_btn.click()
                page.wait_for_timeout(3000)
                
                # 等待页面跳转到补充资料页面
                page.wait_for_timeout(5000)
                current_url = page.url
                print(f"点击后页面URL: {current_url}")
            else:
                print("未找到'提交资料'按钮，尝试直接导航到补充资料页面...")
                supplement_url = "https://e.pay.sina.com.cn/web/reviewCheck"
                page.goto(supplement_url, timeout=60000)
                page.wait_for_timeout(5000)
                current_url = page.url
                print(f"导航后页面URL: {current_url}")
            
            # 如果仍不在补充资料页面，提示用户
            if "reviewCheck" not in current_url:
                print("\n警告: 当前不在补充资料页面")
                print("可能的原因:")
                print("1. 登录失败，请检查账号密码")
                print("2. 基本资料审核尚未通过")
                print("3. 已经在其他页面")
                print("\n请确保:")
                print("1. 已成功登录账号")
                print("2. 基本资料审核已通过")
                print("3. 当前在补充资料页面（URL包含 reviewCheck）")
                
                # 截图保存当前状态
                error_screenshot = get_screenshot_path(f"supplement_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                page.screenshot(path=error_screenshot, full_page=True)
                print(f"\n当前页面截图保存到: {error_screenshot}")
                
                if os.environ.get('NO_WAIT') == '1':
                    print("非交互模式，跳过等待...")
                else:
                    input("\n按回车键关闭浏览器...")
            
            # 执行补充资料页面填写
            if not fill_page4(page, account, business_type_num):
                print("补充资料页面执行失败")
                return
            
            print("\n" + "=" * 50)
            print("补充资料页面填写完成！")
            print("=" * 50)
            
            # 等待用户查看
            if os.environ.get('NO_WAIT') == '1':
                print("非交互模式，跳过等待，5秒后关闭浏览器...")
                page.wait_for_timeout(5000)
            else:
                input("按回车键关闭浏览器...")
            
        except Exception as e:
            print(f"执行出错: {e}")
            error_screenshot = get_screenshot_path(f"supplement_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            page.screenshot(path=error_screenshot, full_page=True)
            print(f"错误截图保存到: {error_screenshot}")
            
        finally:
            browser.close()


if __name__ == "__main__":
    import sys
    # 支持格式:
    #   python sina_register.py babweb 业务1
    #   python sina_register.py babweb 业务1 法人身份证
    #   python sina_register.py babweb 业务1 法人港澳通行证
    #   python sina_register.py babweb 业务1 法人护照
    #   python sina_register.py babweb 业务1 法人台胞证
    #   python sina_register.py babweb 业务1 补充资料  # 审核通过后填写补充资料页面
    #   python sina_register.py babweb 业务1 补充资料 babwebyw11202606161348  # 指定登录账号

    input_param = 'babweb 业务1'  # 默认
    id_type = None  # 默认使用配置文件中的证件类型
    is_supplement = False  # 是否为补充资料页面模式
    login_account = None  # 登录账号（用于补充资料页面）
    no_wait = '--no-wait' in sys.argv  # 非交互模式，跳过input等待
    os.environ['NO_WAIT'] = '1' if no_wait else '0'
    
    # 从 sys.argv 中移除 --no-wait，避免被当作位置参数解析
    filtered_argv = [a for a in sys.argv if a != '--no-wait']

    # 证件类型别名映射（支持简写）
    ID_TYPE_ALIASES = {
        "身份证": "身份证",
        "护照": "护照",
        "港澳通行证": "港澳居民来往内地通行证",
        "港澳居民来往内地通行证": "港澳居民来往内地通行证",
        "居住证": "港澳居民居住证",
        "港澳居民居住证": "港澳居民居住证",
    }

    if len(filtered_argv) > 4:
        # 格式: python sina_register.py babweb 业务1 补充资料 babwebyw11202606161348
        input_param = f"{filtered_argv[1]} {filtered_argv[2]}"
        third_arg = filtered_argv[3]
        fourth_arg = filtered_argv[4]
        
        # 检查是否为补充资料模式
        if third_arg == "补充资料" or third_arg == "supplement":
            is_supplement = True
            login_account = fourth_arg
            print(f"命令行参数解析: input_param={input_param}, 模式=补充资料页面, 登录账号={login_account}")
        else:
            # 解析证件类型（去掉"法人"前缀）
            if third_arg.startswith("法人"):
                id_type_short = third_arg[2:]  # 去掉"法人"两个字
            else:
                id_type_short = third_arg
            # 映射到完整的证件类型名称
            id_type = ID_TYPE_ALIASES.get(id_type_short, id_type_short)
            print(f"命令行参数解析: input_param={input_param}, id_type={id_type}")
    elif len(filtered_argv) > 3:
        # 格式: python sina_register.py babweb 业务2 法人身份证
        # 或: python sina_register.py babweb 业务1 补充资料
        input_param = f"{filtered_argv[1]} {filtered_argv[2]}"
        third_arg = filtered_argv[3]
        
        # 检查是否为补充资料模式
        if third_arg == "补充资料" or third_arg == "supplement":
            is_supplement = True
            print(f"命令行参数解析: input_param={input_param}, 模式=补充资料页面")
        else:
            # 解析证件类型（去掉"法人"前缀）
            if third_arg.startswith("法人"):
                id_type_short = third_arg[2:]  # 去掉"法人"两个字
            else:
                id_type_short = third_arg
            # 映射到完整的证件类型名称
            id_type = ID_TYPE_ALIASES.get(id_type_short, id_type_short)
            print(f"命令行参数解析: input_param={input_param}, id_type={id_type}")
    elif len(filtered_argv) > 2:
        # 格式: python sina_register.py babweb 业务2
        input_param = f"{filtered_argv[1]} {filtered_argv[2]}"
        print(f"命令行参数解析: input_param={input_param}, id_type=None")
    elif len(filtered_argv) > 1:
        # 可能是完整字符串或只有业务类型
        arg1 = filtered_argv[1]
        # 如果是"业务X"格式，自动补上 babweb 前缀
        if arg1.startswith("业务"):
            input_param = f"babweb {arg1}"
            print(f"命令行参数解析: 检测到业务类型，自动补全 -> input_param={input_param}")
        else:
            input_param = arg1
            print(f"命令行参数解析: input_param={input_param}, id_type=None")

    # 根据模式执行不同的流程
    if is_supplement:
        # 执行补充资料页面填写
        register_supplement(input_param, login_account=login_account)
    else:
        # 执行正常注册流程
        register_sina_member(input_param, id_type=id_type)
