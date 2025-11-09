项目需求文档 (Requirements Project Document)1. 项目概述1.1 项目名称X.com 关注人数跟踪器 (X Followers Tracker)1.2 项目描述本项目旨在开发一个自动化工具，用于每天在固定时间点从 X.com (原 Twitter) API 获取指定用户的关注人数 (followers count)，计算与前一天的增长量 (delta) 和增长率 (percentage)，并将数据记录到表格文件中。表格可以是本地 CSV 文件或在线 Google Sheets。整个过程通过 Python 脚本实现，并使用 GitHub Actions 进行每日调度自动化执行，以实现最低成本（完全免费）的部署。项目目标：

- 自动化数据采集和计算，无需手动干预。
- 数据持久化，便于后续分析。
- 最低成本：利用免费的 GitHub Actions 和 X API 免费 tier。

1.3 项目范围

- 包含：API 数据获取、增长计算、数据追加到表格、每日调度。
- 不包含：用户界面、实时监控、错误警报通知、多用户支持、数据可视化（可后续扩展）。

1.4 目标用户

- 拥有 X.com 账号的用户（程序员或开发者），用于个人关注人数跟踪。
- 假设用户有编程经验，能配置 API token 和 GitHub repo。

1.5 业务价值

- 提供简单、低成本的社交媒体指标跟踪，帮助用户监控账号增长。
- 可扩展为其他指标跟踪（如 likes、retweets）。

\2. 功能需求2.1 核心功能

1. 数据获取：
   - 使用 X API v2 的免费 endpoint (GET /2/users/by/username/:username?user.fields=public_metrics) 获取指定用户的 followers_count。
   - 输入：用户名 (username)，Bearer Token（从 X Developer Platform 获取）。
   - 输出：当前 followers_count (整数)。
2. 增长计算：
   - 从表格中读取上一次记录的 followers_count。
   - 计算增长量：delta = 当前_count - 上次_count。
   - 计算增长率：rate = (delta / 上次_count) * 100%（如果上次_count 为 0，则 rate = 0%）。
   - 处理首次运行：如果无历史记录，delta = 0, rate = 0%。
3. 数据存储：
   - 将数据追加到表格，包括字段：日期 (YYYY-MM-DD)、关注数 (followers_count)、增长量 (delta)、增长率 (rate, 格式为 "%.2f%%")。
   - 支持两种存储方式：
     - 本地 CSV 文件（默认，存储在 GitHub repo 中）。
     - 在线 Google Sheets（可选，需要 Google 服务账号配置）。
4. 调度执行：
   - 使用 GitHub Actions 每日固定时间运行脚本（例如，每天 UTC 8:00，可配置）。
   - 自动 commit 和 push 更新后的表格文件到 repo。

2.2 输入/输出

- 输入：
  - 配置：Bearer Token、用户名、表格文件路径（CSV 或 Sheets ID）。
  - 运行时：无手动输入，全自动化。
- 输出：
  - 更新后的表格文件。
  - 控制台日志（可选，用于调试）。

2.3 用户故事

- 作为用户，我希望脚本每天自动运行，以便获取最新关注数据。
- 作为用户，我希望数据保存到易访问的表格中，以便查看历史记录。
- 作为用户，我希望计算准确，避免除零错误。

\3. 非功能需求3.1 性能

- 脚本执行时间 < 10 秒（API 调用 + 计算 + 写入）。
- 每日运行一次，GitHub Actions 免费额度足够（每月 2000 分钟）。

3.2 可靠性

- 处理 API 错误：如果 API 调用失败，重试 1 次或记录错误日志，不崩溃。
- 数据完整性：确保追加模式，避免覆盖历史数据。

3.3 安全性

- Bearer Token 存储在 GitHub Secrets（环境变量），不硬编码到代码。
- 仅读取公开 metrics，不涉及敏感数据。

3.4 可维护性

- 代码模块化：分离 API 调用、计算、存储逻辑。
- 注释和文档：每函数添加 docstring。
- 测试：提供单元测试示例（可选）。

3.5 兼容性

- Python 3.8+。
- GitHub Actions 支持的 runner (ubuntu-latest)。

\4. 技术栈

- 语言：Python 3。
- 库：
  - requests：API 调用。
  - csv：CSV 处理（内置）。
  - datetime：日期处理（内置）。
  - 可选：gspread 和 google-auth：Google Sheets 集成。
- 平台：
  - X Developer API：免费 tier。
  - GitHub：repo 存储代码和数据，Actions 调度。
- 配置：
  - X App：创建免费 App 获取 Bearer Token。
  - GitHub Secrets：存储 Token。

\5. 实施步骤

1. 准备阶段：
   - 注册 X Developer 账号，创建 App，获取 Bearer Token。
   - 创建 GitHub repo。
2. 开发阶段：
   - 编写 Python 脚本（track_followers.py）。
   - 配置 GitHub Actions workflow (.github/workflows/daily.yml)。
3. 测试阶段：
   - 本地运行脚本验证 API 和计算。
   - 模拟 Actions 运行。
4. 部署阶段：
   - Push 到 GitHub，启用 Actions。
   - 监控首次运行。
5. 维护阶段：
   - 更新 Token 如果过期。
   - 扩展功能（如邮件通知）。

\6. 假设和依赖

- 假设：
  - 用户有有效的 X 账号和 Developer 访问。
  - API 免费 tier 限额足够（每月 1500 请求）。
  - GitHub 账号免费。
- 依赖：
  - 互联网连接（Actions runner 有）。
  - X API 可用性（如果 downtime，脚本应优雅失败）。

\7. 潜在风险和缓解

- 风险：API rate limit 超限。
  - 缓解：每日仅一次调用，监控使用。
- 风险：Token 泄露。
  - 缓解：使用 GitHub Secrets。
- 风险：数据文件过大。
  - 缓解：CSV 简单，Sheets 有免费限额。
- 风险：时区差异。
  - 缓解：Actions 使用 UTC，文档中注明调整 cron。

\8. 附录8.1 版本历史

- v1.0：初始需求文档（2025-11-08）。

8.2 审批

- 作者：Grok AI（基于用户查询生成）。
- 审批人：karlomgg（后续实现时确认）。