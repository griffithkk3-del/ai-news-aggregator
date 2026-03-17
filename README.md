# 🤖 AI News Aggregator

> 每日自动获取 AI 新闻，聚合 28+ 数据源，推送到飞书群

## ✨ 特性

- 📰 **28+ 数据源**：全球科技、中文资讯、AI 论文一网打尽
- ⏰ **定时任务**：GitHub Actions 每日自动运行
- 🇨🇳 **中文友好**：36氪、华尔街见闻、微博热搜
- 📱 **飞书推送**：实时推送到群

## 📦 数据源

### AI/技术
- Hacker News (AI 关键词过滤)
- GitHub Trending
- Hugging Face Daily Papers

### 中文资讯
- 36氪
- 华尔街见闻
- 微博热搜

### 全球热点
- V2EX
- Product Hunt

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/griffithkk3-del/ai-news-aggregator.git
cd ai-news-aggregator
```

### 2. 配置 Secrets

在 GitHub 仓库 Settings → Secrets 添加：

| Secret | 说明 |
|--------|------|
| `FEISHU_WEBHOOK` | 飞书群机器人 Webhook |

### 3. 手动触发

进入 Actions → Daily AI News → Run workflow

## 📁 项目结构

```
ai-news-aggregator/
├── .github/workflows/     # GitHub Actions
├── scripts/
│   ├── daily_runner.py   # 主程序
│   └── fetch_news.py     # 数据源抓取
├── reports/              # 每日报告
├── requirements.txt
└── README.md
```

## ⏰ 定时任务

默认每天 UTC 1:00 (北京时间 9:00) 自动运行

## 📝 本地运行

```bash
pip install -r requirements.txt
python3 scripts/daily_runner.py
```

## 📄 License

MIT
