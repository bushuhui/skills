#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Long audio splitter + ASR transcriber for PI-LLM-Server.
Splits audio into 5-minute segments and transcribes each via API.

Usage:
    python split_transcribe.py audio.mp3 [segment_seconds]
    python split_transcribe.py audio.mp3 300  # 5 min segments (default)
"""
import os, sys, requests, glob, subprocess

API_URL = 'http://api.adv-ci.com:8090/v1/audio/transcriptions'
API_KEY = os.environ.get('PI_LLM_API_KEY', 'sk-5f8b839908d14561590b70227c72ca86')

def split_and_transcribe(audio_path, seg_seconds=300):
    audio_path = os.path.abspath(audio_path)
    out_dir = os.path.join(os.path.dirname(audio_path), 'audio_segments')
    os.makedirs(out_dir, exist_ok=True)

    # Split
    print(f"Splitting {audio_path} into {seg_seconds}s segments...")
    cmd = f'ffmpeg -y -i "{audio_path}" -f segment -segment_time {seg_seconds} -c copy "{out_dir}/part_%03d.mp3"'
    if os.system(cmd) != 0:
        print("FFmpeg failed."); sys.exit(1)

    parts = sorted(glob.glob(os.path.join(out_dir, 'part_*.mp3')))
    print(f"Found {len(parts)} segments. Transcribing...")

    session = requests.Session()
    session.trust_env = False
    full_text = []

    for i, part in enumerate(parts, 1):
        fname = os.path.basename(part)
        print(f"  [{i}/{len(parts)}] {fname}...", end=" ")
        try:
            with open(part, 'rb') as f:
                r = session.post(API_URL,
                    headers={'Authorization': f'Bearer {API_KEY}'},
                    files={'file': (fname, f, 'audio/mpeg')},
                    data={'model': 'Qwen/Qwen3-ASR-1.7B'},
                    timeout=1800)
            if r.status_code == 200:
                txt = r.json().get('text', '')
                full_text.append(txt)
                print(f"OK ({len(txt)} chars)")
            else:
                print(f"FAIL ({r.status_code}): {r.text[:80]}")
        except Exception as e:
            print(f"ERROR: {e}")

    out_file = os.path.splitext(audio_path)[0] + '_transcript.txt'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('\n\n---\n\n'.join(full_text))
    print(f"\nDone! -> {out_file} ({sum(len(t) for t in full_text)} total chars)")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} audio.mp3 [segment_seconds]")
        sys.exit(1)
    seg = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    split_and_transcribe(sys.argv[1], seg)
