# KYC 开户自动化系统

一站式企业开户自动化解决方案，覆盖**注册 → 审批 → 补充资料**全流程。

---

## 功能概览

| 模块 | 脚本 | 说明 |
|------|------|------|
| 会员注册 | `sina_register.py` | 企业会员注册，自动填写表单、上传材料 |
| 补充资料 | `sina_register_buchong.py` | 审批通过后补充结算账户、受益人、视频认证等资料 |
| 初审审批 | `merchant_access_approval.py` | Guardian 系统商户准入初审（经办 + 复核） |
| 复审审批 | `merchant_review_approval.py` | Guardian 系统商户准入复审 |
| 调度器 | `scheduler.py` | 链式调用多个脚本，自动传递变量 |
| Web 服务 | `server.py` | 提供可视化操作界面 |

---

## 环境准备

### 1. 安装依赖

```bash
pip install playwright
playwright install
pip install cx_Oracle    # 数据库查询需要
```

### 2. 配置 Oracle 客户端

数据库查询功能需要 Oracle Instant Client：

- 下载地址：https://www.oracle.com/database/technologies/instant-client/macos-intel-x86-downloads.html
- 安装后在 `config/env.py` 中配置 `ORACLE_CLIENT_PATH`

### 3. 环境配置

复制 `.env.example` 为 `.env`，或直接修改 `config.py` 和 `src/config/env.py` 中的配置项。

---

## 快速开始

### 方式一：独立运行单个脚本

```bash
# 会员注册
python3 sina_register.py babweb 业务1

# 补充资料
python3 sina_register_buchong.py babwebyw11202607011200

# 初审审批
python3 merchant_access_approval.py 6482

# 非交互模式（执行完自动关闭浏览器）
python3 merchant_access_approval.py 6482 --no-wait
```

### 方式二：调度器链式执行

```bash
# 完整流程：注册 → 审批 → 补充资料
python3 scheduler.py

# 只执行审批
python3 scheduler.py --id 6482 --chain approve_only

# 只执行补充资料
python3 scheduler.py --account babwebyw11202607011200 --chain buchong_only

# 自定义步骤顺序
python3 scheduler.py --chain register,approve

# 查看所有可用链路
python3 scheduler.py --list
```

---

## 调度器说明

调度器可以按顺序执行多个脚本，并自动在步骤间传递变量（如登录账号、审批任务ID）。

### 预定义链路

| 链路名 | 步骤 | 说明 |
|--------|------|------|
| `default` | register → approve → buchong | 完整流程 |
| `register_only` | register | 仅注册 |
| `approve_only` | approve | 仅审批（需指定 `--id`） |
| `buchong_only` | buchong | 仅补充资料（需指定 `--account`） |
| `approve_and_buchong` | approve → buchong | 审批+补充资料 |

### 添加自定义链路

编辑 `scheduler_config.json`，在 `chains` 中添加：

```json
"my_chain": ["register", "approve"]
```

也可以添加新脚本配置到 `scripts` 中：

```json
"my_script": {
  "name": "自定义脚本",
  "script": "my_script.py",
  "args_template": ["{account}", "--no-wait"]
}
```

### 变量传递

- `account`：注册成功后提取的登录账号
- `id`：注册成功后提取的审批任务ID
- `email`：注册成功后提取的邮箱
- `business_type`：业务类型（默认：业务1）

---

## 目录结构

```
├── sina_register.py           # 会员注册脚本
├── sina_register_buchong.py   # 补充资料脚本
├── merchant_access_approval.py # 初审审批脚本
├── merchant_review_approval.py # 复审审批脚本
├── scheduler.py               # 调度器
├── scheduler_config.json      # 调度器配置
├── server.py                  # Web 服务
├── config.py                  # 主配置
├── src/
│   ├── config/
│   │   ├── env.py             # 环境配置（数据库等）
│   │   └── business.py        # 业务配置
│   ├── services/
│   │   ├── database_service.py # 数据库服务
│   │   └── registration_service.py # 注册服务
│   └── utils/
│       ├── account_generator.py # 账号生成器
│       └── screenshot_manager.py # 截图管理
└── screenshot/                # 运行截图（自动生成）
```

---

## 常见问题

### 审批脚本找不到申请ID？

- 确认申请ID是否正确
- 确认该申请是否在待审批列表中（已审批完成的不会显示）
- 可以先手动登录系统确认申请状态

### 注册后审批任务ID查询不到？

数据库同步可能有延迟，注册成功后等待几秒再查询。

### 浏览器启动失败？

确保已安装 Playwright 浏览器：

```bash
playwright install chromium
```
