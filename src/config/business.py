#!/usr/bin/env python3
"""
业务配置模块
包含注册流程所需的业务数据配置
"""

# ==================== 页面1：用户创建 ====================

LOGIN_PASSWORD = "Test@1234"

OPERATOR_NAME = "造数"
OPERATOR_PHONE = "19447541989"
SMS_CODE = "111111"
OPERATOR_EMAIL = "sunwnejiao@staff.sinaft.com"
EMAIL_CODE = "111111"

# ==================== 页面2：业务类型选择 ====================

PARTNER_COMPANY_NAME = "微汇金融"
PARTNER_MERCHANT_ID = "200007285769"

# ==================== 页面3：企业信息 ====================

COMPANY_NAME_PREFIX = "测深圳市和琪时货疤有限责任公司"
COMPANY_SHORT_NAME_PREFIX = "测深圳市和琪时货疤有限责任公司"
CREDIT_CODE = "914403003664917216"

INDUSTRY_LEVEL1 = "采矿业"
INDUSTRY_LEVEL2 = "其他采矿业"
INDUSTRY_LEVEL3 = "其他采矿业"

PRODUCT_TYPE = "APP"
APP_NAME = "测试APP"

BANK_ACCOUNT_NAME = "造数"
BANK_NAME = "平安银行"
BANK_ACCOUNT_NUMBER = "6221881437330930226"

# ==================== 法人信息 ====================

LEGAL_NAME = "测烫单"
LEGAL_ID_TYPE = "身份证"
LEGAL_ID_NUMBER = "650100200204177266"
LEGAL_PHONE = "14243701813"

ID_EXPIRY_LONG_TERM = True
ID_EXPIRY_START_DATE = ""
ID_EXPIRY_END_DATE = ""

ID_CARD_TYPE_CONFIG = {
    "身份证": {
        "display_name": "身份证",
        "need_front": True,
        "need_back": True,
        "front_label": "人像面",
        "back_label": "国徽面",
        "front_file": "身份证正面.png",
        "back_file": "身份证反面.png",
    },
    "护照": {
        "display_name": "护照",
        "need_front": True,
        "need_back": False,
        "front_label": "护照",
        "back_label": None,
        "front_file": "身份证正面.png",
        "back_file": None,
    },
    "港澳居民来往内地通行证": {
        "display_name": "港澳居民来往内地通行证",
        "need_front": True,
        "need_back": True,
        "front_label": "港澳居民来往内地通行证正面",
        "back_label": "港澳居民来往内地通行证反面",
        "front_file": "身份证正面.png",
        "back_file": "身份证反面.png",
    },
    "港澳居民居住证": {
        "display_name": "港澳居民居住证",
        "need_front": True,
        "need_back": True,
        "front_label": "港澳居民居住证正面",
        "back_label": "港澳居民居住证反面",
        "front_file": "身份证正面.png",
        "back_file": "身份证反面.png",
    },
}

# ==================== 文件路径配置 ====================

ATTACHMENT_DIR = "./attachment"

FILE_BUSINESS_LICENSE = "营业执照.png"
FILE_COOPERATION_AGREEMENT_ZIP = "视频压缩包.zip"
FILE_COOPERATION_AGREEMENT_PDF = "aaaa.pdf"
FILE_BANK_CERTIFICATE = "aaaa.pdf"
FILE_VIDEO = "视频压缩包.zip"

# ==================== 其他配置 ====================

WAIT_TIME_SHORT = 1000
WAIT_TIME_MEDIUM = 2000
WAIT_TIME_LONG = 3000
WAIT_TIME_OCR = 5000

BROWSER_VIEWPORT_WIDTH = 1280
BROWSER_VIEWPORT_HEIGHT = 800
