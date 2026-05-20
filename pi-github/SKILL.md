---
name: pi-github
description: |
  GitHub MCP 全功能封装 — 通过远程 GitHub MCP Server 访问 GitHub API。
  触发条件：
  - 用户需要操作 GitHub（仓库、Issue、PR、Actions、Code Scanning 等）
  - 需要查询/搜索 GitHub 仓库、代码、用户、组织
  - 需要创建或管理 Issue、Pull Request、Workflow、Gist
  - 用户提到 "github"、"gh"、"GitHub 操作"
  - 需要获取当前 GitHub 用户信息、仓库内容、代码分析
  - 需要处理 GitHub 通知、项目管理、安全告警
---

## 环境配置

```bash
# 必需：GitHub Personal Access Token (PAT)
export GITHUB_TOKEN="your_pat_token_here"

# 可选：自定义 MCP 端点 URL（默认使用官方远程服务器）
export GITHUB_MCP_URL="https://api.githubcopilot.com/mcp/"

# 可选：代理设置（默认使用 192.169.1.2:7890）
export HTTPS_PROXY="http://192.169.1.2:7890"
```

**Token 权限建议**：创建 PAT 时至少启用以下 scopes：
- `repo` — 仓库读写操作
- `read:packages` — Docker 镜像访问（如果用本地服务）
- `read:org` — 组织/团队信息
- `security_events` — Code Scanning 等安全工具
- `workflow` — GitHub Actions 操作

## 工具用法

所有操作通过 `scripts/github_mcp.py` 脚本调用，使用 MCP JSON-RPC 协议与远程 GitHub MCP Server 通信。

### 基本语法

```bash
python3 <skill_dir>/scripts/github_mcp.py <tool_name> --json '<params_json>'
```

### 查询可用工具/资源

```bash
# 列出所有可用工具
python3 github_mcp.py --list-tools

# 列出所有可用资源
python3 github_mcp.py --list-resources

# 列出所有可用提示词
python3 github_mcp.py --list-prompts
```

### Context（上下文 — 强烈建议优先使用）

```bash
# 获取当前用户信息
python3 github_mcp.py get_me

# 获取组织团队成员
python3 github_mcp.py get_team_members --json '{"org":"my-org","team_slug":"engineering"}'

# 获取用户所属的所有团队
python3 github_mcp.py get_teams --json '{"user":"username"}'
```

### Repos（仓库操作）

```bash
# 获取仓库文件/目录内容
python3 github_mcp.py get_file_contents --json '{"owner":"octocat","repo":"hello-world","path":"README.md"}'

# 搜索仓库
python3 github_mcp.py search_repositories --json '{"query":"machine learning language:python","sort":"stars"}'

# 列出分支
python3 github_mcp.py list_branches --json '{"owner":"octocat","repo":"hello-world"}'

# 列出标签
python3 github_mcp.py list_tags --json '{"owner":"octocat","repo":"hello-world"}'

# 搜索代码
python3 github_mcp.py search_code --json '{"q":"function main language:go"}'

# 获取仓库 collaborators
python3 github_mcp.py list_repository_collaborators --json '{"owner":"octocat","repo":"hello-world"}'

# 创建仓库
python3 github_mcp.py create_repository --json '{"name":"my-new-repo","description":"My project"}'

# Fork 仓库
python3 github_mcp.py fork_repository --json '{"owner":"octocat","repo":"hello-world"}'

# 列出 Commits
python3 github_mcp.py list_commits --json '{"owner":"octocat","repo":"hello-world"}'

# 获取 Commit 详情
python3 github_mcp.py get_commit --json '{"owner":"octocat","repo":"hello-world","sha":"abc123"}'

# 获取 Tag 详情
python3 github_mcp.py get_tag --json '{"owner":"octocat","repo":"hello-world","tag":"v1.0"}'

# 创建分支
python3 github_mcp.py create_branch --json '{"owner":"octocat","repo":"hello-world","branch":"feature-x","sha":"abc123"}'

# 创建/更新文件
python3 github_mcp.py create_or_update_file --json '{"owner":"octocat","repo":"hello-world","path":"hello.txt","content":"hello world","message":"Add hello.txt"}'

# 删除文件
python3 github_mcp.py delete_file --json '{"owner":"octocat","repo":"hello-world","path":"old.txt","message":"Remove old file","sha":"abc123"}'

# 批量推送文件
python3 github_mcp.py push_files --json '{"owner":"octocat","repo":"hello-world","branch":"feature-x","files":[{"path":"a.txt","content":"hello"}],"message":"Add files"}'

# 列出 Releases
python3 github_mcp.py list_releases --json '{"owner":"octocat","repo":"hello-world"}'

# 获取最新 Release
python3 github_mcp.py get_latest_release --json '{"owner":"octocat","repo":"hello-world"}'
```

### Issues（Issue 操作）

```bash
# 读取单个 Issue
python3 github_mcp.py issue_read --json '{"owner":"octocat","repo":"hello-world","issue_number":1}'

# 列出 Issues
python3 github_mcp.py list_issues --json '{"owner":"octocat","repo":"hello-world"}'

# 创建/更新 Issue
python3 github_mcp.py issue_write --json '{"owner":"octocat","repo":"hello-world","title":"Bug report","body":"Description...","method":"create"}'

# 搜索 Issues
python3 github_mcp.py search_issues --json '{"q":"is:open label:bug repo:owner/repo"}'

# 添加 Issue 评论
python3 github_mcp.py add_issue_comment --json '{"owner":"octocat","repo":"hello-world","issue_number":1,"body":"Great fix!"}'

# 添加子 Issue
python3 github_mcp.py sub_issue_write --json '{"owner":"octocat","repo":"hello-world","issue_number":1,"sub_issue_number":2}'

# 列出 Issue 类型
python3 github_mcp.py list_issue_types --json '{"owner":"my-org"}'
```

### Pull Requests（PR 操作）

```bash
# 获取 PR 详情
python3 github_mcp.py pull_request_read --json '{"owner":"octocat","repo":"hello-world","pull_number":42}'

# 列出 PRs
python3 github_mcp.py list_pull_requests --json '{"owner":"octocat","repo":"hello-world"}'

# 搜索 PRs
python3 github_mcp.py search_pull_requests --json '{"q":"is:open repo:owner/repo"}'

# 创建 PR
python3 github_mcp.py create_pull_request --json '{"owner":"octocat","repo":"hello-world","title":"Add feature X","head":"feature-branch","base":"main","body":"PR description..."}'

# 更新 PR
python3 github_mcp.py update_pull_request --json '{"owner":"octocat","repo":"hello-world","pull_number":42,"title":"Updated title"}'

# 合并 PR
python3 github_mcp.py merge_pull_request --json '{"owner":"octocat","repo":"hello-world","pull_number":42,"merge_method":"squash"}'

# 添加 PR 评论回复
python3 github_mcp.py add_reply_to_pull_request_comment --json '{"owner":"octocat","repo":"hello-world","pull_number":42,"comment_id":123,"body":"Thanks!"}'

# 添加 PR Review 评论
python3 github_mcp.py add_comment_to_pending_review --json '{"owner":"octocat","repo":"hello-world","path":"src/main.py","line":10,"body":"LGTM"}'

# 创建/提交 PR Review
python3 github_mcp.py pull_request_review_write --json '{"owner":"octocat","repo":"hello-world","pull_number":42,"method":"create","body":"Approved","event":"APPROVE"}'

# 更新 PR 分支
python3 github_mcp.py update_pull_request_branch --json '{"owner":"octocat","repo":"hello-world","pull_number":42}'

# 请求 Copilot Review
python3 github_mcp.py request_copilot_review --json '{"owner":"octocat","repo":"hello-world","pull_number":42}'
```

### Search（搜索）

```bash
# 搜索用户
python3 github_mcp.py search_users --json '{"q":"location:Xi\\\"an"}'
```

### Secret Scanning（密钥扫描）

```bash
# 扫描内容中的密钥
python3 github_mcp.py run_secret_scanning --json '{"content":"some content with potential secrets"}'
```

## 工作流

### 搜索并研究一个开源项目

1. 用 `search_repositories` 找到目标仓库
2. 用 `get_file_contents` 获取 README（path="README.md"）
3. 用 `list_branches` 查看分支
4. 用 `list_issues` 查看 open issues 了解活跃度
5. 用 `get_latest_release` 获取最新版本

### 修改文件并提交

1. 用 `get_file_contents` 读取要修改的文件
2. 用 `create_or_update_file` 更新文件
3. 用 `create_branch` 创建新分支
4. 用 `create_pull_request` 创建 PR

### 排查 PR 并 Review

1. 用 `pull_request_read` 获取 PR 详情
2. 用 `request_copilot_review` 请求 Copilot 自动审查
3. 用 `pull_request_review_write` 提交 Review

## 注意事项

- **所有参数** 必须通过 `--json` 以 JSON 格式传递
- **owner** 通常是用户名或组织名，**repo** 是仓库名（不含 owner/ 前缀）
- **Token 权限** 不同的工具需要不同的 OAuth scope，遇到权限错误检查 PAT 权限
- **速率限制** GitHub API 有速率限制，频繁调用时注意
- **代理** 默认使用 `192.169.1.2:7890` 代理，脚本会自动检测代理连通性，不通则直连
- **响应格式** 远程服务器返回 SSE (text/event-stream) 格式，脚本自动解析
- **Session 管理** 脚本自动维护 `Mcp-Session-Id`，无需手动处理

## 远程服务器专属工具（本地 MCP 不可用）

| 工具 | 说明 |
|------|------|
| `run_secret_scanning` | 扫描内容中的密钥（API keys, tokens 等） |
| `request_copilot_review` | 请求 Copilot 自动审查 PR |
| `create_pull_request` | 创建 PR（远程版支持 Copilot 集成） |
| `add_comment_to_pending_review` | 添加到待提交 review 的评论 |
| `sub_issue_write` | 添加子 Issue |

## 本地 vs 远程工具差异

远程 GitHub MCP Server 的工具集与本地 Docker 版不同：
- 远程版**不包含** Actions、Dependabot、Code Scanning、Gists、Projects、Notifications、Stargazers 等 toolset
- 远程版**独有** `run_secret_scanning`、`create_or_update_file`、`push_files` 等文件操作工具
- 如需完整工具集，可使用本地 Docker 版 `github-mcp-server`
