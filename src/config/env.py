#!/usr/bin/env python3
"""
环境配置模块
包含运行环境相关的配置，可通过前端页面维护
"""

# ==================== 环境配置 ====================

ENVIRONMENT = "test"

API_URL = "https://e.pay.sina.com.cn"

# ==================== 浏览器配置 ====================

BROWSER_TYPE = "chrome"

BROWSER_PATHS = {
    "chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "firefox": "/Applications/Firefox.app/Contents/MacOS/firefox",
    "edge": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
}

# ==================== 运行配置 ====================

TIMEOUT = 60

HEADLESS_MODE = False

DISABLE_AUTOMATION = True

# ==================== 日志配置 ====================

VERBOSE_LOGGING = True

SCREENSHOT_DIR = "./screenshots"

# ==================== 后端服务配置 ====================

BACKEND_HOST = "localhost"
BACKEND_PORT = 5001

# ==================== Oracle数据库配置 ====================

ORACLE_CONFIG = {
    'username': 'ermuser',
    'password': 'yxPFDImVfNn2hO',
    'host': '10.65.193.34',
    'port': 1521,
    'service_name': 'erm',
    'driver': 'oracledb'
}

# ==================== 用户ID查询SQL配置 ====================

USER_ID_QUERY_SQL = """
    SELECT a.audit_task_id 
    FROM ERM.T_AUDIT_TASK a 
    JOIN erm.t_enterprise e ON a.MEMBER_ID = e.MEMBER_ID 
    WHERE e.LOGIN_NAME = :email
"""

SQL_PARAMS = {
    'email': 'email'
}

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
    return f"http://{BACKEND_HOST}:{BACKEND_PORT}"

def get_oracle_config():
    return ORACLE_CONFIG

def get_user_id_query_sql():
    return USER_ID_QUERY_SQL

def get_sql_params():
    return SQL_PARAMS

def get_unified_login_url():
    return UNIFIED_LOGIN_URL
