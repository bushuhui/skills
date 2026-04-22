---
name: doc2x
description: |
  使用 Doc2X API 将 PDF 或图片解析为 Markdown（含本地图片）。触发条件：
  - 用户要求解析/转换 PDF 为 Markdown
  - 用户要求 OCR 识别图片中的文字/公式/表格
  - 用户提到 doc2x、PDF 转 Markdown、文档解析
  支持：PDF（异步，含轮询）、图片 jpg/png（同步）
---

# Doc2X Parse Skill

将 PDF 或图片通过 Doc2X API v2 解析为 Markdown + 本地图片。

## 环境变量

访问的key从环境变量 `DOC2X_KEY` 获取。

## 存储规则

输出目录：`/home/bushuhui/data-all/note/resources/YYYYMM/{文件名}/`

```
{文件名}/
├── {原始文件}          # 复制原始 PDF/图片
├── {文件名}.md         # 解析后的 Markdown
├── images/             # 文档中提取的图片
├── parse_result.json   # API 原始返回（调试用）
```

## 工作流程

### 1. 准备

```bash
# 确定输出目录
YYYYMM=$(date +%Y%m)
BASENAME="文件名（不含扩展名）"
OUTPUT_DIR="/home/bushuhui/data-all/note/resources/${YYYYMM}/${BASENAME}"
mkdir -p "$OUTPUT_DIR"

# 复制原始文件到输出目录
cp <input_file> "$OUTPUT_DIR/"
```

### 2. 运行解析脚本

PDF 解析耗时较长（几十秒到几分钟），建议用 `exec` 后台运行：

```bash
DOC2X_KEY=sk-a3ne3fg04blohlp1v1fh3six64zzh5oy \
  bash scripts/doc2x_parse.sh <input_file> "$OUTPUT_DIR"
```

脚本会自动：
- PDF：预上传 → 上传 → 轮询解析 → 导出 Markdown → 轮询导出 → 下载 zip → 解压
- 图片：同步上传 → 获取 Markdown + 提取图片

### 3. 后处理（Agent 完成）

脚本完成后，Agent 应：

1. 读取生成的 `.md` 文件
2. 检查图片引用路径是否正确（应指向 `images/` 子目录）
3. 如果用户要求保存到知识库，复制到 Obsidian Clippings 目录
4. 运行 WebDAV 同步：`/home/bushuhui/scripts/backup_bushuhui_webdav.sh`

### 4. 如果用户要求保存到知识库

```bash
# 复制 Markdown 和图片到 Clippings
CLIPPINGS="/home/bushuhui/data-all/note/bushuhui/Clippings/${YYYYMM}"
mkdir -p "${CLIPPINGS}/${BASENAME}"
cp "$OUTPUT_DIR/${BASENAME}.md" "${CLIPPINGS}/${BASENAME}/"
cp -r "$OUTPUT_DIR/images" "${CLIPPINGS}/${BASENAME}/" 2>/dev/null || true

# 同步
/home/bushuhui/scripts/backup_bushuhui_webdav.sh
```

## 注意事项

- PDF 解析是异步的，大文件可能需要几分钟，用 `exec` 的 `yieldMs` 或 `background` 模式
- 图片接口是同步的，通常几秒完成
- 单个 PDF 限制：≤300MB，≤2000 页
- 单张图片限制：≤7MB，仅 jpg/png
- 如果图片很多或长宽比一致，建议先合成 PDF 再解析（吞吐更高）
- 服务器结果只保留 24h，脚本会立即下载
- API 并发限制：图片 30 张/30s
