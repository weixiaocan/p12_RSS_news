"""
测试脚本 - 验证各模块是否正常工作
"""
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_imports():
    """测试导入"""
    logger.info("测试导入模块...")
    try:
        from config import RSS_SOURCES, AI_CONFIG
        logger.info(f"  ✓ config.py - RSS源数量: {len(RSS_SOURCES)}")
    except Exception as e:
        logger.error(f"  ✗ config.py 导入失败: {e}")
        return False

    try:
        from src.rss_fetcher.fetcher import RSSFetcher
        logger.info("  ✓ src.rss_fetcher.fetcher")
    except Exception as e:
        logger.error(f"  ✗ src.rss_fetcher.fetcher 导入失败: {e}")
        return False

    try:
        from src.ai_processor.processor import AIProcessor
        logger.info("  ✓ src.ai_processor.processor")
    except Exception as e:
        logger.error(f"  ✗ src.ai_processor.processor 导入失败: {e}")
        return False

    try:
        from src.page_generator.generator import PageGenerator
        logger.info("  ✓ src.page_generator.generator")
    except Exception as e:
        logger.error(f"  ✗ src.page_generator.generator 导入失败: {e}")
        return False

    return True


def test_rss_fetcher():
    """测试RSS抓取器"""
    logger.info("\n测试RSS抓取器...")
    from config import RSS_SOURCES, DATA_DIR
    from src.rss_fetcher.fetcher import RSSFetcher

    # 只测试一个源
    test_sources = {"Simon Willison": RSS_SOURCES["Simon Willison"]}
    fetcher = RSSFetcher(test_sources, DATA_DIR)

    articles = fetcher.fetch_source("Simon Willison", test_sources["Simon Willison"])
    logger.info(f"  抓取到 {len(articles)} 篇文章")

    if articles:
        article = articles[0]
        logger.info(f"  示例文章: {article['title'][:50]}...")
        logger.info("  ✓ RSS抓取器正常")
        return True
    else:
        logger.warning("  ⚠ 未抓取到文章（可能是没有新文章或网络问题）")
        return True


def test_page_generator():
    """测试网页生成器（使用模拟数据）"""
    logger.info("\n测试网页生成器...")
    from config import OUTPUT_DIR, TEMPLATES_DIR, SITE_CONFIG
    from src.page_generator.generator import PageGenerator
    from datetime import datetime

    generator = PageGenerator(OUTPUT_DIR, TEMPLATES_DIR, SITE_CONFIG)

    # 模拟数据
    mock_articles = [
        {
            'url': 'https://example.com/article1',
            'title': 'OpenAI发布GPT-5：推理能力大幅提升',
            'source': 'OpenAI Blog',
            'published': datetime.now().isoformat(),
            'summary': 'OpenAI发布GPT-5，推理能力比GPT-4提升5倍',
            'is_featured': True,
            'core_content': 'OpenAI正式发布GPT-5模型，在推理、数学和编程能力上均有显著提升。',
            'what_you_learn': '了解最新AI模型的能力边界和应用场景',
            'action_advice': '可以尝试在OpenAI Playground中测试新模型',
        },
        {
            'url': 'https://example.com/article2',
            'title': 'Hugging Face开源新工具包',
            'source': 'Hugging Face',
            'published': datetime.now().isoformat(),
            'summary': 'Hugging Face发布新的模型训练工具包',
            'is_featured': False,
        },
    ]

    try:
        generator.generate(mock_articles)
        logger.info(f"  ✓ 网页已生成到: {OUTPUT_DIR / 'index.html'}")
        return True
    except Exception as e:
        logger.error(f"  ✗ 网页生成失败: {e}")
        return False


def main():
    """运行所有测试"""
    logger.info("=" * 50)
    logger.info("AI每日前沿 - 模块测试")
    logger.info("=" * 50)

    results = []

    # 测试导入
    results.append(("导入测试", test_imports()))

    # 测试RSS抓取器
    results.append(("RSS抓取器", test_rss_fetcher()))

    # 测试网页生成器
    results.append(("网页生成器", test_page_generator()))

    # 总结
    logger.info("\n" + "=" * 50)
    logger.info("测试结果总结:")
    logger.info("=" * 50)
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"  {name}: {status}")

    all_passed = all(r for _, r in results)
    if all_passed:
        logger.info("\n所有测试通过！项目可以正常运行。")
        logger.info("\n使用方法:")
        logger.info("  1. 复制 .env.example 为 .env")
        logger.info("  2. 在 .env 中设置 OPENAI_API_KEY")
        logger.info("  3. 运行: python main.py once")
    else:
        logger.info("\n部分测试失败，请检查错误信息。")

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
