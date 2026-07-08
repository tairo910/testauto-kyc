#!/usr/bin/env python3
"""
新浪支付会员注册自动化脚本 - 配置文件
修改此文件中的内容即可自定义填写的文字
"""

# ==================== 页面1：用户创建 ====================

# 登录兜底账号
LOGIN_ACCOUNT = "sunwnejiao@staff.sinaft.com"

# 登录兜底密码
LOGIN_PASSWORD = "sina@1234"

# 经办人信息
OPERATOR_NAME = "造数"  # 经办人姓名
OPERATOR_PHONE = "19447541989"  # 经办人手机号码
SMS_CODE = "111111"  # 短信验证码
OPERATOR_EMAIL = "sunwnejiao@staff.sinaft.com"  # 经办人邮箱
EMAIL_CODE = "111111"  # 邮箱验证码


# ==================== 页面2：业务类型选择 ====================

# 合作企业信息（业务3/4使用）
PARTNER_COMPANY_NAME = "微汇金融"  # 合作企业全称
PARTNER_MERCHANT_ID = "200007285769"  # 合作企业新浪支付商户号


# ==================== 页面3：企业信息 ====================

# 企业信息
COMPANY_NAME_PREFIX = "测深圳市和琪时货疤有限责任公司"  # 企业名称前缀（后面会自动加上账号）
COMPANY_SHORT_NAME_PREFIX = "测深圳市和琪时货疤有限责任公司"  # 企业简称前缀
CREDIT_CODE = "914403003664917216"  # 统一社会信用代码

# 所属行业（三级级联选择）
INDUSTRY_LEVEL1 = "采矿业"  # 第一层
INDUSTRY_LEVEL2 = "其他采矿业"  # 第二层
INDUSTRY_LEVEL3 = "其他采矿业"  # 第三层

# 业务1/2：公司官网或产品
PRODUCT_TYPE = "APP"  # 产品类型
APP_NAME = "测试APP"  # APP名称

# 结算账户信息（业务3/4使用）
BANK_ACCOUNT_NAME = "造数"  # 银行户名
BANK_NAME = "平安银行"  # 开户银行
BANK_ACCOUNT_NUMBER = "6221881437330930226"  # 企业银行账号


# ==================== 法人信息 ====================

# 法人基本信息
LEGAL_NAME = "测烫单"  # 法人姓名
LEGAL_ID_TYPE = "身份证"  # 证件类型（可选：身份证、港澳通行证、护照、台胞证等）
LEGAL_ID_NUMBER = "220104195710294432"  # 法人证件号码
LEGAL_PHONE = "14243701813"  # 法人手机号

# 证件有效期
ID_EXPIRY_LONG_TERM = True  # 是否勾选长期（True=长期，False=需要填写具体日期）
ID_EXPIRY_START_DATE = ""  # 证件有效期开始时间（如果不是长期）
ID_EXPIRY_END_DATE = ""  # 证件有效期截止时间（如果不是长期）

# 证件类型对应的文件上传配置
# 根据页面实际展示，支持四种证件类型：
ID_CARD_TYPE_CONFIG = {
    "身份证": {
        "display_name": "身份证",
        "need_front": True,      # 需要上传人像面
        "need_back": True,       # 需要上传国徽面
        "front_label": "人像面",  # 页面上显示的文字
        "back_label": "国徽面",
        "front_file": "身份证正面.png",
        "back_file": "身份证反面.png",
    },
    "护照": {
        "display_name": "护照",
        "need_front": True,      # 只需要上传护照（1张）
        "need_back": False,
        "front_label": "护照",
        "back_label": None,
        "front_file": "身份证正面.png",
        "back_file": None,
    },
    "港澳居民来往内地通行证": {
        "display_name": "港澳居民来往内地通行证",
        "need_front": True,      # 需要上传正面
        "need_back": True,       # 需要上传反面
        "front_label": "港澳居民来往内地通行证正面",
        "back_label": "港澳居民来往内地通行证反面",
        "front_file": "身份证正面.png",
        "back_file": "身份证反面.png",
    },
    "港澳居民居住证": {
        "display_name": "港澳居民居住证",
        "need_front": True,      # 需要上传正面
        "need_back": True,       # 需要上传反面
        "front_label": "港澳居民居住证正面",
        "back_label": "港澳居民居住证反面",
        "front_file": "身份证正面.png",
        "back_file": "身份证反面.png",
    },
}


# ==================== 文件路径配置 ====================

# 附件文件夹路径（相对路径）
ATTACHMENT_DIR = "./attachment"

# 文件名（注意：身份证/证件的文件名已在 ID_CARD_TYPE_CONFIG 中配置）
FILE_BUSINESS_LICENSE = "营业执照.png"  # 营业执照
FILE_COOPERATION_AGREEMENT_ZIP = "视频压缩包.zip"  # 合作协议（zip格式）
FILE_COOPERATION_AGREEMENT_PDF = "aaaa.pdf"  # 合作协议/申请表（pdf格式）
FILE_BANK_CERTIFICATE = "aaaa.pdf"  # 开户证明材料
FILE_VIDEO = "视频压缩包.zip"  # 开户意愿视频

# 注意：法人证件的文件名请在 ID_CARD_TYPE_CONFIG 中配置
# 身份证：ID_CARD_TYPE_CONFIG["身份证"]["front_file"] 和 ["back_file"]
# 港澳通行证：ID_CARD_TYPE_CONFIG["港澳通行证"]["front_file"]
# 护照：ID_CARD_TYPE_CONFIG["护照"]["front_file"]
# 台胞证：ID_CARD_TYPE_CONFIG["台胞证"]["front_file"]


# ==================== 其他配置 ====================

# 页面等待时间（毫秒）
WAIT_TIME_SHORT = 1000  # 短等待时间
WAIT_TIME_MEDIUM = 2000  # 中等等待时间
WAIT_TIME_LONG = 3000  # 长等待时间
WAIT_TIME_OCR = 5000  # OCR识别等待时间

# 浏览器配置
BROWSER_VIEWPORT_WIDTH = 1280  # 浏览器窗口宽度
BROWSER_VIEWPORT_HEIGHT = 800  # 浏览器窗口高度
