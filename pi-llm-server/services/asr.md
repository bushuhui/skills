# ASR 语音识别服务

将音频文件转写为文字。

## 端点

```
POST /v1/audio/transcriptions
Content-Type: multipart/form-data
```

## 模型

- `Qwen/Qwen3-ASR-1.7B`（默认）

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | 是 | 音频文件 |
| `model` | string | 否 | 模型名称，默认 `Qwen/Qwen3-ASR-1.7B` |

## 返回格式

```json
{
  "text": "转写后的文字内容..."
}
```

## Python 调用示例

```python
import requests
import os

PI_LLM_URL = os.environ.get('PI_LLM_URL', 'http://api.adv-ci.com:8090/v1')
PI_LLM_API_KEY = os.environ.get('PI_LLM_API_KEY', 'sk-5f8b839908d14561590b70227c72ca86')

def transcribe_audio(audio_path, model="Qwen/Qwen3-ASR-1.7B"):
    session = requests.Session()
    session.trust_env = False  # 禁用代理

    with open(audio_path, 'rb') as f:
        files = {'file': (os.path.basename(audio_path), f, 'audio/mpeg')}
        data = {'model': model}

        response = session.post(
            f'{PI_LLM_URL}/audio/transcriptions',
            headers={"Authorization": f"Bearer {PI_LLM_API_KEY}"},
            files=files,
            data=data,
            timeout=600
        )

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    return response.json().get('text', '')
```

## 命令行调用

```bash
python scripts/pi_llm_server_skill.py transcribe /path/to/audio.mp3
```

## 超时

600 秒（10 分钟）

## 支持格式

`.mp3`, `.wav`, `.m4a`, `.flac`
