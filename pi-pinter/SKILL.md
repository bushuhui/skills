---
name: pi-pinter
description: 文字生成图片 skill，调用 aicodewith.com 的 text-to-image API 生成图片。Use when 用户要求生成图片、文生图、根据描述画图、image generation、text to image。支持文生图和图生图两种模式。
---

# pi-pinter — 文字生成图片

通过 aicodewith.com API 将文字描述转换为图片，支持文生图和图生图。

## 前置条件

- 需要环境变量 `AICODEWITH_API_KEY` 已设置
- 需要 `curl` 和 `jq` 命令可用

## 快速使用

```bash
bash "${SKILL_DIR}/scripts/generate.sh" \
  --prompt "一只可爱的猫咪在阳光下打盹" \
  --output "./output.png"
```

## 工作流

### 1. 文生图（默认）

用户给出一段文字描述，生成对应图片：

```bash
bash "${SKILL_DIR}/scripts/generate.sh" \
  --prompt "一只可爱的猫咪在阳光下打盹" \
  --model gpt-image-2 \
  --size "1:1" \
  --resolution "2K" \
  --quality "medium" \
  --output "./cat.png"
```

### 2. 图生图（公网 URL）

用户提供原图 URL 作为参考生成新图：

```bash
bash "${SKILL_DIR}/scripts/generate.sh" \
  --prompt "改成蓝色的" \
  --model gpt-image-2 \
  --size "1:1" \
  --resolution "4K" \
  --quality "high" \
  --image-url "https://example.com/original.png" \
  --output "./blue_version.png"
```

### 3. 图生图（本地图片）

直接传入本地图片路径，脚本会自动上传到 WebDAV 并获取公网 URL：

```bash
bash "${SKILL_DIR}/scripts/generate.sh" \
  --prompt "把背景换成雪景" \
  --image-url "./my_photo.jpg" \
  --output "./snow_version.png"
```

> 本地图片会通过 `PUT` 请求上传到 `https://pub.adv-ci.com/pi-pinter/`，自动生成带时间戳的唯一文件名。

## 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--prompt` | string | 是 | - | 图片描述，不能为空 |
| `--model` | string | 否 | gpt-image-2-beta | 模型名称，支持 gpt-image-2、gpt-image-2-beta |
| `--size` | string | 否 | 1:1 | 图片尺寸，推荐 auto、1:1、16:9、9:16 |
| `--resolution` | enum | 否 | 1K | 分辨率档位：1K、2K、4K；仅 gpt-image-2 可用 |
| `--n` | integer | 否 | 1 | 生成数量，范围 1-10；仅 gpt-image-2 支持多张 |
| `--quality` | string | 否 | medium | 图片质量：high、medium、low；仅 gpt-image-2 支持 |
| `--image-url` | string | 否 | - | 原图 URL 或本地文件路径，可传多个。本地文件会自动上传到 WebDAV |
| `--output` | string | 否 | ./generated.png | 输出文件路径 |
| `--download` | flag | 否 | - | 是否下载图片到本地（默认下载） |

## API 接口

- **创建任务**: `POST https://api.aicodewith.com/v1/images/generations`
- **查询状态**: `GET https://api.aicodewith.com/v1/tasks/{task_id}`

## 注意事项

- size 建议优先使用 auto、1:1、16:9 等比例格式
- resolution 仅在 size 为比例格式时生效，默认 1K
- n 范围 1-10，默认 1；每张独立计费
- 仅 gpt-image-2 支持 n > 1；gpt-image-2-beta 只支持单张
- 建议轮询间隔 3-5 秒，任务一般 30-120 秒完成
- 图片 URL 有效期短，建议生成后立即下载
- gpt-image-2-beta 不要传 quality 参数

## 错误码

| 状态码 | 说明 |
|--------|------|
| 400 | 参数错误，如不支持的 size 格式 |
| 401 | API Key 无效 |
| 402 | 余额不足 |
| 404 | 任务不存在或无权访问 |
| 503 | 无可用渠道 |
