# YueYun Demo v0.1 工程规格

项目启动日期：2026-10-05

## 1. 核心目标

验证一个最小“个人数字连续体”闭环，而不是制作完整产品。

用户的重要长期信息由用户掌控，独立于某一个 AI 模型保存在本地。用户授权后，相关信息可以被检索并重新提供给模型；未来更换模型时，仍能沿用同一份个人连续性数据。

历史说明：初次规格定义阶段不编写程序代码、不安装依赖，本文当时仅描述后续实现目标。

规格收口决定（2026-10-06）：依据阶段性 Acceptance Review 与已记录的实际人工实验，`YueYun Demo v0.1 Core PoC` 已达到核心概念验证完成，当前状态为 `PASS`。这不等于 v0.1 Final 已封版或完整产品完成；下文仍保留待补能力与验证边界。

当前状态：`YueYun Demo v0.1 — FEATURE FROZEN`，依据见 [FEATURE_FREEZE_v0.1.md](FEATURE_FREEZE_v0.1.md)（2026-10-06）。Feature Freeze 仅锁定最小工程研究原型功能范围，不等于产品 Final Release、安全认证或已经公开发布。本文继续区分当前实现、人工 Acceptance evidence、当前限制和 Future Work。

## 2. 三个核心能力

### 2.1 跨模型迁移（Model Portability）

- 个人长期信息不绑定某一个 AI 模型、供应商或特定会话。
- 本地个人连续性数据是独立的数据来源，模型是可替换的使用方。
- 数据应采用简单、公开、可读、可导出的表示方式，不依赖模型私有记忆格式。
- 检索得到的相关上下文应能够重新提供给不同模型，不要求重建或重新录入全部个人数据。
- v0.1 验证数据与上下文能够复用，不要求不同模型给出完全相同的回答，也不宣称完成所有模型的兼容。

### 2.2 本地长期记忆（Local Long-Term Memory）

- 用户明确确认的重要长期信息可以保存到用户自己的本地存储中。
- 已保存的信息不依赖模型会话存续；结束会话后仍可读取和检索。
- 最小记忆记录应能辨认其内容、来源或用户确认情况，以及记录时间，便于理解和核对。
- 用户可以查看记忆，并控制其后续使用。最小 append-only Correction / Evolution 已实现，并已完成与 Permission 的回归验证；不据此单独宣布 v0.1 Final 整体验收完成。删除及复杂 Memory 管理继续暂缓。原记录保留，覆盖或删除操作必须遵守项目批准边界。
- 检索结果应能对应到原始记忆记录，用户能够核对提供给模型的内容。
- 本地存储不等于模型完全离线运行。若使用远程模型，发送上下文前仍须取得用户对相关内容和目标模型的授权。

当前已实现的最小 Memory lifecycle：

- 用户明确选择 `relationship_type = correction` 或 `evolution`，新增独立 ID / JSON；`previous_memory_id` 指向前序记录，旧内容、来源和创建时间不原地覆盖。
- Correction 表示原记录当时就是错误的；`effective_from` 继承前序明确日期，未知则保持未知。被纠正旧记录不再作为 current 或 historical 的有效事实，仅保留供 audit 查看。
- Evolution 表示真实状态变化；用户必须提供 `effective_from`（YYYY-MM-DD），已有前序生效日期时，新日期必须更晚。旧状态保留为历史事实。
- `effective_until` 是 Retrieval 根据后继关系与生效日期派生的查询字段，不写入或修改旧 Memory JSON；有效区间开始日包含、截止日不包含。
- current 默认使用本地当天；historical 必须提供明确查询日期，无日期事实不能冒充已证明的历史状态；evolution 展示显式关系链，audit 展示原始记录及派生状态，不做自然语言时间理解。
- 关系校验对缺失前序、重复后继、循环或非法关系 fail closed；关系链不自动选择记录，也不扩大 Permission 授权范围。

上述是当前实现与既有回归范围；正式 Acceptance 001–004 不单独证明所有 lifecycle 分支均已人工验收。

### 2.3 身份与权限边界（Identity & Permission）

- 用户：个人数据的所有者和授权决策者。
- 个人数据：由用户控制的本地长期信息，不属于任何模型。
- 模型：在授权范围内使用相关上下文的工具，不是个人数据的所有者。
- 本地记忆组件：按用户指令保存、检索并组织上下文，不自行扩大授权范围。
- 保存长期信息与提供信息给模型是两个独立动作，分别需要明确的用户意图。
- 每次授权绑定目标模型、用途、当前问题、用户选择的 Memory IDs 及批准快照。相关输入或 Memory 状态发生变化后，旧授权失效，必须重新选择并授权；不得自动替换 Memory、扩大授权范围或继承旧批准。
- 未获授权的信息不得提供给模型。模型输出不得自动成为已确认的长期记忆，也不得自行触发数据修改或权限变更。
- Permission 阶段已实现并通过最终验收，状态为 `PASS`。生命周期为 `Preview/Pending → Denied`，或 `Preview/Pending → Approved-Unconsumed → Consumed / Revoked / Invalidated`；待决定请求也可失效。终止后的旧请求或授权不能恢复，再次使用必须建立新请求。Current / Historical / Correction / Evolution 与 Permission 已完成回归验证。
- Revoke 在 Permission 层只终止已批准但尚未消费的本地 Context 导出权限，并与 Consume 互斥；一次授权只能消费一次。拒绝、撤销、失效或已消费的授权不能导出 Context。
- 批准 ≠ 生成 Context ≠ 发送给外部模型。当前 Manual Adapter 不自动调用或发送给模型。已经生成的 Context 无法通过本地 Revoke 远程追回、删除或保证外部模型遗忘，也不能宣称收回用户已持有的副本；复杂远程撤销机制不属于 v0.1。
- 授权决定审计和独立撤销事件只是历史记录，不是权限凭证，不能恢复运行时 grant。
- 当前一次性授权采用运行时 grant：进程重启后旧 grant 不恢复，必须重新授权。这是当前 v0.1 的 fail-closed 行为；没有持久化消费账本，不将其视为 Core PoC 阻塞项，也不宣称已实现跨重启的持久化消费审计。
- v0.1 使用简单、可核对的身份与授权表达，不引入复杂身份基础设施。

正式人工 Acceptance 支持正常 UI 流程中的以下边界：`Memory ≠ Permission`、`Approve ≠ Consume`、`Consume ≠ External Disclosure`、`Pre-consumption Revoke ≠ Post-consumption Recall`。Deny 终止本次正常导出路径；Approved-Unconsumed 可在消费前 Revoke，消费后不再表现为尚未消费的可撤销授权。已经外部披露的数据不受本地 Revoke 远程召回。该范围不是密码学证明、绝对安全或防攻击能力验证。

## 3. 最小验证闭环

1. 用户提供一条重要长期信息，并明确确认保存。
2. 信息写入本地记忆，用户能够查看并核对记录。
3. 结束原有模型会话后，用户提出一个需要该信息的问题。
4. 从本地检索相关记忆，展示其来源和拟提供的上下文。
5. 用户授权将这些具体上下文提供给指定模型，模型据此回应。
6. 更换模型后，从同一份本地记忆重新检索，在新的授权范围内提供上下文并继续使用。
7. 核对数据仍由用户保有，迁移不需要重新录入原始信息；另行验证拒绝授权时不会提供上下文。

### 3.1 当前 Runtime 协调层（Current Implementation）

`runtime.py` 管理一次本地 Run：保存 Preparing 草稿、查询元数据及候选/所选 IDs，协调 Retrieval、Permission 和 Adapter，记录状态转换及事件摘要。Runtime 完全内存化，不持久化 Run、完整 Memory 副本或完整 Context；可持有 Permission 返回的真实对象引用，但不自行批准、恢复 grant 或把 ID 当权限凭证，也不跟踪外部模型状态。

主要状态与语义：

| Runtime 状态 | 当前含义 |
| --- | --- |
| Preparing | 用户形成草稿、检索和选择；尚无 Permission 绑定时的草稿变化不终止 Run。 |
| Awaiting Decision | 已建立授权预览，等待明确决定。 |
| Approved-Unconsumed | Permission 已批准，尚未消费；可以 Revoke。 |
| Denied / Revoked | 分别为拒绝或消费前撤销后的终止状态。 |
| Context Ready | Permission 已被一次性消费，成功生成本地 Context；不表示已发送给外部模型。 |
| Completed | 用户在 Context Ready 后结束本地 Run；不表示模型已收到 Context 或已经回答。 |
| Invalidated / Cancelled / Error | 绑定失效、用户取消或错误的辅助终止状态。 |

正常路径为 `Preparing → Awaiting Decision → Approved-Unconsumed → Context Ready → Completed`，另有 Denied / Revoked 等终止路径。结束仍有 pending / approved-unconsumed 权限的 Run 时，调用 Permission 终止权限；不能只清理 UI。服务重启后 Run 消失，旧 grant 不恢复。用户在生成前结束 Run 为 Cancelled；刷新或关闭浏览器不是可靠 Revoke。

当前实现不代表上述全部分支均由四份正式 Acceptance 覆盖；其人工证据范围见第 4 节。

## 4. 验收标准

| 验证项 | 通过条件 |
| --- | --- |
| 本地持久性 | 结束会话后，用户仍能读取此前确认保存的记忆。 |
| 可检索与可核对 | 按相关问题检索到记忆，结果可对应到本地原始记录。 |
| 上下文重新提供 | 用户授权后，相关记忆能够作为上下文提供给指定模型。 |
| 跨模型复用 | 至少两个不同实际模型分别经过独立授权，使用同一份 YueYun 本地 Memory 并正确利用该信息，无需重建或重新录入记忆；接受 manual cross-model validation，不要求 API 自动调用或自动模型切换。 |
| 权限生效 | denied、revoked、invalidated、consumed 或 snapshot mismatch 的授权不能导出 Context；一次授权只能消费一次，Revoke 与 Consume 互斥；模型、用途、当前问题、Memory 选择或相关状态变化后必须重新授权，不得替换 Memory、扩大范围或继承批准；批准及生成 Context 均不自动发送给外部模型。 |
| 所有权清晰 | 用户、数据与模型的角色可明确辨认；模型无法自行决定保存、修改或扩大数据使用权限。 |

验收优先使用虚构或用户明确批准的少量示例信息。仅完成数据导出、或仅由模拟使用方读取上下文，不足以宣称跨模型验证已经完成；应如实记录实际验证范围与尚未验证的部分。

当前已实际完成的 manual cross-model validation（用户人工复制 Context 至 ChatGPT、Claude，各自独立授权并正确利用同一本地 Memory）是 v0.1 Model Portability / Cross-Model Continuity 的有效验收方式。当前主要人工验收索引如下；`TEST_REPORT_001.md` 与 `TEST_REPORT_v0.1.md` 保留为历史测试资料。外部回答由项目负责人人工观察，不是程序自动采集。API Adapter 继续作为后续阶段候选，不属于 v0.1 Core PoC 必需条件。

| 正式人工 Acceptance（均记录为 PASS） | 实际证据范围 |
| --- | --- |
| [ACCEPTANCE_TEST_001.md](ACCEPTANCE_TEST_001.md) | Manual Cross-Model Portability / independent authorization：同一本地 Memory 分别授权并人工提供给 ChatGPT、Claude。 |
| [ACCEPTANCE_TEST_002.md](ACCEPTANCE_TEST_002.md) | Explicit Denial：正常 UI 拒绝后终止 Run，不生成本次授权 Context。 |
| [ACCEPTANCE_TEST_003.md](ACCEPTANCE_TEST_003.md) | Pre-Consumption Revoke：批准但未消费时撤销，正常生成路径结束。 |
| [ACCEPTANCE_TEST_004.md](ACCEPTANCE_TEST_004.md) | Post-Consumption Boundary：消费后不能正常重复生成或消费前撤销；Consume ≠ External Disclosure，本次未外部发送。 |

这些是少量虚构数据下的人工 Acceptance evidence，不是自动回归测试、安全认证、渗透测试或密码学证明；不外推为全部异常路径、所有模型兼容或远程服务端行为验证。

Core PoC 状态为 `PASS`；Permission 阶段已通过最终验收，状态为 `PASS`。最小 append-only Correction / Evolution 已实现，并已完成与 Permission 的回归验证；不据此单独宣布 v0.1 Final 整体验收完成。删除及复杂 Memory 管理继续暂缓。双击启动脚本、API、向量数据库、加密、DID、多用户、多 Agent 均不加入当前 Core PoC 完成条件。

当前未实现持久化消费账本、跨进程恢复 grant、独立授权超时、完整消费/失效审计账本、审计保留和清理策略、加密、多用户和复杂角色权限、API 自动模型调用/切换；不宣称远程撤回、远程删除、保证模型遗忘或生产级安全保证。这些边界不改变当前 Permission 阶段的验收结论。

## 5. v0.1 不做的内容

人格吊坠、穿戴设备、区块链、Web3、DID、联邦网络、全球公网、数字人、多 Agent、训练模型、LoRA、复杂数据库、移动端、商业化功能。

不为这些内容预先搭建基础设施，不将最小验证闭环扩展为完整产品。

## 6. 工程原则

- Local-First：本地数据是个人长期信息的基础，用户保有数据控制权。
- 简单：使用完成最小闭环所需的最少组件。
- 可理解：数据、流程和权限规则能够直接阅读和说明。
- 可验证：每个核心能力都有可执行、可核对的验收条件。
- 可迁移：个人数据与模型分离，避免供应商和私有格式绑定。
- 尽量少依赖：优先简单文件存储与直接流程，避免不必要的复杂技术栈。

本规格不锁定编程语言、框架、模型供应商或具体存储格式；后续实现选择应服从上述原则。

## 7. 目录与阶段边界

以下目录安全原则继续有效；末两项为初次规格定义时的 Historical stage constraint，不代表当前 FEATURE FROZEN 原型的全部已实现能力或本轮修改范围。原开发机器路径的可迁移适用说明见 PROJECT_RULES.md；不据此扩大操作权限。

- 唯一允许操作的项目目录：`E:\YueYun\Demo-v0.1`。
- 不读取、修改、移动或删除 `E:\YueYun` 之外的任何用户数据。
- 未经明确批准，不执行具有破坏性的删除、覆盖或批量修改操作。
- 历史规格定义阶段仅创建 `SPEC.md`，不修改 `README.md` 和 `PROJECT_RULES.md`，不创建其他文件，不安装软件或依赖，不修改系统配置。
- 历史阶段要求：规格定义完成后停止，等待用户明确指示下一阶段。
