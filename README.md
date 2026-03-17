# 🤖 AI News Aggregator

> 每日自动获取 AI 新闻，聚合 Hacker News、GitHub、arXiv、Twitter 等28个数据源，推送到飞书群

## ✨ 特性

- 📰 **多源聚合**：28个新闻源一键获取
- ⏰ **定时任务**：每日自动运行
- 🇨🇳 **中文摘要**：自动翻译整理
- 📱 **飞书推送**：实时推送到群
- 🐙 **GitHub Actions**：零服务器成本

## 📦 数据源 (28个)

### 全球科技
- Hacker News、36氪、华尔街见闻、腾讯新闻、微博热搜、V2EX、Product Hunt、GitHub Trending

### AI/技术
- Hugging Face Papers、AI Newsletters (5个)、Ben's Bites、Interconnects、ChinAI、KDnuggets

### 播客
- Lex Fridman、80,000 Hours、Latent Space

### 随笔
- Paul Graham、Wait But Why、James Clear、Farnam Street

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ai-news-aggregator.git
cd ai-news-aggregator
```

### 2. 配置 Secrets

在 GitHub 仓库 Settings → Secrets 添加：

| Secret | 说明 | 获取方式 |
|--------|------|----------|
| `FEISHU_WEBHOOK` | 飞书群机器人Webhook | 飞书群设置 → 群机器人 → Webhook |
| `SERPER_API_KEY` | 搜索API (可选) | [serper.dev](https://serper.dev) 免费2500次/月 |

### 3. 手动触发

进入 Actions → Daily AI News → Run workflow

## 📁 项目结构

```
ai-news-aggregator/
├── .github/workflows/     # GitHub Actions
├── scripts/              # 核心脚本
├── reports/              # 每日报告输出
├── requirements.txt      # Python 依赖
└── README.md
```

## ⏰ 定时任务

默认每天 UTC 1:00 (北京时间 9:00) 自动运行

修改时间在 `.github/workflows/daily-news.yml`:
```yaml
schedule:
  - cron: '0 1 * * *'  # 修改这里
```

## 📝 使用示例

```bash
# 获取 AI 新闻 (默认)
python3 scripts/fetch_news.py --source hackernews --keyword "AI,LLM,Claude"

# 获取所有源 (深度扫描)
python3 scripts/fetch_news.py --source all --limit 15 --deep

# 每日简报 (预配置)
python3 scripts/daily_briefing.py --profile ai_daily
```

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 License

MIT
