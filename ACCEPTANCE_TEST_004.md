# YueYun Demo v0.1 — Post-Consumption Irreversibility Boundary Test 004

## 1. 实验信息与目标

- 测试日期：2026-10-06。
- 测试方式：项目负责人在真实浏览器 UI 中人工操作并观察本地授权消费后的行为与提示。
- 总体结果：**PASS**（限定于本次正常 UI 流程中的本地 post-consumption 边界）。

本次实验核心问题：当用户已批准授权，该授权已被消费、Context 已在 YueYun 本地生成后，系统是否仍错误地把该授权表现为可以撤销，或错误承诺已生成/已披露的数据能够被远程收回？

同时验证页面是否明确区分：`Authorization consumed ≠ Context sent to external model`。

本记录依据项目负责人提供的人工操作与观察事实编写，不是程序自动采集结果。本轮未重新运行实验，也未核查或改写授权审计记录；不补写未提供的 Run ID、authorization ID、精确操作时间、截图编号或其他证据。

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
| 本次已发生 | 授权批准、消费及本地 Context 生成 |
| 本次未发生 | 用户复制 Context 或向 ChatGPT 发送 Context |

## 3. 与实验相关的状态边界

| 概念 | 语义 |
| --- | --- |
| Deny | 用户从未批准本次授权。 |
| Approved-Unconsumed | 用户已经批准，但 grant 尚未用于生成 Context。 |
| Revoke | 用户在消费之前收回 Approved-Unconsumed grant。 |
| Consume | 已批准 grant 被实际用于生成本次 Context；该授权进入已消费状态。 |
| External Disclosure / Model Delivery | Context 实际离开 YueYun 用户侧流程并被提供给外部模型。 |

**Consume ≠ External Disclosure。** 本次发生了 Consume 和本地 Context generation，没有发生真实的 External Model Delivery。

消费后不能沿用同一次授权重复生成 Context，也不再把该 grant 表现为普通的消费前可撤销授权。这是本次观察到的本地流程边界，不表示本地文本不能再由用户处理，也不是远程数据召回能力的验证。

## 4. 人工操作过程

1. 用户建立新的 Run。
2. 用户检索关键词“游泳”。
3. 系统找到对应本地 Memory。
4. 用户选择该 Memory。
5. 设置 Target model = `chatgpt`。
6. 设置 Purpose = “回答当前问题”。
7. 设置 Current question = “小星周日喜欢做什么？”。
8. 用户查看授权预览。
9. 用户点击“仅本次授权”。
10. Runtime 进入 Approved-Unconsumed。
11. 此时授权已批准但尚未消费。
12. 用户点击“生成 Context”。
13. 系统消费本次授权并在本地生成 Context。
14. 页面明确显示“本次授权已消费”。
15. 页面提示该次授权不能再次生成 Context。
16. 页面明确提示：“已生成文本无法远程撤回，无法保证外部模型删除数据。”
17. “生成 Context”不再可继续用于第二次生成。
18. 原先 pre-consumption 阶段可用的“撤销本次授权”不再作为正常可执行 revoke 操作存在。
19. 页面出现“已授权 Context”。
20. 页面同时明确说明：“Context 已生成，但尚未发送给任何模型。”
21. 用户没有将本次生成的 Context 复制或发送给 ChatGPT。
22. 因此本次实验只验证 YueYun 本地 post-consumption 边界，不涉及真实外部模型接收数据后的行为。

## 5. 人工观察结果

**实验结果：PASS。** 生成 Context 后，页面明确显示授权已消费，同一次授权不能通过正常流程再次生成 Context，且不再提供普通的 pre-consumption revoke 操作。

页面同时展示本地已生成的 Context，并明确提示尚未发送给任何模型，以及已生成文本无法远程撤回、无法保证外部模型删除数据。本次用户未复制或发送 Context，因此这些提示是系统对能力边界的表达，不是对外部模型收到数据后的实际行为验证。

## 6. 已验证的结论

| 验证项 | 本次结果与依据 |
| --- | --- |
| Approved-Unconsumed 与 Consumed 不同 | PASS：批准后尚未消费；用户主动生成 Context 后，页面显示“本次授权已消费”。 |
| 生成 Context 消费本次 grant | PASS：本次操作完成本地生成，正常流程进入已消费状态；未另行执行底层接口攻击测试。 |
| 一次性授权不能重复生成第二份 Context | PASS：页面提示需重新授权，同次“生成 Context”不再可继续执行；限定于正常 UI 路径。 |
| pre-consumption revoke 与 post-consumption 状态有明确边界 | PASS：消费后该 grant 不再表现为普通的尚可撤销授权。 |
| 不承诺远程撤回或强制删除 | PASS：页面明确说明已生成文本无法远程撤回，无法保证外部模型删除数据。 |
| 本地生成与外部发送是不同事件 | PASS：页面同时显示“已授权 Context”和“Context 已生成，但尚未发送给任何模型”。 |
| 本次没有 External Model Delivery | PASS：用户没有复制或发送本次 Context 给 ChatGPT。 |
| post-consumption irreversibility boundary 的最小工程表达 | PASS：正常流程区分一次性消费、消费前撤销及外部提供，并明确提示本地能力限制。 |

## 7. 尚未验证与结论限制

- 本次不是安全攻击、渗透或恶意绕过测试。
- 尚未证明底层不存在安全漏洞。
- 尚未验证并发、多进程、异常崩溃或服务重启后的全部消费语义。
- 尚未验证远程模型 API。
- 本次没有把 Context 发送给 ChatGPT，没有验证 ChatGPT 或其他外部模型收到 Context 后的保存、删除或数据处理行为。
- 不能声称 YueYun 可以召回已经发送给外部系统的数据，或强制外部模型删除已经获得的数据。
- 不能把本地 Context generation 描述成已经发生外部数据披露。
- 不应声称该边界具有密码学保证，或系统已经通过隐私、安全认证及绝对隐私安全验证。
- 消费后的权限不可重复使用，不等于任何已消费数据都绝对无法处理；本次不作此类扩大结论。
- 本次 PASS 仅适用于上述人工观察范围，不表示完整产品或 v0.1 Final 整体验收完成。

## 8. Acceptance Conclusion

**PASS。** 本次人工实验支持 YueYun Demo v0.1 的 post-consumption boundary：当一次 Approved-Unconsumed grant 被用于生成 Context 后，该授权进入已消费状态，不能继续通过正常流程重复生成 Context，也不再被表现为普通的 pre-consumption 可撤销授权。

系统同时明确区分“Context 已在本地生成”与“Context 已发送给外部模型”。本次实验只发生前者，没有发生后者。

当前实验支持以下边界：

- `Approve ≠ Consume`
- `Consume ≠ External Disclosure`
- `Pre-consumption Revoke ≠ Post-consumption Recall`

这些结论限定于本次正常 UI 人工流程，不构成远程召回、外部强制删除或全面安全保证。
