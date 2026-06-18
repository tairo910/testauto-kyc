#!/usr/bin/env python3
"""
新浪支付会员注册自动化脚本 - 入口文件
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.services.registration_service import run_registration

def main():
    if len(sys.argv) >= 3:
        business_type = sys.argv[2]
    else:
        business_type = "业务1"
    
    print(f"启动注册流程，业务类型: {business_type}")
    
    try:
        result = run_registration(business_type)
        print(f"注册完成: {result}")
    except Exception as e:
        print(f"注册失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()