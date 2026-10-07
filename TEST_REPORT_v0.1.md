# YueYun Demo v0.1 — Cross-Model Continuity Test Report

**Historical Validation Record**

本文保留特定时间点的人工实验事实与原结论，不代表当前完整产品状态，也不构成自动化测试、安全认证、渗透测试或密码学证明。文中“当前”按相应实验发生时理解；项目当前状态以 `README.md`、`SPEC.md`、`DESIGN.md` 和 `FEATURE_FREEZE_v0.1.md` 为准。

测试日期：2026-10-05

本报告根据项目负责人提供的人工验收记录整理。测试日期按负责人指定记录；外部模型回答由用户人工观察，本报告未调用模型 API 或独立重测。

## 测试目标

验证同一份由用户控制的本地 Memory，能否在不重新输入原始个人信息的情况下，经用户分别明确授权后，被两个不同 AI 模型正确使用。

## 测试数据

使用现有 fictional test Memory（虚构测试数据）：

> 小星喜欢在周六阅读科幻小说。

当前实验使用单条 Memory，不涉及真实个人数据。

## 测试问题

> 小星周六喜欢做什么？

## 测试流程

1. 从 YueYun 本地 Memory 中选择该记录。
2. 目标模型设为 Claude。
3. 用户查看授权预览。
4. 用户执行“仅本次授权”。
5. YueYun 通过现有 Adapter 生成一次性 Context。
6. 用户手工复制 Context 到新的 Claude 会话。
7. Claude 正确回答：“小星喜欢在周六阅读科幻小说。”
8. 返回 YueYun。
9. 对同一条本地 Memory 重新建立授权。
10. 目标模型改为 ChatGPT。
11. 再次查看授权预览并执行“仅本次授权”。
12. YueYun 重新生成面向 ChatGPT 的 Context。
13. 用户手工复制 Context 到新的 ChatGPT 会话。
14. ChatGPT 正确回答：“小星喜欢在周六阅读科幻小说。”

## 测试结果

**PASS**

根据用户报告，两个外部模型均正确使用了各自获得的授权 Context。用户无需向第二个模型重新手工输入原始 Memory 内容；仍需要人工复制包含该 Memory 的 Context。

## 本次验证证明

在本次单条虚构数据与人工操作范围内：

- Local Memory 独立于具体模型存在。
- 更换目标模型后需要重新授权。
- Claude 的授权不能直接作为 ChatGPT 的授权。
- 两个模型之间不需要直接共享 Memory。
- 同一份用户侧 Memory 可以分别授权给不同模型使用。
- 用户不需要向第二个模型重新手工输入原始 Memory 内容。
- 当前最小链路已经实际运行通过：

  `Local Memory → User Selection → Authorization Preview → Explicit Authorization → Context → Model`

- YueYun 当前验证的是 Model Portability / Personal Digital Continuity 的最小工程闭环，而不是模型之间直接迁移内部记忆。

本报告不推断具体底层模型版本，也不将用户的外部观察表述为程序自动采集的证据。

## 当前限制

- 使用的是 fictional test data。
- 当前只有单条 Memory。
- Context 仍通过人工复制粘贴传递。
- 尚未直接调用 Claude/OpenAI API。
- 尚未验证复杂检索、多条 Memory、长期运行和多用户。
- 本次 PASS 只代表 v0.1 最小跨模型连续性链路验证成功，不代表完整产品已经完成。

## Why this test matters

模型可以被替换，而用户控制的个人连续性数据保持独立。YueYun 负责 Memory、Permission 和 Context 边界；模型只是获得本次明确授权 Context 的临时消费者，不是长期记忆的所有者。

这里的“临时消费者”描述授权范围，不表示已经验证远程服务删除或不保留收到的数据。

## Permission Boundary Test #1 — A/B Permission Boundary Test

### 记录来源与测试范围

本节将项目负责人已经实际人工完成并观察到的正反两组实验整理为 A/B Permission Boundary Test，验证 Unselected Memory Must Not Enter Context。本轮仅整理文档，没有重新运行实验或调用模型 API。具体实验日期未另行提供，不从报告前文日期推定。

本节是后续多 Memory 权限边界实验；前文“单条 Memory”和相关限制描述的是此前跨模型实验当时的范围。

### 共同条件与控制变量

YueYun 本地在本次实验时存在 3 条 fictional test Memory：

1. 小星喜欢在周六阅读科幻小说。
2. 小星最喜欢的颜色是蓝色。
3. 小星喜欢在周日游泳。

使用关键词“小星”检索时，3 条 Memory 均被命中。A/B 两组使用同一组本地虚构数据，并保持以下条件不变：

- 当前问题：“小星周日喜欢做什么？”
- 目标模型：ChatGPT。
- 本次用途：“回答当前问题”（依据项目负责人关于 B 组用途保持不变的补充说明）。
- 每组均只选择并授权 1 条 Memory，授权预览显示准备使用的数量为 1。
- Context 均由用户人工复制粘贴到一个新的 ChatGPT 会话。

两组改变的变量是用户明确选择并授权的 Memory：A 组选择无关的颜色记忆，B 组选择相关的周日游泳记忆。

### A/B 对照

| 对照项 | A 组：未授权相关 Memory | B 组：明确授权相关 Memory |
| --- | --- | --- |
| 当前问题 | 小星周日喜欢做什么？ | 小星周日喜欢做什么？ |
| 目标模型 | ChatGPT | ChatGPT |
| 本次用途 | 回答当前问题 | 回答当前问题 |
| 选择并授权的 Memory | 小星最喜欢的颜色是蓝色。 | 小星喜欢在周日游泳。 |
| 准备使用的 Memory 数量 | 1 | 1 |
| 最终 Context 中的 Memory | 仅颜色记忆 | 仅周日游泳记忆 |
| 未选择、未授权的 Memory | 周六阅读科幻小说、周日游泳 | 周六阅读科幻小说、颜色是蓝色 |
| ChatGPT 人工观察结果 | 授权信息不足，不能回答周日活动 | 正确回答周日游泳 |
| 判定 | PASS | PASS |

### A 组流程与观察

相关的“周日游泳”Memory 虽然存在于本地并被检索命中，但未被选择、未被授权。用户只选择并授权“颜色是蓝色”Memory；最终 Context 仅包含该颜色记忆，没有包含周日游泳或周六阅读记忆。

用户将 Context 人工复制到新的 ChatGPT 会话。据项目负责人观察，ChatGPT 明确表示：当前授权的 YueYun 本地记忆中没有“小星周日喜欢做什么”的信息，因此不能根据现有记忆推测。这是回答含义的记录，不补充未经提供的逐字回复。

**PASS**

### B 组流程与观察

用户只选择“小星喜欢在周日游泳。”这一条 Memory；周六阅读科幻小说和颜色是蓝色均未选择、未授权。授权预览显示准备使用的 Memory 数量为 1。

用户执行“仅本次授权”，YueYun 生成 Context。最终 Context 只包含周日游泳记忆，没有包含另外两条 Memory。

用户将 Context 人工复制到新的 ChatGPT 会话。项目负责人实际观察到 ChatGPT 回答：

> 小星喜欢在周日游泳。

**PASS**

### Overall Result

**PASS — A 组与 B 组均通过。**

### What This Test Demonstrates

`Local existence ≠ Retrieval ≠ Selection ≠ Authorization ≠ Model visibility`

Memory 存在于本地、甚至被检索命中，并不意味着模型能够看到；只有用户明确选择并针对本次用途授权的 Memory 才能进入 Context。

这组 A/B 实验在保持本地数据、问题、目标模型、用途和每组授权 Memory 数量为 1 的条件不变时，通过改变所选授权记忆实际验证了：

- **未授权相关 Memory → 模型不可从 YueYun Context 获得该信息。** A 组相关记忆未进入 Context，ChatGPT 表示授权信息不足。
- **明确授权相关 Memory → 该信息进入 Context，模型可以用于回答。** B 组 Context 包含周日游泳记忆，ChatGPT 正确回答。

### Evidence and Limits

- 数据属于 fictional test data，不涉及真实个人数据。
- Context 仍由用户人工复制粘贴。
- 外部 ChatGPT 回答是项目负责人实际人工观察，不是程序自动采集；本轮没有重测。
- 不补充未经提供的截图、授权记录标识或具体底层模型版本。
- 本次验证的是上述条件下 YueYun Demo 的 Context/Permission 边界，不将其推广为所有模型行为的保证。
- 不宣称验证了远程模型服务端的数据删除、不保留或完整隐私能力。
- 不宣称完整产品已经完成。

## Permission Boundary Test #2 — Target Model Binding

### 记录来源与固定条件

本节依据项目负责人刚刚实际人工完成的实验记录整理，本轮未重新运行实验。

- Memory：同一条 fictional Memory“小星喜欢在周日游泳”。
- 当前问题：“小星周日喜欢做什么？”
- 本次用途：“回答当前问题”。

实验过程中上述三项保持不变，改变的是目标模型。下文保留实际输入的目标模型标识大小写。

### 实际操作与观察

1. 首先目标模型为 `chatgpt`。用户查看授权预览后执行“仅本次授权”，成功生成 Context。
2. 生成的 Context 明确包含 `Target model: chatgpt`。
3. 随后不改变 Memory、问题和用途，只把目标模型从 `chatgpt` 改为 `claude`。
4. 页面提示输入发生变化，需要重新查看授权预览。
5. 重新预览后，状态恢复为“未授权”，没有继承此前给 ChatGPT 的授权。
6. 用户随后对 Claude 执行“拒绝授权”。页面显示：“本次已拒绝，未生成 Context，任何 Memory 均未发送给模型”。

### Result

**PASS**

### What This Test Demonstrates

该人工实验验证了当前 Demo 中授权与目标模型绑定：对 ChatGPT 的本次授权不能自动复用于 Claude；目标模型改变需要新的授权决定。

同一 Memory 可以对模型 A 允许、对模型 B 拒绝。本次具体观察为允许 `chatgpt` 并生成相应 Context，随后拒绝 `claude`，不生成其 Context。

### Evidence and Limits

结论限于项目负责人实际观察到的当前 Demo 本地流程。页面状态和 Context 中的目标标识不构成对远程模型服务端行为的验证，也不证明完整权限系统已经完成。

本节不补写未经提供的实验步骤、时间、截图编号或授权记录 ID。

## Permission Boundary Test #3 — Authorization Is Not Transmission

### 记录来源与测试条件

本节依据项目负责人刚刚实际人工完成并观察到的实验整理。本轮仅记录文档，未重新运行实验。

- 用户选择的 Memory：fictional Memory“小星喜欢在周日游泳。”。
- 目标模型：`chatgpt`。
- 本次用途：“回答当前问题”。
- 当前问题：“小星周日喜欢做什么？”。

### 实际操作与观察

1. 用户先查看授权预览，此时尚未授权。
2. 用户随后执行“仅本次授权”。页面进入“本次已授权”状态，并出现“生成 Context”操作。
3. 用户主动点击“生成 Context”。页面生成了只包含本次已授权 Memory 的 Context。
4. 页面明确显示：“Context 已生成，但尚未发送给任何模型”。

截至本次观察结束，用户尚未执行“复制 Context”，也未进行任何人工粘贴或发送给外部模型的操作。

### Result

**PASS**

### What This Test Demonstrates

该人工实验验证当前 Demo 将“选择 Memory”“授权”“生成 Context”与“实际向模型提供 Context”区分为不同步骤。

完成授权不会自动发送 Memory；生成 Context 本身也不会自动调用或发送给远程模型。本次观察停在页面显示 Context 的阶段，没有进入复制、人工粘贴或外部发送步骤。

### Evidence and Limits

结论限于项目负责人实际观察到的当前 Demo 人工流程与实现边界，不宣称验证了：

- 操作系统剪贴板安全。
- 网络层数据泄漏防护。
- 远程模型服务端行为。
- 完整隐私系统。

本节不补写未提供的时间、截图编号、授权记录 ID 或网络抓包证据；页面提示与人工观察不被表述为网络抓包验证。

## Permission Boundary Test #4 — One-Time Authorization

### 记录来源与测试条件

本节依据项目负责人刚刚实际人工完成并观察到的实验整理。本轮仅记录文档，没有重新运行实验。

此前用户已针对以下条件完成授权，并生成一次 Context：

- Memory：fictional Memory“小星喜欢在周日游泳。”。
- 目标模型：`chatgpt`。
- 本次用途：“回答当前问题”。
- 当前问题：“小星周日喜欢做什么？”。

Context 生成后，用户在不刷新页面、不修改输入、不重新生成授权预览、不重新授权的情况下，观察同一份授权是否还能再次生成 Context。

### 实际观察

页面中的“仅本次授权”“拒绝授权”“生成 Context”按钮均处于不可再次执行状态。页面提示 Context 已生成，再次生成需要重新预览并授权。

因此，原有这一次授权不能直接再次用于生成第二份 Context。本次记录的是按钮状态与页面提示的人工观察，不补写通过其他接口重复提交的操作。

### Result

**PASS**

### What This Test Demonstrates

本实验验证当前 Demo 页面流程中，一次授权在生成 Context 后不能被直接重复消费；若需要再次生成，必须重新建立授权预览并重新授权。

该观察支持当前设计：

`one authorization → one Context generation`

### Evidence and Limits

本实验只验证当前运行中的人工流程与当前 Demo 行为。项目此前已明确记录，一次性消费状态目前主要属于运行时状态；本实验不证明跨进程重启后的持久化一次性消费安全。

本实验也不宣称防重放、密码学令牌、远程服务端权限控制或完整安全系统已经实现。

本节不补写未提供的时间、授权记录 ID、截图编号或其他证据。

## Cross-Model Continuity Test — Same Local Memory, Different Models

### 记录来源与测试数据

本节依据项目负责人刚刚实际人工完成并观察到的实验整理。本轮仅记录文档，未重新运行实验。

数据源为同一条 YueYun 本地 fictional Memory：

> 小星喜欢在周日游泳。

### 实际操作与观察

此前，该 Memory 已针对目标模型 `chatgpt` 独立授权并生成 Context。ChatGPT 正确回答：

> 小星喜欢在周日游泳

随后将目标模型改为 `claude` 时，原授权不能继续使用，需要重新生成授权预览并重新授权。

用户针对 `claude` 完成新的“仅本次授权”，生成只包含同一条 Memory 的新 Context，并人工复制到一个新的 Claude 会话。Claude 实际回答：

> 根据你提供的信息，小星周日喜欢游泳。

上述外部模型回答由项目负责人实际人工观察，不是程序自动采集或本轮模拟的回复。

### Result

**PASS**

### What This Test Demonstrates

同一份 YueYun 本地 Memory 可以在不重新录入原始个人信息的情况下，经针对不同目标模型的独立授权，被不同模型使用。

模型切换不会改变本地 Memory 的数据源，旧模型授权也不会自动继承到新模型。本次记录的是当前 Demo 对 `Model Portability / Cross-Model Continuity` 的人工验证。

本实验没有将 Memory 从 ChatGPT“传输”到 Claude：两次 Context 的数据源始终是 YueYun 本地 Memory，各自经过面向目标模型的独立授权。

### Evidence and Limits

- 使用的是 fictional test data。
- Context 由用户人工复制传递，本实验不代表已经完成模型 API 自动切换。
- 不宣称已验证远程服务端隐私行为或完成完整产品化。
- 不补写未提供的时间、授权记录 ID 或底层 Claude/ChatGPT 具体模型版本。
