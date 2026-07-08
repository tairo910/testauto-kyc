#!/usr/bin/env python3
"""
脚本调度器 - 支持链式调用多个脚本，可配置执行顺序

用法:
    # 使用默认链路执行（注册 -> 审批 -> 补充资料）
    python3 scheduler.py --id 6482 --business-type 业务1

    # 指定链路执行
    python3 scheduler.py --id 6482 --chain register,approve,buchong

    # 只执行某个步骤
    python3 scheduler.py --id 6482 --chain approve

    # 查看可用链路
    python3 scheduler.py --list

    # 自定义链路配置文件
    python3 scheduler.py --id 6482 --config my_chain.json

链路配置文件格式 (JSON):
{
    "chains": {
        "default": ["register", "approve", "buchong"],
        "register_only": ["register"],
        "approve_only": ["approve"],
        "full": ["register", "approve", "buchong"]
    },
    "scripts": {
        "register": {
            "script": "sina_register.py",
            "args_template": ["babweb", "{business_type}"],
            "timeout": 300,
            "description": "商户注册"
        },
        "approve": {
            "script": "merchant_access_approval.py",
            "args_template": ["{id}", "--no-wait"],
            "timeout": 300,
            "description": "商户准入审批"
        },
        "buchong": {
            "script": "sina_register_buchong.py",
            "args_template": ["{account}"],
            "timeout": 300,
            "description": "补充资料"
        }
    }
}
"""

import os
import sys
import json
import argparse
import subprocess
import time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, 'scheduler_config.json')


def get_default_config():
    """获取默认配置"""
    return {
        "chains": {
            "default": ["register", "approve", "buchong"],
            "register_only": ["register"],
            "approve_only": ["approve"],
            "approve_and_buchong": ["approve", "buchong"],
            "buchong_only": ["buchong"],
            "full": ["register", "approve", "buchong"]
        },
        "scripts": {
            "register": {
                "script": "sina_register.py",
                "args_template": ["babweb", "{business_type}", "--no-wait"],
                "timeout": 300,
                "description": "商户注册"
            },
            "approve": {
                "script": "merchant_access_approval.py",
                "args_template": ["{id}", "--no-wait"],
                "timeout": 300,
                "description": "商户准入审批"
            },
            "buchong": {
                "script": "sina_register_buchong.py",
                "args_template": ["{account}"],
                "timeout": 300,
                "description": "补充资料"
            }
        }
    }


def load_config(config_path=None):
    """加载配置文件，不存在则创建默认配置"""
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        config = get_default_config()
        save_config(config, config_path)
        print(f"已创建默认配置文件: {config_path}")
        return config


def save_config(config, config_path=None):
    """保存配置文件"""
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def resolve_args(args_template, variables):
    """解析参数模板，替换变量占位符"""
    resolved = []
    for arg in args_template:
        for key, value in variables.items():
            arg = arg.replace('{' + key + '}', str(value) if value else '')
        resolved.append(arg)
    # 过滤掉空参数
    return [a for a in resolved if a]


def check_required_variables(args_template, variables, step_name):
    """检查参数模板中所需的变量是否已就绪"""
    import re
    placeholders = re.findall(r'\{(\w+)\}', ' '.join(args_template))
    missing = []
    for ph in placeholders:
        if ph not in variables or not variables[ph]:
            missing.append(ph)
    if missing:
        print(f"  ⚠️ 步骤 {step_name} 缺少必要变量: {', '.join(missing)}")
        return False
    return True


def run_script(script_config, variables, step_num, total_steps):
    """执行单个脚本"""
    script_name = script_config['script']
    script_path = os.path.join(SCRIPT_DIR, script_name)
    args_template = script_config.get('args_template', [])
    timeout = script_config.get('timeout', 300)
    description = script_config.get('description', script_name)
    
    if not os.path.exists(script_path):
        print(f"\n❌ 步骤 {step_num}/{total_steps}: 脚本不存在 - {script_path}")
        return False, ""
    
    # 检查必要变量是否已就绪
    step_name = script_config.get('name', script_name)
    if not check_required_variables(args_template, variables, step_name):
        print(f"❌ 步骤 {step_num}/{total_steps}: 缺少必要变量，跳过执行")
        return False, ""
    
    # 解析参数
    args = resolve_args(args_template, variables)
    cmd = ['python3', script_path] + args
    
    print(f"\n{'='*60}")
    print(f"步骤 {step_num}/{total_steps}: {description}")
    print(f"脚本: {script_name}")
    print(f"命令: {' '.join(cmd)}")
    print(f"超时: {timeout}秒")
    print(f"{'='*60}")
    
    start_time = time.time()
    stdout_lines = []
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=SCRIPT_DIR
        )
        
        # 实时输出 stdout
        for line in proc.stdout:
            print(line, end='')
            stdout_lines.append(line)
        
        proc.wait(timeout=timeout)
        elapsed = time.time() - start_time
        
        # 输出 stderr
        stderr_output = proc.stderr.read()
        if stderr_output:
            print(f"[stderr] {stderr_output}")
        
        stdout_text = ''.join(stdout_lines)
        
        if proc.returncode == 0:
            print(f"\n✅ 步骤 {step_num} 完成 ({elapsed:.1f}秒)")
            return True, stdout_text
        else:
            print(f"\n❌ 步骤 {step_num} 失败 (返回码: {proc.returncode}, 耗时: {elapsed:.1f}秒)")
            return False, stdout_text
    
    except subprocess.TimeoutExpired:
        proc.kill()
        elapsed = time.time() - start_time
        print(f"\n❌ 步骤 {step_num} 超时 ({timeout}秒)")
        return False, ""
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ 步骤 {step_num} 异常: {e}")
        return False, ""


def extract_output_variables(script_name, stdout, variables):
    """从脚本输出中提取变量，传递给后续脚本"""
    if not stdout:
        return variables
    
    if script_name == 'sina_register.py':
        # 从注册脚本输出中提取账号、邮箱、审批任务ID
        for line in stdout.split('\n'):
            if '登录账号:' in line and '****' not in line:
                account = line.split(':')[1].strip()
                if account:
                    variables['account'] = account
                    print(f"  📋 提取变量: account={account}")
            elif '邮箱:' in line and '@' in line:
                email = line.split(':')[1].strip()
                if email:
                    variables['email'] = email
                    print(f"  📋 提取变量: email={email}")
            elif '审批任务ID:' in line:
                audit_id = line.split(':')[1].strip()
                # 过滤掉"未查询到"等无效值
                if audit_id and audit_id not in ('未查询到', 'None', ''):
                    variables['id'] = audit_id
                    print(f"  📋 提取变量: id={audit_id}")
    
    elif script_name == 'merchant_access_approval.py':
        # 审批脚本成功后，account 和 id 变量保持不变
        pass
    
    return variables


def run_chain(chain_name, config, variables, stop_on_error=True):
    """执行一个调度链路"""
    chains = config.get('chains', {})
    scripts = config.get('scripts', {})
    
    if chain_name not in chains:
        print(f"❌ 未找到链路: {chain_name}")
        print(f"可用链路: {', '.join(chains.keys())}")
        return False
    
    chain = chains[chain_name]
    total_steps = len(chain)
    
    # 如果链路包含 register 步骤，清除命令行传入的 id，
    # 强制使用注册步骤输出的新审批任务ID
    if 'register' in chain and variables.get('id'):
        old_id = variables['id']
        variables['id'] = ''
        print(f"  ℹ️ 链路包含注册步骤，忽略命令行传入的ID: {old_id}，将使用注册后新生成的ID")
    
    print(f"\n{'#'*60}")
    print(f"# 调度链路: {chain_name}")
    print(f"# 步骤数: {total_steps}")
    print(f"# 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")
    
    results = []
    
    for i, step_name in enumerate(chain):
        if step_name not in scripts:
            print(f"\n❌ 步骤 {i+1}: 未找到脚本配置 - {step_name}")
            results.append({'step': step_name, 'success': False, 'error': '脚本配置不存在'})
            if stop_on_error:
                break
            continue
        
        script_config = scripts[step_name]
        success, stdout = run_script(script_config, variables, i+1, total_steps)
        
        results.append({
            'step': step_name,
            'script': script_config['script'],
            'success': success
        })
        
        if success:
            # 从输出中提取变量，传递给后续步骤
            variables = extract_output_variables(script_config['script'], stdout, variables)
            
            # 注册步骤成功后，校验关键变量
            if step_name == 'register':
                if not variables.get('account'):
                    print(f"\n❌ 注册成功但未提取到登录账号，无法继续后续步骤")
                    results[-1]['success'] = False
                    if stop_on_error:
                        break
                if not variables.get('id'):
                    print(f"\n❌ 注册成功但未提取到审批任务ID，无法继续审批步骤")
                    print(f"   可能原因：数据库同步延迟，请稍后手动查询")
                    results[-1]['success'] = False
                    if stop_on_error:
                        break
                else:
                    print(f"\n  📋 注册结果: 账号={variables.get('account')}, 审批ID={variables.get('id')}, 邮箱={variables.get('email')}")
        else:
            if stop_on_error:
                print(f"\n⚠️ 步骤 {step_name} 失败，停止执行后续步骤")
                break
    
    # 打印执行摘要
    print(f"\n{'#'*60}")
    print(f"# 执行摘要")
    print(f"{'#'*60}")
    for r in results:
        status = "✅ 成功" if r['success'] else "❌ 失败"
        print(f"  {r['step']} ({r.get('script', 'N/A')}): {status}")
    
    all_success = all(r['success'] for r in results)
    print(f"\n最终结果: {'✅ 全部成功' if all_success else '❌ 部分失败'}")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return all_success


def list_chains(config):
    """列出所有可用的链路和脚本"""
    chains = config.get('chains', {})
    scripts = config.get('scripts', {})
    
    print("\n可用链路:")
    print("-" * 40)
    for name, steps in chains.items():
        desc = " -> ".join(steps)
        default_mark = " (默认)" if name == "default" else ""
        print(f"  {name}{default_mark}: {desc}")
    
    print("\n可用脚本:")
    print("-" * 40)
    for name, cfg in scripts.items():
        desc = cfg.get('description', name)
        script = cfg.get('script', 'N/A')
        args = ' '.join(cfg.get('args_template', []))
        print(f"  {name}: {desc}")
        print(f"    脚本: {script}")
        print(f"    参数: {args}")
        print()


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='脚本调度器 - 链式调用多个脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 scheduler.py --id 6482 --business-type 业务1
    python3 scheduler.py --id 6482 --chain approve
    python3 scheduler.py --id 6482 --chain register,approve,buchong
    python3 scheduler.py --list
    python3 scheduler.py --id 6482 --account babwebyw11202606161803 --chain buchong_only
        """
    )
    
    parser.add_argument(
        '--id', '-i',
        type=str,
        help='申请ID（审批脚本需要）'
    )
    
    parser.add_argument(
        '--business-type', '-b',
        type=str,
        default='业务1',
        help='业务类型（默认: 业务1）'
    )
    
    parser.add_argument(
        '--account', '-a',
        type=str,
        help='登录账号（补充资料脚本需要）'
    )
    
    parser.add_argument(
        '--email', '-e',
        type=str,
        help='注册邮箱'
    )
    
    parser.add_argument(
        '--chain', '-c',
        type=str,
        default='default',
        help='链路名称，逗号分隔的步骤名，或预定义链路名（默认: default）'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='自定义配置文件路径'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出所有可用的链路和脚本'
    )
    
    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='某步骤失败后继续执行后续步骤'
    )
    
    parser.add_argument(
        '--username', '-u',
        type=str,
        default='liuchunen',
        help='登录用户名（默认: liuchunen）'
    )
    
    parser.add_argument(
        '--password', '-p',
        type=str,
        default='Abc@1234',
        help='登录密码（默认: Abc@1234）'
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 列出链路
    if args.list:
        list_chains(config)
        return
    
    # 构建变量
    variables = {
        'id': args.id or '',
        'business_type': args.business_type,
        'account': args.account or '',
        'email': args.email or '',
        'username': args.username,
        'password': args.password,
    }
    
    # 解析链路：可能是预定义名称，也可能是逗号分隔的步骤
    chain_name = args.chain
    chains = config.get('chains', {})
    
    if chain_name in chains:
        # 预定义链路
        run_chain(chain_name, config, variables, stop_on_error=not args.continue_on_error)
    elif ',' in chain_name:
        # 逗号分隔的步骤列表，动态创建链路
        steps = [s.strip() for s in chain_name.split(',')]
        dynamic_chain_name = f"dynamic_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        config['chains'][dynamic_chain_name] = steps
        run_chain(dynamic_chain_name, config, variables, stop_on_error=not args.continue_on_error)
    else:
        # 单个步骤
        config['chains']['_single'] = [chain_name]
        run_chain('_single', config, variables, stop_on_error=not args.continue_on_error)


if __name__ == '__main__':
    main()
