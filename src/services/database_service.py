#!/usr/bin/env python3
"""
数据库服务模块
提供Oracle数据库查询功能
支持连接复用：先连接数据库，再进行查询
"""

import os
import oracledb
from src.config.env import (
    get_oracle_config,
    get_user_id_query_sql,
    get_sql_params,
    get_unified_login_url
)

_oracle_client_initialized = False
try:
    oracledb.init_oracle_client(lib_dir=os.path.expanduser("~/.cache/instantclient"))
    print(f"[OK] Oracle Instant Client initialized (~/.cache/instantclient)")
    _oracle_client_initialized = True
except Exception as e:
    print(f"[WARN] Failed to initialize Oracle Instant Client: {e}")

_connection = None

def _list_oracle_services(host, port):
    """
    通过 TNS ping 监听器，列出该 Oracle 实例上已注册的所有 service
    用于诊断 service_name 配置错误问题 (ORA-12514)
    """
    services = []
    try:
        # 尝试连接多个常见 service_name
        common_services = ['orcl', 'ORCL', 'xe', 'XE', 'erm', 'ERM', 'test', 'TEST', 'pay', 'PAY']
        for svc in common_services:
            try:
                test_conn = oracledb.connect(
                    user="",
                    password="",
                    dsn=f"{host}:{port}/{svc}",
                    mode=oracledb.SYSDBA if svc.upper() in ['ERM', 'PAY'] else oracledb.DEFAULT_AUTH
                )
                test_conn.close()
                services.append(svc)
            except oracledb.DatabaseError:
                continue
            except Exception:
                continue
    except Exception:
        pass
    return services

def connect_database():
    """
    建立数据库连接
    在查询数据库之前需要先调用此方法
    """
    global _connection

    if _connection is not None:
        try:
            _connection.ping()
            print("数据库已连接，跳过重复连接")
            return True
        except Exception:
            try:
                _connection.close()
            except Exception:
                pass
            _connection = None

    config = get_oracle_config()
    
    try:
        _connection = oracledb.connect(
            user=config['username'],
            password=config['password'],
            dsn=f"{config['host']}:{config['port']}/{config['service_name']}"
        )
        print(f"✅ 数据库连接成功 (host: {config['host']}, port: {config['port']}, service: {config['service_name']})")
        return True
    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        print(f"❌ 数据库连接失败: {error_obj.message}")
        print(f"连接参数: host={config['host']}, port={config['port']}, service_name={config['service_name']}, username={config['username']}")
        
        # ORA-12514: service 未注册，尝试获取可用的 service 列表
        if 'DPY-6001' in str(error_obj.message) or '12514' in str(error_obj.message) or 'not registered' in str(error_obj.message).lower():
            print("💡 提示: service_name 未在 Oracle 监听器中注册")
            print("🔍 正在尝试扫描该 Oracle 实例上可能可用的 service_name...")
            available = _list_oracle_services(config['host'], config['port'])
            if available:
                print(f"✅ 发现以下可用的 service_name: {available}")
                print(f"💡 请将 env.py 中 ORACLE_CONFIG['service_name'] 修改为上述任一值")
            else:
                print("⚠️ 未能发现可用的 service_name，请联系 DBA 获取正确配置")
        # ORA-01017: 用户名/密码错误
        elif 'DPY-4011' in str(error_obj.message) or '01017' in str(error_obj.message):
            print("💡 提示: 用户名或密码错误，请检查 env.py 中的 ORACLE_CONFIG 配置")
        # ORA-12541: 无法连接
        elif 'DPY-6005' in str(error_obj.message) or '12541' in str(error_obj.message):
            print("💡 提示: 无法连接到数据库，请检查网络和数据库服务状态")
        
        return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        print(f"连接参数: host={config['host']}, port={config['port']}, service_name={config['service_name']}, username={config['username']}")
        return False

def is_connected():
    """
    检查数据库连接状态
    """
    if _connection is None:
        return False
    
    try:
        _connection.ping()
        return True
    except Exception:
        return False

def close_connection():
    """
    关闭数据库连接
    """
    global _connection
    
    if _connection is not None:
        try:
            _connection.close()
            print("✅ 数据库连接已关闭")
        except Exception as e:
            print(f"关闭连接时出错: {str(e)}")
        finally:
            _connection = None

def get_user_id_by_login(login_name):
    """
    根据登录名查询用户ID
    如果数据库未连接，会自动尝试连接
    """
    if not is_connected():
        print("数据库未连接，正在尝试连接...")
        if not connect_database():
            print("错误: 数据库连接失败，无法查询")
            return None
    
    query_sql = get_user_id_query_sql()
    sql_params = get_sql_params()
    
    if not query_sql:
        print("错误: 未配置查询SQL")
        return None
    
    try:
        with _connection.cursor() as cursor:
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
    """
    根据邮箱查询审批任务ID
    如果数据库未连接，会自动尝试连接
    """
    return get_user_id_by_login(email)

def execute_custom_sql(sql, params=None):
    """
    执行自定义SQL
    如果数据库未连接，会自动尝试连接
    """
    if not is_connected():
        print("数据库未连接，正在尝试连接...")
        if not connect_database():
            print("错误: 数据库连接失败，无法执行SQL")
            return None
    
    try:
        with _connection.cursor() as cursor:
            cursor.execute(sql, params or {})
            return cursor.fetchall()
            
    except Exception as e:
        print(f"SQL执行失败: {str(e)}")
        return None
