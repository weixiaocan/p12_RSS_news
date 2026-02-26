"""
RSS抓取模块
负责从各个RSS源抓取最新文章
"""
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from pathlib import Path
import json
import pytz

logger = logging.getLogger(__name__)

# 北京时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')


class RSSFetcher:
    """RSS抓取器"""

    def __init__(self, sources: Dict[str, str], data_dir: Path):
        """
        初始化RSS抓取器

        Args:
            sources: RSS源字典 {名称: URL}
            data_dir: 数据存储目录
        """
        self.sources = sources
        self.data_dir = data_dir
        self.seen_file = data_dir / "seen_articles.json"
        self.seen_articles = self._load_seen_articles()

    def _load_seen_articles(self) -> Dict[str, str]:
        """加载已处理文章记录"""
        if self.seen_file.exists():
            try:
                with open(self.seen_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载已处理文章记录失败: {e}")
        return {}

    def _save_seen_articles(self):
        """保存已处理文章记录"""
        try:
            with open(self.seen_file, 'w', encoding='utf-8') as f:
                json.dump(self.seen_articles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存已处理文章记录失败: {e}")

    def _cleanup_old_seen(self, days: int = 7):
        """清理超过指定天数的已处理文章记录"""
        cutoff = (datetime.now(SHANGHAI_TZ) - timedelta(days=days)).isoformat()
        self.seen_articles = {
            url: date for url, date in self.seen_articles.items()
            if date > cutoff
        }
        self._save_seen_articles()

    def fetch_source(self, name: str, url: str) -> List[Dict]:
        """
        抓取单个RSS源

        Args:
            name: RSS源名称
            url: RSS URL

        Returns:
            文章列表
        """
        articles = []
        try:
            logger.info(f"正在抓取: {name} ({url})")
            feed = feedparser.parse(url)

            if feed.bozo:
                logger.warning(f"{name} RSS解析可能有误: {feed.bozo_exception}")

            for entry in feed.entries:
                # 提取基本信息
                article_url = entry.get('link', '')
                if not article_url:
                    continue

                # 检查是否已处理过
                if article_url in self.seen_articles:
                    continue

                # 提取发布时间
                published = entry.get('published_parsed')
                if published:
                    pub_date = datetime(*published[:6])
                else:
                    pub_date = datetime.now(SHANGHAI_TZ)

                # 只处理24小时内的新文章
                if pub_date.tzinfo is None:
                    pub_date = SHANGHAI_TZ.localize(pub_date)
                if pub_date < datetime.now(SHANGHAI_TZ) - timedelta(hours=24):
                    continue

                # 提取标题
                title = entry.get('title', '无标题')

                # 提取内容/摘要
                content = ""
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description

                articles.append({
                    'url': article_url,
                    'title': title,
                    'source': name,
                    'published': pub_date.isoformat(),
                    'content': content,
                })

                # 标记为已处理
                self.seen_articles[article_url] = datetime.now(SHANGHAI_TZ).isoformat()

            logger.info(f"{name} 抓取到 {len(articles)} 篇新文章")

        except Exception as e:
            logger.error(f"抓取 {name} 失败: {e}")

        return articles

    def fetch_all(self) -> List[Dict]:
        """
        抓取所有RSS源

        Returns:
            所有新文章列表
        """
        all_articles = []

        for name, url in self.sources.items():
            articles = self.fetch_source(name, url)
            all_articles.extend(articles)

        # 保存已处理文章记录
        self._save_seen_articles()

        # 按发布时间排序
        all_articles.sort(key=lambda x: x['published'], reverse=True)

        logger.info(f"共抓取到 {len(all_articles)} 篇新文章")
        return all_articles

    def cleanup(self, days: int = 7):
        """清理旧数据"""
        self._cleanup_old_seen(days)
