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
    """
    语音识别命令行
    输出到源文件所在目录:
        /path/to/audio.txt
    """
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

    src_dir = os.path.dirname(os.path.abspath(audio_path))
    file_name = os.path.basename(audio_path)
    base_name = os.path.splitext(file_name)[0]
    print(f"Transcribing {file_name}...")

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

    # 保存为同名 .txt 文件
    dst_txt = os.path.join(src_dir, f"{base_name}.txt")
    with open(dst_txt, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"  Text: {dst_txt}")
    print(f"  长度：{len(text)} 字符")


def parse_document_cmd(file_path, backend="pipeline"):
    """
    文档解析命令行
    输出到源文件所在目录:
        /path/to/document.md
        /path/to/document_images/
    """
    import shutil
    import re

    session = requests.Session()
    session.trust_env = False

    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    src_dir = os.path.dirname(os.path.abspath(file_path))
    print(f"Parsing {file_name}...")

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

    # 找到 markdown 和 images 目录
    md_files = []
    temp_images_dir = None
    for root, dirs, files_list in os.walk(temp_dir):
        for f in files_list:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
        if 'images' in dirs:
            temp_images_dir = os.path.join(root, 'images')

    # 目标目录
    final_images_dir = os.path.join(src_dir, f"{base_name}_images")
    os.makedirs(final_images_dir, exist_ok=True)

    # 复制 markdown 并修正图片路径
    for temp_md in md_files:
        dst_md = os.path.join(src_dir, f"{base_name}.md")
        shutil.copy2(temp_md, dst_md)

        if temp_images_dir:
            with open(dst_md, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = re.sub(
                r'!\[([^\]]*)\]\(images/',
                f'![\\1]({base_name}_images/',
                content
            )
            with open(dst_md, 'w', encoding='utf-8') as f:
                f.write(new_content)

    # 复制图片
    if temp_images_dir and os.path.exists(temp_images_dir):
        if os.path.exists(final_images_dir):
            shutil.rmtree(final_images_dir)
        shutil.copytree(temp_images_dir, final_images_dir)

    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)

    # 统计图片数量
    img_count = len([f for f in os.listdir(final_images_dir) if os.path.isfile(os.path.join(final_images_dir, f))])

    print(f"  Markdown: {os.path.join(src_dir, f'{base_name}.md')}")
    print(f"  Images:   {final_images_dir}/ ({img_count} 张)")


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
