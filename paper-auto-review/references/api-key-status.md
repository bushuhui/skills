# API Key 状态与故障排查

## 环境变量映射

| paper-auto-review 变量 | 来源 | 默认值 |
|----------------------|------|--------|
| `PI_LLM_URL` | 固定值 | `http://api.adv-ci.com:8090/v1` |
| `PI_LLM_API_KEY` | `.hermes/.env` 的 `DASHSCOPE_API_KEY` | — |
| `BAILIAN_URL` | 固定值 | `https://coding.dashscope.aliyuncs.com/v1` |
| `BAILIAN_API_KEY` | `.hermes/.env` 的 `BAILIAN_API_KEY` | — |
| `BAILIAN_MODEL` | 固定值 | `qwen-plus` |

## 已知问题（2026-05-05）

### BAILIAN_API_KEY 过期
- 症状：`HTTP 401 - {"code":"invalid_api_key","message":"invalid access token or token expired"}`
- URL 验证：`https://coding.dashscope.aliyuncs.com/v1/chat/completions` 返回 401
- `dashscope.aliyuncs.com/compatible-mode/v1` 也返回 `Incorrect API key provided`

### PI_LLM_API_KEY 过期
- 症状：`HTTP 401 - {"error":"Unauthorized","message":"Invalid authentication token"}`
- pi-llm-server 端口 8090 可访问，但 OCR 服务返回 401

### 当前状态
- pi-llm-server **OCR 服务**可用（HTTP 200），需使用正确的 `sk-5f8b839908d14561590b70227c72ca86`
- Bailian LLM 服务不可用（key 过期）
- OpenAI API 连接超时（SSL EOF 错误）
- Anthropic API key 无效（`invalid x-api-key`）

## 替代审稿方案

当 LLM 审稿服务不可用时：
1. 确保 pi-llm-server OCR 可用（PDF → Markdown）
2. 读取生成的 `.md` 文件
3. 使用自身模型能力按审稿 prompt 撰写意见
4. 保存到 `review_draft.md`

审稿 prompt 文件：
- 中文论文：`review_prompt_cn.md`（36 行，中文审稿模板）
- 英文论文：`review_prompt.md`（英文审稿模板）

审稿意见应包含：
- 贡献摘要（建设性总结，积极语气）
- 审稿意见列表（按重要性排序，具体问题 + 位置 + 建议）
- 总体评价（接受/修改后重审/拒绝）
