# YueYun Demo v0.1 — Feature Freeze Declaration

- Freeze 日期：2026-10-06
- 状态：**FEATURE FROZEN**
- 冻结对象：YueYun Demo v0.1 最小工程研究原型的功能范围，不是产品 Final Release。

## 1. 声明依据

依据已完成的只读 Freeze Final Audit、后续 README 状态文字修正，以及项目负责人本次最终冻结决定：

| 检查项 | 结果 |
| --- | --- |
| Cleanup 01 — README | PASS |
| Cleanup 02 — SPEC / DESIGN 同步 | PASS |
| Cleanup 03 — Public Data Boundary | PASS |
| Acceptance Test 001 | PASS |
| Acceptance Test 002 | PASS |
| Acceptance Test 003 | PASS |
| Acceptance Test 004 | PASS |
| 当前已知 P0 Freeze Blocker | 0 |
| Freeze 前剩余 P1 | 0 |

此前最终只读检查发现的 README cleanup 状态过时问题已经通过单独的最小文字修正关闭。本声明不表示重新运行了实验，也不将已知 blocker 为零解释为不存在任何潜在缺陷。

本次仅新增本声明；既有文档中的 Freeze Candidate 表述保留为此前阶段记录，本文件记录项目负责人批准的本次 Feature Freeze 决定。

## 2. 已冻结的核心功能范围

- Local Long-Term Memory：用户明确确认后保存本地 JSON，并可重新读取。
- Retrieval：关键词检索及显式 current / historical / evolution / audit 查询，不自动选择或授权。
- Permission / explicit authorization：用户先查看预览，再针对目标模型、用途、当前问题、所选 Memory IDs 和批准快照明确决定。
- Deny：拒绝本次授权，终止正常 Context 导出路径。
- Pre-consumption Revoke：终止已批准但尚未消费的本地 Context 导出权限，不删除 Memory。
- One-time Consume：一次授权仅用于一次 Context 生成，Consume 与 Revoke 互斥。
- Manual Model Adapter / plain-text Context：消费 Permission 批准对象，返回供应商无关纯文本；不自动发送。
- Runtime 状态边界：内存协调一次 Run，区分 Preparing、Awaiting Decision、Approved-Unconsumed、Context Ready、Completed 及终止状态，不恢复 grant。
- Append-only Memory correction/evolution lifecycle：用户明确区分纠错与真实状态变化，新增记录建立关系，保留旧记录，不自动覆盖或推断变化。
- 人工跨模型 portability / continuity 验证：同一本地 Memory 经不同目标模型的独立授权，人工提供给 ChatGPT 与 Claude 并被正确使用。

该清单锁定现有功能范围；不意味着四份人工 Acceptance 覆盖了全部代码分支、Memory lifecycle 分支或异常路径。

## 3. 核心边界

- **Memory ≠ Permission**：本地存在、被检索或被选择，不等于模型获得使用权限。
- **Approve ≠ Consume**：批准后尚需用户主动生成 Context；未消费授权可以撤销。
- **Consume ≠ External Disclosure**：本地生成 Context 不等于向外部模型提供数据。
- **Pre-consumption Revoke ≠ Post-consumption Recall**：本地撤销不能远程追回已生成或已提供的文本，也不能保证外部模型删除或遗忘。
- **Context Ready ≠ 已发送给外部模型**：仅表示本地 Context 已生成，Permission 已消费。
- **Completed ≠ 外部模型已接收或回答**：仅表示本地 Run 已结束。

Permission 仍是唯一授权边界；Runtime、Adapter、Run ID、authorization ID 和 audit JSON 均不能制造或恢复 grant。相关绑定或 Memory 状态变化后必须重新授权，不自动替换 Memory 或扩大范围。服务重启后旧 Run 与运行时 grant 不恢复。

## 4. 当前人工验收依据

| 记录 | 实际人工验收范围 | 结果 |
| --- | --- | --- |
| [ACCEPTANCE_TEST_001.md](ACCEPTANCE_TEST_001.md) | 同一本地 Memory 分别独立授权并人工提供给 ChatGPT / Claude | PASS |
| [ACCEPTANCE_TEST_002.md](ACCEPTANCE_TEST_002.md) | 正常 UI 路径中的 Explicit Denial | PASS |
| [ACCEPTANCE_TEST_003.md](ACCEPTANCE_TEST_003.md) | Approved-Unconsumed 阶段的 Pre-consumption Revoke | PASS |
| [ACCEPTANCE_TEST_004.md](ACCEPTANCE_TEST_004.md) | 消费后正常流程不可重复生成，Consume ≠ External Disclosure | PASS |

这些记录依据项目负责人的真实人工操作和观察，不是自动化测试、安全认证、渗透测试或密码学证明。跨模型结果限定于记录中的虚构数据和实际使用的模型，不证明适用于所有模型。

## 5. 当前限制与非承诺

- 当前为 localhost（127.0.0.1）、单用户研究原型。
- 当前测试数据为 fictional test data；运行 Memory 和 authorization / audit 数据默认不进入公开仓库。
- Context 由用户人工复制和传递；没有自动模型 API 调用或自动模型切换。
- 本地数据为明文；没有加密、多用户权限基础设施或生产级安全保证。
- Runtime / grant 为运行时状态；没有跨进程 grant 恢复或持久化消费账本。
- 未验证大规模 Memory、长期稳定性及全部并发、崩溃、异常路径。
- 没有安全认证、渗透测试或密码学保证，不宣称隐私绝对安全。
- 不证明远程模型收到 Context 后的保存、删除、保留或其他数据处理行为；不提供远程召回或强制遗忘能力。

## 6. Freeze 后原则

1. 不再向 v0.1 增加新功能；新功能进入后续版本或独立阶段。
2. 如发现 blocker，可进行明确记录的 bug fix；不得借 bug fix 扩张 v0.1 scope。
3. 文档、发布卫生和不改变功能语义的修正可以单独记录。
4. 后续工作继续遵守项目目录、用户数据和授权边界；Feature Freeze 本身不授权执行新的开发或发布操作。

## 7. Declaration Conclusion

**FEATURE FROZEN。** YueYun Demo v0.1 当前单用户、localhost、本地 Memory、人工授权与人工 Context 传递范围内的最小工程研究原型功能边界正式锁定。

此次 Feature Freeze 不等于项目结束，不等于产品完成，也不等于 v0.1 Final Release、安全认证或 API 集成完成。它锁定的是已经验证的 v0.1 研究原型边界，为后续独立记录的修正与版本工作提供基线。
