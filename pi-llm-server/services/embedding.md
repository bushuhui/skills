# Embedding 向量生成服务

生成文本的嵌入向量。

## 端点

```
POST /v1/embeddings
Content-Type: application/json
```

## 模型

- `unsloth/Qwen3-Embedding-0.6B`（默认）

## 请求体

```json
{
  "model": "unsloth/Qwen3-Embedding-0.6B",
  "input": ["文本内容"],
  "encoding_format": "float"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 否 | 模型名称，默认 `unsloth/Qwen3-Embedding-0.6B` |
| `input` | string[] | 是 | 输入文本，支持单个或列表 |
| `encoding_format` | string | 否 | `float` 或 `base64`，默认 `float` |

## 返回格式

```json
{
  "data": [
    {
      "index": 0,
      "embedding": [0.012, -0.045, 0.089, ...]
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

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

def generate_embedding(text, model="unsloth/Qwen3-Embedding-0.6B"):
    session = requests.Session()
    session.trust_env = False

    payload = {
        "model": model,
        "input": [text],
        "encoding_format": "float"
    }

    response = session.post(
        f'{PI_LLM_URL}/embeddings',
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    result = response.json()
    if result.get('data'):
        return result['data'][0]['embedding']
    return None
```

## 命令行调用

```bash
python scripts/pi_llm_server_skill.py embed "今天天气真好"
```

## 超时

60 秒
