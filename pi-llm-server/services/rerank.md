# Rerank 文档重排序服务

对文档列表进行查询相关性重排序。

## 端点

```
POST /v1/rerank
Content-Type: application/json
```

## 模型

- `Qwen/Qwen3-Reranker-0.6B`（默认）

## 请求体

```json
{
  "model": "Qwen/Qwen3-Reranker-0.6B",
  "query": "深度学习",
  "documents": ["文档1内容", "文档2内容", "文档3内容"]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 否 | 模型名称，默认 `Qwen/Qwen3-Reranker-0.6B` |
| `query` | string | 是 | 查询语句 |
| `documents` | string[] | 是 | 待排序的文档列表 |

## 返回格式

```json
{
  "results": [
    {
      "index": 2,
      "document": "深度学习是机器学习的子集",
      "relevance_score": 0.8234
    },
    {
      "index": 1,
      "document": "机器学习是实现 AI 的方法",
      "relevance_score": 0.1523
    }
  ]
}
```

- 结果已按相关性从高到低排序
- `index` 为原始文档列表中的索引
- `relevance_score` 为相关性得分，范围 0~1

## Python 调用示例

```python
import requests
import os

PI_LLM_URL = os.environ.get('PI_LLM_URL', 'http://api.adv-ci.com:8090/v1')
PI_LLM_API_KEY = os.environ.get('PI_LLM_API_KEY', 'sk-5f8b839908d14561590b70227c72ca86')

HEADERS = {
    "Authorization": f"Bearer {PI_LLM_API_KEY}",
    "Content-Type": "application/json"
}

def rerank_documents(query, documents, model="Qwen/Qwen3-Reranker-0.6B"):
    session = requests.Session()
    session.trust_env = False

    payload = {
        "model": model,
        "query": query,
        "documents": documents
    }

    response = session.post(
        f'{PI_LLM_URL}/rerank',
        headers=HEADERS,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    return response.json().get('results', [])
```

## 命令行调用

```bash
python scripts/pi_llm_server_skill.py rerank --query "深度学习" --doc "文档1" --doc "文档2" --doc "文档3"
```

## 超时

120 秒
