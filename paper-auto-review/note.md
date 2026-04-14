
## prompt

你帮我仔细阅读 paper-auto-review 这个 skill。现在需要改进这个 skill
- 扫描给定的目录，找到还没有找到审稿的论文，找出没有 review*.md 的论文目录
- 找到 pdf 或者 docx， doc 文件；然后使用 pi-llm-server 将 原始文件转化成 Markdown 文件，保存到原始相同的目录
- 将这个skill 目录下的 review_prompt.md 和 Markdown格式的论文都传给 大语言模型进行审稿，把审稿的结果保存到和原文一样的目录，例如原始的论文是： xxx.pdf， 则审稿意见保存为 xxx_review_draft.md
- 可以使用这个目录 "/home/bushuhui/datacenter/papers/paper-review/2026/航空学报/融合语义特征的低空环境下无人机单目定位" 来测试


pi-llm-server 没有提供LLM对话的功能，你可以使用如下的大模型进行审稿
export BAILIAN_URL=https://coding.dashscope.aliyuncs.com/v1
export BAILIAN_API_KEY=sk-sp-67eXXXX
export BAILIAN_MODEL=qwen3.6-plus


帮我把 paper-auto-review 里面的 review_prompt.md 翻译成中文，保存为 review_prompt_cn.md
如果需要审稿的论文是中文，则使用 review_prompt_cn.md，审稿意见也是中文
如果需要审稿的论文是英文，则使用 review_prompt.md，审稿意见也是英文
