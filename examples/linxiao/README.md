# 林晓 — Fictional Demo Persona

林晓是完全虚构的 Demo Persona，不对应真实个人。这 8 条 fictional demo data 只用于 YueYun Demo / GitHub 示例，已由项目负责人明确确认用于此用途。

## Memory 编号与 identity

D01–D08 仅为文档展示编号；真实 Memory identity 使用 UUID，每条采用现有 schema_version = 1，独立 UTF-8 JSON，文件名与 id 一致。created_at 是本轮实际编制时间，不是事实生效日期。

| 展示编号 | Memory UUID / 文件 | 主题 |
| --- | --- | --- |
| D01 | [dc19f663-9edb-4e4b-83c1-54cdb1c395a7](memories/dc19f663-9edb-4e4b-83c1-54cdb1c395a7.json) | 咖啡偏好 |
| D02 | [bef9b0e4-a478-4dfa-bad0-6aabe9fa821c](memories/bef9b0e4-a478-4dfa-bad0-6aabe9fa821c.json) | 周末游泳 |
| D03 | [1cfd7910-ae8e-4d05-9203-fe5276a76da8](memories/1cfd7910-ae8e-4d05-9203-fe5276a76da8.json) | 日语学习目标 |
| D04 | [57b57f6d-d6c0-47d7-8bd8-09d8d5f19e11](memories/57b57f6d-d6c0-47d7-8bd8-09d8d5f19e11.json) | 电子产品购买偏好 |
| D05 | [e2fc41a6-17c1-43b1-a1c7-739f8d4633d0](memories/e2fc41a6-17c1-43b1-a1c7-739f8d4633d0.json) | 京都旅行原计划 |
| D06 | [dadea39c-b4eb-4700-9c7a-7e8a71ed0dfa](memories/dadea39c-b4eb-4700-9c7a-7e8a71ed0dfa.json) | 旅行行程偏好 |
| D07 | [90b5affd-e0ec-44ed-931d-d80f25a02e0f](memories/90b5affd-e0ec-44ed-931d-d80f25a02e0f.json) | 京都旅行计划变更 |
| D08 | [4ec7f719-669e-4680-b1af-6e4bdb93e666](memories/4ec7f719-669e-4680-b1af-6e4bdb93e666.json) | AI 表达偏好 |

## D05 → D07：append-only Evolution

- D05：effective_from = 2026-09-20；计划于 2026-11-08 去京都。
- D07：effective_from = 2026-09-28；当前计划更新为 2026-11-15，原计划日期为 2026-11-08。
- D07 使用新的 UUID，relationship_type = evolution，previous_memory_id = e2fc41a6-17c1-43b1-a1c7-739f8d4633d0，引用 D05。D07 的生效日期晚于 D05；两个 JSON 均保留，D07 不覆盖或删除 D05。

这表示计划在后来发生真实变化，不表示 D05 原记录有误。effective_from 表示该 Memory 事实从什么时候开始生效，不是旅行发生日期。按现有 Retrieval 语义，D05 的计划状态在 2026-09-20 至 2026-09-28（不含截止日）有效，D07 从 2026-09-28 起有效；截止日期由 Retrieval 派生，fixture 不保存 effective_until 或 status。

## 发布与运行边界

- 当前 v0.1 runtime 固定读取 data/memories/，不会自动读取 examples/。
- 本目录为独立静态示例，不属于冻结的 7 条 Memory / 64 条 authorization-revoke runtime 与 Acceptance 数据基线；不改变已有验收证据。
- 本目录不包含任何 authorization / revoke fixture，不提供或恢复 grant。
- 没有新增 fixture import/load 功能、导入按钮或 runtime 行为。静态文件发布不等于当前 UI 已加载林晓数据，也不代表执行了新的功能验收。
- 本套数据的发布属于 FEATURE FROZEN 后的发布/文档卫生，不扩张 v0.1 功能范围。
