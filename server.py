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
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

# 当前运行状态
running = False
current_progress = 0
progress_message = "等待启动"
current_audit_task_id = None

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
        global running, current_progress, progress_message, current_audit_task_id
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
                
                current_progress = 90
                progress_message = "正在查询审批任务ID..."
                print("步骤4: 查询审批任务ID")
                
                current_audit_task_id = None
                try:
                    from src.services.database_service import get_audit_task_id_by_email
                    audit_task_id = get_audit_task_id_by_email(email)
                    if audit_task_id:
                        current_audit_task_id = audit_task_id
                        print(f"✅ 查询到审批任务ID: {audit_task_id}")
                except Exception as e:
                    print(f"⚠️ 查询审批任务ID失败: {str(e)}")
                
                current_progress = 100
                progress_message = "注册完成！"
                print("✓ 注册成功")
            else:
                current_progress = 0
                if not error_msg:
                    error_msg = f"注册失败: {result.stderr[:100] if result.stderr else '未知错误'}"
                progress_message = error_msg
                print(f"✗ 注册失败: {error_msg}")
                
        except subprocess.TimeoutExpired:
            current_progress = 0
            progress_message = "注册超时！"
            print("✗ 注册超时")
        except Exception as e:
            current_progress = 0
            progress_message = f"执行失败: {str(e)}"
            print(f"✗ 执行异常: {str(e)}")
        finally:
            running = False
            print("=== 注册流程结束 ===\n")
    
    thread = threading.Thread(target=run_script)
    thread.start()
    
    return jsonify({'success': True, 'message': '注册流程已启动，浏览器窗口即将打开'})

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """获取注册进度"""
    print(f"获取进度: {current_progress}% - {progress_message}")
    return jsonify({
        'running': running,
        'progress': current_progress,
        'message': progress_message,
        'audit_task_id': current_audit_task_id
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
    """保存环境配置到 env_config.py"""
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
新浪支付会员注册 - 环境配置文件
"""

ENVIRONMENT = "{environment}"
API_URL = "{api_url}"
BROWSER_TYPE = "{browser_type}"
TIMEOUT = {timeout}
HEADLESS_MODE = False

def get_backend_url():
    return "http://localhost:5001"

def get_unified_login_url():
    return "https://login.sina.com.cn/unified"

def get_oracle_config():
    return {{
        'username': 'ermusr',
        'password': 'yxPFDImVfNn2hO',
        'host': '10.65.193.34',
        'port': 1521,
        'service_name': 'erm'
    }}

def get_user_id_query_sql():
    return "SELECT a.audit_task_id FROM ERM.T_AUDIT_TASK a JOIN erm.t_enterprise e ON a.MEMBER_ID = e.MEMBER_ID WHERE e.LOGIN_NAME = :email"

def get_sql_params():
    return {{"email": "email"}}
'''
        
        with open('env_config.py', 'w') as f:
            f.write(config_content)
        
        print(f"配置已保存: ENV={environment}, API_URL={api_url}, BROWSER={browser_type}, TIMEOUT={timeout}")
        return jsonify({'success': True, 'message': '配置保存成功'})
    except Exception as e:
        print(f"保存配置失败: {str(e)}")
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """测试API是否正常"""
    return jsonify({'success': True, 'message': '后端服务运行正常'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)