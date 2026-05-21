
## TODO

[ ] PI-Dev中， docs/RAD.md - 应该是一个功能等一个单独的文件，RAD.md 是总的汇总文件？还是目前这样，一个文件包含所有的需求？
    RAD.md 里面的 ### 待办事项 需要完成后更新状态。或者这部分不做成TODO item，直接是list条目？


## prompt

### 2025-05-09

这个目录有一些skill，你仔细阅读每一个skill，把每个skill的功能，如何使用，整理成文档，保存为 README.md ; 另外把这些skill 分一下类，每类介绍一下，另外列出每类的 skill 名字


这个项目是一些 skill ， 你把 README.md 里面的详细内容，并结合最新的目录里面的内容，更新到 docs/README_Detail.md 。分类介绍每个skill的目的、用途、用法等。
README.md 就留下简要的说明： 本项目的目的，怎么安装（Claude Code, Codex, OpenClaw, Hermes Agent），有几类 skill，具体的说明链接到 docs/README_Detail.md 


### 2025-05-11

你帮我写一个 clash-verge-control 的 skill，可以使用 write-a-skill
主要的功能包括：
- 查询目前的节点有哪些，那些是可以联通的
- 如果用户想切换到 美国的节点，则切换到美国可以联通的节点
- 查询当前的 clash 的状态
可以把 /home/bushuhui/scripts/clash_ctl.py 拷贝到 skill 的目录里，如果需要改进可以改进skill目录里面的程序


## 2025-05-15

你帮我改进一下 pr-paper-auto-review/prompt/academic_polishing.md ，整理里面的内容，做成论文润色的prompt。使用这个prompt，并给一篇论文，能给出论文润色的建议


帮我改进一下 pr-paper-auto-review
主要的改进点如下：
1. 论文审稿的 prompt 文件改变位置了
  - review_prompt.md -> prompt/review_prompt.md
  - review_prompt_cn.md -> prompt/review_prompt_cn.md
2. 不仅审论文，也需要审如下类型的资料，类型可以是用户数据的，如果没有输入你根据文章的内容自动判断。根据输入文章的类型，选择如下的prompt
  - 英文论文: prompt/paper_review_prompt.md
  - 中文论文: prompt/paper_review_prompt_cn.md
  - 中期答辩: prompt/中期答辩.md
  - 开题答辩: prompt/开题答辩.md.md
  - 硕士论文: prompt/master_thesis.md
  - 博士论文: prompt/doctor_thesis.md
  - 论文精读: prompt/paper_fine_reading.md
  - 审稿屠夫-润色匠人: prompt/critic_mentor_review.md
  - 论文润色: prompt/academic_polishing.md


帮我改进一下 pr-paper-auto-review， 如果用户输入的文件，已经是 Markdown 格式的文件，则直接审稿


帮我改进一下 pr-paper-auto-review， 增加自然基金(NSFC)的申请书的评价，prompt是 prompt/NSFC.md


### 2026-05-20

你帮我仔细读一下 github 的mcp，帮我将这个mcp封装成 一个skill，名字叫 pi-github
mcp的用法是：

claude mcp add -s user --transport http github \
  https://api.githubcopilot.com/mcp \
  -H "Authorization: Bearer YOUR_PAT_HERE"

- `-H` ：通过 Header 传递认证令牌
- 其中的 `YOUR_PAT_HERE`，可以从环境变量 `GITHUB_TOKEN` 获取
- 访问 github 网站，可以使用代理，默认的代理是 192.169.1.2:7890

你仔细分析一下所有的工具和功能，把所有的功能尽可能都封装到 skill里面，可以写一个python脚本程序帮助访问网络的mcp工具


