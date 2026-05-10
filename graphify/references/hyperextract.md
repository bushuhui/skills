# HyperExtract — 知识提取工具参考

GitHub: [yifanfeng97/Hyper-Extract](https://github.com/yifanfeng97/Hyper-Extract) | Stars: 838+ | License: Apache-2.0

## 定位

LLM 驱动的知识提取 CLI，将非结构化文本转化为强类型的 **Knowledge Abstracts (KA)**。与 graphify 不同，HyperExtract 聚焦于**单文档/多文档的知识结构抽取**（实体、关系、时间线），而非代码库图谱构建。

## 三层架构

```
Templates (YAML 声明式) → Methods (提取算法) → Auto-Types (数据结构)
```

- **Auto-Types**: `AutoModel`, `AutoList`, `AutoSet`, `AutoGraph`, `AutoHypergraph`, `AutoTemporalGraph`, `AutoSpatialGraph`, `AutoSpatioTemporalGraph`
- **Methods**: GraphRAG, LightRAG, Hyper-RAG, KG-Gen 等
- **Templates**: 80+ 预设，覆盖 6 大领域（金融/法律/医疗/中医/工业/通用）

## CLI 工作流

```bash
he config init -k API_KEY          # 配置 API
he parse input.md -t general/base_graph -o ./ka -l zh   # 提取 → KA 目录
he search ./ka/ "关键词"            # FAISS 语义搜索
he show ./ka/                       # 知识图谱可视化 (ontosight)
he feed ./ka/ new.md               # 增量合并
he talk ./ka/ -i                    # RAG 对话
```

## Python API

```python
from hyperextract import Template
ka = Template.create("general/biography_graph", lang="zh")
result = ka.parse(text)       # 解析 → 新实例
ka.feed_text(text)            # 增量 → 当前实例
result.search("问题")          # 语义搜索
result.chat("问题")            # RAG 对话
result.dump("./output/")       # 持久化 (data.json + metadata.json + index/)
result.load("./output/")       # 加载
```

## YAML 模板结构

```yaml
language: [zh, en]
name: graph
type: graph
description: {zh: '...', en: '...'}
output:
  entities:
    fields:
    - name: name
      type: str
      description: {...}
    - name: type
      type: str
      description: {...}
  relations:
    fields:
    - name: source; type: str
    - name: target; type: str
    - name: type; type: str
guideline:
  target: {zh: '...', en: '...'}
  rules_for_entities: [...]
  rules_for_relations: [...]
identifiers:
  entity_id: name
  relation_id: '{source}|{type}|{target}'
options:
  extraction_mode: two_stage  # single_stage 或 two_stage
```

## 关键依赖

- `langchain` + `langchain-openai` → LLM 调用
- `faiss-cpu` → 向量语义搜索
- `ontomem` (OMem) → 语义级去重与合并
- `ontosight` → 知识图谱可视化

## 与 graphify 对比

| 特性 | HyperExtract | graphify |
|------|-------------|----------|
| 输入 | 文本/Markdown | 代码+文档+论文+图片 |
| 输出 | 强类型 KA (data.json + index) | 图 JSON + HTML + Obsidian |
| 模板 | YAML 声明式 | 无（LLM 直接提取） |
| 增量 | `he feed` 合并 | `--update` 增量 |
| 适用 | 单文档知识抽取、文献综述 | 代码库理解、跨文档关联 |
| 社区检测 | ❌ | ✅ (Louvain) |
| 代码 AST | ❌ | ✅ |
