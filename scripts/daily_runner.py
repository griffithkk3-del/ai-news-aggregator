#!/usr/bin/env python3
"""
AI News Aggregator - Daily Runner
每日自动获取 AI 新闻并推送到飞书
"""

import os
import sys
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import time
import re

# ============== 配置 ==============
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 关键词
AI_KEYWORDS = "AI,LLM,GPT,Claude,Agent,RAG,DeepSeek,OpenAI,Anthropic,Gemini"

# ============== 飞书推送 ==============
def send_to_feishu(content, webhook_url=None):
    """发送到飞书群"""
    webhook_url = webhook_url or os.getenv('FEISHU_WEBHOOK')
    if not webhook_url:
        print("⚠️ 未配置 FEISHU_WEBHOOK，跳过推送")
        return False
    
    # 构建卡片消息
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"🤖 AI 每日简报 - {datetime.now().strftime('%m/%d')}"},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
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

# ============== 数据源 ==============
def fetch_hackernews(limit=10):
    """获取 Hacker News AI 相关话题"""
    print("📡 抓取 Hacker News...")
    try:
        timestamp_24h = int(time.time() - 24 * 3600)
        keywords = [k.strip() for k in AI_KEYWORDS.split(',')]
        query_str = " OR ".join(keywords[:3])  # 取前3个关键词
        
        url = f"http://hn.algolia.com/api/v1/search_by_date?tags=story&numericFilters=created_at_i>{timestamp_24h}&hitsPerPage={limit*2}&query={requests.utils.quote(query_str)}"
        
        resp = requests.get(url, timeout=10)
        data = resp.json()
        hits = data.get('hits', [])[:limit]
        
        items = []
        for hit in hits:
            items.append({
                'title': hit.get('title', ''),
                'url': hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                'score': hit.get('score', 0),
                'source': 'Hacker News'
            })
        
        print(f"   ✅ 获取 {len(items)} 条")
        return items
    except Exception as e:
        print(f"   ❌ HN 抓取失败: {e}")
        return []

def fetch_github_trending(limit=10):
    """获取 GitHub Trending"""
    print("📡 抓取 GitHub Trending...")
    try:
        url = "https://github.com/trending?since=weekly&spoken_language_code="
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        repos = soup.select('article.box-shadow')[:limit]
        items = []
        
        for repo in repos:
            title_elem = repo.select_one('h2 a')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True).replace('\n', '').replace(' ', '')
            url = "https://github.com" + title_elem.get('href', '')
            stars = repo.select_one('span.d-inline-block.float-sm-right').get_text(strip=True) if repo.select_one('span.d-inline-block.float-sm-right') else "0"
            
            # 过滤 AI 相关
            title_lower = title.lower()
            if any(kw.lower() in title_lower for kw in ['ai', 'llm', 'gpt', 'claude', 'agent', 'rag', 'model', 'ml', 'nlp', 'deep']):
                items.append({
                    'title': title,
                    'url': url,
                    'score': stars,
                    'source': 'GitHub'
                })
        
        print(f"   ✅ 获取 {len(items)} 条")
        return items[:limit]
    except Exception as e:
        print(f"   ❌ GitHub 抓取失败: {e}")
        return []

def fetch_huggingface_papers(limit=8):
    """获取 Hugging Face 每日论文"""
    print("📡 抓取 Hugging Face Papers...")
    try:
        url = "https://huggingface.co/papers"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        papers = soup.select('a[href*="/paper/"]')[:limit*2]
        items = []
        seen = set()
        
        for paper in papers:
            href = paper.get('href', '')
            if href in seen or '/paper/' not in href:
                continue
            seen.add(href)
            
            title_elem = paper.select_one('p')
            title = title_elem.get_text(strip=True) if title_elem else "Untitled"
            
            # 过滤 AI 相关
            title_lower = title.lower()
            if any(kw.lower() in title_lower for kw in ['ai', 'llm', 'gpt', 'claude', 'agent', 'transformer', 'language', 'vision', 'multimodal']):
                items.append({
                    'title': title[:100],
                    'url': "https://huggingface.co" + href,
                    'score': '🔥',
                    'source': 'Hugging Face'
                })
            
            if len(items) >= limit:
                break
        
        print(f"   ✅ 获取 {len(items)} 条")
        return items
    except Exception as e:
        print(f"   ❌ HF 抓取失败: {e}")
        return []

# ============== 格式化输出 ==============
def format_digest(all_news):
    """格式化新闻摘要"""
    lines = [f"**📅 {datetime.now().strftime('%Y-%m-%d')} AI 热点**\n"]
    
    # 按来源分组
    by_source = {}
    for item in all_news:
        source = item.get('source', 'Other')
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(item)
    
    # 输出
    for source, items in by_source.items():
        lines.append(f"\n**📰 {source}**")
        for item in items[:5]:
            title = item['title'][:70] + '...' if len(item['title']) > 70 else item['title']
            lines.append(f"• [{title}]({item['url']})")
    
    lines.append(f"\n---\n*由 AI News Aggregator 自动生成*")
    
    return '\n'.join(lines)

def save_report(content):
    """保存报告到文件"""
    os.makedirs('reports', exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    filepath = f"reports/{date_str}.md"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📄 报告已保存: {filepath}")
    return filepath

# ============== 主函数 ==============
def main():
    print(f"\n🚀 AI News Aggregator 开始运行... {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    all_news = []
    
    # 获取各数据源
    all_news.extend(fetch_hackernews(limit=8))
    all_news.extend(fetch_github_trending(limit=8))
    all_news.extend(fetch_huggingface_papers(limit=6))
    
    if not all_news:
        print("❌ 未能获取任何新闻")
        return
    
    # 按分数排序
    all_news.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # 格式化和输出
    digest = format_digest(all_news)
    print(f"\n{'-'*40}\n")
    print(digest)
    print(f"\n{'-'*40}\n")
    
    # 保存报告
    save_report(digest)
    
    # 推送到飞书
    send_to_feishu(digest)
    
    print(f"\n✅ 完成! 共获取 {len(all_news)} 条新闻\n")

if __name__ == '__main__':
    main()
