#!/usr/bin/env python3
"""
新浪支付会员注册 - 补充资料页面脚本（业务1、业务2）
使用 Playwright 自动填写补充资料页面
先登录，再进入补充资料页面

执行方式:
    python3 sina_register_buchong.py 账号 [密码]
    python3 sina_register_buchong.py babwebyw11202606161803
"""

import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

try:
    import config
except ImportError:
    print("错误: 未找到 config.py 配置文件")
    sys.exit(1)

try:
    from sina_login_simple import login_sina
except ImportError:
    print("错误: 未找到 sina_login_simple.py")
    sys.exit(1)


CURRENT_SCREENSHOT_DIR = None


def get_screenshot_path(filename):
    """获取截图保存路径"""
    if CURRENT_SCREENSHOT_DIR:
        return os.path.join(CURRENT_SCREENSHOT_DIR, filename)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "screenshot", "buchong", filename)


def create_screenshot_dir(account):
    """创建截图文件夹"""
    global CURRENT_SCREENSHOT_DIR
    base_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_dir = os.path.join(base_dir, "screenshot", "buchong", f"{account}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
        print(f"创建截图文件夹: {screenshot_dir}")
    CURRENT_SCREENSHOT_DIR = screenshot_dir
    return screenshot_dir


def fill_page4(page, account):
    """
    填写补充资料页面（页面4）- 仅业务1、业务2审核通过后进入
    URL: https://e.pay.sina.com.cn/web/reviewCheck
    
    参数:
        page: Playwright页面对象
        account: 登录账号
    """
    print("\n" + "="*50)
    print("页面4：补充资料审核")
    print("="*50)
    
    page.wait_for_timeout(3000)
    
    screenshot_path = get_screenshot_path(f"page4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"页面4截图保存到: {screenshot_path}")
    
    print("\n填写结算账户...")
    
    bank_account_name_input = page.locator('input[placeholder*="银行账户名"], input[name*="bankAccountName"]').first
    if bank_account_name_input.count() > 0:
        bank_account_name_input.fill(config.BANK_ACCOUNT_NAME)
        print(f"  已填写银行账户名: {config.BANK_ACCOUNT_NAME}")
    
    print("  选择开户银行...")
    bank_select = page.locator('.ant-form-item:has-text("开户银行") .ant-select').first
    if bank_select.count() > 0:
        js_result = page.evaluate(f'''() => {{
            const selects = document.querySelectorAll('.ant-select');
            for (const select of selects) {{
                const parent = select.closest('.ant-form-item');
                if (parent && parent.textContent.includes('开户银行')) {{
                    const selected = select.querySelector('.ant-select-selection-selected-value, .ant-select-selection-item');
                    if (selected && selected.textContent.includes('{config.BANK_NAME}')) {{
                        return '已选中';
                    }}
                    select.click();
                    setTimeout(() => {{
                        const options = document.querySelectorAll('.ant-select-dropdown-menu-item, .ant-select-item');
                        for (const opt of options) {{
                            if (opt.textContent.includes('{config.BANK_NAME}')) {{
                                opt.click();
                                return '已点击';
                            }}
                        }}
                    }}, 500);
                    return '已触发选择';
                }}
            }}
            return '未找到开户银行下拉框';
        }}''')
        print(f"    {js_result}")
        page.wait_for_timeout(2000)
    
    bank_account_input = page.locator('input[placeholder*="企业银行账号"], input[name*="bankAccount"]').first
    if bank_account_input.count() > 0:
        bank_account_input.fill(config.BANK_ACCOUNT_NUMBER)
        print(f"  已填写企业银行账号: {config.BANK_ACCOUNT_NUMBER}")
    
    cert_path = os.path.join(config.ATTACHMENT_DIR, config.FILE_BANK_CERTIFICATE)
    if os.path.exists(cert_path):
        print(f"\n  上传开户证明材料...")
        js_result = page.evaluate(f'''() => {{
            const formItems = document.querySelectorAll('.ant-form-item');
            for (const item of formItems) {{
                if (item.textContent.includes('开户证明材料')) {{
                    const inputs = item.querySelectorAll('input[type="file"]');
                    if (inputs.length > 0) {{
                        inputs[0].style.display = 'block';
                        inputs[0].style.visibility = 'visible';
                        inputs[0].style.opacity = '1';
                        return '找到开户证明材料区域内的文件上传框';
                    }}
                }}
            }}
            return '未找到开户证明材料区域内的文件上传框';
        }}''')
        print(f"    {js_result}")
        
        file_input = page.locator('.ant-form-item:has-text("开户证明材料") input[type="file"]').first
        if file_input.count() > 0:
            file_input.set_input_files(cert_path)
            print(f"    已上传开户证明材料")
            page.wait_for_timeout(3000)
        else:
            all_file_inputs = page.locator('input[type="file"]').all()
            if len(all_file_inputs) >= 1:
                all_file_inputs[0].set_input_files(cert_path)
                print(f"    已上传开户证明材料到第1个上传框")
                page.wait_for_timeout(3000)
    
    print("\n填写受益人信息...")
    
    if config.BENEFICIARIES:
        for index, beneficiary in enumerate(config.BENEFICIARIES):
            print(f"\n  第 {index + 1} 个受益人:")
            
            # 先点击【新增受益人】按钮
            add_btn = page.locator('button:has-text("添加受益人")').first
            if add_btn.count() > 0:
                add_btn.click()
                print(f"    点击了【添加受益人】按钮")
                page.wait_for_timeout(2000)
            else:
                print(f"    未找到【添加受益人】按钮，可能页面已有一个默认的受益人区域")
            
            # 填写受益人信息
            print(f"    填写姓名: {beneficiary['name']}")
            name_input = page.locator(f'input[placeholder*="请输入姓名"]').last
            if name_input.count() > 0:
                name_input.fill(beneficiary['name'])
                page.wait_for_timeout(500)
            
            print(f"    选择证件类型: {beneficiary['id_type']}")
            id_type_select = page.locator('.ant-form-item:has-text("证件类型") .ant-select').last
            if id_type_select.count() > 0:
                id_type_select.click()
                page.wait_for_timeout(1000)
                id_type_option = page.locator(f'.ant-select-dropdown-menu-item:has-text("{beneficiary["id_type"]}"), .ant-select-item:has-text("{beneficiary["id_type"]}")').first
                if id_type_option.count() > 0:
                    id_type_option.click()
                page.wait_for_timeout(1000)
            
            print(f"    填写身份证号: {beneficiary['id_number']}")
            id_number_input = page.locator(f'input[placeholder*="请输入身份证号码"]').last
            if id_number_input.count() > 0:
                id_number_input.fill(beneficiary['id_number'])
                page.wait_for_timeout(500)
            
            print(f"    勾选长期有效")
            long_term_checkbox = page.locator('.ant-checkbox-wrapper:has-text("长期"), label:has-text("长期")').last
            if long_term_checkbox.count() > 0:
                long_term_checkbox.click()
                page.wait_for_timeout(500)
            
            print(f"    填写居住地址: {beneficiary['address']}")
            address_input = page.locator(f'input[placeholder*="请输入居住地址"]').last
            if address_input.count() > 0:
                address_input.fill(beneficiary['address'])
                page.wait_for_timeout(500)
    
    print("\n选择开户意愿核实方式...")
    
    # 先选择"上传开户意愿视频"
    print("  选择: 上传开户意愿视频...")
    video_radio = page.locator('.ant-radio-wrapper:has-text("上传开户意愿视频")').first
    if video_radio.count() > 0:
        video_radio.click()
        print("    已点击'上传开户意愿视频'单选框")
    else:
        # 备用方式：使用JS
        page.evaluate('''() => {
            const radios = document.querySelectorAll('.ant-radio-wrapper');
            for (const wrapper of radios) {
                if (wrapper.textContent.includes('上传开户意愿视频')) {
                    wrapper.click();
                    return '已点击';
                }
            }
            return '未找到';
        }''')
        print("    已通过JS点击'上传开户意愿视频'")
    page.wait_for_timeout(2000)
    
    # 再选择"由法人本人认证"
    print("  选择: 由法人本人认证...")
    legal_radio = page.locator('.ant-radio-wrapper:has-text("由法人本人认证")').first
    if legal_radio.count() > 0:
        legal_radio.click()
        print("    已点击'由法人本人认证'单选框")
    else:
        # 备用方式：使用JS
        page.evaluate('''() => {
            const radios = document.querySelectorAll('.ant-radio-wrapper');
            for (const wrapper of radios) {
                if (wrapper.textContent.includes('由法人本人认证')) {
                    wrapper.click();
                    return '已点击';
                }
            }
            return '未找到';
        }''')
        print("    已通过JS点击'由法人本人认证'")
    page.wait_for_timeout(2000)
    
    # 滚动到页面底部
    print("\n  滚动到页面底部...")
    page.evaluate('''() => {
        window.scrollTo(0, document.body.scrollHeight);
    }''')
    page.wait_for_timeout(1000)
    
    video_path = os.path.join(config.ATTACHMENT_DIR, config.FILE_VIDEO)
    if os.path.exists(video_path):
        print(f"\n  上传开户意愿视频...")
        
        # 等待上传区域显示
        page.wait_for_timeout(2000)
        
        # 找到页面底部最下面的上传按钮（包含"上传"或"点击上传"文字的按钮）
        # 注意：要找最下面的，不是最上面开户证明材料的上传按钮
        all_upload_btns = page.locator('button:has-text("上传"), button:has-text("点击上传"), .ant-btn:has-text("上传")').all()
        print(f"    当前页面上传按钮数量: {len(all_upload_btns)}")
        
        # 不点击上传按钮，直接找到最下面的文件上传框并上传视频
        file_inputs = page.locator('input[type="file"]').all()
        print(f"    当前页面文件上传框数量: {len(file_inputs)}")
        
        if len(file_inputs) >= 2:
            # 使用最后一个文件上传框（最下面的，应该是开户意愿视频的）
            last_file_input = file_inputs[-1]
            print(f"    使用最后一个（最下面的）文件上传框")
            last_file_input.set_input_files(video_path)
            print(f"    已上传开户意愿视频: {os.path.basename(video_path)}")
            page.wait_for_timeout(3000)
        elif len(file_inputs) == 1:
            print(f"    页面只有1个文件上传框")
            file_inputs[0].set_input_files(video_path)
            print(f"    已上传开户意愿视频: {os.path.basename(video_path)}")
            page.wait_for_timeout(3000)
        else:
            print(f"    未找到文件上传框")
    
    screenshot_path = get_screenshot_path(f"page4_filled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"\n页面4填写完成截图保存到: {screenshot_path}")
    
    print("\n点击【提交】按钮...")
    
    page.evaluate('''() => {
        window.scrollTo(0, document.body.scrollHeight);
    }''')
    page.wait_for_timeout(2000)
    
    page.evaluate('''() => {
        const buttons = document.querySelectorAll('button');
        let result = [];
        for (let btn of buttons) {
            const text = btn.textContent ? btn.textContent.trim() : '';
            const className = btn.className || '';
            const style = btn.style.cssText || '';
            const disabled = btn.disabled || false;
            result.push({ text, className, disabled });
        }
        console.log('页面上所有按钮:', result);
        return result;
    }''')
    
    submit_btn = None
    selectors = [
        'button.ant-btn-primary:has-text("提 交")',
        'button:has-text("提 交")',
        'button.ant-btn-primary:has-text("提交")',
        'button:has-text("提交")',
        '.ant-btn-primary',
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("保存")',
        '.ant-btn-primary:not(:disabled)',
        '.ant-btn:not(:disabled)',
    ]
    
    for selector in selectors:
        btn = page.locator(selector).first
        if btn.count() > 0:
            submit_btn = btn
            print(f"  找到提交按钮: {selector}")
            break
    
    if submit_btn:
        submit_btn.click()
        print("  已点击提交按钮")
        page.wait_for_timeout(5000)
        
        final_screenshot = get_screenshot_path(f"page4_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        page.screenshot(path=final_screenshot, full_page=True)
        print(f"页面4最终截图保存到: {final_screenshot}")
        print("\n页面4提交完成！")
        return True
    else:
        print("  未找到提交按钮，尝试通过JS查找...")
        js_result = page.evaluate('''
            () => {
                const buttons = document.querySelectorAll('button, input[type="submit"]');
                for (const btn of buttons) {
                    const text = btn.textContent ? btn.textContent.trim() : '';
                    const className = btn.className || '';
                    if (text.includes('提交') || text.includes('保存') || 
                        className.includes('ant-btn-primary') && !btn.disabled) {
                        btn.click();
                        return text;
                    }
                }
                return null;
            }
        ''')
        if js_result:
            print(f"  JS找到并点击: {js_result}")
        else:
            print("  JS也未找到提交按钮")
            page.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.classList.contains('ant-btn-primary') && !btn.disabled) {
                        btn.click();
                        return btn.textContent.trim();
                    }
                }
                return '未找到可用的ant-btn-primary';
            }''')
        page.wait_for_timeout(5000)
        
        final_screenshot = get_screenshot_path(f"page4_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        page.screenshot(path=final_screenshot, full_page=True)
        print(f"页面4最终截图保存到: {final_screenshot}")
        print("\n页面4操作完成！")
        return True


def main():
    """主函数：先登录，再执行补充资料页面"""
    account = None
    password = None

    if len(sys.argv) > 1:
        account = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]

    if not account:
        print("错误: 请提供登录账号")
        print("使用方式: python3 sina_register_buchong.py 账号 [密码]")
        sys.exit(1)

    create_screenshot_dir(account)

    print("\n" + "="*60)
    print("新浪支付会员注册 - 补充资料页面")
    print("="*60)
    print(f"登录账号: {account}")
    print("="*60)

    print("\n第一步：登录新浪支付企业版...")
    page, context, browser, playwright = login_sina(account=account, password=password, headless=False, max_retries=3)

    if not page:
        print("\n❌ 登录失败，无法继续执行补充资料页面")
        sys.exit(1)

    print("\n✅ 登录成功！")
    print("\n第二步：进入补充资料页面...")

    review_url = "https://e.pay.sina.com.cn/web/reviewCheck"
    max_retries = 6          # 最大重试次数
    retry_interval = 10     # 重试间隔（秒）
    success = False

    for attempt in range(1, max_retries + 1):
        print(f"\n--- 第 {attempt}/{max_retries} 次尝试访问补充资料页面 ---")
        print(f"正在访问补充资料页面: {review_url}")
        page.goto(review_url, timeout=120000)
        page.wait_for_timeout(5000)

        current_url = page.url
        print(f"当前页面 URL: {current_url}")

        if "reviewCheck" in current_url:
            print(f"\n✅ 成功进入补充资料页面（第 {attempt} 次尝试）")
            success = fill_page4(page, account)
            break
        else:
            print(f"\n⚠️ 当前页面不是补充资料页面: {current_url}")
            if attempt < max_retries:
                print(f"等待 {retry_interval} 秒后重试（审批可能尚未生效）...")
                page.wait_for_timeout(retry_interval * 1000)
                # 刷新登录状态，重新访问
                print("刷新页面...")
                page.goto("http://e.pay.sina.com.cn/console/index", timeout=30000)
                page.wait_for_timeout(2000)
            else:
                print(f"\n❌ 已重试 {max_retries} 次，仍无法进入补充资料页面")
                print("请检查账号是否已通过审批")
                page.screenshot(path=get_screenshot_path("not_review_page.png"), full_page=True)

    print("\n浏览器将保持打开 10 秒...")
    page.wait_for_timeout(10000)

    try:
        browser.close()
        playwright.stop()
        print("\n浏览器已关闭")
    except:
        pass

    if success:
        print("\n✅ 补充资料页面操作完成！")
        sys.exit(0)
    else:
        print("\n❌ 补充资料页面操作失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
