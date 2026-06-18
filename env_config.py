#!/usr/bin/env python3
"""
新浪支付会员注册 - 环境配置文件
"""

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
    return {
        'username': 'ermusr',
        'password': 'yxPFDImVfNn2hO',
        'host': '10.65.193.34',
        'port': 1521,
        'service_name': 'erm'
    }

def get_user_id_query_sql():
    return """SELECT a.audit_task_id FROM ERM.T_AUDIT_TASK a JOIN erm.t_enterprise e ON a.MEMBER_ID = e.MEMBER_ID WHERE e.LOGIN_NAME = :email"""

def get_sql_params():
    return {"email": "email"}