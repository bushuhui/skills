#!/usr/bin/env python3
"""
Audio Transcription Tool - 音频转写工具
使用 Qwen/Qwen3-ASR-1.7B 模型进行语音识别

Usage:
    python audio_transcription.py <audio_file_or_url> [output_file]

Example:
    python audio_transcription.py /path/to/audio.mp3
    python audio_transcription.py https://example.com/audio.mp3 /path/to/output.txt
"""

import os
import sys
import time
import requests

# API 配置
API_BASE = "http://api.adv-ci.com:8090"
API_TOKEN = "sk-5f8b839908d14561590b70227c72ca86"
DEFAULT_MODEL = "Qwen/Qwen3-ASR-1.7B"  # Qwen3 语音识别模型


def get_audio_file(source):
    """获取音频文件，返回本地路径"""
    if os.path.exists(source):
        return source
    
    if source.startswith('http://') or source.startswith('https://'):
        print(f"Downloading from {source}...")
        resp = requests.get(source, proxies={'http': None, 'https': None})
        if resp.status_code == 200:
            temp_path = f"/tmp/audio_{os.path.basename(source)}"
            with open(temp_path, 'wb') as f:
                f.write(resp.content)
            print(f"Downloaded to {temp_path}")
            return temp_path
        else:
            raise Exception(f"Download failed: {resp.status_code}")
    
    raise Exception(f"Invalid source: {source}")


def transcribe_audio(audio_path, model=DEFAULT_MODEL):
    """调用 Whisper API 转写音频"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    session = requests.Session()
    session.trust_env = False  # 禁用代理
    
    print(f"Transcribing {audio_path} with model {model}...")
    
    with open(audio_path, 'rb') as f:
        files = {'file': (os.path.basename(audio_path), f, 'audio/mpeg')}
        data = {'model': model}
        
        response = session.post(
            f'{API_BASE}/v1/audio/transcriptions',
            headers=headers,
            files=files,
            data=data,
            timeout=600
        )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    result = response.json()
    
    if 'text' not in result:
        raise Exception(f"No text in response: {result}")
    
    return result['text']


def save_transcription(text, output_path=None):
    """保存转写结果"""
    if output_path is None:
        output_path = f"/tmp/transcription_{int(time.time())}.txt"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"Transcription saved to {output_path}")
    print(f"Length: {len(text)} chars")
    
    return output_path


def cleanup_temp_files(*paths):
    """清理临时文件"""
    for path in paths:
        if path and path.startswith('/tmp/') and os.path.exists(path):
            try:
                os.remove(path)
                print(f"Cleaned up: {path}")
            except Exception as e:
                print(f"Failed to clean up {path}: {e}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python audio_transcription.py <audio_file_or_url> [output_file]")
        print("Example:")
        print("  python audio_transcription.py /path/to/audio.mp3")
        print("  python audio_transcription.py https://example.com/audio.mp3 /path/to/output.txt")
        sys.exit(1)
    
    audio_source = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Step 1: 获取音频文件
        audio_path = get_audio_file(audio_source)
        
        # Step 2: 转写
        text = transcribe_audio(audio_path)
        
        # Step 3: 保存结果
        output_path = save_transcription(text, output_path)
        
        # Step 4: 清理临时文件（如果是下载的）
        if audio_source.startswith('http') and audio_path.startswith('/tmp/'):
            cleanup_temp_files(audio_path)
        
        print("\n=== Transcription Complete ===")
        print(f"Output: {output_path}")
        print(f"Length: {len(text)} chars")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
