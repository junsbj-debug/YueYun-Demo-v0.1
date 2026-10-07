# YueYun Demo v0.1 — Standard Demo Script

## 1. 演示核心与准备

标准人工演示只讲一个核心故事：同一份属于用户自己的长期信息，不属于某个 AI。用户决定找出哪些信息、授权给哪个模型、用于什么目的；模型可以更换，而人的数字连续性由用户侧保持。

本次不是聊天机器人 Demo。重点链路是：

`Local Memory → Retrieval → Selection → Permission → Approve → Consume → Context → Manual External Disclosure`

仅在用户自行指定、与冻结源项目分离的隔离 Demo 目录中演示，不操作冻结源项目的数据。服务由独立步骤启动，本脚本不提供自动启动、自动授权或自动发送能力。演示者在浏览器使用已确认属于隔离副本的 http://127.0.0.1:8765/。

这是未来人工执行指引，不是新的实验结果记录。演示执行会在隔离副本正常产生新的授权审计，不应把此前 8 / 1 当作未来演示后的固定数量。

公开 clone 不包含历史 runtime Memory / authorization 数据，不能直接复现依赖这些本地运行数据的演示。examples/linxiao/ 是经过整理的 fictional example，当前 Runtime 不会自动加载它。本脚本以已另行准备并核验的隔离 Demo 环境为前提，不提供或新增 loader/import 功能。

## 2. 标准数据

林晓是完全虚构的 Demo Persona；使用现有 fictional fixture，不修改任何 Memory。

| 角色 | Memory ID | 信息 |
| --- | --- | --- |
| 当前旅行计划 D07 | 90b5affd-e0ec-44ed-931d-d80f25a02e0f | 当前计划 2026-11-15 去京都，原计划为 2026-11-08；effective_from 为 2026-09-28。 |
| 旅行偏好 D06 | dadea39c-b4eb-4700-9c7a-7e8a71ed0dfa | 不喜欢行程安排太满，希望每天留出自由时间。 |

原计划 D05 的 ID 是 e2fc41a6-17c1-43b1-a1c7-739f8d4633d0，effective_from 为 2026-09-20。D05 → D07 是 append-only evolution，旧记录仍保留；生效日期表示计划状态何时有效，不是出发日期。正式授权只选 D07 和 D06，不自动加入 D05 或其他记录。

## 3. 标准 7 步演示流程

### Step 1 — 展示本地 Memory

操作：展示林晓 fictional 本地 Memory、当前旅行计划和旅行偏好。

口述：“这些 Memory 保存在用户侧。记录存在不等于模型已经获得权限。旅行计划从 11 月 8 日演化为 11 月 15 日，原计划仍保留，旅行偏好是另一条独立记录。”

当前状态列表不应把旧计划同时当成当前事实。完整 evolution 历史按下一步单独查看。

### Step 2 — Retrieval

操作：选择“当前状态”，以“旅行”等关键词检索。展示命中解释和当前有效记录。

如需展示 evolution，切换到变化历史模式，输入 D07 或 D05 的 UUID，查看原计划 → 当前计划。该视图仅供查看，不自动选择或授权。展示完成后返回“当前状态”，重新检索“旅行”，再进行后续选择；切换查询会清理旧选择/授权流程，不沿用旧预览。

口述：“系统从本地找到了相关记录。当前状态和历史状态不同；变化链可以单独核对，检索本身不会发送信息。”

### Step 3 — Selection

操作：只勾选 D07 当前旅行计划和 D06 旅行偏好，核对选择数量为 2，以及两个 UUID。

口述：“检索命中不等于自动授权。我主动选择本次任务需要的两条信息，不需要把全部 Memory 提供给模型。”

若范围不正确，先调整选择，再创建预览。

### Step 4 — 准备授权请求

填写：

- Target model：chatgpt
- Purpose：规划京都旅行
- Current question：请根据我的计划和旅行偏好，帮我安排京都旅行。

口述：“授权绑定目标模型、用途、当前问题、所选 Memory 和 Preview snapshot。更换这些内容，需要重新预览并授权，不能继承旧批准。”

### Step 5 — Authorization Preview

操作：点击“查看授权预览”，核对 Awaiting Decision、目标模型、用途、问题、两条 Memory 的完整预览及状态信息。

口述：“现在只是授权预览，尚未授权，任何 Memory 都没有因为预览而自动发送给模型。Memory ≠ Permission。”

预览不符时不批准，先修改输入并重新预览。

### Step 6 — Approve / Consume / Context

操作：用户主动点击“仅本次授权”，先停留展示 Approved-Unconsumed。

口述：“现在批准了本次使用，但还没有消费。Approve ≠ Consume。此时仍可在生成之前撤销本次授权。”

本标准主流程继续点击“生成 Context”，展示 Context Ready 和已授权纯文本。核对仅含两条所选 Memory；不根据输入框重新拼接文本。

口述：“一次授权已被消费，本地 Context 已生成。Consume ≠ External Disclosure；Context Ready 不等于已经发送给外部模型。YueYun 此时只在本地生成经用户批准的 Context。”

不要重复生成。同一授权只能消费一次；若撤销、拒绝或失效，必须新建预览并重新明确决定。

### Step 7 — Manual External Disclosure

操作：用户主动点击“复制 Context”，在 YueYun 之外人工粘贴至目标 ChatGPT 会话并发送，观察模型是否利用 2026-11-15 的当前日期及宽松行程偏好。不要预设或伪造回答；如未实际回答，如实记录。

随后回到 YueYun，用户结束本次运行，展示 Completed。

口述：“当前 v0.1 不自动调用 ChatGPT API。复制、粘贴和发送是我的人工动作。Completed 只表示本地 Run 结束，不代表外部模型已经接收或回答。模型回答不会自动写回 YueYun 长期 Memory。”

Authorization audit 记录批准与预览快照，不能独立证明 Consume、复制、外部发送或回答。上述外部动作和回答应作为 manual observation 单独记录。复制到剪贴板本身也不证明模型收到。

## 4. 核心边界

| 边界 | 简要说明 |
| --- | --- |
| Memory ≠ Permission | 数据保存在本地，不代表模型有使用权。 |
| Retrieval ≠ Authorization | 检索命中不批准任何模型使用。 |
| Selection ≠ Authorization | 勾选仅确定候选范围，还需明确授权决定。 |
| Approve ≠ Consume | 批准后尚需主动生成 Context。 |
| Consume ≠ External Disclosure | 消费用于本地生成，不自动外部发送。 |
| Context Ready ≠ External Model Received | 本地生成状态不能证明模型已收到。 |
| Completed ≠ External Model Answered | 本地结束不能证明外部回答成功。 |
| Pre-consumption Revoke ≠ Post-consumption Recall | 消费前可撤销未消费 grant；不能远程追回已披露文本或保证模型删除。 |

## 5. 演示结束时可以说什么

- 用户侧 Local Memory 可以独立于目标模型存在。
- 同一用户侧 Memory 可以在针对新模型重新授权后，人工提供给不同模型。
- 用户可以选择具体 Memory 范围，授权绑定模型、用途、问题和 Context snapshot。
- Approve、Consume、External Disclosure 是不同阶段。
- 已实现的 append-only correction/evolution 保留历史，并支持查询当前有效状态；本脚本展示 evolution，不宣称本次重新测试了 correction。
- v0.1 已通过既有人工 Acceptance 验证最小 Personal Continuity / Model Portability 流程。仅执行本脚本的 ChatGPT 单模型流程，不构成新的双模型验证；既有依据是 Acceptance 001–004，不扩大其范围。

## 6. 演示结束时不能声称什么

本 Demo 不证明或不代表已完成：

- 自动跨模型同步或自动模型 API 集成；
- 通用模型兼容性、云端同步或多用户系统；
- 完整人格模型、数字人或 AGI；
- 区块链 / Web3 能力；
- 密码学安全、安全认证或渗透测试通过；
- 远程模型删除数据或不留存数据；
- 外部模型一定遵守 Context 中的声明；
- 完整商业产品已经完成。

## 7. Freeze 边界

本脚本属于冻结后的演示/发布卫生文档，不修改 YueYun Demo v0.1 功能，不改变 FEATURE FROZEN 状态，不把隔离 Demo Runtime 定义为新产品版本，也不改变任何 Acceptance 结论。编写脚本不等于执行演示。

## 8. 30 秒演示总结

“YueYun v0.1 把人的长期信息与具体模型分离：Memory 保留在用户侧，用户决定为哪个任务选择哪些信息、授权给哪个模型。同一本地数据可以重新授权给不同模型使用。当前通过人工 Context 传递验证最小连续性闭环，没有实现自动跨模型网络，也不代表完整产品已经完成。”
