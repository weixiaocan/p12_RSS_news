# AI每日前沿

自动抓取AI领域头部英文RSS博客，用AI提炼核心内容，生成每日可浏览的网页。

📱 **在线访问**: [https://weixiaocan.github.io/p12_RSS_news/](https://weixiaocan.github.io/p12_RSS_news/)

## 功能特点

- 🤖 自动抓取 19 个 AI 领域权威 RSS 源
- 🧠 AI 智能筛选高价值内容（每日精选 3-5 篇）
- 📄 生成简洁可读的静态网页
- 📅 支持查看最近 7 天历史记录
- ⏰ GitHub Actions 每天自动运行，无需手动操作
- 🌐 通过 GitHub Pages 自动部署，手机随时可看

## 工作原理

```
每天自动触发 (GitHub Actions, 北京时间 ~7:00)
    │
    ├─ 1. 抓取 RSS 源 (19个AI博客/媒体)
    ├─ 2. AI 处理文章 (DeepSeek 智能筛选+摘要)
    ├─ 3. 生成静态 HTML 页面
    └─ 4. 自动部署到 GitHub Pages
            │
            └─ 📱 手机/电脑访问网页
```

## 项目结构

```
p12_RSS_news/
├── main.py                     # 主程序入口
├── config.py                   # 配置文件（RSS源、AI配置等）
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量（API Key，不提交到Git）
├── .github/
│   └── workflows/
│       └── daily-update.yml    # GitHub Actions 自动化配置
├── src/
│   ├── rss_fetcher/            # RSS 抓取模块
│   ├── ai_processor/           # AI 处理模块
│   └── page_generator/         # 网页生成模块
├── data/                       # 数据存储目录
├── output/                     # 网页输出目录
│   ├── index.html              # 首页
│   ├── daily/                  # 每日页面
│   └── data/                   # 每日数据 JSON
└── logs/                       # 日志目录
```

## 自动更新（推荐）

项目已配置 **GitHub Actions**，每天北京时间约 7:00 自动执行以下流程：
1. 抓取所有 RSS 源的最新文章
2. 使用 AI 处理和筛选文章
3. 生成静态网页
4. 自动部署到 GitHub Pages

**无需任何手动操作**，部署成功后访问：
👉 https://weixiaocan.github.io/p12_RSS_news/

### 手动触发

如需立即更新，可在 GitHub 仓库的 **Actions** 页面点击 **Run workflow** 手动触发。

### 自动更新时间配置

在 `.github/workflows/daily-update.yml` 中修改 cron 表达式：

```yaml
schedule:
  - cron: '0 23 * * *'  # UTC 23:00 = 北京时间次日 7:00
```

## 本地运行

如需在本地运行：

1. **创建虚拟环境并安装依赖**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

2. **配置环境变量**

创建 `.env` 文件，填入以下内容：
```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-reasoner
```

3. **执行一次**
```bash
python main.py once
```

4. **查看结果**

在浏览器中打开 `output/index.html`。

## RSS 源列表

**AI 实验室**
- OpenAI News、Google DeepMind、Mistral AI

**AI 工具与开发者**
- Hugging Face、LangChain

**AI 实践派博客**
- Simon Willison、Eugene Yan、Lilian Weng
- Chip Huyen、Jay Alammar、Sebastian Raschka

**AI 行业媒体**
- MIT Tech Review AI、The Verge AI、Ars Technica AI
- The Gradient、Ben's Bites

**AI Newsletter**
- The Keyword (Google AI)、AINews by smol.ai
- Peter Yang、Every (Chain of Thought)

## AI 筛选标准

文章进入"今日精选"需满足以下至少两个条件：
1. **有新东西**：新模型、新工具、新方法、新研究成果
2. **跟实践相关**：能改变读者做事方式
3. **有深度**：信息量丰富，值得深入阅读

## 许可

MIT License
