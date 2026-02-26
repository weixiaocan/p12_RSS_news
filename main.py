"""
AI每日前沿 - 主程序
定时抓取RSS源，AI处理内容，生成网页
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
import time
import schedule
import pytz
from colorlog import ColoredFormatter

# 北京时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')

from config import (
    RSS_SOURCES,
    AI_CONFIG,
    SCHEDULER_CONFIG,
    LOG_LEVEL,
    LOG_FILE,
    DATA_DIR,
    OUTPUT_DIR,
    DATA_RETENTION_DAYS,
    SITE_CONFIG,
)

# 导入各模块
from src.rss_fetcher.fetcher import RSSFetcher
from src.ai_processor.processor import AIProcessor
from src.page_generator.generator import PageGenerator


def setup_logging():
    """配置日志"""
    LOG_FILE.parent.mkdir(exist_ok=True)

    # 控制台彩色日志
    console_formatter = ColoredFormatter(
        '%(log_color)s%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # 文件日志
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(file_formatter)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return logging.getLogger(__name__)


logger = setup_logging()


def run_job():
    """执行一次完整的抓取-处理-生成流程"""
    start_time = datetime.now(SHANGHAI_TZ)
    logger.info("=" * 60)
    logger.info(f"开始执行任务: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        # 检查AI配置
        if not AI_CONFIG.get('api_key'):
            logger.error("未配置 OPENAI_API_KEY 环境变量！")
            logger.info("请设置: export OPENAI_API_KEY=your_key_here")
            return False

        # 第一步：抓取RSS
        logger.info("\n" + "=" * 40)
        logger.info("第一步: 抓取RSS源")
        logger.info("=" * 40)
        fetcher = RSSFetcher(RSS_SOURCES, DATA_DIR)
        articles = fetcher.fetch_all()

        if not articles:
            logger.warning("没有抓取到新文章，使用空数据生成页面")
            articles = []

        # 第二步：AI处理
        logger.info("\n" + "=" * 40)
        logger.info("第二步: AI处理文章")
        logger.info("=" * 40)
        processor = AIProcessor(AI_CONFIG)

        if articles:
            processed_articles = processor.process_articles(
                articles,
                max_articles=AI_CONFIG.get('max_articles_per_day', 50)
            )
        else:
            processed_articles = []

        # 第三步：生成网页
        logger.info("\n" + "=" * 40)
        logger.info("第三步: 生成网页")
        logger.info("=" * 40)

        from config import TEMPLATES_DIR
        generator = PageGenerator(OUTPUT_DIR, TEMPLATES_DIR, SITE_CONFIG)
        generator.generate(processed_articles)

        # 清理旧数据
        logger.info("\n" + "=" * 40)
        logger.info("第四步: 清理旧数据")
        logger.info("=" * 40)
        fetcher.cleanup(days=DATA_RETENTION_DAYS)

        # 完成
        end_time = datetime.now(SHANGHAI_TZ)
        duration = (end_time - start_time).total_seconds()
        logger.info("\n" + "=" * 60)
        logger.info(f"任务完成! 耗时: {duration:.1f}秒")
        logger.info(f"抓取文章: {len(articles)} 篇")
        logger.info(f"精选文章: {sum(1 for a in processed_articles if a.get('is_featured'))} 篇")
        logger.info(f"网页位置: {OUTPUT_DIR / 'index.html'}")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"任务执行失败: {e}", exc_info=True)
        return False


def run_once():
    """手动执行一次任务"""
    logger.info("手动执行模式")
    run_job()


def run_scheduler():
    """运行定时调度器"""
    tz = pytz.timezone(SCHEDULER_CONFIG['timezone'])
    run_time = SCHEDULER_CONFIG['run_time']

    logger.info(f"定时调度模式")
    logger.info(f"时区: {SCHEDULER_CONFIG['timezone']}")
    logger.info(f"执行时间: 每天 {run_time}")
    logger.info("按 Ctrl+C 停止")

    # 设置定时任务
    schedule.every().day.at(run_time, tz).do(run_job)

    # 首次启动时也执行一次（可选）
    # run_job()

    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description='AI每日前沿 - RSS抓取与AI内容生成')
    parser.add_argument(
        'action',
        nargs='?',
        choices=['run', 'once', 'schedule'],
        default='run',
        help='执行动作: run(默认)=定时运行, once=执行一次后退出, schedule=仅定时调度'
    )
    args = parser.parse_args()

    if args.action == 'once':
        run_once()
    elif args.action == 'schedule':
        run_scheduler()
    else:  # run
        # 默认模式：先执行一次，然后进入定时调度
        run_once()
        if "--no-schedule" not in sys.argv:
            run_scheduler()


if __name__ == '__main__':
    main()
