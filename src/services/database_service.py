#!/usr/bin/env python3
"""
数据库服务模块
提供Oracle数据库查询功能
"""

import oracledb
from src.config.env import (
    get_oracle_config,
    get_user_id_query_sql,
    get_sql_params,
    get_unified_login_url
)

def get_user_id_by_login(login_name):
    config = get_oracle_config()
    query_sql = get_user_id_query_sql()
    sql_params = get_sql_params()
    
    if not query_sql:
        print("错误: 未配置查询SQL")
        return None
    
    try:
        with oracledb.connect(
            user=config['username'],
            password=config['password'],
            dsn=f"{config['host']}:{config['port']}/{config['service_name']}"
        ) as connection:
            with connection.cursor() as cursor:
                params = {sql_params['email']: login_name}
                cursor.execute(query_sql, **params)
                result = cursor.fetchone()
                
                if result:
                    audit_task_id = str(result[0])
                    print(f"查询到审批任务ID: {audit_task_id}")
                    return audit_task_id
                else:
                    print(f"未找到审批任务ID，查询条件: {login_name}")
                    return None
                    
    except Exception as e:
        print(f"Oracle查询失败: {str(e)}")
        return None

def get_audit_task_id_by_email(email):
    return get_user_id_by_login(email)

def execute_custom_sql(sql, params=None):
    config = get_oracle_config()
    
    try:
        with oracledb.connect(
            user=config['username'],
            password=config['password'],
            dsn=f"{config['host']}:{config['port']}/{config['service_name']}"
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params or {})
                return cursor.fetchall()
                
    except Exception as e:
        print(f"SQL执行失败: {str(e)}")
        return None
