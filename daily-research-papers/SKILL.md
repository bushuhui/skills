---
name: daily-research-papers
description: |
  每日科研论文收集整理。从 arXiv、HuggingFace Daily Papers、X/Twitter 抓取最新论文，
  聚焦：大语言模型(LLM)、强化学习(RL)、Agent、无人机(UAV/Drone)、量化交易(Quant)、机器人(Robotics)。
  触发条件：
  - 每天早上 7:00 cron 自动执行
  - 用户要求抓取最新论文
  - 用户提到 "论文速递" 或 "paper digest"
---

# Daily Research Papers

每日从多个来源收集 AI/ML 相关科研论文，筛选关注领域，翻译摘要为中文，保存到 Obsidian 知识库。

## 关注领域

1. **大语言模型 (LLM)** — 训练、推理、对齐、评测、架构
2. **强化学习 (RL)** — RLHF、GRPO、在线/离线 RL、多智能体 RL
3. **Agent** — LLM Agent、工具使用、规划、多智能体协作
4. **无人机 (UAV/Drone)** — 自主导航、视觉感知、路径规划、集群
5. **量化交易 (Quant)** — AI 量化策略、金融 LLM、时序预测
6. **机器人 (Robotics)** — 具身智能、操作、VLA、运动控制

## 工作流程

### 步骤 1：抓取 arXiv 论文

运行抓取脚本：

```bash
python3 scripts/fetch_arxiv.py [hours]
```

- 默认抓取过去 24 小时
- 覆盖 arXiv 分类：cs.CL, cs.AI, cs.LG, cs.MA, cs.RO, cs.CV, stat.ML, q-fin.TR, q-fin.CP, eess.SY
- 输出 JSON 数组到 stdout

### 步骤 2：抓取 HuggingFace Daily Papers

```bash
python3 scripts/fetch_hf_papers.py
```

- 抓取 https://huggingface.co/papers 当日论文
- 输出 JSON 数组到 stdout

### 步骤 3：抓取 X/Twitter 论文动态

```bash
python3 scripts/fetch_x_papers.py
```

- 通过 Chrome MCP 或 web_fetch 抓取以下账号最近的论文分享：
  - @OpenAI, @AnthropicAI, @GoogleDeepMind, @MetaAI
  - @_akhaliq (AK，每日论文速递大佬)
  - @aabordes, @kabordes (Meta AI)
  - @labordes (SGLang)
  - @DrJimFan (Jim Fan, NVIDIA 具身智能)
  - @kabordes
- 如果 X 抓取失败（常见），跳过此步骤，不影响整体流程
- 输出 JSON 数组到 stdout

### 步骤 4：合并去重 & 领域筛选

对三个来源的论文进行：
1. 按 arXiv ID 去重（同一篇论文可能出现在多个来源）
2. 按关注领域筛选（关键词匹配 + 分类匹配）
3. 按来源热度排序（HuggingFace 上榜 > 多来源出现 > 单来源）

### 步骤 5：翻译并保存到知识库（带重试机制）

⚠️ 文件命名规则（避免 bisync 冲突）：
- 目标文件：`/home/bushuhui/data-all/note/bushuhui/Clippings/YYYYMM/YYYYMMDD-research-papers.md`
- 独立文件，不要写入 `YYYYMMDD.md` 主文件！

**写入策略（防止 LiveSync 锁定导致失败）：**

1. **先写骨架**：用 `write` 创建只有标题行的小文件（< 500 字节）
2. **分段追加**：用 `edit` 逐段追加内容，每次不超过 1.5KB
3. **重试机制**：
   - 如果 `write`/`edit` 失败，等待 2 秒后重试
   - 最多重试 3 次，每次间隔递增（2s → 4s → 6s）
   - 如果 3 次都失败，用 `read` 检查文件是否实际已写入成功
   - 如果文件存在且内容正确，视为成功（LiveSync 锁定导致的误报）
   - 如果文件不存在或内容为空，报告失败

**伪代码：**
```
function writeWithRetry(path, content, maxRetries=3):
  for i in 1..maxRetries:
    result = write/edit(path, content)
    if result.success: return true
    wait(2 * i seconds)
  
  # 所有重试失败，检查是否实际成功
  fileContent = read(path)
  if fileContent contains expected content:
    log("写入验证误报，文件实际存在")
    return true
  else:
    throw("写入失败：文件不存在或内容不完整")
```

文件格式：

```markdown
# 每日科研论文速递 - YYYY-MM-DD

> 来源: arXiv + HuggingFace Daily Papers + X/Twitter
> 抓取时间: YYYY-MM-DD HH:MM
> 论文数: N 篇

## 🔥 热门论文（多来源推荐）

### [中文标题翻译]
- 原文: [英文标题](arXiv链接)
- 作者: xxx et al.
- 领域: LLM / RL / Agent / UAV / Quant / Robotics
- 来源: arXiv + HuggingFace + X(@xxx)
- 摘要: [中文摘要，3-5 句话概括核心贡献和方法]

## 📄 LLM 大语言模型

### [中文标题翻译]
...

## 🎯 强化学习

### [中文标题翻译]
...

## 🤖 Agent

...

## 🚁 无人机

...

## 📈 量化交易

...

## 🦾 机器人

...
```

翻译要求：
- 标题翻译成中文，括号内保留英文原标题
- 摘要翻译成中文，3-5 句话，突出核心贡献和方法创新
- 专有名词保留英文（如 Transformer、RLHF、PPO、VLA 等）
- 如果论文跨多个领域，放在最相关的分类下，其他分类加引用

### 步骤 6：同步

```bash
bash /home/bushuhui/scripts/backup_bushuhui_webdav.sh
```

## 注意事项

- 脚本路径相对于此 skill 目录：`scripts/`
- arXiv API 不需要代理，HuggingFace 可能需要代理
- X/Twitter 抓取经常失败，设计为可选步骤
- 如果总论文数为 0，说明没有新内容，跳过保存
- 每天论文量可能很大（50-100+），筛选后保留 20-40 篇最相关的
