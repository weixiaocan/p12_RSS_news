"""
配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent

# 目录配置
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"

# 确保目录存在
for dir_path in [DATA_DIR, OUTPUT_DIR, LOGS_DIR, TEMPLATES_DIR]:
    dir_path.mkdir(exist_ok=True)

# RSS源配置
RSS_SOURCES = {
    # === AI实验室 ===
    "OpenAI News": "https://openai.com/news/rss.xml",
    "Google DeepMind": "https://deepmind.google/blog/rss.xml",
    "Mistral AI": "https://raw.githubusercontent.com/0xSMW/rss-feeds/main/feeds/feed_mistral_news.xml",

    # === AI工具与开发者向 ===
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "LangChain": "https://blog.langchain.dev/rss/",

    # === AI实践派个人博客 ===
    "Simon Willison": "https://simonwillison.net/atom/everything",
    "Eugene Yan": "https://eugeneyan.com/rss/",
    "Lilian Weng": "https://lilianweng.github.io/index.xml",
    "Chip Huyen": "https://huyenchip.com/feed.xml",
    "Jay Alammar": "https://jalammar.github.io/feed.xml",
    "Sebastian Raschka": "https://magazine.sebastianraschka.com/feed",

    # === AI行业媒体与全景扫描 ===
    "MIT Tech Review AI": "https://www.technologyreview.com/feed/",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Ars Technica AI": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "The Gradient": "https://thegradient.pub/rss/",
    "Ben's Bites": "https://www.bensbites.com/feed",

    # === AI Newsletter ===
    "The Keyword (Google AI)": "https://blog.google/technology/ai/rss/",
    "AINews by smol.ai": "https://news.smol.ai/rss.xml",
    "Peter Yang": "https://creatoreconomy.so/feed",
    "Every (Chain of Thought)": "https://every.to/chain-of-thought/feed",
}

# AI处理配置
AI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "model": os.getenv("AI_MODEL", "gpt-4o-mini"),
    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "max_articles_per_day": int(os.getenv("MAX_ARTICLES_PER_DAY", "50")),
    "timeout": int(os.getenv("AI_TIMEOUT", "60")),
}

# 定时任务配置
SCHEDULER_CONFIG = {
    "run_time": os.getenv("RUN_TIME", "07:00"),  # 北京时间
    "timezone": os.getenv("TIMEZONE", "Asia/Shanghai"),
}

# 数据保留配置
DATA_RETENTION_DAYS = 7

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "ai_daily_frontier.log"

# 网页配置
SITE_CONFIG = {
    "title": "AI每日前沿",
    "description": "自动抓取AI领域头部英文RSS博客，用AI提炼核心内容，生成每日可浏览的网页",
    "domain": os.getenv("SITE_DOMAIN", "http://localhost:8000"),
}
