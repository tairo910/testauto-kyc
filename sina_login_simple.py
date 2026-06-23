#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新浪支付企业版登录脚本 - 简单版"""
from playwright.sync_api import sync_playwright
import time
import sys
import os

try:
    import config
except ImportError:
    print("错误: 未找到 config.py 配置文件")
    sys.exit(1)


def login_sina(account=None, password=None, captcha=None, sms_code=None, headless=False, max_retries=3):
    """登录新浪支付企业版"""
    login_account = (account or config.LOGIN_ACCOUNT or '').strip()
    login_password = (password or config.LOGIN_PASSWORD or '').strip()
    
    if not login_account or not login_password:
        print("错误: 未设置登录账号或密码")
        return None
    
    print(f"\n{'='*60}")
    print("新浪支付企业版登录")
    print(f"{'='*60}")
    print(f"登录账号: {login_account}")
    print(f"登录密码: {'*' * len(login_password)}")
    print(f"最大重试次数: {max_retries}")
    print(f"{'='*60}\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=['--ignore-certificate-errors', '--ignore-ssl-errors']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        page = context.new_page()
        
        for retry in range(max_retries):
            print(f"\n{'='*60}")
            print(f"第 {retry + 1}/{max_retries} 次尝试登录")
            print(f"{'='*60}")
            
            timestamp = time.strftime("%Y%m%d%H%M%S")
            screenshot_dir = f"screenshot/login/{login_account}_{timestamp}_retry{retry + 1}"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            try:
                print("\n正在访问登录页面: http://e.pay.sina.com.cn/site/login")
                page.goto("http://e.pay.sina.com.cn/site/login", wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(3000)
                
                page.screenshot(path=f"{screenshot_dir}/01_login_page.png", full_page=True)
                print("  已截图: 01_login_page.png")
                
                # 切换到管理员登录
                admin_tab = page.locator('text=管理员登录')
                if admin_tab.count() > 0:
                    admin_tab.click()
                    page.wait_for_timeout(1000)
                    print("  已切换到管理员登录")
                
                # 填写用户名（先点击输入框再填写）
                print("\n填写用户名...")
                username_input = page.locator('#loginName, input[name="username"], input[placeholder*="账号"], input[placeholder*="用户名"]').first
                username_input.click()
                print("  ✅ 已点击用户名输入框")
                page.wait_for_timeout(500)
                username_input.fill(login_account)
                print(f"  ✅ 已填写用户名: {login_account}")
                
                # 填写密码（先点击输入框再填写）
                print("\n填写密码...")
                
                # 先获取页面上所有输入框信息，帮助调试
                inputs_info = page.evaluate('''() => {
                    const inputs = document.querySelectorAll('input');
                    const info = [];
                    inputs.forEach((input, index) => {
                        info.push({
                            index: index,
                            id: input.id,
                            type: input.type,
                            name: input.name,
                            placeholder: input.placeholder,
                            className: input.className
                        });
                    });
                    return info;
                }''')
                print(f"  页面上的输入框数量: {len(inputs_info)}")
                for idx, info in enumerate(inputs_info):
                    print(f"    [{idx}] id={info['id']}, type={info['type']}, name={info['name']}, placeholder={info['placeholder']}")
                
                # 使用id=passwordEncrypt输入框，这是页面上显示的密码输入框
                password_input = page.locator('#passwordEncrypt').first
                
                # 检查并移除readonly和disabled属性
                page.evaluate('''() => {
                    const pwdInput = document.querySelector('#passwordEncrypt');
                    if (pwdInput) {
                        pwdInput.removeAttribute('readonly');
                        pwdInput.removeAttribute('disabled');
                    }
                }''')
                
                # 确保输入框获得焦点，再输入
                password_input.click()           # 确保点击获取焦点
                print("  ✅ 已点击密码输入框")
                page.wait_for_timeout(300)
                
                password_input.clear()           # 先清空
                password_input.press("End")      # 光标移到末尾
                password_input.type(login_password, delay=100)  # 逐字符输入，模拟手动输入
                print(f"  ✅ 已填写密码: {'*' * len(login_password)}")
                
                page.screenshot(path=f"{screenshot_dir}/02_filled_form.png", full_page=True)
                print("  已截图: 02_filled_form.png")
                
                # 填写验证码（自动输入1234）
                print("\n填写验证码...")
                captcha_input = page.locator('#graphicCode, input[name="captcha"], input[placeholder*="验证码"]').first
                captcha_input.click()
                print("  ✅ 已点击验证码输入框")
                page.wait_for_timeout(500)
                
                # 自动输入验证码1234
                captcha_code = "1234"
                captcha_input.fill(captcha_code)
                print(f"  ✅ 已填写验证码: {captcha_code}")
                
                # 点击下一步按钮
                print("\n点击下一步按钮...")
                next_btn = page.locator('button:has-text("下一步"), button:has-text("登 录"), button:has-text("登录"), #loginBtn, .login-btn, [type="submit"]').first
                next_btn.click()
                print("  ✅ 已点击下一步按钮")
                page.wait_for_timeout(3000)
                
                # 检查是否需要短信验证码
                sms_input = page.locator('input[placeholder*="短信验证码"], input[name*="sms"], #smsCode')
                if sms_input.count() > 0 and sms_input.is_visible():
                    print("  检测到短信验证码输入框")
                    
                    # 自动输入短信验证码111111
                    sms = "111111"
                    sms_input.fill(sms)
                    print(f"  已填写短信验证码: {sms}")
                    
                    # 点击确定/登录按钮
                    print("  点击确定按钮...")
                    login_btn = page.locator('button:has-text("确定"), button:has-text("登 录"), button:has-text("登录"), #loginBtn, .login-btn, [type="submit"]').first
                    login_btn.wait_for(state='visible', timeout=5000)
                    login_btn.click()
                    print("  已点击确定按钮")
                    page.wait_for_timeout(3000)
                
                # 检查登录结果
                current_url = page.url
                print(f"\n当前页面 URL: {current_url}")
                
                if 'console' in current_url or 'index' in current_url:
                    print(f"\n{'='*60}")
                    print("✅ 登录成功！")
                    print(f"{'='*60}")
                    
                    page.screenshot(path=f"{screenshot_dir}/05_login_success.png", full_page=True)
                    print("  已截图: 05_login_success.png")
                    
                    return page, context, browser
                
                elif 'login' in current_url:
                    print(f"\n{'='*60}")
                    print(f"❌ 第 {retry + 1} 次登录失败")
                    print(f"{'='*60}")
                    
                    page.screenshot(path=f"{screenshot_dir}/05_login_failed.png", full_page=True)
                    print("  已截图: 05_login_failed.png")
                    
                    if retry < max_retries - 1:
                        print(f"\n等待 3 秒后进行第 {retry + 2} 次尝试...")
                        page.wait_for_timeout(3000)
                
                else:
                    print(f"\n未知页面: {current_url}")
                    page.screenshot(path=f"{screenshot_dir}/05_unknown.png", full_page=True)
                    print("  已截图: 05_unknown.png")
                    
            except Exception as e:
                print(f"\n❌ 执行出错: {e}")
                try:
                    page.screenshot(path=f"{screenshot_dir}/error.png", full_page=True)
                    print("  已截图: error.png")
                except:
                    pass
        
        print(f"\n{'='*60}")
        print("已达到最大重试次数，登录失败")
        print(f"{'='*60}")
        
        browser.close()
        return None


if __name__ == "__main__":
    account = None
    password = None
    captcha = None
    sms_code = None
    
    # 从命令行参数获取
    if len(sys.argv) > 1:
        account = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]
    if len(sys.argv) > 3:
        captcha = sys.argv[3]
    if len(sys.argv) > 4:
        sms_code = sys.argv[4]
    
    # 如果命令行没有传入，从配置文件读取
    if not account:
        account = getattr(config, 'LOGIN_ACCOUNT', '')
    if not password:
        password = getattr(config, 'LOGIN_PASSWORD', '')
    
    # 如果还是没有，交互式输入
    if not account:
        account = input("请输入登录账号: ")
    if not password:
        from getpass import getpass
        password = getpass("请输入登录密码: ")
    
    print(f"\n登录账号: {account}")
    print(f"登录密码: {'*' * len(password)}")
    
    result = login_sina(account=account, password=password, captcha=captcha, sms_code=sms_code)
    if result:
        page, context, browser = result
        print("\n✅ 登录成功！浏览器将保持打开...")
        input("按回车键关闭浏览器...")
        browser.close()
    else:
        print("\n❌ 登录失败，请检查账号密码或验证码")
