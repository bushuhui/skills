---
name: pi-llm-server
description: 统一 LLM 服务网关，提供语音识别 (ASR)、文档解析 (OCR)、Embedding 向量生成、文档重排序 (Rerank) 服务。支持 PDF、图片、Office 文档、音频等多种文件格式。当用户需要转写音频、解析文档为 Markdown、生成嵌入向量或重排序文档时使用此技能。
triggers:
  - 语音识别
  - 转写
  - 音频转文字
  - 文档解析
  - PDF 转 Markdown
  - OCR
  - embedding
  - rerank
---

## 📺 技能描述

**功能**: 提供统一的 LLM 服务网关访问，包括：
- **语音识别 (ASR)**: 将音频文件转写为文字
- **文档解析 (OCR)**: 解析 PDF、图片、Office 文档为 Markdown 和图片
- **Embedding**: 生成文本嵌入向量
- **Rerank**: 文档相关性重排序

**API 端点**: 
- 默认：`http://api.adv-ci.com:8090/v1`
- 可通过环境变量 `PI_LLM_URL` 自定义

**认证 Token**: 
- 默认：`sk-5f8b839908d14561590b70227c72ca86`
- 可通过环境变量 `PI_LLM_API_KEY` 自定义

**可用服务**:

| 服务 | 端点 | 模型 | 说明 |
|------|------|------|------|
| **ASR** | `/v1/audio/transcriptions` | `Qwen/Qwen3-ASR-1.7B` | 语音识别 |
| **Embedding** | `/v1/embeddings` | `unsloth/Qwen3-Embedding-0.6B` | 文本向量化 |
| **Reranker** | `/v1/rerank` | `Qwen/Qwen3-Reranker-0.6B` | 文档重排序 |
| **MinerU (OCR)** | `/v1/ocr/parser` | `mineru/pipeline` | 文档解析 |

**支持的文件格式**:

| 类型 | 扩展名 | 说明 |
|------|--------|------|
| PDF | `.pdf` | 原生 PDF 文档 |
| 图片 | `.jpg`, `.jpeg`, `.png` | 自动转换为 PDF 后解析 |
| Word | `.docx`, `.doc` | 使用 libreoffice 转换为 PDF 后解析 |
| PPT | `.pptx`, `.ppt` | 使用 libreoffice 转换为 PDF 后解析 |
| Excel | `.xlsx`, `.xls` | 使用 libreoffice 转换为 PDF 后解析 |
| 音频 | `.mp3`, `.wav`, `.m4a`, `.flac` | 语音识别 |

---

## 🚀 快速使用

### 方式 1: 自然语言调用

```
帮我转写这个音频文件：[文件路径]
把这个 PDF 解析成 Markdown：[文件路径]
生成这段文本的 embedding 向量：[文本内容]
对这些文档进行重排序，查询词是：[查询词]
```

### 方式 2: 命令行调用

```bash
# 语音识别
/skill pi-llm-server transcribe /path/to/audio.mp3

# 文档解析（默认输出到源文件同目录）
/skill pi-llm-server parse /path/to/document.pdf
# 输出：
#   /path/to/document.md
#   /path/to/document_images/

# 文档解析（自定义输出目录）
/skill pi-llm-server parse /path/to/document.pdf --output /custom/dir

# Embedding
/skill pi-llm-server embed "今天天气真好"

# Rerank
/skill pi-llm-server rerank --query "深度学习" --docs "文档 1" "文档 2" "文档 3"
```

### 方式 3: Python 脚本调用

```bash
python scripts/pi_llm_server_skill.py <command> [arguments]
```

---

## 📋 执行步骤

### Step 1: 配置 API 端点和 Token

```python
import os

# API 配置（优先级：环境变量 > 默认值）
PI_LLM_URL = os.environ.get('PI_LLM_URL', 'http://api.adv-ci.com:8090/v1')
PI_LLM_API_KEY = os.environ.get('PI_LLM_API_KEY', 'sk-5f8b839908d14561590b70227c72ca86')

HEADERS = {
    "Authorization": f"Bearer {PI_LLM_API_KEY}",
    "Content-Type": "application/json"
}
```

---

### Step 2: 服务状态查询

```python
import requests

def check_service_status():
    """检查服务状态"""
    session = requests.Session()
    session.trust_env = False  # 禁用代理
    
    # 健康检查
    health_resp = session.get(f'{PI_LLM_URL.replace("/v1", "")}/health', timeout=10)
    
    # 详细状态
    status_resp = session.get(f'{PI_LLM_URL.replace("/v1", "")}/status', 
                               headers=HEADERS, timeout=10)
    
    # 可用模型
    models_resp = session.get(f'{PI_LLM_URL}/models', 
                               headers=HEADERS, timeout=10)
    
    return {
        'health': health_resp.json() if health_resp.status_code == 200 else None,
        'status': status_resp.json() if status_resp.status_code == 200 else None,
        'models': models_resp.json() if models_resp.status_code == 200 else None
    }
```

---

### Step 3: 语音识别 (ASR)

```python
def transcribe_audio(audio_path, model="Qwen/Qwen3-ASR-1.7B"):
    """
    将音频文件转写为文字
    
    Args:
        audio_path: 音频文件路径或 URL
        model: 模型名称
    
    Returns:
        str: 转写文字
    """
    import os
    import tempfile
    
    # 如果是 URL，先下载
    if audio_path.startswith('http://') or audio_path.startswith('https://'):
        print(f"Downloading from {audio_path}...")
        resp = requests.get(audio_path, proxies={'http': None, 'https': None})
        if resp.status_code != 200:
            raise Exception(f"Download failed: {resp.status_code}")
        
        temp_path = os.path.join(tempfile.gettempdir(), f"audio_{os.path.basename(audio_path)}")
        with open(temp_path, 'wb') as f:
            f.write(resp.content)
        audio_path = temp_path
    
    session = requests.Session()
    session.trust_env = False
    
    print(f"Transcribing {audio_path}...")
    
    with open(audio_path, 'rb') as f:
        files = {'file': (os.path.basename(audio_path), f, 'audio/mpeg')}
        data = {'model': model}
        
        response = session.post(
            f'{PI_LLM_URL}/audio/transcriptions',
            headers={"Authorization": f"Bearer {PI_LLM_API_KEY}"},
            files=files,
            data=data,
            timeout=600  # 10 分钟超时
        )
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    result = response.json()
    return result.get('text', '')
```

---

### Step 4: 文档解析 (OCR/MinerU)

```python
def parse_document(file_path, backend="pipeline", return_md=True, return_images=True, 
                   output_dir=None, fix_image_paths=True):
    """
    解析文档为 Markdown 和图片
    
    Args:
        file_path: 文件路径（支持 PDF、图片、Office 文档）
        backend: 解析后端 (pipeline/hybrid-auto-engine/vlm-auto-engine)
        return_md: 是否返回 Markdown
        return_images: 是否返回图片
        output_dir: 输出目录 (默认与源文件同目录)
        fix_image_paths: 是否自动修正 Markdown 中的图片路径
    
    Returns:
        dict: 解析结果，包含 markdown 和 images 路径
    
    输出结构:
        - 源文件：/path/to/document.pdf
        - Markdown: /path/to/document.md
        - 图片目录：/path/to/document_images/
    """
    import os
    import zipfile
    import tempfile
    import re
    import shutil
    
    session = requests.Session()
    session.trust_env = False
    
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    print(f"Parsing {file_name}...")
    
    # 准备表单数据
    files = {'files': (file_name, open(file_path, 'rb'), 'application/octet-stream')}
    data = {
        'backend': backend,
        'parse_method': 'auto',
        'lang_list': 'ch',
        'return_md': str(return_md).lower(),
        'return_images': str(return_images).lower(),
        'response_format_zip': 'true'
    }
    
    response = session.post(
        f'{PI_LLM_URL}/ocr/parser',
        headers={"Authorization": f"Bearer {PI_LLM_API_KEY}"},
        files=files,
        data=data,
        timeout=1800  # 30 分钟超时
    )
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    # 确定输出目录（默认与源文件同目录）
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    
    # 创建临时目录解压
    temp_dir = tempfile.mkdtemp(prefix='mineru_')
    zip_path = os.path.join(temp_dir, 'result.zip')
    
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    
    # 解压
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(temp_dir)
    
    # 找到 markdown 文件和解压后的 images 目录
    md_files = []
    temp_images_dir = None
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
        if 'images' in dirs:
            temp_images_dir = os.path.join(root, 'images')
    
    # 输出文件路径
    final_md_paths = []
    final_images_dir = os.path.join(output_dir, f"{base_name}_images")
    
    # 创建图片目录
    os.makedirs(final_images_dir, exist_ok=True)
    
    for temp_md in md_files:
        # 目标 Markdown 路径（与源文件同目录）
        dst_md = os.path.join(output_dir, f"{base_name}.md")
        
        # 复制 Markdown 文件
        shutil.copy2(temp_md, dst_md)
        final_md_paths.append(dst_md)
        
        # 修正图片路径
        if fix_image_paths and temp_images_dir:
            with open(dst_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 将 images/ 替换为 xxx_images/
            new_content = re.sub(
                r'!\[([^\]]*)\]\(images/',
                f'![\\1]({base_name}_images/',
                content
            )
            
            with open(dst_md, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✓ Fixed image paths in {dst_md}")
    
    # 复制图片到目标目录
    if temp_images_dir and os.path.exists(temp_images_dir):
        if os.path.exists(final_images_dir):
            shutil.rmtree(final_images_dir)
        shutil.copytree(temp_images_dir, final_images_dir)
        print(f"  ✓ Images copied to {final_images_dir}")
    
    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    print(f"✓ Parsing complete: {dst_md}")
    
    return {
        'markdown_files': final_md_paths,
        'images_dir': final_images_dir,
        'output_dir': output_dir
    }
```

---

### Step 5: 生成 Embedding

```python
def generate_embedding(text, model="unsloth/Qwen3-Embedding-0.6B", encoding_format="float"):
    """
    生成文本嵌入向量
    
    Args:
        text: 输入文本或文本列表
        model: 模型名称
        encoding_format: 编码格式 (float | base64)
    
    Returns:
        list: 嵌入向量（float 数组）
    """
    session = requests.Session()
    session.trust_env = False
    
    payload = {
        "model": model,
        "input": text if isinstance(text, list) else [text],
        "encoding_format": encoding_format
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
    
    # 返回第一个嵌入向量
    if result.get('data'):
        embedding = result['data'][0]['embedding']
        
        # 如果是 base64 格式，需要解码
        if encoding_format == "base64":
            import base64
            import struct
            decoded = base64.b64decode(embedding)
            float_count = len(decoded) // 4
            embedding = list(struct.unpack(f'{float_count}f', decoded))
        
        return embedding
    
    return None
```

---

### Step 6: 文档重排序 (Rerank)

```python
def rerank_documents(query, documents, model="Qwen/Qwen3-Reranker-0.6B"):
    """
    对文档进行相关性重排序
    
    Args:
        query: 查询语句
        documents: 文档列表
        model: 模型名称
    
    Returns:
        list: 排序后的结果，包含 index、document、relevance_score
    """
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
    
    result = response.json()
    return result.get('results', [])
```

---

## 📦 完整 Python 脚本

```python
#!/usr/bin/env python3
"""
PI-LLM-Server Skill - 统一 LLM 服务网关

功能:
- 语音识别 (ASR)
- 文档解析 (OCR/MinerU)
- Embedding 向量生成
- 文档重排序 (Rerank)

使用方法:
    python pi_llm_server_skill.py transcribe audio.mp3
    python pi_llm_server_skill.py parse document.pdf
    python pi_llm_server_skill.py embed "文本内容"
    python pi_llm_server_skill.py rerank --query "查询" --doc "文档 1" --doc "文档 2"
    python pi_llm_server_skill.py status
"""

import os
import sys
import json
import requests
import zipfile
import tempfile
import argparse

# API 配置
PI_LLM_URL = os.environ.get('PI_LLM_URL', 'http://api.adv-ci.com:8090/v1')
PI_LLM_API_KEY = os.environ.get('PI_LLM_API_KEY', 'sk-5f8b839908d14561590b70227c72ca86')

HEADERS = {
    "Authorization": f"Bearer {PI_LLM_API_KEY}",
    "Content-Type": "application/json"
}


def check_status():
    """检查服务状态"""
    base_url = PI_LLM_URL.replace('/v1', '')
    session = requests.Session()
    session.trust_env = False
    
    print("=== PI-LLM-Server 状态检查 ===\n")
    
    # 健康检查
    try:
        health = session.get(f'{base_url}/health', timeout=10)
        if health.status_code == 200:
            print(f"✓ 健康状态：{json.dumps(health.json(), indent=2)}")
    except Exception as e:
        print(f"✗ 健康检查失败：{e}")
    
    # 模型列表
    try:
        models = session.get(f'{PI_LLM_URL}/models', headers=HEADERS, timeout=10)
        if models.status_code == 200:
            print(f"\n✓ 可用模型:")
            for m in models.json().get('data', []):
                print(f"  - {m.get('id', 'N/A')}")
    except Exception as e:
        print(f"✗ 获取模型列表失败：{e}")


def transcribe_audio_cmd(audio_path, model="Qwen/Qwen3-ASR-1.7B"):
    """语音识别命令行"""
    if audio_path.startswith('http://') or audio_path.startswith('https://'):
        print(f"Downloading from {audio_path}...")
        session = requests.Session()
        session.trust_env = False
        resp = session.get(audio_path, proxies={'http': None, 'https': None})
        if resp.status_code != 200:
            print(f"Download failed: {resp.status_code}")
            return
        
        temp_path = os.path.join(tempfile.gettempdir(), f"audio_{os.path.basename(audio_path)}")
        with open(temp_path, 'wb') as f:
            f.write(resp.content)
        audio_path = temp_path
    
    session = requests.Session()
    session.trust_env = False
    
    print(f"Transcribing {audio_path}...")
    
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
        print(f"API error: {response.status_code} - {response.text}")
        return
    
    result = response.json()
    text = result.get('text', '')
    print(f"\n=== 转写结果 ===")
    print(text)
    print(f"\n长度：{len(text)} 字符")


def parse_document_cmd(file_path, backend="pipeline", output_dir=None):
    """
    文档解析命令行
    
    输出结构:
        - 源文件：/path/to/document.pdf
        - Markdown: /path/to/document.md
        - 图片目录：/path/to/document_images/
    """
    import os
    import shutil
    import re
    import zipfile
    import tempfile
    
    session = requests.Session()
    session.trust_env = False
    
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    print(f"Parsing {file_name}...")
    
    # 默认输出目录为源文件所在目录
    if output_dir is None:
        output_dir = os.path.dirname(file_path) or '.'
    
    files = {'files': (file_name, open(file_path, 'rb'), 'application/octet-stream')}
    data = {
        'backend': backend,
        'parse_method': 'auto',
        'lang_list': 'ch',
        'return_md': 'true',
        'return_images': 'true',
        'response_format_zip': 'true'
    }
    
    response = session.post(
        f'{PI_LLM_URL}/ocr/parser',
        headers={"Authorization": f"Bearer {PI_LLM_API_KEY}"},
        files=files,
        data=data,
        timeout=1800
    )
    
    if response.status_code != 200:
        print(f"API error: {response.status_code} - {response.text}")
        return
    
    # 临时目录解压
    temp_dir = tempfile.mkdtemp(prefix='mineru_')
    zip_path = os.path.join(temp_dir, 'result.zip')
    
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(temp_dir)
    
    # 找到 markdown 文件和解压后的 images 目录
    md_files = []
    temp_images_dir = None
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
        if 'images' in dirs:
            temp_images_dir = os.path.join(root, 'images')
    
    # 最终输出路径
    final_images_dir = os.path.join(output_dir, f"{base_name}_images")
    os.makedirs(final_images_dir, exist_ok=True)
    
    for temp_md in md_files:
        # 目标 Markdown 路径（与源文件同目录）
        dst_md = os.path.join(output_dir, f"{base_name}.md")
        
        # 复制 Markdown 文件
        shutil.copy2(temp_md, dst_md)
        
        # 修正图片路径：images/ -> xxx_images/
        with open(dst_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = re.sub(
            r'!\[([^\]]*)\]\(images/',
            f'![\\1]({base_name}_images/',
            content
        )
        
        with open(dst_md, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✓ Markdown: {dst_md}")
    
    # 复制图片到目标目录
    if temp_images_dir and os.path.exists(temp_images_dir):
        if os.path.exists(final_images_dir):
            shutil.rmtree(final_images_dir)
        shutil.copytree(temp_images_dir, final_images_dir)
        print(f"  ✓ Images: {final_images_dir}")
    
    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    print(f"\n=== 解析完成 ===")
    print(f"Markdown: {dst_md}")
    print(f"Images: {final_images_dir}/")


def embed_text_cmd(text, model="unsloth/Qwen3-Embedding-0.6B"):
    """Embedding 命令行"""
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
        print(f"API error: {response.status_code} - {response.text}")
        return
    
    result = response.json()
    if result.get('data'):
        embedding = result['data'][0]['embedding']
        print(f"\n=== Embedding ===")
        print(f"维度：{len(embedding)}")
        print(f"前 10 个值：{embedding[:10]}")


def rerank_cmd(query, documents, model="Qwen/Qwen3-Reranker-0.6B"):
    """Rerank 命令行"""
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
        print(f"API error: {response.status_code} - {response.text}")
        return
    
    result = response.json()
    print(f"\n=== Rerank 结果 ===")
    print(f"查询：{query}")
    print()
    for item in result.get('results', []):
        print(f"[{item['index']}] 得分：{item['relevance_score']:.4f}")
        print(f"     文档：{item['document'][:100]}...")
        print()


def main():
    parser = argparse.ArgumentParser(description='PI-LLM-Server Skill')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # status 命令
    subparsers.add_parser('status', help='检查服务状态')
    
    # transcribe 命令
    transcribe_parser = subparsers.add_parser('transcribe', help='语音识别')
    transcribe_parser.add_argument('audio_file', help='音频文件路径')
    transcribe_parser.add_argument('--model', default='Qwen/Qwen3-ASR-1.7B', help='模型名称')
    
    # parse 命令
    parse_parser = subparsers.add_parser('parse', help='文档解析')
    parse_parser.add_argument('file', help='文件路径')
    parse_parser.add_argument('--backend', default='pipeline', help='解析后端')
    parse_parser.add_argument('--output', '-o', default=None, help='输出目录（默认与源文件同目录）')
    
    # embed 命令
    embed_parser = subparsers.add_parser('embed', help='生成 Embedding')
    embed_parser.add_argument('text', help='输入文本')
    embed_parser.add_argument('--model', default='unsloth/Qwen3-Embedding-0.6B', help='模型名称')
    
    # rerank 命令
    rerank_parser = subparsers.add_parser('rerank', help='文档重排序')
    rerank_parser.add_argument('--query', required=True, help='查询语句')
    rerank_parser.add_argument('--doc', action='append', dest='documents', required=True, help='文档列表')
    rerank_parser.add_argument('--model', default='Qwen/Qwen3-Reranker-0.6B', help='模型名称')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        check_status()
    elif args.command == 'transcribe':
        transcribe_audio_cmd(args.audio_file, args.model)
    elif args.command == 'parse':
        parse_document_cmd(args.file, args.backend, args.output)
    elif args.command == 'embed':
        embed_text_cmd(args.text, args.model)
    elif args.command == 'rerank':
        rerank_cmd(args.query, args.documents, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

---

## 🔧 激活关键词

以下关键词会触发此 skill：

**语音识别**:
- "转写音频"
- "语音转文字"
- "transcribe audio"
- "会议录音转写"
- "音频转 markdown"

**文档解析**:
- "解析 PDF"
- "PDF 转 Markdown"
- "文档识别"
- "OCR 识别"
- "parse document"
- "docx 转 markdown"
- "提取图片"

**Embedding**:
- "生成 embedding"
- "向量化"
- "文本嵌入"
- "生成向量"

**Rerank**:
- "重排序"
- "rerank"
- "文档排序"
- "相关性排序"

**状态查询**:
- "服务状态"
- "检查服务"
- "可用模型"

---

## 📝 使用示例

### 示例 1: 语音识别

```
用户：帮我转写这个会议录音
文件：meeting_20260409.mp3

AI: 正在转写音频...
    ✓ 转写完成，共 3456 字符
    结果：[转写内容]
```

### 示例 2: PDF 解析（新行为）

```
用户：把这个产品规格书解析成 Markdown
文件：/path/to/product_spec.pdf

AI: 正在解析 PDF...
    ✓ Markdown: /path/to/product_spec.md
    ✓ Images: /path/to/product_spec_images/ (共 15 张图片)

输出结构:
    /path/to/product_spec.pdf       # 源文件
    /path/to/product_spec.md        # Markdown 文件（与源文件同目录）
    /path/to/product_spec_images/   # 图片目录（源文件_ images）
```

### 示例 3: Office 文档解析

```
用户：解析这个 Word 文档
文件：/path/to/report.docx

AI: 正在转换 docx 为 PDF...
    ✓ Markdown: /path/to/report.md
    ✓ Images: /path/to/report_images/

注意：图片路径已自动修正为 report_images/
```

### 示例 4: Embedding

```
用户：生成"今天天气真好"的 embedding 向量

AI: ✓ 生成完成
    维度：1024
    前 10 个值：[0.012, -0.045, 0.089, ...]
```

### 示例 5: Rerank

```
用户：对以下文档关于"深度学习"进行排序：
     1. "人工智能是计算机科学的一个分支"
     2. "机器学习是实现 AI 的方法"
     3. "深度学习是机器学习的子集"

AI: ✓ 排序完成
    [2] 得分：0.8234 - 深度学习是机器学习的子集
    [1] 得分：0.1523 - 机器学习是实现 AI 的方法
    [0] 得分：0.0821 - 人工智能是计算机科学的一个分支
```

---

## ⚠️ 注意事项

### 0. 输出结构（已改进）

**文档解析输出结构**:

```
源文件：    /path/to/document.pdf
Markdown:   /path/to/document.md           # 与源文件同目录
图片目录：  /path/to/document_images/      # 源文件同名 + _images
```

**图片路径自动修正**:
- Markdown 中的 `images/` 路径会自动修正为 `document_images/`
- 示例：`![](images/001.jpg)` → `![](document_images/001.jpg)`

**自定义输出目录**:
```bash
# 默认：输出到源文件所在目录
/skill pi-llm-server parse /path/to/doc.pdf

# 自定义：输出到指定目录
/skill pi-llm-server parse /path/to/doc.pdf --output /custom/output/dir
```

### 1. 代理配置

必须禁用系统代理：
```python
session = requests.Session()
session.trust_env = False
```

### 2. 超时设置

| 操作 | 超时时间 |
|------|----------|
| 语音识别 | 600 秒 (10 分钟) |
| 文档解析 | 1800 秒 (30 分钟) |
| Embedding | 60 秒 |
| Rerank | 120 秒 |

### 3. 文件大小限制

- 音频文件：建议不超过 100MB
- 文档文件：建议不超过 50MB

### 4. Office 文档转换

需要服务器安装 libreoffice：
```bash
sudo apt-get install libreoffice
```

---

## 🔗 相关资源

### API 文档
- **Swagger UI**: `http://api.adv-ci.com:8090/docs`
- **OpenAPI**: `http://api.adv-ci.com:8090/openapi.json`

### 相关项目
- **PI-LLM-Server**: 统一 LLM 服务网关
- **MinerU**: PDF/文档解析引擎
- **Qwen3-ASR**: 语音识别模型
- **Qwen3-Embedding**: 嵌入模型
- **Qwen3-Reranker**: 重排序模型

---

**创建者**: AI Assistant
**最后更新**: 2026-04-09
**版本**: 1.0.0
