#!/usr/bin/env python3
"""
账号生成工具
"""

import random
from datetime import datetime

EMAIL_DOMAINS = [
    "163.com",
    "126.com",
    "qq.com",
    "gmail.com",
    "outlook.com",
    "sina.com",
    "sohu.com",
    "139.com",
    "aliyun.com",
    "hotmail.com"
]

ID_TYPE_NUMBER_MAP = {
    "身份证": "1",
    "护照": "2",
    "港澳居民来往内地通行证": "3",
    "港澳居民居住证": "4",
}

def generate_random_email(account):
    domain = random.choice(EMAIL_DOMAINS)
    return f"{account}@{domain}"

def generate_account(prefix="babweb", business_type="业务1", id_type="身份证"):
    business_num = business_type.replace("业务", "").strip()
    id_type_num = ID_TYPE_NUMBER_MAP.get(id_type, "1")
    time_str = datetime.now().strftime("%Y%m%d%H%M")
    return f"{prefix}yw{business_num}{id_type_num}{time_str}"
