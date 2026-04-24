#!/usr/bin/env python3
"""
OpenClaw Skill: YouTube Video Transcribe
自动提取 YouTube 视频字幕并保存到知识库
"""

import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("❌ 错误：缺少依赖 youtube-transcript-api")
    print("请运行：pip install youtube-transcript-api")
    sys.exit(1)


def extract_video_id(url: str) -> str:
    """从 YouTube URL 提取视频 ID"""
    if len(url) == 11:  # 直接是 ID
        return url

    import re
    match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/live/)([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)

    return url


def fetch_transcript(video_id: str, languages: list = None) -> dict:
    """获取视频字幕"""
    if languages is None:
        languages = ['zh-Hans', 'zh-CN', 'zh-Hant', 'en']
    
    ytt_api = YouTubeTranscriptApi()
    
    try:
        # 获取字幕
        transcript = ytt_api.fetch(video_id, languages=languages)
        
        return {
            'success': True,
            'video_id': video_id,
            'language': transcript.language,
            'language_code': transcript.language_code,
            'is_generated': transcript.is_generated,
            'snippets': [
                {
                    'text': snippet.text,
                    'start': snippet.start,
                    'duration': snippet.duration
                }
                for snippet in transcript
            ]
        }
    except Exception as e:
        return {
            'success': False,
            'video_id': video_id,
            'error': str(e)
        }


def format_markdown(transcript_data: dict, include_timestamps: bool = True) -> str:
    """格式化为 Markdown"""
    md = f"# YouTube 视频转写\n\n"
    md += f"**视频 ID**: {transcript_data['video_id']}\n"
    md += f"**语言**: {transcript_data['language']}\n"
    md += f"**自动生成**: {'是' if transcript_data['is_generated'] else '否'}\n"
    md += f"**片段数量**: {len(transcript_data['snippets'])}\n"
    md += f"**转写时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += "---\n\n"
    
    for snippet in transcript_data['snippets']:
        if include_timestamps:
            md += f"[{snippet['start']:.1f}s] {snippet['text']}\n"
        else:
            md += f"{snippet['text']}\n"
    
    return md


def save_to_file(content: str, output_path: str):
    """保存到文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    """主函数 - 支持命令行和 OpenClaw Skill 调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube 视频转写')
    parser.add_argument('--url', required=True, help='YouTube 视频 URL 或 ID')
    parser.add_argument('--languages', default='zh-Hans,zh-CN,en', help='语言优先级（逗号分隔）')
    parser.add_argument('--output', default=None, help='输出文件路径')
    parser.add_argument('--output-dir', default='Clippings/YouTube-Transcripts/', help='输出目录')
    parser.add_argument('--no-timestamps', action='store_true', help='不包含时间戳')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    # 提取视频 ID
    video_id = extract_video_id(args.url)
    
    # 解析语言列表
    languages = [lang.strip() for lang in args.languages.split(',')]
    
    print(f"🚀 正在获取字幕：{video_id}")
    
    # 获取字幕
    transcript = fetch_transcript(video_id, languages)
    
    if not transcript['success']:
        print(f"❌ 错误：{transcript['error']}")
        if args.json:
            print(json.dumps(transcript, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    if args.json:
        # 输出 JSON
        print(json.dumps(transcript, ensure_ascii=False, indent=2))
    else:
        # 确定输出路径
        if args.output:
            output_path = args.output
        else:
            # 自动生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(args.output_dir, f"{video_id}_{timestamp}.md")
        
        # 格式化为 Markdown
        md_content = format_markdown(transcript, include_timestamps=not args.no_timestamps)
        
        # 保存文件
        save_to_file(md_content, output_path)
        
        # 输出结果
        print(f"✅ 已保存到：{output_path}")
        print(f"📊 语言：{transcript['language']}")
        print(f"📊 片段数量：{len(transcript['snippets'])}")
        print(f"📊 文件大小：{len(md_content)} 字符")
        
        # 输出 JSON 结果（供 OpenClaw 使用）
        result = {
            'success': True,
            'video_id': video_id,
            'language': transcript['language'],
            'snippet_count': len(transcript['snippets']),
            'output_path': output_path,
            'file_size': len(md_content)
        }
        print(f"\n📋 结果：{json.dumps(result, ensure_ascii=False)}")


if __name__ == '__main__':
    main()
