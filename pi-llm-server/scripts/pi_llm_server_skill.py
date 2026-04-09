#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


def parse_document_cmd(file_path, backend="pipeline"):
    """文档解析命令行"""
    session = requests.Session()
    session.trust_env = False

    print(f"Parsing {file_path}...")

    files = {'files': (os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream')}
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

    output_dir = tempfile.mkdtemp(prefix='mineru_')
    zip_path = os.path.join(output_dir, 'result.zip')

    with open(zip_path, 'wb') as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(output_dir)

    print(f"\n=== 解析完成 ===")
    print(f"输出目录：{output_dir}")

    for root, dirs, files in os.walk(output_dir):
        for f in files:
            if f.endswith('.md'):
                print(f"Markdown: {os.path.join(root, f)}")
            elif f.endswith(('.jpg', '.png')):
                print(f"Image: {os.path.join(root, f)}")


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
        parse_document_cmd(args.file, args.backend)
    elif args.command == 'embed':
        embed_text_cmd(args.text, args.model)
    elif args.command == 'rerank':
        rerank_cmd(args.query, args.documents, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
