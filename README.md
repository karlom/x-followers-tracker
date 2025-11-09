# X Followers Tracker

自动跟踪 X.com (Twitter) 关注人数并记录每日增长数据的工具。

## 功能特性

- 🤖 **自动化执行** - 通过 GitHub Actions 每日自动运行
- 📊 **增长追踪** - 计算每日关注数变化（delta）和增长率
- 💾 **数据持久化** - 支持 CSV 本地存储、Google Sheets 在线存储和 Notion 数据库存储
- 🔄 **容错机制** - API 调用失败自动重试
- 💰 **零成本** - 完全基于免费服务（GitHub Actions + X API Free Tier）

## 快速开始

### 1. 获取 X API Token

1. 访问 [X Developer Platform](https://developer.twitter.com/en/portal/dashboard)
2. 创建一个新的 App（或使用现有 App）
3. 在 "Keys and Tokens" 页面生成 Bearer Token
4. 保存 Token（仅显示一次）

### 2. 本地运行

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的信息
# X_BEARER_TOKEN=你的Bearer_Token
# X_USERNAME=你要追踪的用户名
```

#### 运行脚本

```bash
python main.py
```

首次运行将创建 `followers_log.csv` 文件并记录当前关注数。

### 3. GitHub Actions 自动化部署

#### 配置 GitHub Secrets

1. 进入你的 GitHub 仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 添加以下 secrets：
   - `X_BEARER_TOKEN`: 你的 X API Bearer Token
   - `X_USERNAME`: 要追踪的 X 用户名

#### 启用 GitHub Actions

推送代码到 GitHub 后，GitHub Actions 将自动：
- 每天北京时间早上 5:00（UTC 21:00）运行脚本
- 将数据保存到配置的存储后端（CSV/Google Sheets/Notion）
- CSV 模式下会自动提交并推送更改到仓库

## 数据格式

CSV 文件包含以下列：

| 列名 | 说明 | 示例 |
|------|------|------|
| date | 记录日期 | 2025-11-09 |
| followers_count | 当前关注数 | 1250 |
| delta | 与前一天的变化 | +16 |
| rate | 增长率 | +1.30% |

示例输出：

```csv
date,followers_count,delta,rate
2025-11-08,1234,0,0.00%
2025-11-09,1250,16,1.30%
2025-11-10,1240,-10,-0.80%
```

## 配置选项

环境变量（在 `.env` 文件中配置）：

### 基础配置

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `X_BEARER_TOKEN` | 是 | - | X API Bearer Token |
| `X_USERNAME` | 是 | - | 要追踪的 X 用户名 |
| `STORAGE_TYPE` | 否 | `csv` | 存储类型：`csv`、`sheets` 或 `notion` |

### CSV 存储配置（当 STORAGE_TYPE=csv 时）

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `CSV_FILE_PATH` | 否 | `followers_log.csv` | CSV 文件路径 |

### Google Sheets 存储配置（当 STORAGE_TYPE=sheets 时）

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `GOOGLE_SHEETS_ID` | 是 | - | Google Sheets 文档 ID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | 是 | - | Google 服务账号 JSON（字符串） |

### Notion 存储配置（当 STORAGE_TYPE=notion 时）

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `NOTION_TOKEN` | 是 | - | Notion Integration Token |
| `NOTION_DATABASE_ID` | 是 | - | Notion Database ID |

## Google Sheets 配置指南

### 1. 创建 Google Cloud 服务账号

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google Sheets API 和 Google Drive API
4. 创建服务账号：
   - IAM & Admin → Service Accounts → Create Service Account
   - 记录服务账号邮箱（如 `xxx@xxx.iam.gserviceaccount.com`）
5. 创建密钥：
   - 点击服务账号 → Keys → Add Key → Create New Key
   - 选择 JSON 格式
   - 下载 JSON 文件

### 2. 配置 Google Sheets

1. 创建一个新的 Google Sheets 文档
2. 从 URL 中复制 Spreadsheet ID：
   ```
   https://docs.google.com/spreadsheets/d/【这部分是ID】/edit
   ```
3. 共享文档给服务账号邮箱（Editor 权限）

### 3. 配置环境变量

```bash
# .env 文件
STORAGE_TYPE=sheets
GOOGLE_SHEETS_ID=你的Spreadsheet_ID
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
```

**注意**: JSON 内容需要压缩成一行，或者使用文件路径。

### 4. GitHub Actions 配置

在 GitHub Secrets 中添加（如果使用 Sheets 模式）：
- `STORAGE_TYPE`: `sheets`
- `GOOGLE_SHEETS_ID`: 你的 Spreadsheet ID
- `GOOGLE_SERVICE_ACCOUNT_JSON`: 服务账号 JSON 内容（完整）

## Notion 配置指南

### 1. 创建 Notion Integration

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 点击 "+ New integration"
3. 填写信息：
   - **Name**: X Followers Tracker（或任意名称）
   - **Associated workspace**: 选择你的工作区
   - **Type**: Internal integration
4. 点击 "Submit"
5. **复制 Internal Integration Token**（格式：`secret_xxx...`）

### 2. 创建 Notion Database

1. 在 Notion 中创建一个新 Page
2. 在 Page 中创建 Database（输入 `/database` 选择 "Table - Inline"）
3. 创建以下列（Properties）：
   - **Date** - 类型：Date
   - **Followers Count** - 类型：Number
   - **Delta** - 类型：Number
   - **Rate** - 类型：Text

### 3. 共享 Database 给 Integration

1. 在 Database 页面，点击右上角 "..."
2. 选择 "Connections" → "Connect to"
3. 找到并选择你刚创建的 Integration

### 4. 获取 Database ID

从 Database URL 中复制 ID：
```
https://www.notion.so/workspace/<这部分是Database_ID>?v=...
```

Database ID 是一串32位字符（含连字符）。

### 5. 配置环境变量

```bash
# .env 文件
STORAGE_TYPE=notion
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 6. GitHub Actions 配置

在 GitHub Secrets 中添加（如果使用 Notion 模式）：
- `STORAGE_TYPE`: `notion`
- `NOTION_TOKEN`: 你的 Integration Token
- `NOTION_DATABASE_ID`: 你的 Database ID

## 项目结构

```
x-followers-tracker/
├── main.py                 # 主脚本
├── storage.py              # 存储抽象层（CSV/Sheets/Notion）
├── test_tracker.py         # 功能测试
├── test_storage.py         # 存储后端测试
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略规则
├── CLAUDE.md               # Claude Code 项目文档
├── LICENSE                 # MIT 许可证
├── README.md               # 项目文档
└── .github/
    └── workflows/
        └── daily.yml       # GitHub Actions 工作流
```

## 运行测试

```bash
# 测试核心功能
python test_tracker.py

# 测试存储后端
python test_storage.py
```

**功能测试**包含：
- CSV 初始化
- 首次运行（无历史数据）
- 增长计算
- 数据持久化

**存储测试**包含：
- CSV 存储后端
- 存储工厂函数
- 模式切换

## 故障排查

### API 调用失败

**错误**: `API error: 401 Unauthorized`

**解决方案**:
- 检查 `X_BEARER_TOKEN` 是否正确
- 确认 Token 未过期
- 验证 Token 权限包含读取用户信息

### 找不到用户

**错误**: `API error: 404 Not Found`

**解决方案**:
- 检查 `X_USERNAME` 拼写是否正确
- 确认用户账号存在且未被暂停

### 环境变量未加载

**错误**: `Missing required environment variables`

**解决方案**:
- 确认 `.env` 文件存在于项目根目录
- 检查环境变量名称拼写
- 确保 `.env` 文件格式正确（无引号）

## 技术栈

- **语言**: Python 3.8+
- **依赖**: requests, python-dotenv
- **API**: X API v2 (免费 tier)
- **自动化**: GitHub Actions
- **存储**: CSV 文件 / Google Sheets / Notion Database（可选）

## API 使用限制

X API Free Tier 限制：
- **每月请求数**: 1,500 次
- **本项目用量**: ~30 次/月（每日一次）
- **剩余配额**: 充足

## 路线图

- [x] Stage 1: 核心 CSV 追踪功能
- [x] Stage 2: 项目配置和文档
- [x] Stage 3: GitHub Actions 自动化
- [x] Stage 4: Google Sheets 支持
- [x] Stage 5: Notion 数据库支持
- [x] Stage 6: 最终验证和文档完善

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [X API 文档](https://developer.twitter.com/en/docs/twitter-api)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

