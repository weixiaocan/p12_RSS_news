

"""
网页生成模块
负责生成静态HTML页面
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from jinja2 import Template
import pytz

logger = logging.getLogger(__name__)

# 北京时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')


class PageGenerator:
    """网页生成器"""

    def __init__(self, output_dir: Path, templates_dir: Path, site_config: Dict):
        """
        初始化网页生成器

        Args:
            output_dir: 输出目录
            templates_dir: 模板目录
            site_config: 网站配置
        """
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        self.site_config = site_config

    def _get_date_str(self, date: datetime = None) -> str:
        """获取日期字符串（使用北京时间）"""
        if date is None:
            date = datetime.now(SHANGHAI_TZ)
        return date.strftime("%Y-%m-%d")

    def _save_data(self, date_str: str, data: Dict):
        """保存数据文件"""
        data_file = self.output_dir / "data" / f"{date_str}.json"
        data_file.parent.mkdir(exist_ok=True)

        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"数据已保存: {data_file}")

    def _load_data(self, date_str: str) -> Dict:
        """加载数据文件"""
        data_file = self.output_dir / "data" / f"{date_str}.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _cleanup_old_data(self, days: int = 7):
        """清理旧数据"""
        cutoff = datetime.now(SHANGHAI_TZ) - timedelta(days=days)
        data_dir = self.output_dir / "data"

        if not data_dir.exists():
            return

        for file in data_dir.glob("*.json"):
            try:
                # 从文件名提取日期
                date_str = file.stem
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff:
                    file.unlink()
                    logger.info(f"已清理旧数据: {file.name}")
            except ValueError:
                continue

    def _render_index_page(self) -> str:
        """渲染首页（重定向到今天）"""
        today = self._get_date_str()
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0;url=daily/{today}/">
    <title>{self.site_config['title']}</title>
</head>
<body>
    <p>正在跳转到今日内容...</p>
    <p>如果没有跳转，请<a href="daily/{today}/">点击这里</a></p>
</body>
</html>'''

    def _render_daily_page(self, date_str: str, data: Dict) -> str:
        """渲染每日页面"""
        template_str = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ date }} - {{ site.title }}</title>
    <meta name="description" content="{{ site.description }}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0e1a;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.7);
            --bg-card-hover: rgba(22, 31, 48, 0.85);
            --border-card: rgba(56, 189, 248, 0.08);
            --border-card-hover: rgba(56, 189, 248, 0.2);
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-cyan: #22d3ee;
            --accent-emerald: #34d399;
            --accent-gradient: linear-gradient(135deg, #22d3ee, #34d399);
            --accent-warm: #f59e0b;
            --featured-glow: rgba(34, 211, 238, 0.12);
            --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3);
            --shadow-card-hover: 0 8px 40px rgba(0, 0, 0, 0.4);
            --radius: 16px;
            --radius-sm: 10px;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.7;
            color: var(--text-primary);
            background: var(--bg-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ── 动态背景 ── */
        .bg-mesh {
            position: fixed;
            inset: 0;
            z-index: 0;
            overflow: hidden;
            pointer-events: none;
        }
        .bg-mesh::before,
        .bg-mesh::after {
            content: '';
            position: absolute;
            border-radius: 50%;
            filter: blur(120px);
            opacity: 0.3;
            animation: float 20s ease-in-out infinite;
        }
        .bg-mesh::before {
            width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(34,211,238,0.25), transparent 70%);
            top: -200px; right: -100px;
        }
        .bg-mesh::after {
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(52,211,153,0.2), transparent 70%);
            bottom: -150px; left: -100px;
            animation-delay: -10s;
        }
        @keyframes float {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(30px, -40px) scale(1.05); }
            66% { transform: translate(-20px, 20px) scale(0.95); }
        }

        .container {
            position: relative;
            z-index: 1;
            max-width: 860px;
            margin: 0 auto;
            padding: 24px 20px 60px;
        }

        /* ── 顶部 Header ── */
        header {
            text-align: center;
            padding: 48px 20px 36px;
            margin-bottom: 36px;
        }
        .logo {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        .logo-icon {
            width: 44px; height: 44px;
            background: var(--accent-gradient);
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 22px;
            box-shadow: 0 0 24px rgba(34,211,238,0.3);
        }
        .logo-text {
            font-size: 1.8em;
            font-weight: 800;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
        }
        header .subtitle {
            color: var(--text-secondary);
            font-size: 0.95em;
            max-width: 480px;
            margin: 0 auto;
        }

        /* ── 导航 Tabs ── */
        .nav-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 28px;
            flex-wrap: wrap;
        }
        .nav-tabs {
            display: flex;
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 4px;
            border: 1px solid var(--border-card);
        }
        .nav-tab {
            padding: 10px 22px;
            background: none;
            border: none;
            cursor: pointer;
            font-family: inherit;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            border-radius: 9px;
            transition: all 0.25s ease;
        }
        .nav-tab.active {
            background: var(--accent-gradient);
            color: var(--bg-primary);
            box-shadow: 0 2px 12px rgba(34,211,238,0.25);
        }
        .nav-tab:not(.active):hover {
            color: var(--text-primary);
            background: rgba(255,255,255,0.04);
        }

        /* ── 日期导航 ── */
        .date-nav {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .date-nav button {
            padding: 8px 14px;
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border-card);
            border-radius: 9px;
            cursor: pointer;
            font-family: inherit;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.25s ease;
        }
        .date-nav button:hover:not(:disabled) {
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
            background: rgba(34,211,238,0.06);
        }
        .date-nav button:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }
        .date-nav .current-date {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* ── 精选卡片 ── */
        .featured-card {
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: var(--radius);
            padding: 28px 28px 24px;
            margin-bottom: 20px;
            box-shadow: var(--shadow-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            opacity: 0;
            transform: translateY(20px);
            animation: cardIn 0.5s ease forwards;
        }
        .featured-card:nth-child(1) { animation-delay: 0.1s; }
        .featured-card:nth-child(2) { animation-delay: 0.2s; }
        .featured-card:nth-child(3) { animation-delay: 0.3s; }
        .featured-card:nth-child(4) { animation-delay: 0.4s; }
        .featured-card:nth-child(5) { animation-delay: 0.5s; }

        @keyframes cardIn {
            to { opacity: 1; transform: translateY(0); }
        }

        .featured-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--accent-gradient);
            opacity: 0;
            transition: opacity 0.35s;
        }
        .featured-card:hover {
            border-color: var(--border-card-hover);
            box-shadow: var(--shadow-card-hover);
            background: var(--bg-card-hover);
            transform: translateY(-2px);
        }
        .featured-card:hover::before { opacity: 1; }

        .card-header {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 20px;
        }
        .card-index {
            flex-shrink: 0;
            width: 32px; height: 32px;
            background: var(--accent-gradient);
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            font-size: 14px;
            font-weight: 700;
            color: var(--bg-primary);
            margin-top: 2px;
        }
        .card-title-group { flex: 1; }
        .card-title {
            font-size: 1.2em;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 6px;
            letter-spacing: -0.01em;
        }
        .card-title a {
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.2s;
        }
        .card-title a:hover { color: var(--accent-cyan); }

        .source-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 3px 10px;
            background: rgba(34,211,238,0.08);
            border: 1px solid rgba(34,211,238,0.15);
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            color: var(--accent-cyan);
        }

        .card-section {
            margin-bottom: 16px;
            padding: 14px 16px;
            background: rgba(255,255,255,0.02);
            border-radius: var(--radius-sm);
            border-left: 3px solid transparent;
        }
        .card-section.core { border-left-color: var(--accent-cyan); }
        .card-section.learn { border-left-color: var(--accent-emerald); }
        .card-section.action { border-left-color: var(--accent-warm); }

        .section-label {
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 6px;
        }
        .section-label.core { color: var(--accent-cyan); }
        .section-label.learn { color: var(--accent-emerald); }
        .section-label.action { color: var(--accent-warm); }

        .card-section p {
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.7;
        }

        .read-more-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-top: 8px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
            color: var(--bg-primary);
            background: var(--accent-gradient);
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.25s;
            box-shadow: 0 2px 8px rgba(34,211,238,0.2);
        }
        .read-more-link:hover {
            box-shadow: 0 4px 16px rgba(34,211,238,0.35);
            transform: translateY(-1px);
        }

        /* ── 全部更新列表 ── */
        .list-header {
            text-align: center;
            color: var(--text-muted);
            margin-bottom: 20px;
            font-size: 14px;
        }
        .list-header span {
            font-weight: 700;
            color: var(--text-primary);
        }

        .list-item {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: var(--radius-sm);
            padding: 16px 20px;
            margin-bottom: 10px;
            backdrop-filter: blur(8px);
            transition: all 0.25s ease;
            opacity: 0;
            animation: cardIn 0.4s ease forwards;
        }
        .list-item:nth-child(n) { animation-delay: calc(0.05s * var(--i, 0)); }
        .list-item:hover {
            border-color: var(--border-card-hover);
            background: var(--bg-card-hover);
            transform: translateX(4px);
        }

        .list-dot {
            flex-shrink: 0;
            width: 8px; height: 8px;
            border-radius: 50%;
            background: var(--text-muted);
            margin-top: 8px;
        }
        .list-item.featured .list-dot {
            background: var(--accent-warm);
            box-shadow: 0 0 8px rgba(245,158,11,0.5);
        }

        .list-content { flex: 1; }
        .list-title {
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 4px;
            line-height: 1.4;
        }
        .list-title a {
            color: var(--text-primary);
            text-decoration: none;
            transition: color 0.2s;
        }
        .list-title a:hover { color: var(--accent-cyan); }
        .list-item.featured .list-title a { color: #fbbf24; }
        .list-item.featured .list-title a:hover { color: var(--accent-warm); }

        .list-meta {
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.5;
        }
        .list-source {
            font-weight: 600;
            color: var(--text-secondary);
        }
        .list-featured-tag {
            display: inline-flex;
            align-items: center;
            gap: 3px;
            padding: 1px 7px;
            background: rgba(245,158,11,0.12);
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            color: var(--accent-warm);
            margin-left: 6px;
        }

        /* ── 空状态 ── */
        .empty-state {
            text-align: center;
            padding: 80px 20px;
        }
        .empty-icon {
            font-size: 56px;
            margin-bottom: 16px;
            opacity: 0.8;
        }
        .empty-state h3 {
            color: var(--text-secondary);
            font-size: 1.1em;
            margin-bottom: 8px;
        }
        .empty-state p {
            color: var(--text-muted);
            font-size: 14px;
        }

        /* ── Footer ── */
        footer {
            text-align: center;
            padding: 40px 20px 20px;
            color: var(--text-muted);
            font-size: 13px;
            border-top: 1px solid var(--border-card);
            margin-top: 40px;
        }
        footer .powered {
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 600;
        }

        /* ── 响应式 ── */
        @media (max-width: 640px) {
            .container { padding: 16px 14px 40px; }
            header { padding: 32px 16px 24px; }
            .logo-text { font-size: 1.4em; }
            .nav-bar { flex-direction: column; align-items: stretch; }
            .nav-tabs { justify-content: center; }
            .date-nav { justify-content: center; }
            .featured-card { padding: 20px 18px 18px; }
            .card-title { font-size: 1.05em; }
            .card-section { padding: 12px 14px; }
        }
    </style>
</head>
<body>
    <div class="bg-mesh"></div>
    <div class="container">
        <header>
            <div class="logo">
                <div class="logo-icon">⚡</div>
                <span class="logo-text">{{ site.title }}</span>
            </div>
            <p class="subtitle">{{ site.description }}</p>
        </header>

        <div class="nav-bar">
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('featured')">⭐ 今日精选</button>
                <button class="nav-tab" onclick="showTab('all')">📋 全部更新</button>
            </div>
            <div class="date-nav">
                <button onclick="changeDate(-1)" id="prevBtn">← 前一天</button>
                <span class="current-date" id="currentDate">📅 {{ date }}</span>
                <button onclick="changeDate(1)" id="nextBtn">后一天 →</button>
            </div>
        </div>

        <div id="featured-tab" class="tab-content active">
            {% if featured_articles %}
                {% for article in featured_articles %}
                <div class="featured-card">
                    <div class="card-header">
                        <div class="card-index">{{ loop.index }}</div>
                        <div class="card-title-group">
                            <div class="card-title"><a href="{{ article.url }}" target="_blank">{{ article.title }}</a></div>
                            <span class="source-badge">{{ article.source }}</span>
                        </div>
                    </div>

                    <div class="card-section core">
                        <div class="section-label core">📌 核心内容</div>
                        <p>{{ article.core_content }}</p>
                    </div>

                    <div class="card-section learn">
                        <div class="section-label learn">💡 你可以学到</div>
                        <p>{{ article.what_you_learn }}</p>
                    </div>

                    <div class="card-section action">
                        <div class="section-label action">🎯 行动建议</div>
                        <p>{{ article.action_advice }}</p>
                    </div>

                    <a href="{{ article.url }}" target="_blank" class="read-more-link">阅读原文 →</a>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <div class="empty-icon">🌙</div>
                    <h3>今日暂无高价值精选</h3>
                    <p>可以切换到「全部更新」查看所有文章</p>
                </div>
            {% endif %}
        </div>

        <div id="all-tab" class="tab-content">
            <p class="list-header">📅 {{ date }} · 共 <span>{{ all_articles|length }}</span> 篇更新</p>
            {% for article in all_articles %}
            <div class="list-item {% if article.is_featured %}featured{% endif %}" style="--i: {{ loop.index }}">
                <div class="list-dot"></div>
                <div class="list-content">
                    <div class="list-title">
                        <a href="{{ article.url }}" target="_blank">{{ article.title }}</a>
                        {% if article.is_featured %}<span class="list-featured-tag">🔥 精选</span>{% endif %}
                    </div>
                    <p class="list-meta"><span class="list-source">{{ article.source }}</span> · {{ article.summary }}</p>
                </div>
            </div>
            {% endfor %}
        </div>

        <footer>
            <p><span class="powered">{{ site.title }}</span> · 自动生成于 {{ date }}</p>
        </footer>
    </div>

    <script>
        const availableDates = {{ available_dates }};
        let currentDate = '{{ date }}';

        function showTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));

            if (tab === 'featured') {
                document.getElementById('featured-tab').classList.add('active');
                document.querySelectorAll('.nav-tab')[0].classList.add('active');
            } else {
                document.getElementById('all-tab').classList.add('active');
                document.querySelectorAll('.nav-tab')[1].classList.add('active');
            }
        }

        function changeDate(delta) {
            const currentIndex = availableDates.indexOf(currentDate);
            const newIndex = currentIndex + delta;

            if (newIndex >= 0 && newIndex < availableDates.length) {
                currentDate = availableDates[newIndex];
                window.location.href = '../' + currentDate + '/';
            }
        }

        function updateButtons() {
            const currentIndex = availableDates.indexOf(currentDate);
            document.getElementById('prevBtn').disabled = (currentIndex === 0);
            document.getElementById('nextBtn').disabled = (currentIndex === availableDates.length - 1);
        }

        updateButtons();
    </script>
</body>
</html>'''

        featured_articles = [a for a in data.get('articles', []) if a.get('is_featured')]
        all_articles = data.get('articles', [])

        # 获取可用的日期列表（最近7天）
        available_dates = []
        for i in range(7):
            d = datetime.now(SHANGHAI_TZ) - timedelta(days=i)
            date_str = d.strftime("%Y-%m-%d")
            data_file = self.output_dir / "data" / f"{date_str}.json"
            if data_file.exists():
                available_dates.append(date_str)
        available_dates.reverse()

        template = Template(template_str)
        return template.render(
            site=self.site_config,
            date=date_str,
            featured_articles=featured_articles,
            all_articles=all_articles,
            available_dates=available_dates,
        )

    def generate(self, articles: List[Dict], date: datetime = None):
        """
        生成网页

        Args:
            articles: 处理后的文章列表
            date: 日期，默认为今天
        """
        if date is None:
            date = datetime.now(SHANGHAI_TZ)

        date_str = self._get_date_str(date)

        # 准备数据
        data = {
            'date': date_str,
            'timestamp': date.isoformat(),
            'articles': articles,
            'featured_count': sum(1 for a in articles if a.get('is_featured')),
        }

        # 保存数据
        self._save_data(date_str, data)

        # 创建每日页面目录
        daily_dir = self.output_dir / "daily" / date_str
        daily_dir.mkdir(parents=True, exist_ok=True)

        # 生成每日页面
        html = self._render_daily_page(date_str, data)
        html_file = daily_dir / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"页面已生成: {html_file}")

        # 生成/更新首页
        index_html = self._render_index_page()
        index_file = self.output_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)

        # 清理旧数据
        self._cleanup_old_data()

        logger.info(f"网页生成完成: {date_str}")
