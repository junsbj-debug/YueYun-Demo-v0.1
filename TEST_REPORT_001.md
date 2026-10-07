# YueYun Demo v0.1 — Cross-Model Continuity Test #001

**Historical Validation Record**

本文保留特定时间点的人工实验事实与原结论，不代表当前完整产品状态，也不构成自动化测试、安全认证、渗透测试或密码学证明。文中“当前”按相应实验发生时理解；项目当前状态以 `README.md`、`SPEC.md`、`DESIGN.md` 和 `FEATURE_FREEZE_v0.1.md` 为准。

测试日期：2026-10-05

本地证据链接说明：本报告第 2 节的 Memory JSON 链接及第 4 节的两份 authorization JSON 链接，共三个链接，属于本地历史实验环境中的证据引用。运行数据目录在公开仓库中默认排除，因此公开版本中这些链接可能不可用；这不改变历史实验记录，也不表示重新生成或伪造证据。不得为补全公开链接而将这些 JSON 复制到文档、examples 或其他公开目录，亦不将完整 Memory / authorization / Context 内容嵌入报告。本次仅补充此说明，不改写原实验事实或结论。

## 1. Test Objective

验证同一份 YueYun 本地长期记忆，在不绑定具体模型的情况下，能否经过两次独立用户授权，被两个不同厂商的 AI 模型分别使用，而无需用户重新输入原始记忆事实。

本次采用人工复制 Context 的方式，不通过模型 API。结果仅适用于本次虚构数据、固定问题和人工操作范围。

## 2. Test Memory

以下字段从现有本地 JSON 核实。本记录明确属于 **fictional test data（虚构测试数据）**，不是真实个人数据。

| 字段 | 实际值 |
| --- | --- |
| Memory ID | `138e5271-ba21-476e-9808-1c1a554d11fe` |
| source | `fictional test / explicitly confirmed` |
| tags | `["fictional", "阅读"]` |
| created_at | `2026-10-05T14:03:44.087580+00:00` |
| user_confirmed | `true` |
| content | `虚构测试数据：小星喜欢在周六阅读科幻小说。` |

记忆中的事实为：小星喜欢在周六阅读科幻小说。JSON 原文保留了“虚构测试数据：”前缀。

证据文件：[Memory JSON](data/memories/138e5271-ba21-476e-9808-1c1a554d11fe.json)。时间字段按原始 JSON 记录，`+00:00` 表示 UTC。

## 3. Test Question

根据你获得的授权上下文，小星周六喜欢做什么？

## 4. Authorization

以下内容从本次实验的两份 authorization audit JSON 核实。

| 字段 | Model-A | Model-B |
| --- | --- | --- |
| authorization_id | `8b26c4c5-ded5-4e8c-9618-2f9366e55e53` | `83a779c0-a410-4f9c-8663-3c3d9655d106` |
| target_model | `Model-A` | `Model-B` |
| purpose | `YueYun v0.1 cross-model continuity experiment` | `YueYun v0.1 cross-model continuity experiment` |
| selected_memory_ids | `["138e5271-ba21-476e-9808-1c1a554d11fe"]` | `["138e5271-ba21-476e-9808-1c1a554d11fe"]` |
| user_approved | `true` | `true` |
| decision / status | `approved` | `approved` |
| created_at | `2026-10-05T14:44:00.100545+00:00` | `2026-10-05T14:44:00.105561+00:00` |

两次授权是独立的新请求：授权 ID 不同，分别指向 Model-A 和 Model-B，并各有独立的批准记录。Model-B 未继承 Model-A 的批准。

两份审计记录中的 `user_question` 均与第 3 节一致，`context_preview` 均包含同一 Memory 的 ID、来源、时间、标签和内容；除 `Target model` 行外，两份预览文本一致。

证据文件：[Model-A authorization JSON](data/authorizations/8b26c4c5-ded5-4e8c-9618-2f9366e55e53.json) 与 [Model-B authorization JSON](data/authorizations/83a779c0-a410-4f9c-8663-3c3d9655d106.json)。审计证明本地批准与预览内容，不单独证明远程模型已收到或处理了上下文。

## 5. Actual External Models

根据项目负责人提供的人工测试记录：

- Model-A：OpenAI ChatGPT。
- Model-B：Anthropic Claude。

本地授权记录使用的是 Model-A / Model-B 标识；与外部产品的对应关系来自用户的人工测试说明。本次没有可靠证据证明具体底层模型版本，因此不记录或声称已验证具体版本。

## 6. Observed Results

外部测试由用户人工完成。以下回答及“没有要求重新输入事实”的观察来自用户提供的实验结果，不是本地程序模拟的模型回复。

ChatGPT 根据 Model-A 授权 Context 正确回答：

> 小星喜欢在周六阅读科幻小说。

Claude 根据 Model-B 授权 Context 正确回答：

> 根据你提供的授权上下文，小星周六喜欢阅读科幻小说。

两个外部模型均没有要求用户重新输入原始记忆事实。用户提供的是从本地 Memory 生成的已授权 Context，而非重新录入记忆事实。

## 7. Result

**PASS**

本次单条虚构记忆的人工跨厂商连续性实验通过。此结果不等于全部 v0.1 工程目标或直接 API 跨模型验收已经完成。

## 8. What This Test Demonstrates

本次实验验证了 v0.1 的最小跨模型连续性链路：

`Local Memory → Retrieval → Explicit Authorization → Context Export → Model-A / Model-B`

同一份本地 Memory 可以在针对不同目标模型分别授权后，被不同厂商模型使用。此结论依据本地记忆与授权快照，以及用户报告的人工外部测试结果；范围限于本次问题和数据。

## 9. What This Test Does NOT Demonstrate

本次实验尚未证明：

- 完整人格连续性。
- 自动跨模型迁移。
- 模型 API 集成。
- 加密或安全存储。
- 多用户系统。
- 大规模 Memory 检索能力。
- 长期稳定性。
- 模型是否真正删除或不保留已经发送到远程服务的数据。
- 生产环境安全性。

Context 中的权限说明表达用户授权边界，不能据此证明远程服务的数据保留行为。

## 10. Evidence / Reproducibility

- 本地 Memory ID：`138e5271-ba21-476e-9808-1c1a554d11fe`。
- Model-A authorization ID：`8b26c4c5-ded5-4e8c-9618-2f9366e55e53`。
- Model-B authorization ID：`83a779c0-a410-4f9c-8663-3c3d9655d106`。
- 两份 Context 来自同一 Memory，两次授权分别针对 Model-A / Model-B。
- 本地流程使用“小星”“周六”检索，只选择上述必要记忆，分别生成预览、批准并导出；两份实际预览保存在对应授权 JSON 的 `context_preview` 字段中。
- 外部模型回答由用户人工完成，并由用户向项目提供观察结果。本报告没有自行调用、重测或模拟外部模型。
- 项目文件清单中未发现 ChatGPT / Claude 截图文件；不提供虚构截图路径。

External model responses were manually observed by the user; screenshots were not stored in the project at the time this report was created.

复现实验时，应使用相同本地 Memory、问题和用途，为每个目标模型分别创建新的请求、预览并明确批准，再进行一次性 Context Export。历史 audit JSON 用于核对，不能复用为新的导出许可。外部测试仍需用户实际完成并记录结果，不保证再次运行的回答措辞完全相同。

Conclusion: The model changed; the authorized local memory source remained the same.
