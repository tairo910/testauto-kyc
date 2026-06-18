#!/usr/bin/env python3
"""
新浪支付会员注册 - 环境配置文件
包含敏感信息，请妥善保管
"""

import os

# 环境配置
ENVIRONMENT = "test"
API_URL = "https://test.pay.sina.com.cn"
BROWSER_TYPE = "chrome"
TIMEOUT = 60
HEADLESS_MODE = False

def get_backend_url():
    return "http://localhost:5001"

def get_unified_login_url():
    return "https://login.sina.com.cn/unified"

def get_oracle_config():
    """Oracle数据库配置"""
    return {
        'username': os.environ.get('DB_USERNAME', 'ermusr'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'host': os.environ.get('DB_HOST', '10.65.193.34'),
        'port': int(os.environ.get('DB_PORT', '1521')),
        'service_name': os.environ.get('DB_SERVICE_NAME', 'erm')
    }

def get_user_id_query_sql():
    return """SELECT a.audit_task_id FROM ERM.T_AUDIT_TASK a JOIN erm.t_enterprise e ON a.MEMBER_ID = e.MEMBER_ID WHERE e.LOGIN_NAME = :email"""

def get_sql_params():
    return {"email": "email"}

# 环境变量说明：
# export DB_USERNAME="ermusr"
# export DB_PASSWORD="your_password_here"
# export DB_HOST="10.65.193.34"
# export DB_PORT="1521"
# export DB_SERVICE_NAME="erm"