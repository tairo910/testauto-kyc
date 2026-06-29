#!/usr/bin/env python3
"""
新浪支付会员注册 - 后端服务
提供REST API接口
"""

import os
import sys
import json
import subprocess
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))

# 加载 .env 文件
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

app = Flask(__name__)
CORS(app)

# 当前运行状态
running = False
current_progress = 0
progress_message = "等待启动"
current_audit_task_id = None
current_account = None
current_email = None
current_password = None

@app.route('/api/register', methods=['POST'])
def start_register():
    """启动注册流程"""
    global running, current_progress, progress_message
    
    if running:
        return jsonify({'success': False, 'message': '注册流程正在进行中，请稍候'})
    
    data = request.get_json()
    business_type_full = data.get('business_type', '业务1')
    account = data.get('account', '')
    password = data.get('password', '')
    email = data.get('email', '')
    
    # 业务类型映射
    business_type_mapping = {
        '新浪支付商户-综合业务': '业务1',
        '新浪支付商户-收款业务': '业务2',
        '商户的合作机构-综合业务': '业务3',
        '商户的合作机构-收款业务': '业务4',
        '业务1': '业务1',
        '业务2': '业务2',
        '业务3': '业务3',
        '业务4': '业务4'
    }
    business_type = business_type_mapping.get(business_type_full, '业务1')
    
    print(f"业务类型(完整): {business_type_full}")
    print(f"业务类型(脚本参数): {business_type}")
    print(f"账号: {account}")
    print(f"密码: {password}")
    print(f"邮箱: {email}")
    
    running = True
    current_progress = 0
    progress_message = "正在启动..."
    
    def run_script():
        global running, current_progress, progress_message, current_audit_task_id, current_account, current_email, current_password
        try:
            current_progress = 10
            progress_message = "正在启动浏览器..."
            print("步骤1: 启动浏览器")
            
            current_progress = 30
            progress_message = "正在执行注册脚本..."
            print("步骤2: 执行注册脚本")
            
            cmd = ['python3', 'sina_register.py', 'babweb', business_type]
            print(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=os.path.dirname(__file__),
                timeout=300
            )
            
            print(f"返回码: {result.returncode}")
            if result.stdout:
                print(f"标准输出:\n{result.stdout}")
            if result.stderr:
                print(f"错误输出:\n{result.stderr}")
            
            has_error = False
            error_msg = ""
            
            if result.returncode != 0:
                has_error = True
                error_msg = f"脚本返回码错误: {result.returncode}"
            elif "执行出错" in result.stdout or "Error" in result.stdout or "error" in result.stdout.lower():
                has_error = True
                if "执行出错:" in result.stdout:
                    start_idx = result.stdout.find("执行出错:")
                    end_idx = result.stdout.find("\n", start_idx)
                    error_msg = result.stdout[start_idx:end_idx]
                else:
                    error_msg = "脚本执行过程中发生错误"
            elif "Timeout" in result.stdout:
                has_error = True
                error_msg = "脚本执行超时"
            
            if not has_error and result.returncode == 0:
                current_progress = 80
                progress_message = "脚本执行完成..."
                print("步骤3: 脚本执行完成")
                
                # 解析注册脚本输出，提取账号和邮箱
                parsed_account = None
                parsed_email = None
                parsed_password = "sina@1234"
                
                for line in result.stdout.split('\n'):
                    if '登录账号:' in line and '****' not in line:
                        parsed_account = line.split(':')[1].strip()
                    elif '注册邮箱:' in line and '@' in line:
                        parsed_email = line.split(':')[1].strip()
                
                # 保存解析结果
                if parsed_account:
                    current_account = parsed_account
                    print(f"✅ 解析到注册账号: {current_account}")
                if parsed_email:
                    current_email = parsed_email
                    print(f"✅ 解析到注册邮箱: {current_email}")
                current_password = parsed_password
                
                current_progress = 90
                progress_message = "正在查询审批任务ID..."
                print("步骤4: 查询审批任务ID")
                
                current_audit_task_id = None
                try:
                    from src.services.database_service import get_audit_task_id_by_email
                    # 使用解析到的邮箱查询，如果没有则使用前端传入的邮箱
                    query_email = parsed_email if parsed_email else email
                    if query_email:
                        audit_task_id = get_audit_task_id_by_email(query_email)
                        if audit_task_id:
                            current_audit_task_id = audit_task_id
                            print(f"✅ 查询到审批任务ID: {audit_task_id}")
                except Exception as e:
                    print(f"⚠️ 查询审批任务ID失败: {str(e)}")
                
                # 判断注册成功的条件：必须查询到审批任务ID
                if current_audit_task_id:
                    current_progress = 100
                    progress_message = "注册完成！"
                    print("✓ 注册成功（已查询到审批任务ID）")
                else:
                    current_progress = 0
                    current_account = None
                    current_email = None
                    current_password = None
                    error_msg = f"注册失败: 未能查询到审批任务ID，请检查注册是否成功"
                    progress_message = error_msg
                    print(f"✗ 注册失败: {error_msg}")
            else:
                current_progress = 0
                current_account = None
                current_email = None
                current_password = None
                if not error_msg:
                    error_msg = f"注册失败: {result.stderr[:100] if result.stderr else '未知错误'}"
                progress_message = error_msg
                print(f"✗ 注册失败: {error_msg}")
                
        except subprocess.TimeoutExpired:
            current_progress = 0
            progress_message = "注册超时！"
            current_account = None
            current_email = None
            current_password = None
            print("✗ 注册超时")
        except Exception as e:
            current_progress = 0
            progress_message = f"执行失败: {str(e)}"
            current_account = None
            current_email = None
            current_password = None
            print(f"✗ 执行异常: {str(e)}")
        finally:
            running = False
            print("=== 注册流程结束 ===\n")
    
    thread = threading.Thread(target=run_script)
    thread.start()
    
    return jsonify({'success': True, 'message': '注册流程已启动，浏览器窗口即将打开'})

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """获取注册进度和注册结果"""
    print(f"获取进度: {current_progress}% - {progress_message}")
    return jsonify({
        'running': running,
        'progress': current_progress,
        'message': progress_message,
        'audit_task_id': current_audit_task_id,
        'account': current_account,
        'email': current_email,
        'password': current_password
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取环境配置"""
    try:
        import env_config
        config = {
            'environment': env_config.ENVIRONMENT,
            'api_url': env_config.API_URL,
            'browser_type': env_config.BROWSER_TYPE,
            'timeout': env_config.TIMEOUT,
            'headless_mode': env_config.HEADLESS_MODE,
            'backend_url': env_config.get_backend_url(),
            'unified_login_url': env_config.get_unified_login_url(),
            'env_urls': {
                'test': 'https://test.pay.sina.com.cn',
                'development': 'https://dev.pay.sina.com.cn',
                'production': 'https://e.pay.sina.com.cn'
            },
            'browser_paths': {
                'chrome': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                'firefox': '/Applications/Firefox.app/Contents/MacOS/firefox',
                'edge': '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
            }
        }
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def save_config():
    """保存环境配置到 src/config/env.py"""
    try:
        data = request.get_json()
        environment = data.get('environment', 'test')
        api_url = data.get('api_url', '')
        browser_type = data.get('browser_type', 'chrome')
        timeout = data.get('timeout', 60)
        
        import re
        if '/web/register' in api_url:
            api_url = re.sub(r'/web/register/?$', '', api_url)
        
        config_content = f'''#!/usr/bin/env python3
"""
环境配置模块
包含运行环境相关的配置，可通过前端页面维护
"""

# ==================== 环境配置 ====================

ENVIRONMENT = "{environment}"

API_URL = "{api_url}"

# ==================== 浏览器配置 ====================

BROWSER_TYPE = "{browser_type}"

BROWSER_PATHS = {{
    "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
    "edge": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
}}

# ==================== 运行配置 ====================

TIMEOUT = {timeout}

HEADLESS_MODE = False

DISABLE_AUTOMATION = True

# ==================== 日志配置 ====================

VERBOSE_LOGGING = True

SCREENSHOT_DIR = "./screenshots"

# ==================== 后端服务配置 ====================

BACKEND_HOST = "localhost"
BACKEND_PORT = 5001

# ==================== Oracle数据库配置 ====================

ORACLE_CONFIG = {{
    'username': 'ermuser',
    'password': 'yxPFDImVfNn2hO',
    'host': '10.65.193.34',
    'port': 1521,
    'service_name': 'erm',
    'driver': 'oracledb'
}}

# ==================== 用户ID查询SQL配置 ====================

USER_ID_QUERY_SQL = """
    SELECT a.audit_task_id 
    FROM ERM.T_AUDIT_TASK a 
    JOIN erm.t_enterprise e ON a.MEMBER_ID = e.MEMBER_ID 
    WHERE e.LOGIN_NAME = :email
"""

SQL_PARAMS = {{
    'email': 'email'
}}

# ==================== 统一登录系统配置 ====================

UNIFIED_LOGIN_URL = "https://login.sina.com.cn/unified"

# ==================== 辅助函数 ====================

def get_api_url():
    return API_URL

def get_browser_path():
    return BROWSER_PATHS.get(BROWSER_TYPE, BROWSER_PATHS["chrome"])

def get_timeout():
    return TIMEOUT

def get_headless_mode():
    return HEADLESS_MODE

def get_environment():
    return ENVIRONMENT

def get_browser_type():
    return BROWSER_TYPE

def get_backend_url():
    return f"http://{{BACKEND_HOST}}:{{BACKEND_PORT}}"

def get_oracle_config():
    return ORACLE_CONFIG

def get_user_id_query_sql():
    return USER_ID_QUERY_SQL

def get_sql_params():
    return SQL_PARAMS

def get_unified_login_url():
    return UNIFIED_LOGIN_URL
'''
        
        config_path = os.path.join(os.path.dirname(__file__), 'src', 'config', 'env.py')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"配置已保存到 {config_path}: ENV={environment}, API_URL={api_url}, BROWSER={browser_type}, TIMEOUT={timeout}")
        return jsonify({'success': True, 'message': '配置保存成功'})
    except Exception as e:
        print(f"保存配置失败: {str(e)}")
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """测试API是否正常"""
    return jsonify({'success': True, 'message': '后端服务运行正常'})

@app.route('/api/getUserId', methods=['POST'])
def get_user_id():
    """根据邮箱查询审批任务ID"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        if not email:
            return jsonify({'success': False, 'message': '邮箱不能为空'})
        
        from src.services.database_service import get_audit_task_id_by_email
        audit_task_id = get_audit_task_id_by_email(email)
        if audit_task_id:
            return jsonify({'success': True, 'audit_task_id': audit_task_id})
        else:
            return jsonify({'success': False, 'message': '未查询到审批任务ID'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def index():
    """提供前端页面"""
    return send_from_directory(os.path.dirname(__file__), 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)