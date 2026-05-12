# AI Agent Skills 详细文档

本文档分类介绍每个 skill 的目的、用途和用法。

---

## 📄 文档处理

### minimax-pdf
**目的**: 创建高质量 PDF 文档，注重视觉设计和品牌识别
**用途**: 从零生成 PDF（报告、提案、简历）、填写 PDF 表单、应用设计模板重新排版
**技术特点**: 基于 Token 的设计系统（颜色、排版、间距），支持打印就绪输出
**用法**:
```
"创建一个专业的商业计划书 PDF"
"填写这个 PDF 表单"
"把这个文档重新排版成漂亮的 PDF"
```

### minimax-docx
**目的**: 专业 Word 文档创建、编辑和格式化（使用 OpenXML SDK）
**用途**: 创建/编辑 Word 文档，支持 IEEE/ACM/APA/MLA/Chicago 等学术模板
**用法**:
```
"写一份研究报告"
"起草一个合同"
"把这个文档格式化成 APA 格式"
```

### minimax-xlsx
**目的**: Excel 电子表格的创建、编辑、分析和验证
**用途**: 从零创建电子表格、修改现有 xlsx（零格式损失）、修复公式错误、数据验证
**用法**:
```
"创建一个财务模型"
"分析这个 Excel 文件的数据"
"修复这个 spreadsheet 的公式错误"
```

### docx
**目的**: Word 文档处理（通用技能）
**用途**: 读取/解析/创建/编辑 .docx 文件，支持查找替换、图片处理、追踪修订
**技术说明**: .docx 是包含 XML 的 ZIP 压缩包，可 unpack→edit→repack

### xlsx
**目的**: Excel 电子表格处理（通用技能）
**用途**: 创建/读取/分析/验证 xlsx 文件，遵循零公式错误标准、金融模型颜色编码规范
**规范**: 蓝色=输入、黑色=公式、绿色=链接；支持货币、百分比、倍数格式化

### pdf
**目的**: PDF 文件处理
**用途**: 文本/表格提取、合并/拆分 PDF、旋转页面、添加水印、OCR 识别扫描件、填写表单
**核心库**: `pypdf`

### pyword
**目的**: Word 自动化 Python 脚本体系
**用途**: 文档创建、标题编号、样式控制、页眉页脚、页码、目录、表格、图片、公式处理
**用法**: 优先复用 skill 内置的 `docs/` 和 `scripts/*.py` 脚本

### markdown-to-docx
**目的**: Markdown 转 Word DOCX 格式
**用途**: 两种转换模式：
- **方式 A（pandoc 直接转换）**: 适合含 LaTeX 公式的学术论文，支持图片
- **方式 B（python-docx 模板转换）**: 适合公文/技术方案/报告，支持中文字体完美匹配
**内置**: 自动格式检查修复（HTML 表格、分隔行、图片引用）

### fireworks-tech-graph
**目的**: 生成生产级技术架构图和流程图，导出为 SVG+PNG
**用途**: 架构图、数据流图、流程图、时序图、Agent/Memory 图、概念图
**用法**: 触发词：`画图`、`帮我画`、`架构图`、`流程图`、`可视化一下`
**安装**: `npx skills add yizhiyanhua-ai/fireworks-tech-graph`
**输出**: SVG 图表通过 `rsvg-convert` 导出为 PNG

---

## 🔬 研究与知识管理

### arxiv-watcher
**目的**: ArXiv 论文搜索和摘要生成
**用途**: 按关键词/作者/分类搜索论文，提取摘要并生成简洁总结
**用法**:
```bash
scripts/search_arxiv.sh "<query>"
```
**特性**: 自动保存到 `memory/RESEARCH_LOG.md`，支持深度挖掘 PDF 内容

### daily-research-papers
**目的**: 每日科研论文收集整理
**用途**: 从 arXiv、HuggingFace Daily Papers、X/Twitter 自动收集论文
**聚焦领域**: LLM、RL、Agent、UAV/Drone、Quant、Robotics
**特性**: 翻译摘要为中文，支持 cron 定时执行（每天 7:00）

### literature-review
**目的**: 学术文献综述写作辅助
**用途**: 多源搜索（Semantic Scholar、OpenAlex、Crossref、PubMed）、自动去重、按主题分组起草综述
**环境变量**: `USER_EMAIL`（礼貌访问 API）

### deep-research
**目的**: 多轮迭代深度研究
**用途**: 整合多源信息生成调研报告
**命令**:
```bash
python3 scripts/search.py "query" -n 10      # DuckDuckGo 搜索
python3 scripts/search.py "query" --news     # 新闻搜索
```
**特性**: 支持 spawn 子 agent 处理复杂调研

### ontology
**目的**: 结构化知识图谱（类型化实体记忆系统）
**用途**: 实体 CRUD（Person/Project/Task/Event/Document）、关系链接与约束验证、跨技能共享状态
**触发词**: `remember`、`what do I know about`、`link X to Y`

### obsidian-bases
**目的**: 创建和编辑 Obsidian Bases（.base 文件）
**用途**: 定义视图（table/cards/list/map）、过滤器（标签/文件夹/属性/日期）、公式属性
**特性**: YAML 格式验证

### obsidian-cli
**目的**: Obsidian 命令行工具
**用途**: 读取/创建/搜索笔记、任务管理、属性操作、插件/主题开发支持
**命令示例**:
```bash
obsidian create name="My Note" content="Hello"
obsidian search query="tag:#todo"
```

### obsidian-markdown
**目的**: Obsidian Flavored Markdown 编辑
**用途**: Wikilinks（`[[Note]]`）、Embeds（`![[embed]]`）、Callouts（`> [!type]`）、Frontmatter 属性、标签别名

### andrej-karpathy-curated-rss
**目的**: 抓取 Andrej Karpathy 精选 RSS 订阅包（92 个顶级技术博客）
**用途**: 抓取过去 24 小时新文章，翻译摘要为中文，保存到 Obsidian 知识库
**命令**:
```bash
python3 scripts/fetch_rss.py [hours]
```

---

## 🤖 AI 辅助工具

### brave-search
**目的**: Brave Search API 网页/新闻搜索
**用途**: 支持代理、限制结果数、时间范围过滤、新闻搜索模式
**命令**:
```bash
python3 scripts/brave_search.py "query" -n 10
python3 scripts/brave_search.py "query" --news
```

### ai-news-collectors
**目的**: AI 新闻聚合与热度排序
**用途**: 多维度分层搜索（最少 8 次），来源涵盖周报/Newsletter、Hacker News、Product Hunt、X/Twitter
**用法**:
```
"今天有什么 AI 新闻？"
"总结一下这周的 AI 动态"
```
**输出**: 中文摘要列表 + 原文链接

### find-skills
**目的**: 发现和安装 agent skills
**用途**: 搜索技能库、安装技能（`npx skills add <package>`）、检查更新（`npx skills check`）

### humanizer-zh
**目的**: 去除中文文本中的 AI 生成痕迹
**用途**: 检测 23 种 AI 写作模式，基于维基百科 WikiProject AI Cleanup 指南
**核心规则**: 删除填充短语、打破公式结构、变化节奏、用具体替代模糊、删除夸张强调词
**质量评分**: 5 维度评估（直接性、节奏、信任度、真实性、精炼度），满分 50 分

### agent-reach
**目的**: 配置多平台访问工具
**用途**: 支持 Twitter/X、Reddit、YouTube、GitHub、Bilibili、小红书、抖音、LinkedIn、Boss 直聘、RSS
**命令**:
```bash
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach doctor    # 环境检测
```

### pi-llm-server
**目的**: 统一 LLM 服务网关，提供 4 种服务
**用途**:
| 服务 | 端点 | 模型 | 说明 |
|------|------|------|------|
| ASR | `/v1/audio/transcriptions` | Qwen/Qwen3-ASR-1.7B | 语音识别 |
| OCR | `/v1/ocr/parser` | mineru/pipeline | 文档解析 |
| Embedding | `/v1/embeddings` | unsloth/Qwen3-Embedding-0.6B | 文本向量化 |
| Reranker | `/v1/rerank` | Qwen/Qwen3-Reranker-0.6B | 文档重排序 |
**API 地址**: `http://api.adv-ci.com:8090/v1`（环境变量 `PI_LLM_URL`）
**支持格式**: PDF、图片、Word、PPT、Excel、音频，统一输出 Markdown + 图片

### postgres
**目的**: PostgreSQL 最佳实践和查询优化
**用途**: Schema 设计、索引优化、分区、MVCC/VACUUM、查询模式优化、连接池和内存管理

### mcp-builder
**目的**: MCP（Model Context Protocol）服务器开发指南
**用途**: Python（FastMCP）或 Node/TypeScript 的 MCP 工具开发，Agent-centric 设计模式
**核心原则**: 为工作流而非 API 端点设计工具

### pi-memory
**目的**: 查询本地知识库（笔记、文章、剪报等），支持向量语义检索
**用途**: 搜索本地资料/笔记/知识库、查找已收藏或已索引的文档
**服务地址**: `http://agent.adv-ci.com:9873`（默认）
**触发词**: `搜索知识库`、`查一下知识库`、`搜一下笔记`、`knowledge search`

---

## 🧠 思维模型

### thinker-elon-musk
**目的**: 马斯克的思维操作系统
**核心心智模型**: 渐近极限法、五步算法、存在主义锚定、垂直整合、快速迭代
**决策启发式**: 需求附人名、先算渐近极限、删到过度再补回、白痴指数
**用法**: `"这个成本合理吗？" → 白痴指数分析`、`"流程有必要吗？" → 五步算法审视`
**信息源**: Walter Isaacson 传记、法庭证词、SpaceX/Tesla 财报会议

### thinker-feynman
**目的**: 费曼的思维框架与表达方式
**核心心智模型**: 命名≠理解、反自欺原则、不确定性是力量、具象化思考、深度游戏
**决策启发式**: 货物崇拜检测、演示>论证、12 个问题过滤器
**用法**: `"这是不是 cargo cult？" → 检测形式与实质`、`"能不能做个演示？" → 演示>论证原则`
**信息源**: 《别闹了，费曼先生》、Cargo Cult Science 演讲、挑战者号调查记录

### thinker-munger
**目的**: 查理·芒格的思维框架
**核心心智模型**: 多元思维模型、逆向思考、Lollapalooza 效应、能力圈、激励机制
**决策启发式**: 逆向切入、三筐分类法、坐在屁股上、配得上法则、25 种认知偏误清单
**用法**: `"逆向思考一下" → 不问如何成功，问如何确保失败`
**信息源**: 《穷查理宝典》、伯克希尔股东会、《如何保证人生痛苦》

### thinker-naval
**目的**: Naval Ravikant 的思维操作系统
**核心心智模型**: 杠杆思维、特定知识、欲望即合同、重新定义术、痛苦→系统重构
**决策启发式**: 无需许可原则、日历测试、纠结即否定、手册测试
**用法**: `"这份工作有杠杆吗？" → 评估劳动力/资本/代码/媒体杠杆`
**信息源**: 《The Almanack of Naval Ravikant》、How to Get Rich Tweetstorm

### thinker-steve-jobs
**目的**: 史蒂夫·乔布斯的思维框架
**核心心智模型**: 聚焦即说不、端到端控制、连点成线、死亡过滤器、现实扭曲力场、技术×人文
**决策启发式**: 先做减法、不问用户要什么、A Player 自我增强、一句话定义
**用法**: `"帮我用乔布斯的角度想想" → 聚焦/减法/端到端控制审视`
**信息源**: Isaacson 授权传记、Stanford 演讲、Lost Interview

### thinker-taleb
**目的**: 塔勒布的思维框架
**核心心智模型**: 非对称风险、反脆弱偏好、Skin in the Game、林迪效应、Via Negativa
**决策启发式**: 预防原则、杠铃策略、遍历性检验、火鸡问题、凸性试错
**用法**: `"会不会黑天鹅？" → 评估尾部风险和非对称性`
**信息源**: Incerto 五部曲、EconTalk 访谈、COVID 预警论文

### thinker-zhangxuefeng
**目的**: 张雪峰的思维框架与表达方式
**核心心智模型**: 社会筛子论、选择>努力、就业倒推法、阶层现实主义
**决策启发式**: 灵魂追问法、中位数原则、不可替代性检验、500 强测试、10 年后压迫测试
**用法**: `"帮我用张雪峰的角度想想" → 就业倒推/社会筛子分析`
**信息源**: 5 本著作、15+ 篇权威采访、完整人生时间线

---

## 🎨 创意与写作

### brainstorming
**目的**: 头脑风暴和设计规划
**用途**: 理解项目现状、提问澄清需求、提出 2-3 个方案并权衡、分块呈现设计（200-300 字/节）

### algorithmic-art
**目的**: 算法艺术创作（p5.js）
**用途**: 种子随机性 + 交互式参数探索，粒子系统、流场、噪声场
**流程**: 创建算法哲学（.md）→ 用 p5.js 表达（.html + .js）
**输出**: .md（哲学）、.html + .js（交互查看器）

### canvas-design
**目的**: 视觉设计哲学创作
**用途**: 形式、空间、色彩、构图，图片、图形、形状、图案
**流程**: 创建设计哲学（.md）→ 视觉表达（.pdf/.png）
**输出**: .md（哲学）、.pdf/.png（视觉作品）

### artifacts-builder
**目的**: 构建复杂 HTML 工件
**用途**: 创建多组件、动画丰富的交互式网页应用

---

## 🎬 音视频处理

### youtube-subtitle
**目的**: 提取 YouTube 视频字幕并保存到知识库
**用途**: 使用 `youtube-transcript-api` 直接拉取字幕轨道，无需下载音频
**特性**: 多语言支持（zh-CN、en 等）、自动格式化 Markdown、自动保存到知识库、WebDAV 同步
**依赖**: `pip install youtube-transcript-api`
**用法**: `转写这个视频：https://www.youtube.com/watch?v=xxx`

### youtube-asr
**目的**: YouTube/Bilibili 视频音频自动转写（ASR）
**流程**: CDP 导出 Chrome cookies → yt-dlp 下载音频 → Qwen3-ASR-1.7B 转写 → 保存到知识库
**性能**: 下载 ~1-5 MB/s，转写 ~1-2 分钟/10 分钟音频，中文准确率 ~95%
**支持**: 可选 `--save-to-obsidian` 保存至 Obsidian

### video-frames
**目的**: 从视频中提取帧或短视频片段
**用途**: 提取关键帧用于分析、演示、文档配图
**用法**: 指定时间范围提取特定画面

### audio-transcription
**目的**: 音频文件转写（MP3/WAV）
**用途**: 会议录音、播客、语音笔记转文字
**模型**: Qwen/Qwen3-ASR-1.7B，API: `http://api.adv-ci.com:8090/v1/audio/transcriptions`

---

## 📝 写作与润色

### critic-mentor-review
**目的**: 学术论文审稿与润色（双核对抗引擎）
**用途**:
- **Critic（审稿屠夫）**: 攻击逻辑漏洞、质疑数据、评估创新性
- **Mentor（润色匠人）**: 提升语言地道性、优化逻辑流
- 模拟 Nature/Science 级审稿人，生成 Cover Letter、优化 Abstract
**约束**: 原意保留红线、分块处理、强制输出 Review Dashboard

### literature-review
**目的**: 学术文献综述写作辅助
> 完整说明详见 [研究与知识管理](#研究与知识管理)

### humanizer-zh
**目的**: 去除 AI 生成文本痕迹
> 完整说明详见 [AI 辅助工具](#ai-辅助工具)

### markdown-to-docx
**目的**: Markdown 转 Word DOCX
> 完整说明详见 [文档处理](#文档处理)

---

## 🎨 图表与演示

### drawio-skill
**目的**: 创建图表、流程图、架构图
**用途**: 生成 `.drawio` XML 文件，支持 ERD/UML/Sequence/Architecture/Flowchart 等多种类型
**特性**: 自检功能（自动检测重叠、标签溢出）、支持嵌入式导出（可编辑 XML）
**触发词**: `diagram`、`visualize`、`flowchart`、`architecture diagram`
**依赖**: draw.io desktop app CLI

### frontend-slides
**目的**: 创建动画丰富的 HTML 幻灯片
**特性**: 零依赖（单 HTML 文件）、避免"AI slop"审美、精确适配 100vh
**流程**: 内容发现 → 风格发现（3 个预览） → 生成完整演示 → 交付/导出 PDF
**分享**: 支持部署到 Vercel、导出 PDF

### visual-cognition-slides
**目的**: 视觉认知设计协作者
**用途**: 基于认知科学与教学设计，把知识转化为观众能接收、理解、记住的视觉叙事
**工作流**: Intake 问诊 → 叙事骨架 → 视觉风格选择（11 种） → Visual Translation → 生成 HTML
**禁止**: bullet point 堆砌、渐变背景白字、AI 味审美

### pptx
**目的**: PowerPoint 演示文稿处理
**用途**: 读取/提取内容、编辑现有演示、从零创建幻灯片
**用法**: 支持 `markitdown` 提取内容，基于 python-pptx 创建/编辑

### graphify
**目的**: 将任意输入（代码、文档、论文、图片）转换为知识图谱
**用途**: 自动聚类社区检测，输出交互式 HTML、GraphRAG JSON、审计报告
**用法**:
```
/graphify <path> --mode deep          # 深度提取
/graphify <path> --update             # 增量更新
/graphify <path> --neo4j-push <url>   # 推送到 Neo4j
```
**导出格式**: GraphML、SVG、Neo4j Cypher

---

## ⚙️ 系统与工具

### openclaw-optimization
**目的**: OpenClaw AI Agent 性能优化
**用途**: Session 管理（清理孤儿 sessions）、Context budget 优化、Token 跟踪、自动化维护
**健康检查**:
```bash
bash scripts/health-check.sh
```
**指标**: Active sessions <100（健康）、最大 session <5MB、Context 使用率 <60%

### paper-auto-review
**目的**: 自动审稿工具
**用途**: 扫描论文目录 → pi-llm-server 转 Markdown → Bailian LLM（qwen3.6-plus）生成审稿意见
**特性**: 自动检测论文语言（中文/英文），使用对应审稿 Prompt
**用法**:
```bash
python3 paper_auto_review.py --year 2026 --dry-run   # 预览
python3 paper_auto_review.py --year 2026              # 执行审稿
```
**输出**: 每篇论文目录下 `{原名}_review_draft.md`

### paper-fetch
**目的**: 通过合法开放获取源下载论文 PDF
**用途**: 给定 DOI/标题/URL，依次尝试 Unpaywall → Semantic Scholar → arXiv → PubMed Central → bioRxiv/medRxiv
**特性**: 不使用 Sci-Hub，结构化 JSON 输出，支持批量处理
**用法**:
```bash
python scripts/fetch.py <DOI>
python scripts/fetch.py --batch <FILE|->
```

### paper-innovation
**目的**: 学术论文创新点挖掘（5-Skill 工作流）
**用途**: 范式爆破 → 理论碰撞+异常值 → 方法论升级 → 贡献声明
**适用场景**: 找论文创新点、提炼创新点、系统性探索研究新视角
**流程**: 5 个专精 Skill 串联，多维度审视研究领域

### pd_doc
**目的**: 基于文档索引的迭代开发 — 项目文档自动管理与增量更新
**用途**: 新项目创建文档骨架（architecture.md/api.md/changelog.md），已有项目增量更新
**触发**: `/pd_doc`
**原则**: 基于实际代码分析、先验证再记录、大模块才独立文档

### pd_brainstorming
**目的**: 深度头脑风暴 + 设计追问 — 把模糊想法变成完整设计方案
**用途**: 分析需求、规划任务、讨论设计方案、把想法想透想彻底
**触发**: `/pd_brainstorming`
**流程**: 理解上下文 → 深度追问（Grill 模式） → 方案输出 → 保存到 `docs/RAD.md`

### write-a-skill
**目的**: 创建新的 agent skills
**用途**: 帮助用户从零构建 skill，包括 SKILL.md 结构、渐进式披露、内置资源打包
**流程**: 收集需求 → 起草 SKILL.md → 用户审阅 → 最终发布
**触发**: `"创建一个新的 skill"`、`"我想写一个技能"`

### tmux
**目的**: 远程管理 tmux 会话
**用途**: 创建/连接/管理 tmux 会话，支持后台任务运行

### lesson
**目的**: 从对话中存储经验教训
**用途**: 触发 `/lesson` 将当前对话中的经验保存到 memory 系统

---

## 快速索引

| 技能名 | 分类 | 一句话 |
|--------|------|--------|
| agent-reach | AI 辅助工具 | 多平台访问配置 |
| ai-news-collectors | AI 辅助工具 | AI 新闻聚合与热度排序 |
| algorithmic-art | 思维与创意 | p5.js 算法艺术创作 |
| andrej-karpathy-curated-rss | 研究与知识管理 | Karpathy 精选 RSS |
| arxiv-watcher | 研究与知识管理 | ArXiv 论文搜索 |
| audio-transcription | 音视频处理 | 音频文件转文字 |
| brave-search | AI 辅助工具 | Brave 网页搜索 |
| brainstorming | 思维与创意 | 头脑风暴与规划 |
| canvas-design | 思维与创意 | 视觉设计哲学创作 |
| critic-mentor-review | 写作与润色 | 论文审稿双核引擎 |
| daily-research-papers | 研究与知识管理 | 每日论文收集 |
| deep-research | 研究与知识管理 | 多轮深度研究 |
| docx | 文档处理 | Word 文档处理 |
| drawio-skill | 图表与演示 | Draw.io 图表 |
| fireworks-tech-graph | 图表与演示 | 技术架构图 SVG+PNG |
| find-skills | AI 辅助工具 | 技能发现与安装 |
| frontend-slides | 图表与演示 | HTML 幻灯片 |
| graphify | 图表与演示 | 知识图谱转换 |
| humanizer-zh | 写作与润色 | AI 文本人性化 |
| lesson | 系统与工具 | 经验存储 |
| literature-review | 写作与润色 | 文献综述写作 |
| markdown-to-docx | 文档处理 | MD 转 Word |
| mcp-builder | AI 辅助工具 | MCP 服务器开发 |
| minimax-docx | 文档处理 | Word 文档（OpenXML） |
| minimax-pdf | 文档处理 | PDF 生成与设计 |
| minimax-xlsx | 文档处理 | Excel 处理 |
| obsidian-bases | 研究与知识管理 | Obsidian Bases |
| obsidian-cli | 研究与知识管理 | Obsidian CLI |
| obsidian-markdown | 研究与知识管理 | Obsidian Markdown |
| ontology | 研究与知识管理 | 知识图谱实体系统 |
| openclaw-optimization | 系统与工具 | Agent 性能优化 |
| paper-auto-review | 系统与工具 | 自动审稿 |
| paper-fetch | 系统与工具 | 论文 PDF 下载 |
| paper-innovation | 系统与工具 | 创新点挖掘 |
| pd_brainstorming | 系统与工具 | 深度设计追问 |
| pd_doc | 系统与工具 | 项目文档管理 |
| pdf | 文档处理 | PDF 处理 |
| pi-llm-server | AI 辅助工具 | LLM 服务网关 |
| pi-memory | AI 辅助工具 | 本地知识库查询 |
| postgres | AI 辅助工具 | PostgreSQL 最佳实践 |
| pptx | 图表与演示 | PowerPoint 处理 |
| pyword | 文档处理 | Word 自动化 Python |
| thinker-elon-musk | 思维模型 | 马斯克思维 |
| thinker-feynman | 思维模型 | 费曼思维 |
| thinker-munger | 思维模型 | 芒格决策 |
| thinker-naval | 思维模型 | Naval 财富哲学 |
| thinker-steve-jobs | 思维模型 | 乔布斯产品思维 |
| thinker-taleb | 思维模型 | 塔勒布反脆弱 |
| thinker-zhangxuefeng | 思维模型 | 张雪峰教育规划 |
| tmux | 系统与工具 | tmux 会话管理 |
| video-frames | 音视频处理 | 视频帧提取 |
| visual-cognition-slides | 图表与演示 | 视觉认知设计 |
| write-a-skill | 系统与工具 | 创建新 Skill |
| xlsx | 文档处理 | Excel 处理 |
| youtube-asr | 音视频处理 | YouTube 音频转写 |
| youtube-subtitle | 音视频处理 | YouTube 字幕提取 |
