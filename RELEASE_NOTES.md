# 📋 Release Notes - v1.0.0

## 🏗️ 项目概述

新浪支付会员注册自动化系统 - 一站式企业开户服务

---

## 🆕 新增功能

### 1. 前端注册页面
- **文件**: `index.html`, `server.py`
- **功能**: 提供可视化的商户注册界面
- **特性**:
  - 环境配置管理（API地址、浏览器类型、超时时间）
  - 业务类型选择（业务1-4）
  - 测试数据自动生成
  - 注册进度实时显示
  - 审批任务ID查询

### 2. 商户准入审批脚本
- **文件**: `merchant_access_approval.py`
- **功能**: 自动化商户审批流程
- **特性**:
  - 登录系统
  - 点击"商户风险管理"菜单
  - 点击"商户准入管理"子菜单
  - 查询申请ID
  - 填写审批意见（建议通过）
  - 填写风险分析与结论
  - 填写经办初审意见
  - 提交复核

### 3. 补充资料脚本
- **文件**: `sina_register_buchong.py`
- **功能**: 审核通过后的补充资料填写
- **特性**:
  - 自动登录新浪支付企业版
  - 填写结算账户信息
  - 上传开户证明材料
  - 填写受益人信息
  - 上传开户意愿视频

### 4. 账号生成工具
- **文件**: `src/utils/account_generator.py`
- **功能**: 自动生成登录账号和邮箱
- **特性**:
  - 账号格式: `babweb + yw + 业务编号 + 证件类型编号 + 时间戳`
  - 邮箱格式: `账号@随机域名`

---

## 🔧 修复问题

| 问题 | 原因 | 修复方案 |
|------|------|----------|
| SSL证书错误 | 目标网站SSL证书过期 | 将API URL从HTTPS改为HTTP |
| 密码明文显示 | 脚本修改了密码框类型为text | 保持password类型，移除readonly属性 |
| 验证码输入超时 | 手动输入验证码 | 自动填充固定验证码(1234) |
| 浏览器自动关闭 | Playwright生命周期问题 | 使用`start()`替代`with`语句 |
| 短信验证码页面失败 | 密码框元素定位失败 | 跳过密码重填，直接提交验证码 |

---

## 📁 项目结构

```
.
├── index.html                 # 前端注册页面
├── server.py                  # 后端服务
├── config.py                  # 全局配置
├── sina_login_simple.py       # 简化版登录脚本
├── sina_register.py           # 注册主入口
├── sina_register_buchong.py   # 补充资料脚本
├── merchant_access_approval.py # 审批脚本
└── src/
    ├── config/                # 配置模块
    │   ├── business.py        # 业务配置
    │   └── env.py             # 环境配置
    ├── services/              # 服务模块
    │   └── registration_service.py # 注册服务
    └── utils/                 # 工具模块
        ├── account_generator.py   # 账号生成器
        └── screenshot_manager.py  # 截图管理
```

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install playwright
playwright install chromium

# 2. 启动后端服务
python3 server.py

# 3. 访问前端页面
# 打开浏览器访问: http://localhost:5001/

# 4. 直接运行注册脚本
python3 sina_register.py babweb 业务1

# 5. 运行审批脚本
python3 merchant_access_approval.py

# 6. 运行补充资料脚本
python3 sina_register_buchong.py 账号 密码
```

---

## 📝 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/register` | POST | 启动注册流程 |
| `/api/progress` | GET | 获取注册进度 |
| `/api/config` | GET/POST | 获取/保存配置 |
| `/api/test` | GET | 测试服务状态 |
| `/api/getUserId` | POST | 查询审批任务ID |

---

## 📊 注册流程

```
用户创建 → 业务选择 → 企业信息填写 → 审核完成 → 补充资料
   ↓           ↓              ↓           ↓           ↓
  页面1      页面2          页面3        页面4       页面5
```

---

## 🛠️ 技术栈

- **语言**: Python 3.8+
- **框架**: Playwright (浏览器自动化)
- **Web框架**: Flask (后端服务)
- **前端**: HTML5 + CSS3 + JavaScript
- **数据库**: Oracle (审批任务查询)

---

## 📌 重要提示

1. 确保浏览器已正确安装（推荐使用Chrome）
2. 注册过程中浏览器窗口会自动打开，请勿手动关闭
3. 验证码默认自动填充为 `1234`（图形验证码）和 `111111`（短信验证码）
4. 注册成功后会显示审批任务ID，用于后续审批流程
5. 补充资料功能需要账号通过审核后才能使用

---

## ✅ 测试验证

- [x] 前端页面正常访问
- [x] 注册流程自动化完成
- [x] 登录功能正常
- [x] 验证码自动填充
- [x] 审批脚本正常运行
- [x] 补充资料脚本正常运行

---

**版本**: v1.0.0  
**日期**: 2026-06-24  
**仓库**: https://github.com/tairo910/testauto-kyc
