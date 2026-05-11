
## 2025-05-11

能否基于这个仓库里面的规范、规则，帮我做一个 skill ，当用户针对自己的项目，想分析并判断本项目是否符合规范。是否可以查找这个skill 里面的refernce目录的规则，然后给用户针对用户的项目给出建议。你先不实现，先帮我分析清楚

能否先扫描项目，然后根据项目的特点、问题，再推荐使用哪个rule。或者用户提出需求，可以把所有的 rule 都列出来，并给出每个rule的使用场景，有什么用处，特点是什么。用户选择1个或多个rule，对项目进行分析，并给出建议。建议可以保持为 docs/pd-rule-check.md
另外，能否把rule的原始文件放到 skill目录的 references 目录，这样不用在依赖外部的资料。
你分析清楚后，把上面分析的结果、方案等增加到 docs/skill_design.md


你按照 docs/skill_design.md 里面的方案，并使用 write-a-skill 编写 pd-rules-check
编写的 skill 保存到： /home/a409/knowledge_base/codebase/skills_mcp_plugin/dev/pd-rules-check

