# X Followers Tracker

自动跟踪 X.com (Twitter) 关注人数并记录每日增长数据的工具。

## 功能特性

- 🤖 **自动化执行** - 通过 GitHub Actions 每日自动运行
- 📊 **增长追踪** - 计算每日关注数变化（delta）和增长率
- 💾 **数据持久化** - 支持 CSV 本地存储和 Google Sheets 在线存储
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
- 每天 UTC 8:00 运行脚本
- 更新 CSV 文件
- 提交并推送更改到仓库

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

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `X_BEARER_TOKEN` | 是 | - | X API Bearer Token |
| `X_USERNAME` | 是 | - | 要追踪的 X 用户名 |
| `CSV_FILE_PATH` | 否 | `followers_log.csv` | CSV 文件路径 |

## 项目结构

```
x-followers-tracker/
├── main.py                 # 主脚本
├── test_tracker.py         # 测试套件
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略规则
├── CLAUDE.md               # Claude Code 项目文档
├── IMPLEMENTATION_PLAN.md  # 开发计划（开发中）
└── followers_log.csv       # 数据文件（自动生成）
```

## 运行测试

```bash
python test_tracker.py
```

测试包含：
- CSV 初始化
- 首次运行（无历史数据）
- 增长计算
- 数据持久化

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
- **存储**: CSV 文件 / Google Sheets（可选）

## API 使用限制

X API Free Tier 限制：
- **每月请求数**: 1,500 次
- **本项目用量**: ~30 次/月（每日一次）
- **剩余配额**: 充足

## 路线图

- [x] Stage 1: 核心 CSV 追踪功能
- [ ] Stage 2: 项目配置和文档（进行中）
- [ ] Stage 3: GitHub Actions 自动化
- [ ] Stage 4: Google Sheets 支持
- [ ] Stage 5: 最终验证和文档

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [X API 文档](https://developer.twitter.com/en/docs/twitter-api)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

