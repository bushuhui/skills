# OpenClaw Skills 文档

本目录包含 45+ 个 OpenClaw AI Agent 技能，涵盖文档处理、研究分析、量化金融、音视频转写、AI 辅助工具等多个领域。

---

## 技能分类总览

| 分类 | 技能数量 | 说明 |
|------|----------|------|
| 📄 文档处理 | 8 | PDF、Word、Excel、PPTX 文档的创建、编辑、解析 |
| 🔬 研究与知识管理 | 9 | 论文检索、文献综述、知识库管理、知识图谱 |
| 📈 量化金融 | 4 | A 股监控、金融数据接口、股票分析 |
| 🎬 音视频转写 | 3 | YouTube 视频、音频文件转文字 |
| 🤖 AI 辅助工具 | 8 | 搜索、新闻聚合、AI 内容检测、技能发现 |
| 🧠 思维与创意 | 11 | 头脑风暴、算法艺术、设计哲学、思维模型 |
| ⚙️ 系统与工具 | 5 | OpenClaw 优化、MCP 服务、数据库、Obsidian 工具 |
| 📚 写作与润色 | 3 | 学术写作、文稿润色、AI 文本人性化 |

---

## 📄 文档处理技能

### 1. minimax-pdf
**功能**: 创建高质量 PDF 文档，注重视觉设计和品牌识别
- **CREATE**: 从零生成 PDF（报告、提案、简历）
- **FILL**: 填写 PDF 表单字段
- **REFORMAT**: 应用设计模板到现有文档
- **技术特点**: 基于 Token 的设计系统（颜色、排版、间距），支持打印就绪输出

**使用场景**:
```
"创建一个专业的商业计划书 PDF"
"填写这个 PDF 表单"
"把这个文档重新排版成漂亮的 PDF"
```

---

### 2. minimax-docx
**功能**: 专业 Word 文档创建、编辑和格式化（使用 OpenXML SDK）
- **Pipeline A**: 从零创建文档
- **Pipeline B**: 编辑现有文档内容
- **Pipeline C**: 应用模板格式化 + XSD 验证
- **支持标准**: IEEE/ACM/APA/MLA/Chicago/Turabian、Springer/Nature 模板

**使用场景**:
```
"写一份研究报告"
"起草一个合同"
"把这个文档格式化成 APA 格式"
```

---

### 3. minimax-xlsx
**功能**: Excel 电子表格的创建、编辑、分析和验证
- **READ**: 使用 pandas 分析现有数据
- **CREATE**: 从零创建电子表格
- **EDIT**: 修改现有 xlsx 文件（零格式损失）
- **FIX**: 修复损坏的公式
- **VALIDATE**: 检查公式错误

**使用场景**:
```
"创建一个财务模型"
"分析这个 Excel 文件的数据"
"修复这个 spreadsheet 的公式错误"
```

---

### 4. docx
**功能**: Word 文档处理（通用技能）
- 读取/解析内容
- 创建新文档
- 编辑现有文档
- 查找替换、图片处理、追踪修订

**技术说明**: .docx 是包含 XML 的 ZIP 压缩包，可 unpack→edit→repack

---

### 5. xlsx
**功能**: Excel 电子表格处理（通用技能）
- 专业字体要求（Arial/Times New Roman）
- 零公式错误标准
- 金融模型颜色编码（蓝=输入，黑=公式，绿=链接）
- 数字格式化标准（货币、百分比、倍数）

---

### 6. pptx
**功能**: PowerPoint 演示文稿处理
- 读取/提取内容：`python -m markitdown presentation.pptx`
- 编辑或从模板创建
- 从零创建幻灯片

---

### 7. pdf
**功能**: PDF 文件处理
- 文本/表格提取
- 合并/拆分 PDF
- 旋转页面、添加水印
- OCR 识别扫描件
- 填写 PDF 表单

**核心库**: `pypdf`

---

### 8. pyword
**功能**: Word 自动化 Python 脚本体系
- 文档创建、排版、解析
- 标题编号、样式控制
- 页眉页脚、页码、目录
- 表格、图片、公式处理
- 结构化解构

**使用方式**: 优先复用 skill 内置的 `docs/` 和 `scripts/*.py`

---

## 🔬 研究与知识管理技能

### 1. arxiv-watcher
**功能**: ArXiv 论文搜索和摘要
- 按关键词/作者/分类搜索
- 提取摘要并生成简洁总结
- 自动保存到 `memory/RESEARCH_LOG.md`
- 深度挖掘 PDF 内容

**命令**:
```bash
scripts/search_arxiv.sh "<query>"
```

---

### 2. daily-research-papers
**功能**: 每日科研论文收集整理
- 来源：arXiv、HuggingFace Daily Papers、X/Twitter
- 聚焦领域：LLM、RL、Agent、UAV/Drone、Quant、Robotics
- 翻译摘要为中文
- 支持每天早上 7:00 cron 自动执行

---

### 3. literature-review
**功能**: 学术文献综述写作辅助
- 多源搜索：Semantic Scholar、OpenAlex、Crossref、PubMed
- 自动去重（按 DOI）
- 完整摘要提取
- 按主题分组并起草综述章节

**环境变量**: `USER_EMAIL`（礼貌访问 API）

---

### 4. deep-research
**功能**: 多轮迭代深度研究
- 整合多源信息生成调研报告
- 搜索脚本：`scripts/search.py`（DuckDuckGo）
- 网页抓取：`web_fetch`
- 支持 spawn 子 agent 处理复杂调研

**命令**:
```bash
python3 scripts/search.py "query" -n 10
python3 scripts/search.py "query" --news
```

---

### 5. graphify
**功能**: 将任意输入（代码、文档、论文、图片）转换为知识图谱
- 自动聚类社区检测
- 输出：交互式 HTML、GraphRAG JSON、审计报告
- 支持增量更新
- 多种导出格式（GraphML、SVG、Neo4j Cypher）

**触发**: `/graphify`

**命令**:
```
/graphify <path> --mode deep          # 深度提取
/graphify <path> --update             # 增量更新
/graphify <path> --neo4j-push <url>   # 推送到 Neo4j
```

---

### 6. ontology
**功能**: 结构化知识图谱（类型化实体记忆系统）
- 实体 CRUD：Person、Project、Task、Event、Document
- 关系链接与约束验证
- 跨技能共享状态
- 多步骤规划建模为图变换

**触发词**: "remember"、"what do I know about"、"link X to Y"

---

### 7. obsidian-bases
**功能**: 创建和编辑 Obsidian Bases（.base 文件）
- 定义视图：table、cards、list、map
- 过滤器：按标签/文件夹/属性/日期筛选
- 公式属性：计算字段
- YAML 格式验证

---

### 8. obsidian-cli
**功能**: Obsidian 命令行工具
- 读取/创建/搜索笔记
- 任务管理、属性操作
- 插件/主题开发支持
- 运行 JavaScript、捕获错误、DOM 检查

**命令示例**:
```bash
obsidian create name="My Note" content="Hello"
obsidian search query="tag:#todo"
```

---

### 9. obsidian-markdown
**功能**: Obsidian Flavored Markdown 编辑
- Wikilinks：`[[Note]]`、`[[Note#Heading]]`
- Embeds：`![[embed]]`
- Callouts：`> [!type]`
- Frontmatter 属性
- 标签、别名

---

## 📈 量化金融技能

### 1. a-stock-monitor-1-1-2
**功能**: A 股量化选股和实时监控系统
- **7 维度市场情绪评分**: 涨跌家数比、平均涨幅、涨停/跌停比等
- **智能选股引擎**: 短线 5 策略 + 中长线 7 策略
- **实时监控**: 全市场 5000+ 股票数据采集
- **自动推荐**: 每日短线 3-5 只、中长线 5-10 只
- **Web 界面**: Flask 前端 + 自动化 Cron 任务

**版本**: v1.1.2（性能提升 6-10 倍，双数据源架构）

---

### 2. tushare
**功能**: Tushare Pro 金融数据接口
- A 股市场数据：股票行情、基本面数据
- 期货市场数据
- 宏观经济指标
- 需要 `TUSHARE_TOKEN` 环境变量

**前置条件**:
```bash
pip install tushare pandas
export TUSHARE_TOKEN="your-api-token"
```

---

### 3. stock-study
**功能**: 个股深度分析（高级股票研究）
- 公司业务描述和商业模式
- Wall Street 共识：分析师评级、目标价
- 机构持仓活动
- 数据来源：Bloomberg、FactSet、SEC filings

---

### 4. critic-mentor-review
**功能**: 学术论文审稿与润色（双核对抗引擎）
- **Critic（审稿屠夫）**: 攻击逻辑漏洞、质疑数据、评估创新性
- **Mentor（润色匠人）**: 提升语言地道性、优化逻辑流
- 模拟 Nature/Science 级审稿人
- 生成 Cover Letter、优化 Abstract

**关键约束**:
- 原意保留红线：润色严禁改变科学原意
- 分块处理：按章节处理，严禁一次性处理全文
- 强制仪表盘：输出 Review Dashboard

---

## 🎬 音视频转写技能

### 1. youtube-transcribe
**功能**: 提取 YouTube 视频字幕并保存到知识库
- 支持自动生成字幕
- 多语言支持（zh-CN、en 等）
- 自动格式化 Markdown
- 依赖：`youtube-transcript-api`

**使用**:
```
转写这个视频：https://www.youtube.com/watch?v=xxx
```

---

### 2. youtube-transcription
**功能**: YouTube 视频音频转写（ASR）
- CDP 导出 Chrome cookies
- yt-dlp 下载音频
- 调用 ASR API（Qwen/Qwen3-ASR-1.7B）
- 保存到知识库

**流程**:
```bash
# 1. 导出 cookies
# 2. yt-dlp -x --audio-format mp3 --cookies ...
# 3. POST to ASR API
# 4. Save to Obsidian
```

---

### 3. audio-transcription
**功能**: 音频文件转写（MP3/WAV）
- API：`http://api.adv-ci.com:8090/v1/audio/transcriptions`
- 模型：Qwen/Qwen3-ASR-1.7B
- 支持场景：会议录音、播客、语音笔记

---

## 🤖 AI 辅助工具技能

### 1. brave-search
**功能**: Brave Search API 网页/新闻搜索
- 支持代理
- 限制结果数、时间范围
- 新闻搜索模式

**命令**:
```bash
python3 scripts/brave_search.py "query" -n 10
python3 scripts/brave_search.py "query" --news
```

---

### 2. ai-news-collectors
**功能**: AI 新闻聚合与热度排序
- 多维度分层搜索（最少 8 次）
- 来源：周报/Newsletter、Hacker News、Product Hunt、X/Twitter
- 按热度排序
- 输出中文摘要列表 + 原文链接

**触发**:
```
"今天有什么 AI 新闻？"
"总结一下这周的 AI 动态"
```

---

### 3. find-skills
**功能**: 发现和安装 agent skills
- 搜索技能库
- 安装技能：`npx skills add <package>`
- 检查更新：`npx skills check`

---

### 4. humanizer-zh
**功能**: 去除 AI 生成文本痕迹
- 检测模式：夸大象征、宣传性语言、模糊归因、AI 词汇
- 基于维基百科"AI 写作特征"指南
- 注入真实个性

**核心规则**:
1. 删除填充短语
2. 打破公式结构
3. 变化节奏
4. 用具体替代模糊
5. 删除"关键""重要"等强调词

---

### 5. agent-reach
**功能**: 配置多平台访问工具
- 支持平台：Twitter/X、Reddit、YouTube、GitHub、Bilibili、小红书、抖音、LinkedIn、Boss 直聘、RSS
- 安装命令：`pip install https://github.com/Panniantong/agent-reach/archive/main.zip`
- 环境检测：`agent-reach doctor`

---

### 6. pi-llm-server
**功能**: 统一 LLM 服务网关
- 语音识别（ASR）
- 文档解析（OCR）：PDF、图片、Office 文档 → Markdown
- Embedding 向量生成
- Rerank 文档重排序

**环境变量**: `DOC2X_KEY`、`API_TOKEN`

---

### 7. postgres
**功能**: PostgreSQL 最佳实践和查询优化
- Schema 设计、索引优化
- 分区、MVCC、VACUUM
- 查询模式优化
- 连接池和内存管理

---

### 8. mcp-builder
**功能**: MCP（Model Context Protocol）服务器开发指南
- Python（FastMCP）或 Node/TypeScript
- 工具设计原则：为工作流而非 API 端点设计
-  Agent-centric 设计模式

---

## 🧠 思维与创意技能

### 1. brainstorming
**功能**: 头脑风暴和设计规划
- 理解项目现状
- 提问澄清需求
- 提出 2-3 个方案 + 权衡
- 分块呈现设计（200-300 字/节）

---

### 2. algorithmic-art
**功能**: 算法艺术创作（p5.js）
- 种子随机性 + 交互式参数探索
- 粒子系统、流场、噪声场
- 输出：.md（哲学）、.html + .js（交互查看器）

**流程**:
1. 创建算法哲学（.md）
2. 用 p5.js 表达（.html + .js）

---

### 3. canvas-design
**功能**: 视觉设计哲学创作
- 形式、空间、色彩、构图
- 图片、图形、形状、图案
- 输出：.md（哲学）、.pdf/.png（视觉作品）

**流程**:
1. 创建设计哲学（.md）
2. 视觉表达（.pdf/.png）

---

### 4. naval-wealth-os
**功能**: 纳瓦尔财富操作系统
- **核心公式**: 专属知识 =（天赋 + 痴迷 + 深度练习）× 独特人生经历
- **五步框架**: 找到专属知识 → 用杠杆搭建 → 产品化 → 规模化 → 长期复利
- **触发话题**: 财富创造、创业决策、杠杆策略、产品化自己

---

### 5. thinker-elon-musk
**功能**: 马斯克的思维操作系统
- **核心心智模型**: 渐近极限法、五步算法、存在主义锚定、垂直整合、快速迭代
- **决策启发式**: 8 条决策原则（需求附人名、先算渐近极限、删到过度再补回等）
- **表达 DNA**: 极简宣言体、工程术语日常化、存亡级框定
- **触发场景**: 成本拆解、第一性原理、白痴指数、五步算法、垂直整合决策
- **信息源**: Walter Isaacson 传记、法庭证词、SpaceX/Tesla 财报会议、Lex Fridman 访谈

**示例**:
```
"这个成本合理吗？" → 用白痴指数分析
"流程有必要吗？" → 用五步算法审视
"能不能垂直整合？" → 评估供应链溢价
```

---

### 6. thinker-feynman
**功能**: 费曼的思维框架与表达方式
- **核心心智模型**: 命名≠理解、反自欺原则、不确定性是力量、具象化思考、深度游戏
- **决策启发式**: 8 条原则（货物崇拜检测、演示>论证、12 个问题过滤器等）
- **表达 DNA**: 口语化短句、从具体开始、自嘲式幽默、反问句替代感叹句
- **触发场景**: 概念理解检验、货物崇拜识别、简单类比解释复杂概念
- **信息源**: 《别闹了，费曼先生》、Cargo Cult Science 演讲、挑战者号调查记录

**示例**:
```
"这是不是 cargo cult？" → 检测形式与实质
"我真的理解了还是只记住了名字？" → 命名≠理解检验
"能不能做个演示？" → 演示>论证原则
```

---

### 7. thinker-munger
**功能**: 查理·芒格的思维框架
- **核心心智模型**: 多元思维模型、逆向思考、Lollapalooza 效应、能力圈、激励机制
- **25 种认知偏误**: 完整误判心理学清单（奖惩超级反应、社会认同、被剥夺超级反应等）
- **决策启发式**: 8 条原则（逆向切入、三筐分类法、坐在屁股上、配得上法则等）
- **表达 DNA**: 极短句、否定句优先、干燥幽默、向下类比（粪便、老鼠药）
- **触发场景**: 投资审视、认知偏误检查、跨学科思考、逆向思考练习
- **信息源**: 《穷查理宝典》、伯克希尔股东会、1986 哈佛演讲《如何保证人生痛苦》

**示例**:
```
"逆向思考一下" → 不问如何成功，问如何确保失败
"这有什么认知偏误？" → 调用 25 种误判心理学检查
"Lollapalooza 效应" → 识别多种偏误叠加的极端风险
```

---

### 8. thinker-naval
**功能**: Naval Ravikant 的思维操作系统
- **核心心智模型**: 杠杆思维、特定知识、欲望即合同、重新定义术、痛苦→系统重构
- **决策启发式**: 8 条原则（无需许可原则、日历测试、纠结即否定、手册测试等）
- **表达 DNA**: 金句体、先结论不铺垫、对称句式、重新定义关键词
- **触发场景**: 职业决策、财富定义、杠杆评估、欲望管理、特定知识识别
- **信息源**: 《The Almanack of Naval Ravikant》、How to Get Rich Tweetstorm、Naval Podcast

**示例**:
```
"这份工作有杠杆吗？" → 评估劳动力/资本/代码/媒体杠杆
"什么是 specific knowledge？" → 识别无法培训的独特能力
"欲望太多怎么办？" → 一次只保留一个欲望
```

---

### 9. thinker-steve-jobs
**功能**: 史蒂夫·乔布斯的思维框架
- **核心心智模型**: 聚焦即说不、端到端控制、连点成线、死亡过滤器、现实扭曲力场、技术×人文
- **决策启发式**: 8 条原则（先做减法、不问用户要什么、A Player 自我增强、一句话定义等）
- **表达 DNA**: 短句 + 三的法则、insanely great 等高频词、戏剧性停顿、二元判断
- **触发场景**: 产品审视、战略决策、团队评估、设计反馈
- **信息源**: Isaacson 授权传记、Stanford 演讲、Lost Interview、D Conference 访谈

**示例**:
```
"帮我用乔布斯的角度想想" → 聚焦/减法/端到端控制审视
"如果乔布斯会怎么做？" → 死亡过滤器/A Player 标准
"切换到乔布斯" → 沉浸式角色扮演回应
```

---

### 10. thinker-taleb
**功能**: 塔勒布的思维框架与表达方式
- **核心心智模型**: 非对称风险、反脆弱偏好、Skin in the Game、林迪效应、Via Negativa、领域特异性
- **决策启发式**: 9 条原则（预防原则、杠铃策略、遍历性检验、火鸡问题、少数派规则等）
- **表达 DNA**: 格言体、确定性极高、攻击性是 feature、古典引用（Seneca、汉谟拉比）
- **触发场景**: 极端风险评估、尾部风险识别、反脆弱策略、专家可信度检验
- **信息源**: Incerto 五部曲、EconTalk 访谈、COVID 预警论文、Twitter/Medium 表达

**示例**:
```
"会不会黑天鹅？" → 评估尾部风险和非对称性
"这个有尾部风险吗？" → 下行风险分析
"skin in the game" → 检验决策者是否承担后果
```

---

### 11. thinker-zhangxuefeng
**功能**: 张雪峰的思维框架与表达方式
- **核心心智模型**: 社会筛子论、选择>努力、就业倒推法、阶层现实主义、争议即传播
- **决策启发式**: 8 条原则（灵魂追问法、中位数原则、不可替代性检验、500 强测试等）
- **表达 DNA**: 短句快节奏、东北式幽默、绝对化表达、金句截图友好
- **触发场景**: 教育选择、职业规划、阶层流动分析、志愿填报决策
- **信息源**: 5 本著作、15+ 篇权威采访、30+ 条一手语录、完整人生时间线

**示例**:
```
"帮我用张雪峰的角度想想" → 就业倒推/社会筛子分析
"如果张雪峰会怎么说" → 中位数原则/500 强测试
"切换到张雪峰" → 东北大哥式直接回应
```

---

## ⚙️ 系统与工具技能

### 1. openclaw-optimization
**功能**: OpenClaw AI Agent 性能优化
- Session 管理：清理孤兒 sessions
- Context budget 优化
- Token 跟踪
- 自动化维护

**健康检查**:
```bash
bash scripts/health-check.sh
```

**指标标准**:
| 指标 | 🟢 健康 | 🟡 观察 | 🔴 需要行动 |
|------|--------|--------|------------|
| Active sessions | <100 | 100-500 | >500 |
| 最大 session | <5MB | 5-15MB | >15MB |
| Context 使用率 | <60% | 60-80% | >80% |

---

### 2. paper-auto-review
**功能**: 自动审稿工具
- 扫描论文目录
- 对未审稿 PDF 调用 Kimi 自动生成审稿意见
- 输出：`review_kimi.md`

**配置**:
- 脚本：`/home/bushuhui/scripts/teching_research/auto_review/kimi_pdf_auto_review.py`
- 论文目录：`/home/bushuhui/datacenter/papers/paper-review/`

---

### 3. lesson
**功能**: 从对话中存储经验教训
- 触发：`/lesson`
- 保存到 memory 系统

---

### 4. writing-assistant
**功能**: 写作团队负责人（协调专业写作工具）
- 分析写作需求
- 创建内容策略
- 协调专门写作工具

---

### 5. andrej-karpathy-curated-rss
**功能**: 抓取 Andrej Karpathy 精选 RSS 订阅
- RSS 源：`https://youmind.com/rss/pack/andrej-karpathy-curated-rss`（92 个顶级技术博客）
- 抓取过去 24 小时新文章
- 翻译摘要为中文
- 保存到 Obsidian 知识库

**命令**:
```bash
python3 scripts/fetch_rss.py [hours]
```

---

## 快速索引

按字母顺序排列的所有技能：

| 技能名 | 分类 | 主要功能 |
|--------|------|----------|
| academic-writing | 写作与润色 | 学术论文写作 |
| agent-reach | AI 辅助工具 | 多平台访问配置 |
| ai-news-collectors | AI 辅助工具 | AI 新闻聚合 |
| algorithmic-art | 思维与创意 | 算法艺术 |
| andrej-karpathy-curated-rss | 系统与工具 | RSS 抓取 |
| a-stock-monitor-1-1-2 | 量化金融 | A 股监控系统 |
| arxiv-watcher | 研究与知识管理 | ArXiv 论文 |
| artifacts-builder | 文档处理 | HTML 构建 |
| audio-transcription | 音视频转写 | 音频转写 |
| brave-search | AI 辅助工具 | 网页搜索 |
| brainstorming | 思维与创意 | 头脑风暴 |
| canvas-design | 思维与创意 | 视觉设计 |
| critic-mentor-review | 量化金融 | 论文审稿 |
| daily-research-papers | 研究与知识管理 | 论文速递 |
| deep-research | 研究与知识管理 | 深度研究 |
| doc2x | 文档处理 | PDF 转 Markdown |
| docx | 文档处理 | Word 文档 |
| find-skills | AI 辅助工具 | 技能发现 |
| graphify | 研究与知识管理 | 知识图谱 |
| humanizer-zh | AI 辅助工具 | AI 文本人性化 |
| lesson | 系统与工具 | 经验存储 |
| literature-review | 研究与知识管理 | 文献综述 |
| mcp-builder | AI 辅助工具 | MCP 服务器 |
| minimax-docx | 文档处理 | Word 文档 |
| minimax-pdf | 文档处理 | PDF 生成 |
| minimax-xlsx | 文档处理 | Excel 处理 |
| naval-wealth-os | 思维与创意 | 纳瓦尔财富 |
| obsidian-bases | 研究与知识管理 | Obsidian Bases |
| obsidian-cli | 研究与知识管理 | Obsidian CLI |
| obsidian-markdown | 研究与知识管理 | Obsidian Markdown |
| ontology | 研究与知识管理 | 知识图谱 |
| openclaw-optimization | 系统与工具 | 性能优化 |
| paper-auto-review | 系统与工具 | 自动审稿 |
| pdf | 文档处理 | PDF 处理 |
| pi-llm-server | AI 辅助工具 | LLM 网关 |
| postgres | AI 辅助工具 | PostgreSQL |
| pptx | 文档处理 | PowerPoint |
| pyword | 文档处理 | Word 自动化 |
| stock-study | 量化金融 | 股票分析 |
| thinker-elon-musk | 思维与创意 | 马斯克思维模型 |
| thinker-feynman | 思维与创意 | 费曼思维框架 |
| thinker-munger | 思维与创意 | 芒格决策智慧 |
| thinker-naval | 思维与创意 | Naval 财富哲学 |
| thinker-steve-jobs | 思维与创意 | 乔布斯产品思维 |
| thinker-taleb | 思维与创意 | 塔勒布反脆弱 |
| thinker-zhangxuefeng | 思维与创意 | 张雪峰教育规划 |
| tushare | 量化金融 | 金融数据 |
| writing-assistant | 系统与工具 | 写作助手 |
| xlsx | 文档处理 | Excel 处理 |
| youtube-transcribe | 音视频转写 | YouTube 字幕 |
| youtube-transcription | 音视频转写 | YouTube 转写 |

---

## 使用指南

### 技能调用方式

1. **自然语言调用**:
   ```
   帮我转写这个 YouTube 视频：https://www.youtube.com/watch?v=xxx
   创建一个财务模型 Excel
   搜索最新的 AI 新闻
   ```

2. **命令行调用**:
   ```bash
   openclaw skill run <skill-name> --args "..."
   ```

3. **Slash 命令**:
   ```
   /graphify <path>
   /lesson
   ```

### 技能开发规范

所有 skill 文件必须以标准 YAML frontmatter 开头：

```yaml
---
name: skill-name
description: 简洁清晰的功能描述
license: MIT（可选）
metadata:（可选）
---
```

---

## 贡献指南

添加新技能时：
1. 创建 `{skill-name}/SKILL.md`
2. 添加标准 frontmatter
3. 编写功能描述和使用示例
4. 更新本 README.md 的分类索引

---

**最后更新**: 2026-04-09
**技能总数**: 51+
