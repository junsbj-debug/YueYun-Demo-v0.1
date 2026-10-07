# YueYun Demo v0.1 — Pre-Consumption Revoke Test 003

## 1. 实验信息与目标

- 测试日期：2026-10-06。
- 测试方式：项目负责人在真实浏览器 UI 中人工操作并观察正常的消费前撤销流程。
- 总体结果：**PASS**（限定于本次正常 UI / Runtime 路径中的 pre-consumption revoke）。

本次实验核心问题：当用户已经明确批准一次授权，但该授权尚未被 Model Adapter 消费、Context 尚未生成时，用户是否仍可撤销该授权，并阻止该 grant 继续用于生成 Context？

本记录依据项目负责人提供的人工操作与观察事实编写，不是程序自动采集的结果。本轮仅建立文档，未重新运行实验，也未核查或改写授权审计记录；不补写未提供的 Run ID、authorization ID、精确操作时间、截图编号或其他证据。

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
| 撤销时点 | 已批准，尚未生成 Context、尚未消费授权 |
| 外部传递 | 用户没有把本次 Memory / Context 人工发送给 ChatGPT |

## 3. 与实验相关的状态边界

本次实际观察的主要状态路径为：

`Awaiting Decision → Approved-Unconsumed → Revoked`

必须区分以下三个概念：

| 概念 | 语义 |
| --- | --- |
| Deny | 用户从未批准本次授权。 |
| Revoke | 用户已经批准，但在授权被消费、Context 生成之前收回授权。 |
| Consume | 已批准的授权实际被用于生成本次 Context。 |

本次用户执行了 Approve 和 Revoke，没有执行 Consume。Approved-Unconsumed 不表示 Context 已生成或已交给模型；撤销针对本次使用授权，不针对本地 Memory 的存在。

`Approve ≠ Consume`

`Revoke ≠ Delete Memory`

这些语义用于解释本次实验，不表示本实验重新验证了 Deny、已消费后的撤销行为或所有异常路径。

## 4. 人工操作过程

1. 用户建立新的 Run。
2. 用户检索关键词“游泳”。
3. 系统找到对应的本地 Memory。
4. 用户选择该 Memory。
5. 设置 Target model = `chatgpt`。
6. 设置 Purpose = “回答当前问题”。
7. 设置 Current question = “小星周日喜欢做什么？”。
8. 用户点击“查看授权预览”。
9. Runtime 进入 Awaiting Decision。
10. 用户点击“仅本次授权”。
11. Runtime 进入 Approved-Unconsumed。
12. 此时授权已经批准，但尚未点击“生成 Context”。
13. 页面当时提供“生成 Context”和“撤销本次授权”操作。
14. 用户没有生成 Context。
15. 用户点击“撤销本次授权”。
16. 页面显示“本次授权已撤销”。
17. Runtime 从 Approved-Unconsumed 进入 Revoked。
18. Run 事件历史中可以观察到：`approved [Approved-Unconsumed] → revoked [Revoked]`。
19. 撤销后，该次授权不再提供正常的 Context 生成路径。
20. 本地 Memory 仍然存在；撤销授权没有删除 Memory。
21. 用户没有把本次 Memory / Context 人工发送给 ChatGPT。

## 5. 人工观察结果

**实验结果：PASS。** 用户在 Approved-Unconsumed 阶段主动撤销后，页面显示“本次授权已撤销”，Runtime 进入 Revoked，该次授权不再通过正常 UI 流程生成 Context；本地 Memory 仍然存在。

本次没有生成 Context，也没有人工向 ChatGPT 提供本次 Memory / Context。因此本实验观察的是消费前撤销，不是已传递数据的远程召回。UI 与事件历史是本次人工观察依据，不能据此推定恶意绕过或底层安全攻击已被验证。

## 6. 已验证的结论

| 验证项 | 本次结果与依据 |
| --- | --- |
| Approved 与 Consumed 是不同状态 | PASS：批准后进入 Approved-Unconsumed，用户尚未生成 Context 即执行撤销。 |
| 批准不等于 Context 已生成或已交给模型 | PASS：批准后仍需独立执行“生成 Context”；本次未执行，也未人工发送。 |
| 尚未消费的 grant 可由用户撤销 | PASS：用户在 Approved-Unconsumed 阶段主动点击“撤销本次授权”。 |
| 撤销后 Runtime 进入 Revoked | PASS：页面状态及事件历史显示 approved → revoked。 |
| 被撤销的 grant 不再用于本次 Context 生成 | PASS：本次正常 UI 流程中，撤销后不再提供该次授权的正常生成路径。 |
| Revoke 不删除本地 Memory | PASS：撤销后本地 Memory 本身仍然存在。 |
| Memory ownership / Permission grant / Context generation-consumption 分层 | PASS：Memory 保留、本次使用权被收回、Context 未生成，表现为不同层次。 |
| 授权在消费前仍可由用户收回 | PASS：本次人工流程支持这一最小工程语义。 |

## 7. 尚未验证与结论限制

- 本次只验证正常 UI / Runtime 路径中的 pre-consumption revoke。
- 本次不是安全攻击、恶意绕过或渗透测试。
- 尚未证明底层实现不存在任何安全漏洞。
- 尚未验证多进程、并发、异常崩溃、服务重启后的全部撤销语义。
- 尚未验证远程模型 API；本次没有把 Context 发送给 ChatGPT。
- 本次不能证明已经发送给外部模型的数据可以被物理召回。
- Revoke 不应被描述成删除外部模型已经获得的数据，或强制外部模型遗忘。
- 本次不证明撤销具有密码学保证，不代表系统通过隐私或安全认证，也不代表绝对隐私安全。
- 本次 PASS 限定于上述人工实验，不表示完整产品或 v0.1 Final 整体验收已经完成。

## 8. Acceptance Conclusion

**PASS。** 本次人工实验支持 YueYun Demo v0.1 的 pre-consumption revoke 权限语义：当用户已经针对指定模型、用途、问题和 Memory 批准一次授权，但该授权尚未被消费、Context 尚未生成时，用户仍可通过正常 UI 撤销该 grant。

撤销后 Run 进入 Revoked，该次授权不再通过正常流程继续生成 Context，而本地 Memory 本身保持存在。这表明在当前 v0.1 实验范围内：**Approve 不等于 Consume，Revoke 不等于 Delete Memory。** 结论不扩展为已发送数据可远程撤回或全面安全保证。
