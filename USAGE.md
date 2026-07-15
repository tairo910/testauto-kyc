# KYC 开户自动化系统 - 使用说明

本文档详细介绍各脚本的使用方法、参数说明和配置项。

---

## 目录

- [1. 脚本总览](#1-脚本总览)
- [2. 会员注册脚本 sina_register.py](#2-会员注册脚本-sina_registerpy)
- [3. 登录脚本 sina_login_simple.py](#3-登录脚本-sina_login_simplepy)
- [4. 补充资料脚本 sina_register_buchong.py](#4-补充资料脚本-sina_register_buchongpy)
- [5. 初审审批脚本 merchant_access_approval.py](#5-初审审批脚本-merchant_access_approvalpy)
- [6. 复审审批脚本 merchant_review_approval.py](#6-复审审批脚本-merchant_review_approvalpy)
- [7. 调度器 scheduler.py](#7-调度器-schedulerpy)
- [8. Web 服务 server.py](#8-web-服务-serverpy)
- [9. 配置说明](#9-配置说明)
- [10. 常见问题](#10-常见问题)

---

## 1. 脚本总览

| 脚本 | 功能 | 输入参数 | 输出 |
|------|------|----------|------|
| `sina_register.py` | 企业会员注册 | 业务类型 | 登录账号、邮箱、审批任务ID |
| `sina_login_simple.py` | 新浪支付登录 | 账号、密码 | 页面对象（供其他脚本复用） |
| `sina_register_buchong.py` | 补充结算账户等资料 | 登录账号 | - |
| `merchant_access_approval.py` | 商户准入初审审批 | 申请ID | 审批结果 |
| `merchant_review_approval.py` | 商户准入复审审批 | 申请ID | 审批结果 |
| `scheduler.py` | 链式调度多个脚本 | 业务类型/ID/账号等 | 全流程结果 |
| `server.py` | Web API 服务 | - | HTTP 接口 |

---

## 2. 会员注册脚本 sina_register.py

自动完成新浪支付企业会员注册的三页面流程。

### 执行方式

```bash
# 基本用法
python3 sina_register.py [业务类型]

# 业务1（默认）
python3 sina_register.py 业务1

# 非交互模式（执行完5秒后自动关闭浏览器）
python3 sina_register.py 业务1 --no-wait
```

### 业务类型说明

| 业务类型 | 说明 | 账号前缀规则 |
|----------|------|-------------|
| 业务1 | 新浪支付商户-综合业务 | `babwebyw1x` |
| 业务2 | 新浪支付商户-收款业务 | `babwebyw2x` |
| 业务3 | 商户的合作机构-综合业务 | `babwebyw3x` |
| 业务4 | 商户的合作机构-收款业务 | `babwebyw4x` |

账号命名规则：`前缀 + yw + 业务号 + 证件类型号 + 年月日时分`

证件类型号：1=身份证，2=护照，3=港澳通行证，4=居住证

### 注册流程

1. **页面1 - 用户创建**：填写登录账号、密码、经办人信息
2. **页面2 - 业务类型选择**：选择业务类型、填写合作企业信息（业务3/4）
3. **页面3 - 企业信息**：填写企业名称、统一社会信用代码、法人信息、上传证件

### 输出信息

注册成功后会输出：
- 登录账号
- 登录密码
- 邮箱
- 审批任务ID（用于后续审批）

---

## 3. 登录脚本 sina_login_simple.py

新浪支付企业版登录脚本，提供 `login_sina()` 函数供其他脚本复用。

### 函数调用

```python
from sina_login_simple import login_sina

# 返回 playwright 的 page 对象
page = login_sina(
    account='your_account',
    password='your_password',
    headless=False,
    max_retries=3
)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `account` | str | `config.LOGIN_ACCOUNT` | 登录账号 |
| `password` | str | `config.LOGIN_PASSWORD` | 登录密码 |
| `captcha` | str | None | 图形验证码（暂不使用） |
| `sms_code` | str | None | 短信验证码（暂不使用） |
| `headless` | bool | `False` | 是否无头模式 |
| `max_retries` | int | `3` | 最大重试次数 |

---

## 4. 补充资料脚本 sina_register_buchong.py

审批通过后，登录并补充结算账户、受益人等资料。

### 执行方式

```bash
# 基本用法
python3 sina_register_buchong.py [账号]

# 指定账号
python3 sina_register_buchong.py babwebyw11202607011200

# 指定账号和密码
python3 sina_register_buchong.py babwebyw11202607011200 your_password
```

### 补充内容

- 结算账户信息（银行账户名、开户银行、银行账号）
- 受益人信息
- 视频认证（如适用）

---

## 5. 初审审批脚本 merchant_access_approval.py

Guardian 系统商户准入初审审批自动化脚本，支持经办和复核阶段。

### 执行方式

```bash
# 基本用法
python3 merchant_access_approval.py [申请ID]

# 指定登录账号密码
python3 merchant_access_approval.py 6482 -u liuchunen -p Abc@1234

# 非交互模式
python3 merchant_access_approval.py 6482 --no-wait
```

### 参数说明

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `id` | - | 申请ID（必填，位置参数） | - |
| `--username` | `-u` | Guardian 登录用户名 | `liuchunen` |
| `--password` | `-p` | Guardian 登录密码 | `Abc@1234` |
| `--no-wait` | - | 非交互模式，完成后自动关闭浏览器 | `False` |

### 审批流程

1. 登录 Guardian 统一登录平台
2. 进入商户准入系统
3. 搜索目标申请ID
4. 自动识别阶段（经办 / 复核）
5. 填写审批意见（建议通过）
6. 提交审批

---

## 6. 复审审批脚本 merchant_review_approval.py

Guardian 系统商户准入初审复核自动化脚本。

### 执行方式

```bash
python3 merchant_review_approval.py [审批任务ID]

# 指定登录账号密码
python3 merchant_review_approval.py 6406 -u liuchunen -p Abc@1234
```

---

## 7. 调度器 scheduler.py

按顺序链式调用多个脚本，自动在步骤间传递变量。

### 查看可用链路

```bash
python3 scheduler.py --list
```

### 预定义链路

| 链路名 | 步骤顺序 | 适用场景 |
|--------|----------|----------|
| `default` / `full` | register → approve → buchong | 完整开户流程 |
| `register_only` | register | 仅注册 |
| `approve_only` | approve | 仅审批（需 `--id`） |
| `approve_and_buchong` | approve → buchong | 审批+补充资料（需 `--id`、`--account`） |
| `buchong_only` | buchong | 仅补充资料（需 `--account`） |

### 命令行参数

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--business-type` | `-b` | 业务类型 | `业务1` |
| `--id` | `-i` | 审批任务ID | - |
| `--account` | `-a` | 登录账号 | - |
| `--email` | `-e` | 注册邮箱 | - |
| `--chain` | `-c` | 链路名称或逗号分隔步骤 | `default` |
| `--config` | - | 自定义配置文件路径 | `scheduler_config.json` |
| `--list` | `-l` | 列出所有可用链路 | - |
| `--continue-on-error` | - | 失败后继续执行后续步骤 | 停止 |
| `--username` | `-u` | Guardian 登录用户名 | `liuchunen` |
| `--password` | `-p` | Guardian 登录密码 | `Abc@1234` |

### 使用示例

```bash
# 完整流程（注册 → 审批 → 补充资料）
python3 scheduler.py --business-type 业务1

# 只执行审批
python3 scheduler.py --id 6482 --chain approve_only

# 审批 + 补充资料
python3 scheduler.py --id 6482 --account babwebyw11xxxx --chain approve_and_buchong

# 自定义步骤顺序
python3 scheduler.py --business-type 业务1 --chain register,approve

# 失败后继续执行
python3 scheduler.py --business-type 业务1 --continue-on-error

# 使用自定义配置文件
python3 scheduler.py --config my_config.json
```

### 变量传递机制

调度器从脚本输出中自动提取以下变量，传递给后续步骤：

| 变量 | 来源 | 用途 |
|------|------|------|
| `account` | 注册脚本输出「登录账号:」 | 补充资料步骤使用 |
| `id` | 注册脚本输出「审批任务ID:」 | 审批步骤使用 |
| `email` | 注册脚本输出「邮箱:」 | 备用 |
| `business_type` | 命令行参数 `--business-type` | 注册步骤使用 |

> 注意：当链路包含 `register` 步骤时，命令行传入的 `--id` 会被忽略，强制使用注册脚本新生成的审批任务ID。

### 自定义链路配置

编辑 `scheduler_config.json`：

```json
{
  "chains": {
    "my_chain": ["register", "approve"]
  },
  "scripts": {
    "my_script": {
      "script": "my_script.py",
      "args_template": ["{account}", "--no-wait"],
      "timeout": 300,
      "description": "自定义脚本"
    }
  }
}
```

---

## 8. Web 服务 server.py

提供 REST API 接口，支持通过 Web 界面触发自动化流程。

### 启动服务

```bash
python3 server.py
```

服务默认启动在 `http://localhost:5000`

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/register` | POST | 启动注册流程 |
| `/api/progress` | GET | 查询执行进度 |
| `/api/status` | GET | 查询当前状态 |

### 注册请求示例

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "业务1",
    "account": "",
    "password": "",
    "email": ""
  }'
```

---

## 9. 配置说明

### 主配置 config.py

主要配置项分类：

| 分类 | 关键配置项 | 说明 |
|------|----------|------|
| 登录信息 | `LOGIN_ACCOUNT`、`LOGIN_PASSWORD` | 登录兜底账号密码 |
| 经办人 | `OPERATOR_NAME`、`OPERATOR_PHONE`、`SMS_CODE` | 经办人信息及验证码 |
| 企业信息 | `COMPANY_NAME_PREFIX`、`CREDIT_CODE` | 企业名称前缀、统一社会信用代码 |
| 所属行业 | `INDUSTRY_LEVEL1/2/3` | 三级级联行业选择 |
| 法人信息 | `LEGAL_NAME`、`LEGAL_ID_NUMBER`、`LEGAL_PHONE` | 法人姓名、证件号、手机号 |
| 结算账户 | `BANK_ACCOUNT_NAME`、`BANK_NAME`、`BANK_ACCOUNT_NUMBER` | 银行账户信息 |
| 证件配置 | `ID_CARD_TYPE_CONFIG` | 各证件类型上传配置 |

### 环境配置 src/config/env.py

数据库连接配置，支持 `.env` 文件：

```
DB_USERNAME=ermusr
DB_PASSWORD=your_password
DB_HOST=10.65.193.34
DB_PORT=1521
DB_SERVICE_NAME=func3
ORACLE_CLIENT_PATH=/path/to/instantclient
```

> 注意：Oracle 数据库必须使用 thick 模式（Instant Client），thin 模式不兼容旧版 Oracle 服务器。

---

## 10. 常见问题

### Q: 注册脚本执行失败，登录页面无法访问？

确认是否为测试环境，且验证码 Mock 已启用。注册流程仅在测试环境中可用。

### Q: 审批脚本找不到申请ID？

- 确认申请ID正确
- 确认该申请处于待审批状态（已审批的不会出现在列表中
- 可先手动登录 Guardian 系统确认

### Q: 注册后审批任务ID查询不到？

数据库同步可能有延迟，注册成功后等待几秒再查询。

### Q: 浏览器启动失败？

确保已安装 Playwright 浏览器：

```bash
playwright install chromium
```

### Q: Oracle 数据库连接失败？

- 确认已安装 Oracle Instant Client
- 确认 `ORACLE_CLIENT_PATH` 配置正确
- 确认服务名为 `func3`（不是 `erm`）
- 必须使用 thick 模式调用 `init_oracle_client()`

### Q: 调度器执行到某步骤失败了怎么办？

- 查看控制台输出的错误信息
- 使用 `--continue-on-error` 参数可以让失败后继续执行后续步骤
- 也可以单独执行失败的步骤进行调试

### Q: 截图保存在哪里？

各脚本的截图保存在 `screenshot/` 目录下，按功能分类：
- `screenshot/login/` - 登录相关截图
- `screenshot/buchong/` - 补充资料截图
- 注册脚本截图按业务类型和账号分目录保存
