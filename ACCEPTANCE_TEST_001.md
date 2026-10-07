# YueYun Demo v0.1 — Manual Cross-Model Continuity Test 001

## 1. 实验信息与目标

- 测试日期：2026-10-06。
- 测试方式：用户实际人工操作 YueYun，并将导出的 Context 人工复制提供给 ChatGPT 与 Claude。
- 总体结果：**PASS**（限定于本次单条虚构 Memory、两个外部模型的人工验证范围）。

验证同一份用户侧本地 Memory 能否在无需重新录入原始 Memory 内容的情况下，经针对不同目标模型和具体用途的独立明确授权，被不同模型理解并用于回答。

本记录依据项目负责人本次人工确认的操作与观察结果编写；外部模型回答不是程序自动采集，本轮未重新运行实验。SPEC.md §2.1、§2.3、§4 与 DESIGN.md §6.2、§7 提供验收口径和权限边界；README.md 标明项目是个人数字连续性系统的工程原型。文档及代码定义本身不替代人工实验依据。

## 2. 测试数据与共同条件

| 项目 | 内容 |
| --- | --- |
| 数据性质 | fictional test data，不是真实个人数据 |
| 测试事实 | 小星喜欢在周日游泳。 |
| 本地 Memory ID | `81bdeea8-1e58-420a-988a-76255948745e` |
| Purpose | 回答当前问题 |
| Current question | 小星周日喜欢做什么？ |
| Context 传递方式 | 用户人工复制并提供给外部模型；YueYun 未自动调用模型 API |

两组使用同一个本地 Memory ID、相同问题和用途，目标模型与本次独立授权不同。Memory ID 及实验事实由项目负责人提供；本记录未补写未核实的授权 ID、Run ID、精确操作时间、截图编号或具体底层模型版本。

## 3. 与实验相关的状态边界

现有 Runtime 的正常本地流程为：

`Preparing → Awaiting Decision → Approved-Unconsumed → Context Ready → Completed`

其中，Preparing 用于形成草稿；Awaiting Decision 对应尚未批准的授权预览；Approved-Unconsumed 表示已批准但尚未消费；Context Ready 表示 Context 已生成，Permission 的本次授权已消费。Completed 只表示本地 Run 结束，不表示外部模型已收到 Context 或回答成功。本次记录没有据此推定两组均执行了 Completed 操作。

Permission 是唯一授权边界，每次授权绑定目标模型、用途、当前问题、用户选择的 Memory IDs 及批准快照。Manual Adapter 通过 Permission 消费真实批准对象，不自行读取 Memory、扩大选择或自动发送。授权审计是历史记录，不是恢复权限的凭证；服务重启后旧运行时 grant 不恢复。

`Approve ≠ Generate Context ≠ Send to model`

上述内容用于解释本次实验流程，不表示本实验重新验收了所有生命周期分支、重启行为或撤销能力。

## 4. A 组：ChatGPT

### 操作过程

1. 从 YueYun 本地 Memory 检索测试记录。
2. 用户选择该 Memory。
3. 设置 Target model 为 `chatgpt`，Purpose 为“回答当前问题”，Current question 为“小星周日喜欢做什么？”。
4. 用户查看授权预览后明确授权。
5. YueYun 生成授权 Context，本次授权被消费。
6. 用户人工将生成的 Context 提供给 ChatGPT。

### 人工观察结果

ChatGPT 根据该 Context 回答：

> 小星喜欢在周日游泳

ChatGPT 同时明确说明该信息来自本次明确授权的 YueYun 本地记忆，不自动保存为 ChatGPT 长期记忆。

这里记录的是用户观察到的模型回答与声明，不能据此证明远程服务端不保留数据、没有建立长期记忆或已经删除数据。

**A 组结果：PASS。**

## 5. B 组：Claude

### 操作过程

1. 使用同一个 YueYun 本地 Memory，没有重新录入原始 Memory 内容。
2. 没有复用 ChatGPT 的授权，为 Claude 创建新的独立授权。
3. 设置 Target model 为 `claude`，Purpose 为“回答当前问题”，Current question 为“小星周日喜欢做什么？”。
4. 用户明确授权后重新生成 Context，本次 Claude 授权被消费。
5. 用户人工将 Context 提供给 Claude。

### 人工观察结果

Claude 根据该 Context 回答：

> 小星周日喜欢游泳

Claude 同时识别该记录属于虚构测试数据。

**B 组结果：PASS。**

## 6. 已验证的结论

| 验证项 | 本次结果与依据 |
| --- | --- |
| 同一本地 Memory 可用于不同模型 | PASS：两组均使用同一个 Memory ID，分别正确回答周日游泳事实。 |
| 更换模型无需重新输入原始 Memory 内容 | PASS：Claude 使用同一用户侧记录，经新的 Context 获得信息。 |
| 模型授权相互独立 | PASS：ChatGPT 与 Claude 分别明确授权，没有复用前一模型的批准。 |
| 已消费授权不能直接作为第二模型的授权复用 | PASS：本次按现有一次性授权与模型绑定边界，为 Claude 新建独立授权；本实验未另外执行恶意重放攻击测试。 |
| 两个模型理解授权 Context | PASS：ChatGPT 与 Claude 均根据所提供 Context 正确回答。 |
| 人工 Model Portability / Personal Continuity 最小闭环 | PASS：本地数据、用户选择、独立授权、Context 导出及实际外部模型使用已经连接。 |

本次实际运行链路为：

`Local Memory → Retrieval → User Selection → Authorization Preview → Explicit Authorization → Context Export / Consume → Manual Provision → ChatGPT / Claude`

数据源始终是 YueYun 用户侧本地 Memory；本实验不是把一个模型的内部记忆传输给另一个模型，也不要求两个模型共享 Memory。

## 7. 尚未验证与结论限制

- 尚未实现模型 API 自动调用或自动模型切换；本次是人工复制 Context 的双模型实验。
- 尚未验证大规模 Memory 或长期运行稳定性。
- 尚未验证加密、DID、云同步或多用户能力。
- 尚未证明所有模型都兼容，仅覆盖本次实际使用的 ChatGPT 和 Claude；没有可靠证据确认具体底层模型版本。
- 外部模型关于信息来源、长期记忆或虚构性质的回答，不构成远程服务端存储、保留、删除或遗忘行为的验证。
- 本次记录不宣称远程撤回能力、生产级安全保证，或完整的跨平台 Personal AI 基础设施已经实现。
- 本次 PASS 仅代表上述人工最小闭环通过，不表示 YueYun Demo v0.1 Final 已完成或完整产品已完成。

## 8. Acceptance Conclusion

**PASS。** 本次实验支持 YueYun Demo v0.1 的核心假设：个人连续性数据可以独立于具体模型保存在用户侧，并在用户针对具体目标模型和具体用途明确授权后，被不同模型重新使用。

模型可以更换，而本次获授权的信息来源保持为同一份 YueYun 本地 Memory。该结论限定于本次已人工观察的单条虚构数据、独立授权和双模型 Context 使用，不扩展为自动迁移或完整产品能力。
