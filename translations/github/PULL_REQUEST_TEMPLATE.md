## 这个 PR 做了什么？

<!-- 清晰地描述变更内容。它解决了什么问题？为什么这个方法是正确的？ -->



## 相关 Issue

<!-- 链接此 PR 所针对的 issue。如果不存在 issue，请考虑先创建一个。 -->

修复 #

## 变更类型

<!-- 勾选适用的选项。 -->

- [ ] 🐛 错误修复（修复问题的非破坏性变更）
- [ ] ✨ 新功能（增加功能的非破坏性变更）
- [ ] 🔒 安全修复
- [ ] 📝 文档更新
- [ ] ✅ 测试（增加或改进测试覆盖率）
- [ ] ♻️ 重构（行为无变化）
- [ ] 🎯 新技能（捆绑或来自技能中心）

## 具体变更

<!-- 列出具体的变更。对于代码变更，请包含文件路径。 -->

- 

## 如何测试

<!-- 验证此变更有效的步骤。对于错误修复：重现步骤 + 证明修复有效的证据。 -->

1. 
2. 
3. 

## 检查清单

<!-- 在请求审查前完成这些。 -->

### 代码

- [ ] 我已阅读 [贡献指南](https://github.com/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md)
- [ ] 我的提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范（`fix(scope):`、`feat(scope):` 等）
- [ ] 我搜索了 [现有 PR](https://github.com/NousResearch/hermes-agent/pulls) 以确保这不是重复的
- [ ] 我的 PR **仅**包含与此修复/功能相关的变更（无无关提交）
- [ ] 我已运行 `pytest tests/ -q` 并且所有测试都通过
- [ ] 我已为我的变更添加了测试（错误修复必需，新功能强烈建议）
- [ ] 我已在我的平台上测试过：<!-- 例如 Ubuntu 24.04, macOS 15.2, Windows 11 -->

### 文档与维护

<!-- 勾选所有适用的选项。如果某个类别不适用于你的变更，勾选“不适用”即可。 -->

- [ ] 我已更新相关文档（README、`docs/`、文档字符串）—— 或不适用
- [ ] 如果我添加/更改了配置键，我已更新 `cli-config.yaml.example` —— 或不适用
- [ ] 如果我更改了架构或工作流，我已更新 `CONTRIBUTING.md` 或 `AGENTS.md` —— 或不适用
- [ ] 我已根据 [兼容性指南](https://github.com/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md#cross-platform-compatibility) 考虑了跨平台影响（Windows、macOS）—— 或不适用
- [ ] 如果我更改了工具行为，我已更新工具描述/模式 —— 或不适用

## 对于新技能

<!-- 仅在你添加新技能时填写此部分。否则请删除。 -->

- [ ] 此技能对大多数用户**广泛有用**（如果是捆绑技能）—— 参见 [贡献指南](https://github.com/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md#should-the-skill-be-bundled)
- [ ] SKILL.md 遵循 [标准格式](https://github.com/NousResearch/hermes-agent/blob/main/CONTRIBUTING.md#skillmd-format)（frontmatter、触发条件、步骤、注意事项）
- [ ] 没有引入尚未可用的外部依赖（优先使用标准库、curl、现有的 Hermes 工具）
- [ ] 我已端到端测试了该技能：`hermes --toolsets skills -q "使用 X 技能来做 Y"`

## 截图 / 日志

<!-- 如果适用，添加截图或日志输出以展示修复/功能的效果。 -->