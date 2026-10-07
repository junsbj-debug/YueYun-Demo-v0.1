# YueYun Demo v0.1 技术设计

项目启动日期：2026-10-05

本设计以 `SPEC.md` 为工程目标依据，整理已批准的技术方案与项目决定。初次编写时文中目录、模块和行为均为后续实现规划；规划本身不构成实现或验收证据。

规格收口决定（2026-10-06）：依据阶段性 Acceptance Review 与现有人工实验记录，`YueYun Demo v0.1 Core PoC` 已达到核心概念验证完成，状态为 `PASS`；这不等于 v0.1 Final 已封版或完整产品完成。以下修订统一当前验收口径，保留后续候选规划。

当前状态为 `YueYun Demo v0.1 — FEATURE FROZEN`，依据见 [FEATURE_FREEZE_v0.1.md](FEATURE_FREEZE_v0.1.md)（2026-10-06）。Feature Freeze 仅锁定最小工程研究原型功能范围，不等于产品 Final Release、安全认证或已经公开发布。当前实现、人工 Acceptance evidence、Current Limitations 与 Future Work / Planned 继续分别标明；文档同步不新增功能。

## 1. 目标与工程原则

只服务于最小“个人数字连续体”闭环的三个验证目标：跨模型迁移、本地长期记忆、身份与权限边界，不扩展为完整产品。

坚持 Local-First、简单、可理解、可验证、可迁移、尽量少依赖。优先 Windows 11 本地运行，并让非程序员用户能够方便启动和演示。

## 2. 已确认的项目决定

1. 采用 Python、本机浏览器 UI、JSON 本地存储和关键词/标签检索。
2. v0.1 首先实现手动模型适配器，以最低复杂度验证闭环。
3. 早期决定曾将手动适配器限定为第一阶段、不作为最终跨模型验收；该验收口径现已调整：v0.1 接受实际完成的 manual cross-model validation。至少两个不同实际模型须分别经过独立授权，使用同一份 YueYun 本地 Memory 并正确利用该信息，不要求 API 自动调用或自动模型切换。直接 API Adapter 保留为核心闭环稳定后的候选评估，不属于 v0.1 Core PoC 必需条件。
4. 模型回复不得自动写入长期记忆，只有用户明确确认后才允许成为长期记忆。
5. 开发和首轮验证只使用虚构数据，不读取或导入真实个人数据。
6. 当前接受单用户、明文 JSON 和预装 Python。

## 3. 运行方式与界面

- Python 后端优先使用标准库，不引入前端框架、复杂数据库或模型开发框架。
- 使用简单 HTML、CSS 和 JavaScript 构成本机浏览器界面。
- 本机网页服务仅监听 `127.0.0.1`，不提供局域网或公网访问。
- 未来提供 `启动 YueYun.cmd`，用户双击后启动程序并自动打开浏览器，不要求手动输入命令。
- 当前界面可结束/取消本地 Run，不停止后台服务；服务通过启动终端 Ctrl+C 停止。关闭浏览器不等于停止服务或可靠 Revoke。自动打开浏览器、双击启动及程序打包仍属 Future Work / Planned。
- 首版使用预装 Python；独立程序打包在闭环验证后再评估。
- 本地服务需要检查请求来源，并对写入、授权和退出等操作做最小请求校验，避免其他网页代替用户触发操作。

### 3.1 当前实际架构（Current Implementation Architecture）

| 文件 | 当前职责 |
| --- | --- |
| `memory_store.py` | 确认保存、读取和 append-only Correction / Evolution，Memory 是用户侧本地数据。 |
| `retrieval.py` | 关键词匹配与显式 current / historical / evolution / audit 状态推导。 |
| `permissions.py` | 唯一授权边界；真实请求/grant、快照、决定、撤销、失效和消费。 |
| `model_adapters.py` | Manual Context Adapter；经 Permission 消费批准对象并返回纯文本。 |
| `runtime.py` | 本地 Run state machine；草稿、元数据、事件摘要与模块协调。 |
| `app.py` | 标准库 HTTP 服务，监听 `127.0.0.1:8765`，连接页面与模块。 |
| `ui/index.html` | 单页浏览器 UI，JavaScript / CSS 内嵌。 |

获准路径为 `Local Memory → Retrieval → User Selection → Permission Preview → Explicit Decision → Approved Grant → Adapter Consume → Local Context`。拒绝、撤销或失效不继续进入获准路径；Local Context 不自动等于 External Model Delivery。

### 3.2 当前 Runtime 层

Runtime 管理一次内存 Run，保存 `run_id`、创建时间、问题/模型/用途草稿、查询元数据、候选与所选 Memory IDs、authorization ID 引用、状态、事件摘要及可选错误。它不复制完整 Memory、不持久化完整 Context，不是 Memory owner、Permission authority 的替代品、外部模型状态跟踪器或云端 orchestration service。

Runtime 持有 Permission 返回的真实请求/批准对象引用，不序列化或恢复它们。真实性仍由 `permissions.py` 负责，`run_id` / `authorization_id` / audit JSON 均不是 grant。生成经过 Adapter；撤销与失效经过 Permission。

`Preparing → Awaiting Decision → Approved-Unconsumed → Context Ready → Completed` 是正常本地路径；终止状态为 `Denied / Revoked / Invalidated / Cancelled / Error`。Preparing 且尚无真实 Permission 绑定时，输入变化只更新草稿；建立绑定后，相关输入或 Memory 状态变化使旧权限失效，不自动替换或扩大选择。

Context Ready 表示 Permission 一次性消费成功、本地 Context 已生成，不表示已发送。用户在 Context Ready 后结束 Run 为 Completed，不表示外部模型已收到或回答；此前结束为 Cancelled。终止仍持有 pending / approved-unconsumed 权限的流程时调用 Permission 失效机制。服务重启后 Run 与旧 grant 均不恢复。

## 4. 本地数据设计

采用 UTF-8 JSON，以简单、公开、可直接查看的格式保存数据。每条记忆一个文件，每次授权决定一个审计文件；撤销成功后另行追加独立撤销事件，不修改原批准记录。

| 数据 | 最小内容 |
| --- | --- |
| 用户资料（Planned，当前没有独立资料文件） | 本地用户标识、显示名称 |
| 记忆记录（Current） | 格式版本、记录标识、内容、标签、来源、用户确认状态、记录时间；关系记录增加 relationship_type、previous_memory_id、effective_from |
| 模型配置（Planned，当前目标模型为请求文本输入） | 模型标识、显示名称、连接方式 |
| 授权记录 | 格式版本、授权标识、目标模型、用途、当前问题、选中记忆标识、当时的完整上下文预览与 Memory 状态快照、决定时间、批准/拒绝决定；撤销事件单独记录状态转换，不重复保存完整 Memory 内容 |

- 本地个人连续性数据独立于模型，不保存供应商专用对象作为记忆主体，不依赖模型会话编号。
- `data` 是可迁移的数据目录；在程序停止时复制整个目录，可作为最小备份和迁移方式。
- 更换模型不要求重建或重新录入记忆。
- 首版以新增、查看和检索为主，避免覆盖现有记录；写入失败应明确提示，不能显示为保存成功。
- 模型回复保存流程仍属 Planned：若未来提供，必须走内容预览和明确保存并记录模型来源。当前没有模型回复接收/入库界面，也不自动保存回复。
- 早期首版暂缓编辑、删除记忆；最小 append-only Correction / Evolution 已实现，并已完成与 Permission 的回归验证；不据此单独宣布 v0.1 Final 整体验收完成。删除及复杂 Memory 管理继续暂缓。原记录保留，覆盖或删除须遵守破坏性操作批准边界。
- 明文 JSON 不提供加密保护；首版依赖当前 Windows 用户的文件访问权限，不宣称具有进程间安全隔离。
- 如后续接入 API，密钥不能进入记忆、授权上下文或普通日志；密钥保存方式在 API 阶段另行确定。

### 4.1 当前 Memory lifecycle architecture

- 更新由用户明确选择 `relationship_type = correction / evolution`，以新 ID 和 JSON 指向 `previous_memory_id`；历史通过新记录 + relationship 建立，不原地覆盖旧事实。
- Correction 表示旧记录原本错误，继承前序 `effective_from`，未知则保持未知；旧错误记录仅供 audit，不作为当前或历史真实事实。
- Evolution 表示状态变化，必须由用户提供 YYYY-MM-DD 生效日期；前序日期明确时，新日期必须更晚，旧状态仍可作为其有效时期的历史事实。
- Retrieval 从关系链及后继有效状态的生效日期派生 `effective_until`，不把截止日期写回旧 JSON；区间开始日包含、截止日不包含。
- current 默认本地当天，historical 必须明确查询日期并排除无生效日期的事实；evolution 展示链，audit 展示所有记录及派生状态，不自动选择或授权。损坏关系 fail closed，不自动修复。
- Permission 只处理明确所选的合格事实并绑定状态快照；前序 ID 可作为元数据，但不自动附带前序内容或授权整条链。

这些属于当前实现与既有回归范围，不将四份正式人工 Acceptance 扩大解释为全部 lifecycle 测试。

## 5. 检索与上下文准备

首版使用关键词和标签检索，不采用向量数据库、嵌入模型或语义检索框架。

流程：用户输入一个或多个关键词 → 匹配记忆内容和标签 → 展示原文、来源与记录时间 → 用户勾选记录 → 生成上下文预览。

当前中文采用文本包含匹配，英文大小写不敏感，多关键词为任一命中（OR），检索 content / tags 并返回命中解释。规则可能遗漏同义表达，不承诺自动理解所有自然语言问题。没有匹配结果时明确显示，不编造记忆。

上下文使用供应商无关纯文本，包含用户问题、所选记忆及必要状态元数据，不采用供应商专用消息格式；本次授权仍绑定目标模型。记忆内容作为资料使用，不作为程序执行指令。

## 6. 模型适配层

### 6.1 统一边界

当前上下文准备与模型连接分离：`model_adapters.py` 是 Manual Context Adapter，接收 Permission 返回的真实批准对象及用户问题，可核对模型、用途和所选 IDs；触发一次性 Consume，返回原批准快照的纯文本 Context 或错误，不返回模型回答，不自动调用 ChatGPT / Claude。

Future Work / Planned：未来统一 API Adapter 可接收获准请求并返回模型回复或执行错误；该通用 API 接口当前未实现，候选规划保留在第 6.3 节。

适配器不能直接读取全部记忆目录，也不能写入长期记忆或扩大授权范围。更换适配器不改变本地记忆格式。

### 6.2 第一阶段：手动适配器

1. 用户选择相关记忆，填写目标模型、用途和当前问题。
2. 用户查看完整授权预览后明确批准或拒绝；批准后处于 Approved-Unconsumed，可主动撤销。
3. 用户主动生成 Context 时，手动适配器消费一次 Permission 层批准的授权快照，提供可复制的最终文本；用户再手工复制、粘贴至目标模型。消费后不能再次生成，也不能再撤销。
4. 用户在外部模型会话查看回复；当前 YueYun 不接收模型回答，回复保存界面尚未实现，任何未来保存仍须明确确认。

手动适配器不自动发送网络请求。授权记录只能反映本地批准和上下文提供情况，不能据此声称外部模型已收到文本或完成调用。程序不能控制用户将复制文本粘贴到何处。

该阶段验证持久化、检索、上下文准备和授权流程。按当前收口决定，实际完成的 manual cross-model validation 可作为 v0.1 Model Portability / Cross-Model Continuity 验收：至少两个不同实际模型分别独立授权，并正确利用同一本地 Memory。现有 ChatGPT、Claude 人工实验已满足该条件，当前正式索引见第 9 节；`TEST_REPORT_001.md`、`TEST_REPORT_v0.1.md` 保留为历史资料。Core PoC 为 `PASS`；仅导出文本或模拟使用方仍不足以通过，且不宣称完整产品完成。

### 6.3 后续评估：直接 API Adapter

核心闭环稳定后，评估至少两个模型的直接 API 接入，让用户在应用内切换模型，并使用同一份本地个人连续性数据。

- 在统一接口下分别实现供应商适配，不把供应商协议渗透到记忆存储。
- 每次调用先确认目标模型、用途和确切上下文；切换目标模型需要相应授权。
- 只有通过授权检查的上下文才能发送；失败时明确显示，不将失败记录为成功。
- 模型回复仅显示，不自动入库；用户明确确认后才可成为长期记忆。
- 接入哪些模型、凭据管理、调用费用、网络行为及是否需要额外依赖，在未来该阶段评估后确定，不属于当前实现或本次文档同步范围。

跨模型验收状态必须依据实际验证证据记录；已完成的双模型人工验证可通过当前 v0.1 验收。API 阶段如未实施或未验证，只记录为后续候选未实施，不否定 Core PoC 的 `PASS`，也不将其变成 Core PoC 阻塞项。

## 7. 身份与权限的最小实现

首版只有一个本地用户，不建设注册、登录或复杂身份系统。

- 用户是数据所有者和授权决策者；个人数据由用户控制；模型是上下文使用工具。
- 保存记忆与提供上下文是两个独立动作，分别需要明确的用户确认。
- 授权限于本次操作，绑定目标模型、用途、当前问题、用户选择的 Memory IDs 及批准快照，不提供默认永久授权全部数据。
- 检索结果不会自动发送。取消或拒绝授权时，不开放最终复制操作，也不执行 API 发送。
- 相关输入或 Memory 状态变化后旧授权失效，需要重新选择并授权；不得自动替换 Memory、扩大授权范围或继承旧批准。Current / Historical / Correction / Evolution 与 Permission 已完成回归验证。
- 权限检查由本地程序执行，不能只依赖界面按钮状态或提示词。
- 模型输出不得自行触发数据修改、长期记忆保存或权限变更。
- Permission 阶段已实现并通过最终验收，状态为 `PASS`。生命周期为 `Preview/Pending → Denied`，或 `Preview/Pending → Approved-Unconsumed → Consumed / Revoked / Invalidated`；待决定请求也可失效。终止后的旧请求或授权不能恢复，再次使用必须建立新请求。
- Revoke 在 Permission 层只终止已批准但尚未消费的本地 Context 导出权限，并与 Consume 互斥；一次授权只能消费一次。撤销先终止真实运行时 grant，再追加独立审计事件；审计保存失败也不恢复权限。
- 批准 ≠ 生成 Context ≠ 发送给外部模型。当前 Manual Adapter 不自动调用或发送给模型。已经生成的 Context 无法通过本地 Revoke 远程追回、删除或保证外部模型遗忘，也不能宣称收回用户副本；复杂远程撤销机制不属于 v0.1。
- 授权决定审计和撤销事件只是历史记录，不是权限凭证，不能恢复运行时 grant；原批准记录的 approved 表示历史决定，不代表仍有导出权限。
- 当前一次性授权采用运行时 grant；进程重启后旧 grant 不恢复，需要重新授权，属于 fail-closed 行为。持久化消费账本不是 Core PoC 阻塞项，不宣称已具备跨重启的持久化消费审计。

人工 Acceptance 支持正常 UI 流程中的 `Memory ≠ Permission`、`Approve ≠ Consume`、`Consume ≠ External Disclosure`、`Pre-consumption Revoke ≠ Post-consumption Recall`。Deny 终止本次正常导出路径；已消费 grant 不再表现为未消费的可撤销授权。拒绝决定仍可保存含完整预览的本地审计，不等于本地没有记录。授权语义不构成远程强制执行、密码学保证或安全认证。

## 8. 建议目录规划

**Current actual structure**：当前有 6 个 Python 模块、1 个内嵌 JS/CSS 的 UI 文件、两类数据目录及工程文档；没有独立 profile / models 配置、启动脚本或仓库内 tests 目录。

```text
Demo-v0.1/
├─ memory_store.py / retrieval.py / permissions.py
├─ model_adapters.py / runtime.py / app.py
├─ ui/index.html
├─ data/memories/            # 每条 Memory 一个 JSON
├─ data/authorizations/      # 授权决定和独立 revoke event JSON
└─ 工程文档                 # README、PROJECT_RULES、SPEC、DESIGN、TEST_REPORT、ACCEPTANCE_TEST
```

**Planned / possible future structure**：以下保留早期目录规划，不是已存在文件清单；Future Work 不属于本轮实现，亦不为文档一致性创建缺失目录。

```text
E:\YueYun\Demo-v0.1\
├─ README.md
├─ PROJECT_RULES.md
├─ SPEC.md
├─ DESIGN.md
├─ 启动 YueYun.cmd
├─ app.py                  # 启动与本机网页服务
├─ memory_store.py         # 记忆保存和读取
├─ retrieval.py            # 关键词与标签检索
├─ permissions.py          # 授权检查和记录
├─ model_adapters.py       # 首版手动适配器，后续按需扩展 API
├─ ui\
│  ├─ index.html
│  ├─ style.css
│  └─ app.js
├─ data\
│  ├─ profile.json
│  ├─ models.json
│  ├─ memories\             # 每条记忆一个 JSON 文件
│  └─ authorizations\       # 每次授权一个 JSON 文件
└─ tests\                   # 持久性、检索、授权等关键检查
```

首版保持少量模块；仅在实际实现需要时拆分适配器，不提前搭建插件系统或复杂架构。

## 9. 开发阶段与验证顺序

### 阶段一：最小本地闭环与手动适配器

1. 确定最小 JSON 字段、检索规则和授权状态，使用虚构数据核对。
2. 实现确认保存、查看和重启后读取，验证本地持久性。
3. 实现关键词/标签检索、来源展示和记忆选择，验证结果可核对。
4. 实现上下文预览与本次授权，验证拒绝授权、改变目标或改变上下文时的行为。
5. 实现手动适配器，完成复制上下文和外部模型使用演示；回复必须经用户明确确认才能保存。
6. 双击启动、自动打开浏览器和退出流程保留为后续易用性规划，不作为当前 Core PoC 完成条件。
7. 按 SPEC.md 记录实际验证范围：双模型独立授权的人工验证已通过，Core PoC 为 `PASS`；Permission 阶段已通过最终验收，状态为 `PASS`。最小 append-only Correction / Evolution 已实现，并已完成与 Permission 的回归验证；不据此单独宣布 v0.1 Final 整体验收完成。删除及复杂 Memory 管理继续暂缓。

### 当前正式人工 Acceptance evidence

| 文档（均记录为 PASS） | 实际验收范围 |
| --- | --- |
| [ACCEPTANCE_TEST_001.md](ACCEPTANCE_TEST_001.md) | Manual Cross-Model Portability / independent authorization。 |
| [ACCEPTANCE_TEST_002.md](ACCEPTANCE_TEST_002.md) | Explicit Denial。 |
| [ACCEPTANCE_TEST_003.md](ACCEPTANCE_TEST_003.md) | Pre-Consumption Revoke。 |
| [ACCEPTANCE_TEST_004.md](ACCEPTANCE_TEST_004.md) | Post-Consumption Boundary / Consume ≠ External Disclosure。 |

上述为当前主要人工验收索引；旧 TEST_REPORT 保留历史价值。人工记录不是自动回归测试套件、安全认证、渗透测试或密码学证明；少量虚构数据与正常 UI 观察不覆盖所有 Runtime / lifecycle / 异常分支，也不验证远程模型数据保留行为。

### 阶段二：核心闭环稳定后的 API 评估

确定至少两个模型的候选方案、凭据管理和调用方式，评估成本与依赖。由项目负责人决定后续接入范围与实施安排。

### 阶段三：获准后的 API 实现与跨模型验证

在统一接口下接入选定模型；在应用内切换模型，从同一份本地记忆检索上下文，分别授权并调用。核对无需重新录入记忆、权限检查生效、回复不自动保存，以及失败状态准确。

以上为未来获准后才实施的 API 候选阶段，不是 v0.1 Core PoC 前置条件。当前实际双模型人工验证已满足跨模型验收；未来若实施 API，应单独验证其实际范围，不要求不同模型回答完全一致。

## 10. 不实现与暂缓的范围

遵守 SPEC.md 的排除项：人格吊坠、穿戴设备、区块链、Web3、DID、联邦网络、全球公网、数字人、多 Agent、训练模型、LoRA、复杂数据库、移动端和商业化功能。

首版还暂缓向量检索、自动摘要、自动提取记忆、完整聊天历史、多用户与登录、云同步、后台常驻、远程访问、数据加密、安装器、自动更新、复杂记忆管理/删除及个人文件自动导入；最小 append-only Correction / Evolution 的当前实现与验证边界见第 4 节。

当前未实现持久化消费账本、跨进程恢复 grant、独立授权超时、完整消费/失效审计账本、审计保留和清理策略、加密、多用户和复杂角色权限、API 自动模型调用/切换；不宣称远程撤回、远程删除、保证模型遗忘或生产级安全保证。这些是后续增强或明确不承诺的能力，不属于当前 Permission 阶段收口的阻塞项。

直接 API 调用不属于阶段一；它是后续阶段候选。双击启动脚本、API、向量数据库、加密、DID、多用户、多 Agent 均不加入当前 v0.1 Core PoC 完成条件。

## 11. 当前操作边界

目录安全原则继续有效；末两项保留初次设计阶段的 Historical stage constraint，不代表当前 FEATURE FROZEN 原型的全部能力或本轮操作范围。原开发机器路径的可迁移适用说明见 PROJECT_RULES.md；不据此扩大操作权限。

- 唯一允许操作的项目目录是 `E:\YueYun\Demo-v0.1`。
- 不读取、修改、移动或删除 `E:\YueYun` 之外的任何用户数据。
- 未经明确批准，不执行具有破坏性的删除、覆盖或批量修改操作。
- 历史初次设计阶段仅创建 `DESIGN.md`，不修改 `README.md`、`PROJECT_RULES.md` 或 `SPEC.md`，不创建其他文件，不写功能代码，不安装依赖，不修改系统配置。
- 历史阶段要求：设计文档完成后停止，等待下一步指示；当时的技术方案批准不等于当轮已获准开始功能实现。
