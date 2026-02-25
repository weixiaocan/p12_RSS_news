"""
AI处理模块
负责调用LLM API进行文章内容处理和筛选
"""
import logging
from typing import Dict, List, Optional
from openai import OpenAI
import re

logger = logging.getLogger(__name__)


# AI筛选标准提示
SELECTION_CRITERIA = """
请判断一篇文章是否值得进入"今日精选"。依据以下三个条件，需同时满足至少两个：

1. **有新东西**：发布了新模型、新工具、新方法、新研究成果，而非旧闻换皮
2. **跟实践相关**：读完后能改变读者做某件事的方式（新技巧、新工具用法、新工作流）
3. **有深度**：原文信息量足够丰富，值得花3分钟以上阅读，而非一段话就能说完的简短公告

请先给出判断（是/否），然后简要说明理由。
"""


class AIProcessor:
    """AI处理器"""

    def __init__(self, config: Dict):
        """
        初始化AI处理器

        Args:
            config: AI配置字典，包含 api_key, model, base_url, timeout 等
        """
        self.config = config
        self.client = OpenAI(
            api_key=config.get("api_key"),
            base_url=config.get("base_url"),
        )
        self.model = config.get("model", "gpt-4o-mini")
        self.timeout = config.get("timeout", 60)

    def _call_llm(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """
        调用LLM API（兼容 OpenAI / DeepSeek 等）

        Args:
            prompt: 提示词
            max_tokens: 最大token数

        Returns:
            AI返回的文本，失败返回None
        """
        system_msg = "你是一个AI领域的内容专家，擅长提炼核心信息和判断文章价值。"
        is_reasoner = "reasoner" in self.model.lower()

        try:
            # deepseek-reasoner 不支持 system role，合并到 user prompt
            if is_reasoner:
                messages = [
                    {"role": "user", "content": f"{system_msg}\n\n{prompt}"}
                ]
            else:
                messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ]

            # 构建 API 参数
            kwargs = {
                "model": self.model,
                "messages": messages,
            }

            # deepseek-reasoner 使用 max_completion_tokens 而非 max_tokens
            if is_reasoner:
                kwargs["max_completion_tokens"] = max_tokens
            else:
                kwargs["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI处理失败: {e}")
            return None

    def generate_summary(self, article: Dict) -> str:
        """
        生成一句话速览（不超过30字）

        Args:
            article: 文章字典

        Returns:
            一句话速览
        """
        content = article.get('content', '')[:3000]  # 限制长度
        title = article.get('title', '')

        prompt = f"""请用一句话概括这篇文章的核心内容，不超过30字。

标题：{title}
内容：{content}

速览："""

        result = self._call_llm(prompt, max_tokens=100)

        if result:
            # 清理引号和多余空白
            result = result.strip('"\'"')
            if len(result) > 50:
                result = result[:50] + "..."

        return result or "AI处理失败，请直接查看原文"

    def is_featured(self, article: Dict, summary: str) -> tuple[bool, str]:
        """
        判断文章是否进入精选

        Args:
            article: 文章字典
            summary: 一句话速览

        Returns:
            (是否精选, 理由)
        """
        content = article.get('content', '')[:4000]
        title = article.get('title', '')

        prompt = f"""{SELECTION_CRITERIA}

标题：{title}
速览：{summary}
内容：{content}

请按以下格式回答：
判断：是/否
理由：（简要说明）

回答："""

        result = self._call_llm(prompt, max_tokens=200)

        if not result:
            return False, "AI处理失败"

        # 解析结果
        is_featured = "判断：是" in result or "判断: 是" in result

        # 提取理由
        reason_match = re.search(r'理由[：:]\s*(.+)', result)
        reason = reason_match.group(1).strip() if reason_match else ""

        return is_featured, reason

    def generate_featured_content(self, article: Dict) -> Optional[Dict]:
        """
        为精选文章生成深度提炼内容

        Args:
            article: 文章字典

        Returns:
            包含核心内容、学到什么、行动建议的字典
        """
        content = article.get('content', '')[:6000]
        title = article.get('title', '')

        prompt = f"""请深度分析这篇AI领域文章，生成以下内容：

标题：{title}
内容：{content}

请按以下格式输出：

【核心内容】
（2-3句话概括这篇文章讲了什么）

【你可以学到】
（1-2句话说明这篇文章对读者的价值）

【行动建议】
（1句话说明读完后可以做什么，如"可以试试XX工具"、"值得关注XX趋势"）

请确保内容准确反映原文，不要添加原文没有的信息："""

        result = self._call_llm(prompt, max_tokens=800)

        if not result:
            return None

        # 解析结果
        featured = {
            "core_content": "",
            "what_you_learn": "",
            "action_advice": "",
        }

        sections = {
            "核心内容": "core_content",
            "你可以学到": "what_you_learn",
            "行动建议": "action_advice",
        }

        for section_cn, section_en in sections.items():
            pattern = rf'【{section_cn}】\s*\n?(.+?)(?=【|$)'
            match = re.search(pattern, result, re.DOTALL)
            if match:
                featured[section_en] = match.group(1).strip()
            else:
                # 尝试简单格式
                pattern = rf'{section_cn}[：:]\s*(.+?)(?=\n\n|$)'
                match = re.search(pattern, result, re.DOTALL)
                if match:
                    featured[section_en] = match.group(1).strip()

        return featured

    def process_article(self, article: Dict) -> Dict:
        """
        处理单篇文章：生成速览、判断精选、生成精选内容

        Args:
            article: 文章字典

        Returns:
            处理后的文章字典
        """
        result = article.copy()

        # 生成速览
        result['summary'] = self.generate_summary(article)

        # 判断是否精选
        is_featured, reason = self.is_featured(article, result['summary'])
        result['is_featured'] = is_featured
        result['featured_reason'] = reason

        # 如果是精选，生成深度内容
        if is_featured:
            featured = self.generate_featured_content(article)
            if featured:
                result.update(featured)
            else:
                # 精选内容生成失败，降级为普通文章
                result['is_featured'] = False

        return result

    def process_articles(self, articles: List[Dict], max_articles: int = 50) -> List[Dict]:
        """
        批量处理文章

        Args:
            articles: 文章列表
            max_articles: 最大处理文章数

        Returns:
            处理后的文章列表
        """
        articles = articles[:max_articles]
        processed = []

        logger.info(f"开始AI处理 {len(articles)} 篇文章...")

        for i, article in enumerate(articles, 1):
            logger.info(f"处理进度: {i}/{len(articles)} - {article['title'][:30]}")
            try:
                processed_article = self.process_article(article)
                processed.append(processed_article)
            except Exception as e:
                logger.error(f"处理文章失败: {article['title']}, 错误: {e}")
                # 失败的文章保留基本信息，但标记处理失败
                failed_article = article.copy()
                failed_article['summary'] = "AI处理失败，请直接查看原文"
                failed_article['is_featured'] = False
                processed.append(failed_article)

        featured_count = sum(1 for a in processed if a.get('is_featured'))
        logger.info(f"AI处理完成: 共 {len(processed)} 篇，其中精选 {featured_count} 篇")

        return processed
