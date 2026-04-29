---
name: pi-memory
description: |
  查询本地知识库（笔记、文章、剪报等），支持向量语义检索。
  触发条件：
  - 用户要求搜索本地资料/笔记/知识库
  - 用户提到 "查一下知识库" / "搜一下笔记" / "知识库有没有"
  - 需要查找用户已收藏或已索引的文档内容
  - 用户在讨论中引用了本地知识库中的概念或文件
  不适用于：纯网络搜索（用 search1api）、简单事实问题（直接回答）
triggers:
  - 搜索知识库
  - 查一下知识库
  - 搜一下笔记
  - 知识库查询
  - knowledge search
  - 本地知识
---

# Pi-Memory Knowledge Skill

查询 pi-memory 服务的知识库，基于向量语义检索已索引的本地笔记、文章、剪报等文档。

## 服务信息

```
API 地址: http://agent.adv-ci.com:9873（默认）
知识库搜索端点: POST /api/knowledge/search
```

用户可传入自定义服务器地址。未指定时使用默认地址。

## 搜索流程

**Step 1：查询扩展**（由 Claude 执行）

将用户关键词扩展为多个查询变体，考虑：
- 中英对照（如 `无人机` ↔ `UAV` ↔ `drone`）
- 同义词/近义词（如 `控制` ↔ `操控` ↔ `导航` ↔ `control`）
- 缩写/全称（如 `LLM` ↔ `大语言模型`）
- 上下位词（如 `强化学习` ↔ `RL`）
- 领域相关术语（如 `无人机控制` → `飞控` → `Mavlink` → `PX4`）

通常扩展为 3-5 个变体。如果关键词已经很明确（如具体文件名），不必扩展。

**Step 2：调用搜索脚本**

```bash
python3 scripts/knowledge_search.py --queries "关键词1" "关键词2" "关键词3" --limit 100
```

## 调用示例

```bash
# 单次搜索（不扩展）
python3 scripts/knowledge_search.py "具体文件名.md"

# 扩展搜索（中英对照 + 同义词）
python3 scripts/knowledge_search.py --queries "无人机控制" "UAV control" "drone导航" --limit 100

# 多领域扩展
python3 scripts/knowledge_search.py --queries "强化学习" "RL" "reinforcement learning" --limit 100

# 自定义服务器
python3 scripts/knowledge_search.py --queries "集群建图" "swarm mapping" --server http://192.168.1.10:9873

# 输出原始 JSON
python3 scripts/knowledge_search.py --queries "大模型" "LLM" --raw
```

## 搜索策略选择

| 场景 | 方式 |
|------|------|
| 已知精确关键词（文件名等） | 单次搜索 |
| 需要全面覆盖 | 扩展为 3-5 个查询变体，传入 `--queries` |
| 用户要求"尽可能全面" | 扩展 5+ 个变体，`--limit 100` |

## 返回格式

```json
{
  "success": true,
  "data": {
    "count": 100,
    "queries": ["无人机控制", "UAV control", "drone导航"],
    "results": [
      {
        "id": "uuid",
        "text": "文档片段内容...",
        "filePath": "/full/path/to/file.md",
        "score": 0.72
      }
    ]
  }
}
```

## 响应规范

搜索完成后：
1. 展示每条结果的 **`filePath`（完整路径）** 和匹配度（score），不要只显示 `fileName`
2. 输出最相关的 3-5 个片段全文内容
3. 如果结果为空，建议用户考虑是否已索引该文件，或尝试不同的关键词
4. 不要将搜索结果与网络搜索结果混为一谈

## 注意事项

- 搜索超时设为 30 秒
- 如果服务器不可达，告知用户并建议检查 `pi-memory` 服务状态
- 查询内容应为具体概念、技术术语、文件名等，避免过于宽泛的搜索词
