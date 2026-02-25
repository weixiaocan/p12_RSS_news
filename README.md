# AI每日前沿

自动抓取AI领域头部英文RSS博客，用AI提炼核心内容，生成每日可浏览的网页。

## 功能特点

- 自动抓取20+个AI领域权威RSS源
- AI智能筛选高价值内容（每日精选3-5篇）
- 生成简洁可读的静态网页
- 支持查看最近7天历史记录

## 项目结构

```
p12_RSS_news/
├── main.py                 # 主程序入口
├── config.py               # 配置文件
├── requirements.txt        # Python依赖
├── .env.example            # 环境变量示例
├── src/
│   ├── rss_fetcher/        # RSS抓取模块
│   ├── ai_processor/       # AI处理模块
│   └── page_generator/     # 网页生成模块
├── data/                   # 数据存储目录
├── output/                 # 网页输出目录
│   ├── index.html          # 首页
│   ├── daily/              # 每日页面
│   └── data/               # 每日数据JSON
└── logs/                   # 日志目录
```

## 安装

1. 克隆项目
```bash
cd p12_RSS_news
```

2. 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置 OPENAI_API_KEY
```

## 使用方法

### 方式1：手动执行一次
```bash
# 双击 run_once.bat
# 或命令行执行:
python main.py once
```

### 方式2：持续运行模式（开发测试）
```bash
# 双击 run_service.bat
# 或命令行执行:
python main.py run
```
程序持续运行，每天7:00自动执行。按 Ctrl+C 停止。

### 方式3：Windows任务计划程序（推荐生产环境）

#### 自动配置（推荐）
以管理员身份运行 PowerShell，执行：
```powershell
.\setup_task.ps1
```

#### 手动配置
1. 按 `Win+R` 输入 `taskschd.msc` 打开任务计划程序
2. 点击右侧"创建基本任务"
3. 名称: `AI每日前沿-RSS抓取`
4. 触发器: 每天 07:00
5. 操作: 启动程序
   - 程序: `cmd.exe`
   - 参数: `/c "D:\huangxh\AI_Projects_100\p12_RSS_news\run_once.bat"`
6. 完成后右键任务选择"运行"测试

#### 任务计划程序常用命令
```powershell
# 查看任务
Get-ScheduledTask -TaskName "AI每日前沿-RSS抓取"

# 立即运行
Start-ScheduledTask -TaskName "AI每日前沿-RSS抓取"

# 禁用任务
Disable-ScheduledTask -TaskName "AI每日前沿-RSS抓取"

# 启用任务
Enable-ScheduledTask -TaskName "AI每日前沿-RSS抓取"

# 删除任务
Unregister-ScheduledTask -TaskName "AI每日前沿-RSS抓取" -Confirm:$false
```

## 查看网页

执行完成后，在浏览器中打开 `output/index.html` 文件，或使用简单的HTTP服务器：

```bash
cd output
python -m http.server 8000
```

然后访问 http://localhost:8000

## RSS源列表

项目默认订阅以下RSS源：

**AI实验室**
- OpenAI News
- Anthropic Blog
- Google DeepMind
- Meta AI
- Mistral AI

**AI工具与开发者**
- Hugging Face
- LangChain
- LlamaIndex
- Ollama

**AI实践派博客**
- Simon Willison
- Eugene Yan
- Lilian Weng
- Chip Huyen
- Jay Alammar
- Sebastian Raschka

**AI行业媒体**
- The Batch (吴恩达)
- MIT Tech Review AI
- The Verge AI
- Ars Technica AI
- The Gradient
- Ben's Bites

## AI筛选标准

文章进入"今日精选"需满足以下至少两个条件：
1. **有新东西**：新模型、新工具、新方法、新研究成果
2. **跟实践相关**：能改变读者做事方式
3. **有深度**：信息量丰富，值得深入阅读

## 许可

MIT License
