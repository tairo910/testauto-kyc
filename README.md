# KYC 开户自动化系统

个人为工作提效，减少重复劳动的ui自动化，自动给测试环境开户，一站式自动化解决方案，覆盖**注册 → 审批 → 补充资料**全流程。

---

## 背景

kyc属于一个成熟但是麻烦的一个流程，在测试环境验证的过程中会需要很多的kyc 开户账号来完成业务覆盖。但是填表单麻烦，审批流程多且长，急需一个快速完成开户，拿到开户测试数据的小工具。当前的内容也算是给自己做一个后续的计划。
1、选择 ui 自动化，避免跳过前端的 bug
2、ui 自动化只在测试环境中进行，前提需要对各类验证码做mock 才能顺利执行
3、部分证件数据也通过 mock 和固定测试数据完成，后续需要完成随机测试数据注入
4、输出测试用户最终数据（数据包含内容要比较全，后续考虑进容器，搭建数据库进行存储）
5、每个核心脚本都可以独立运行，进行造数也可以通通过调度一次性完成开户的全过程拿到最终的测试数据

<!-- TODO: 在此处填写项目背景 -->

---

## 前提条件

- **验证码 Mock**：注册流程中的短信验证码需通过 Mock 方式获取，暂不支持真实验证码
- **环境支持**：目前仅支持**测试环境**

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

---

## 版本变更记录

每次提交的变更记录，按时间倒序排列。

### v1.2.0 - 调度器 & 审批流程优化

**新增：**
- `scheduler.py` 脚本调度器，支持链式调用注册→审批→补充资料
- `scheduler_config.json` 调度器配置，支持自定义链路和步骤顺序
- `merchant_review_approval.py` 复审审批脚本

**优化：**
- 审批脚本：修复弹窗复选框误勾选问题
- 审批脚本：搜索结果精确匹配，避免点击错误申请
- 审批脚本：支持初审经办和初审复核自动判断阶段
- 注册脚本：修复 `--no-wait` 参数误解析问题
- 调度器：从注册输出提取审批任务ID传递给后续步骤
- 调度器：实时输出子进程日志，前置校验必要变量

### v1.1.0 - 审批流程完善

**新增：**
- `merchant_access_approval.py` 商户准入审批自动化脚本
- 审批意见填写、弹窗处理、状态校验

**修复：**
- 配置文件密码及环境变量修正

### v1.0.0 - 初始版本

**新增：**
- 企业会员注册自动化脚本
- 补充资料脚本
- Web 可视化操作界面
- 数据库查询服务
- 账号生成工具
