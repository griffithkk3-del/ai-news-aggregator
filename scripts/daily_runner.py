#!/usr/bin/env python3
"""
AI News Aggregator - Daily Runner (Enhanced)
每日自动获取 AI 新闻并推送到飞书
支持 28+ 数据源
"""

import os
import sys
import json
import requests
from datetime import datetime
import time

# 导入完整的 fetch_news 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_news import (
    fetch_hackernews,
    fetch_github,
    fetch_huggingface_papers,
    fetch_weibo,
    fetch_36kr,
    fetch_wallstreetcn,
    fetch_v2ex,
    fetch_producthunt,
    filter_items,
    enrich_items_with_content
)

# ============== 配置 ==============
AI_KEYWORDS = "AI,LLM,GPT,Claude,Agent,RAG,DeepSeek,OpenAI,Anthropic,Gemini"

# 数据源配置
SOURCES = {
    'ai_tech': {
        'name': 'AI/技术',
        'fetchers': [
            ('hackernews', fetch_hackernews, {'limit': 10, 'keyword': AI_KEYWORDS}),
            ('github', fetch_github, {'limit': 8}),
            ('huggingface', fetch_huggingface_papers, {'limit': 6}),
        ]
    },
    'china_news': {
        'name': '中文资讯',
        'fetchers': [
            ('36kr', fetch_36kr, {'limit': 8, 'keyword': AI_KEYWORDS}),
            ('wallstreetcn', fetch_wallstreetcn, {'limit': 6}),
            ('weibo', fetch_weibo, {'limit': 8}),
        ]
    },
    'global': {
        'name': '全球热点',
        'fetchers': [
            ('v2ex', fetch_v2ex, {'limit': 6}),
            ('producthunt', fetch_producthunt, {'limit': 6}),
        ]
    }
}

# ============== 飞书推送 ==============
def send_to_feishu(content, webhook_url=None):
    """发送到飞书群"""
    webhook_url = webhook_url or os.getenv('FEISHU_WEBHOOK')
    if not webhook_url:
        print("⚠️ 未配置 FEISHU_WEBHOOK，跳过推送")
        return False
    
    card = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"🤖 AI 每日简报 - {datetime.now().strftime('%m/%d')}"},
                "template": "blue"
            },
            "elements": [{"tag": "markdown", "content": content}]
        }
    }
    
    try:
        resp = requests.post(webhook_url, json=card, timeout=10)
        if resp.status_code == 200:
            print("✅ 推送到飞书成功")
            return True
        else:
            print(f"❌ 飞书推送失败: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ 飞书推送异常: {e}")
        return False

# ============== 格式化输出 ==============
def format_digest(all_news, by_category=None):
    """格式化新闻摘要"""
    lines = [f"**📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} AI 热点**\n"]
    
    if by_category:
        for cat_name, items in by_category.items():
            if not items:
                continue
            lines.append(f"\n**📰 {cat_name}**")
            for item in items[:8]:
                title = item['title'][:60] + '...' if len(item['title']) > 60 else item['title']
                heat = item.get('heat', '')
                heat_str = f" ({heat})" if heat else ""
                lines.append(f"• [{title}]({item['url']}){heat_str}")
    else:
        by_source = {}
        for item in all_news:
            source = item.get('source', 'Other')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(item)
        
        for source, items in by_source.items():
            lines.append(f"\n**📰 {source}**")
            for item in items[:5]:
                title = item['title'][:60] + '...' if len(item['title']) > 60 else item['title']
                lines.append(f"• [{title}]({item['url']})")
    
    lines.append(f"\n---\n*由 AI News Aggregator 自动生成 | [GitHub](https://github.com/griffithkk3-del/ai-news-aggregator)*")
    
    return '\n'.join(lines)

def save_report(content, all_news):
    """保存报告到文件"""
    os.makedirs('reports', exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 保存 Markdown
    md_path = f"reports/{date_str}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 保存 JSON
    json_path = f"reports/{date_str}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"📄 报告已保存: {md_path}, {json_path}")
    return md_path

# ============== 主函数 ==============
def main():
    print(f"\n🚀 AI News Aggregator 开始运行... {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print(f"📊 数据源: {sum(len(cat['fetchers']) for cat in SOURCES.values())} 个\n")
    
    all_news = []
    by_category = {}
    
    for cat_key, cat_config in SOURCES.items():
        cat_name = cat_config['name']
        cat_items = []
        print(f"📂 {cat_name}")
        
        for source_key, fetcher, kwargs in cat_config['fetchers']:
            try:
                print(f"   📡 {source_key}...", end=" ")
                items = fetcher(**kwargs)
                print(f"✅ {len(items)} 条")
                cat_items.extend(items)
                all_news.extend(items)
            except Exception as e:
                print(f"❌ {e}")
            time.sleep(0.5)
        
        by_category[cat_name] = cat_items
        print()
    
    if not all_news:
        print("❌ 未能获取任何新闻")
        return
    
    # 格式化和输出
    digest = format_digest(all_news, by_category)
    print(f"\n{'-'*50}\n")
    print(digest[:2000])
    print(f"\n{'-'*50}\n")
    
    # 保存报告
    save_report(digest, all_news)
    
    # 推送到飞书
    send_to_feishu(digest)
    
    print(f"\n✅ 完成! 共获取 {len(all_news)} 条新闻\n")

if __name__ == '__main__':
    main()
