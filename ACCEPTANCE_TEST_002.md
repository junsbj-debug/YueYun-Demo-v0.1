# YueYun Demo v0.1 — Explicit Denial / Permission Boundary Test 002

## 1. 实验信息与目标

- 测试日期：2026-10-06。
- 测试方式：项目负责人在真实浏览器 UI 中人工操作并观察 YueYun 的正常拒绝授权流程。
- 总体结果：**PASS**（限定于本次正常 UI 路径下的显式拒绝）。

验证相关 Memory 已存在、被检索、选择并展示后，用户是否仍可明确拒绝针对指定模型和用途的授权，使正常流程不生成本次可供模型使用的授权 Context。

本记录严格依据项目负责人提供的人工操作与观察事实编写，不是程序自动采集的测试结果。本轮仅建立文档，未重新运行实验；不补写未提供的 Run ID、authorization ID、精确操作时间、截图编号或其他证据。

## 2. 测试数据与条件

| 项目 | 内容 |
| --- | --- |
| 数据性质 | fictional test data，不是真实个人数据 |
| 测试事实 | 小星喜欢在周日游泳。 |
| 本地 Memory ID | `81bdeea8-1e58-420a-988a-76255948745e` |
| 检索关键词 | 游泳 |
| Target model | `chatgpt` |
| Purpose | 回答当前问题 |
| Current question | 小星周日喜欢做什么？ |
| 外部传递 | 用户没有把 Memory 或 Context 人工发送给 ChatGPT |

## 3. 与实验相关的状态边界

本次实际观察的决策路径为：

`Awaiting Decision → Denied`

Awaiting Decision 时页面为“授权预览（未授权）”，尚未生成已授权 Context。用户明确拒绝后，本次 Run 终止于 Denied，授权/拒绝操作按钮不能继续使用。

预览中展示 Memory 不等于已授权 Context，也不等于模型获得该 Memory。拒绝本次使用权限不等于删除本地 Memory。本节仅解释本次已观察路径，不据此推定其他生命周期分支已通过本实验验证。

## 4. 人工操作过程

1. 用户在 YueYun 本地页面检索关键词“游泳”。
2. 系统找到对应的本地 Memory。
3. 用户选择该 Memory。
4. 用户填写 Target model = `chatgpt`。
5. 用户填写 Purpose = “回答当前问题”。
6. 用户填写 Current question = “小星周日喜欢做什么？”。
7. 用户点击“查看授权预览”。
8. Runtime 进入 Awaiting Decision。
9. 页面显示“授权预览（未授权）”。
10. 此时尚未生成已授权 Context。
11. 用户明确点击“拒绝授权”。
12. Runtime 从 Awaiting Decision 进入 Denied。
13. 页面显示“本次已拒绝”。
14. 页面明确显示：“本次已拒绝，未生成 Context，任何 Memory 均未发送给模型。”
15. 授权/拒绝操作按钮进入不可继续使用状态。
16. 本次 Run 终止于 Denied。
17. 用户没有把 Memory 或 Context 人工发送给 ChatGPT。

## 5. 人工观察结果

**实验结果：PASS。** 用户在预览阶段明确拒绝后，正常 UI 流程没有生成本次授权 Context，同一决策流程不能继续用于生成 Context。

页面中的“未发送给模型”与用户没有人工传递的事实，描述的是本次正常实验流程；不是网络抓包结论或网络安全层面的绝对证明。

## 6. 已验证的结论

| 验证项 | 本次结果与依据 |
| --- | --- |
| 本地存在 Memory 不等于模型自动获得 Memory | PASS：记录可被检索、选择和预览，但本次拒绝后没有生成或人工传递授权 Context。 |
| 用户可以明确拒绝本次授权 | PASS：用户在授权预览阶段主动点击“拒绝授权”。 |
| 拒绝后不生成本次授权 Context | PASS：正常 UI 路径进入“本次已拒绝”，页面明确提示未生成 Context。 |
| Denied 是本次 Run 的终止状态 | PASS：Runtime 从 Awaiting Decision 进入 Denied，本次 Run 终止。 |
| 同一决策流程不能继续生成 Context | PASS：授权/拒绝按钮不可继续使用；结论限定于本次正常 UI 流程。 |
| 拒绝使用不等于删除 Memory | PASS：Memory 本身仍存在于本地，拒绝的是本次授权。 |
| Memory ownership / Permission / Context Export 分层 | PASS：本地数据的存在、用户对本次使用的决定与授权 Context 的生成表现为不同层次。 |

## 7. 尚未验证与结论限制

- 本次仅验证正常 UI 路径下的显式拒绝。
- 尚未进行恶意绕过、安全攻击或渗透测试。
- 尚未证明底层实现不存在任何安全漏洞。
- 尚未验证多进程、异常崩溃、并发请求或服务重启后的全部权限边界。
- 尚未验证远程 API 模型调用；v0.1 当前仍采用人工 Context 传递，本次没有向外部模型提供数据。
- “未发送给模型”仅指本次 YueYun 正常实验流程中没有生成/传递授权 Context，不扩展为网络安全层面的绝对证明。
- 本次 PASS 不代表绝对隐私安全、任何模型永远无法取得被拒绝的数据、安全认证或完整产品已经完成。

## 8. Acceptance Conclusion

**PASS。** 本次实验支持 YueYun Demo v0.1 的权限边界假设：即使相关个人 Memory 已存在并被检索、选择和展示，在用户明确拒绝针对指定模型和用途的授权后，正常流程不会生成可供该次模型使用的授权 Context。

Memory 的存在与模型的使用权限是两个独立状态。该结论限定于本次虚构数据、人工观察和正常 UI 拒绝路径，不扩大为全面安全或隐私保证。
