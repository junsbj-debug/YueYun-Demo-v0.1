# YueYun Demo v0.1 — Demo Record 001

- 日期：2026-10-06
- 类型：Manual Personal Continuity / External Disclosure Demonstration
- 环境：用户自行指定的隔离 Demo Runtime 目录，与冻结源项目目录分离。

## 1. 演示目标与数据

本次记录依据项目负责人提供的实际人工操作和观察，以及此前演示后只读核验。编写记录时不重新运行实验，不模拟外部模型回答。

使用林晓 Fictional Demo Persona 的两条本地 Memory：

| Memory ID | 本次使用的信息 |
| --- | --- |
| 90b5affd-e0ec-44ed-931d-d80f25a02e0f | 当前京都旅行日期为 2026-11-15；由原计划 2026-11-08 经 evolution 演化而来，effective_from 为 2026-09-28。 |
| dadea39c-b4eb-4700-9c7a-7e8a71ed0dfa | 不喜欢把旅行行程安排得太满，希望每天留出自由时间。 |

两条均为明确标记的 fictional demo data，不对应真实个人。Evolution 关系用于表达当前计划状态，不表示自动授权前序 Memory 或把前序完整内容加入 Context。

- Target model：chatgpt
- Purpose：规划京都旅行
- User question：请根据我的计划和旅行偏好，帮我安排京都旅行。

## 2. 本地 Runtime 流程与人工外部操作

项目负责人实际观察的本地状态路径：

`Preparing → Awaiting Decision → Approved-Unconsumed → Context Ready → Completed`

1. 用户检索到相关 Memory。
2. 用户人工选择上述两条 Memory，并填写目标模型、用途和问题。
3. 用户查看授权 Preview，Runtime 进入 Awaiting Decision。
4. 用户明确点击授权，Runtime 进入 Approved-Unconsumed。
5. 用户主动生成 Context，流程经 Adapter / Permission 消费一次性授权，页面进入 Context Ready。
6. 用户人工复制 Context。
7. 用户在 YueYun 之外人工粘贴给 ChatGPT。
8. 用户观察到 ChatGPT 根据 Context 返回京都旅行规划回答，利用当前旅行日期和旅行偏好。
9. 用户随后结束本地 Run，Runtime 进入 Completed。

上述状态变化、复制、外部粘贴和回答来自项目负责人的 manual observation，不是本次编写记录时自动采集的结果。没有提供回答全文，故不补写行程细节、回答原文、截图编号或具体底层模型版本。

## 3. 系统可核验证据

此前演示后只读核验确认：

- Demo Runtime Memory：8。
- Authorization audit：1。
- Audit 文件：data/authorizations/f78ae839-ca9c-43ab-83a6-e95440b0750a.json。
- Target model：chatgpt。
- Purpose：规划京都旅行。
- Status：approved。
- User_approved：true。
- Selected Memory IDs：90b5affd-e0ec-44ed-931d-d80f25a02e0f、dadea39c-b4eb-4700-9c7a-7e8a71ed0dfa。
- 8 条初始 fixture 均仍存在，内容、哈希及 mtime 与复制来源基线一致。

该 authorization audit 保存的是历史授权决定及预览/Memory 状态快照，不是当前可用 grant 的凭证。本记录不嵌入完整 Context、authorization preview 或 Memory snapshot。

上述 audit 文件引用属于本地运行证据；公开仓库不提供对应的 runtime audit JSON，因此公开版本中无法直接复查该本地文件。不得为了修补公开证据链接而复制、重建或伪造 runtime JSON。此限制不改变原实验事实、人工观察或证据边界。

## 4. 证据边界

| 证据来源 | 能够支持的事实 | 不能单独证明的事实 |
| --- | --- | --- |
| Authorization audit | 用户批准过本次授权、目标模型、用途、所选 Memory 范围、授权预览快照 | Consume 已发生、Context 已生成或复制、Context 已发送给 ChatGPT、ChatGPT 已收到或回答 |
| 用户观察的 Context Ready | 本地 Runtime 已进入 Context 生成后的状态 | 外部模型已经收到 Context |
| 用户观察的 Completed | 本地 Run 已结束 | 外部模型已经接收或回答成功 |
| Manual observation | 用户复制、人工粘贴给 ChatGPT，并实际观察到规划回答 | 远程服务端的数据存储、删除、保留或其他内部处理行为 |

Audit 中的 approved 是历史批准状态，不能独立判断授权是否已经被消费。当前没有单独的持久化 Consume / External Disclosure 事件可用于证明上述外部流程。不得把人工观察表述成 authorization audit 能够独立证明的系统事实。

本次必须区分：

- `Memory ≠ Permission`
- `Approve ≠ Consume`
- `Consume ≠ External Disclosure`
- `Context Ready ≠ External Model Received`
- `Completed ≠ External Model Answered`

## 5. 本次演示支持的结论与限制

在 YueYun Demo v0.1 的人工流程中，两条由用户控制的本地 Memory——一条当前旅行计划及其 evolution 状态、一条独立旅行偏好——经过明确选择和一次性授权后，被组合为面向指定模型和指定用途的 Context。用户随后人工将该 Context 提供给 ChatGPT，并观察到 ChatGPT 根据当前有效旅行日期和旅行偏好生成相应回答。

本次是人工 Context 传递演示，不证明自动跨模型通信、API 集成、远程模型数据处理行为、安全认证或通用模型兼容性。人工观察不等于网络抓包、渗透测试或密码学证明。

## 6. 隔离性核验

依据此前演示后只读核验：

- 冻结源项目目录保持 Memory / authorization 为 7 / 64。
- 原 71 个 runtime JSON 的哈希与 mtime 保持保存的基线。
- 未发现 Demo Runtime 写回源项目；源项目现有文件未新增、删除或发生哈希/mtime 变化。
- Demo Runtime 的 6 个 Python 文件与 UI 文件哈希仍与冻结源项目一致。
- 本次演示未修改 8 条 fixture Memory；新增的授权审计仅位于隔离 Demo Runtime。

## 7. Freeze 边界

本记录属于冻结后演示证据记录，不修改 YueYun Demo v0.1 功能，不改变 FEATURE FROZEN 状态，也不把隔离 Demo Runtime 视为新的产品版本。

本轮仅编写记录，不访问 localhost/UI，不执行项目 Python、功能测试、Git、网络或安装依赖，不修改已有文件和运行数据，也不停止 Demo Runtime 服务。
