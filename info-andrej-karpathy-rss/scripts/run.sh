#!/bin/bash
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
cd "$(dirname "$0")"
python3 fetch_rss.py 2>&1
