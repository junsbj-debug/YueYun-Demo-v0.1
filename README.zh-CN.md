# YueYun Demo v0.1

[English](README.md) | **简体中文**

启动日期：2026-10-05

这是 YueYun 个人数字连续性系统的第一个可运行工程原型。

## 演示视频

[观看 / 下载 YueYun v0.1.0 官方英文演示（3分28秒）](https://github.com/junsbj-debug/YueYun-Demo-v0.1/releases/download/v0.1.0/YueYun_v0.1.0_Official_English_Demo_Contrast_v3.mp4)

视频展示本地长期记忆、用户显式授权、一次性 Context 生成，以及在 ChatGPT 和 Claude 之间手动复用授权记忆的完整流程。

## What is YueYun Demo v0.1?

一个 local-first 的 Personal Continuity 最小工程研究原型：验证长期个人 Memory 能否独立于具体 AI 模型，由用户保存、检索、选择和授权，并在不同模型之间重复使用。

当前本地流程为：

`Local Memory → Retrieval → User Selection → Permission → Context`

Runtime 在内存中协调一次请求的 Run、状态与结束。模型不是 Memory 的所有者，只在用户明确授权后获得为本次请求准备的 Context；当前由用户手工提供该文本。

## What v0.1 validates

- **Local Long-Term Memory**：用户明确确认后保存到本地 JSON，可以重新读取、检索和选择。已有最小 append-only Correction / Evolution，保留原记录。
- **Manual Model Portability**：同一份用户侧 Memory 已经过独立授权，人工提供给 ChatGPT 和 Claude；两个模型均正确使用 Context。该结果不代表自动 API interoperability 或所有模型兼容。
- **Permission Boundary**：人工验收支持正常 UI 流程中的 Deny、消费前 Revoke、消费后不可重复生成，以及本地生成与外部发送的区分。

`Memory ≠ Permission`

`Approve ≠ Consume`

`Consume ≠ External Disclosure`

`Pre-consumption Revoke ≠ Post-consumption Recall`

验证范围是少量 fictional/demo data 与人工流程，不是完整 Personal AI、人格复制或生产级安全证明。

## Architecture

| 文件 | 当前职责 |
| --- | --- |
| [memory_store.py](memory_store.py) | 确认保存、读取与 append-only Memory 更新。 |
| [retrieval.py](retrieval.py) | 关键词匹配及 current / historical / evolution / audit 查询。 |
| [permissions.py](permissions.py) | 唯一授权边界：预览、批准/拒绝、撤销、失效、快照校验与一次性消费。 |
| [model_adapters.py](model_adapters.py) | 经 Permission 消费批准对象，返回手动使用的纯文本 Context。 |
| [runtime.py](runtime.py) | 内存 Run、草稿、事件摘要及流程协调，不恢复 grant。 |
| [app.py](app.py) | localhost HTTP 服务与各模块接口连接、启动入口。 |
| [ui/index.html](ui/index.html) | 浏览器单页 UI，内嵌 JavaScript / CSS。 |

## Requirements

- Python **3.10+**，且终端中的 `python` 指向该版本。
- Python standard library only；不需要第三方 Python package。
- 支持 JavaScript 的浏览器。
- 当前实际开发与人工 Acceptance 在 Windows 环境完成；未据此宣称其他系统已通过验收，也不限定代码只能在 Windows 运行。

## Run locally

在 Windows PowerShell 中进入项目目录并启动：

```powershell
Set-Location 'E:\YueYun\Demo-v0.1'
python app.py
```

如果项目位于其他目录，请替换路径。启动后保持终端运行，在浏览器打开：

**http://127.0.0.1:8765/**

服务仅监听 `127.0.0.1:8765`。停止服务请在启动终端按 **Ctrl+C**；关闭浏览器不等于停止后台服务，也不代表可靠撤销。服务重启后旧 Run 与运行时 grant 不恢复，必须重新授权。

当前没有双击启动脚本或自动打开浏览器功能。

## Minimal Demo Flow

原本地实验环境已有虚构测试记录，可用关键词“游泳”，问题“小星周日喜欢做什么？”，用途“回答当前问题”进行人工 Demo；新 clone 默认不含这些历史 runtime 数据，不能直接复现该“小星”演示。

1. 检索本地 Memory，并主动选择需要的记录。
2. 填写 Target model（例如 `chatgpt`）、Purpose 和 Current question。
3. 查看完整 Authorization Preview。
4. 点击“仅本次授权”或“拒绝授权”；拒绝后不生成本次授权 Context。
5. 批准后处于 Approved-Unconsumed，可在生成之前点击“撤销本次授权”。
6. 如继续，主动点击“生成 Context”，消费一次授权，查看最终文本。
7. 用户自行决定是否点击“复制 Context”，并手工提供给目标模型。
8. 如需更换模型，重新预览并独立授权；如需结束本地 Run，点击“结束／取消本次运行”。

YueYun v0.1 不自动调用 ChatGPT / Claude API，不自动发送 Context，也不自动保存模型回复。

## Permission States

以下是 **Runtime 状态**；它们反映流程，不是可恢复或伪造权限的凭证。

| 状态 | 含义 |
| --- | --- |
| Preparing | 用户形成草稿、查询与选择，尚未建立授权预览。 |
| Awaiting Decision | 已有预览，等待明确批准或拒绝。 |
| Approved-Unconsumed | 已批准，尚未消费；可撤销。 |
| Denied | 本次授权被拒绝，Run 终止。 |
| Revoked | 尚未消费的授权已撤销，Run 终止。 |
| Context Ready | 本地 Context 已生成，Permission 已消费；不表示已发送给外部模型。 |
| Completed | 用户结束已生成 Context 的本地 Run；不表示模型已收到或回答。 |
| Invalidated / Cancelled / Error | 绑定变化、用户取消或错误导致本次 Run 终止；不恢复旧权限。 |

正常路径为 `Preparing → Awaiting Decision → Approved-Unconsumed → Context Ready → Completed`，拒绝或撤销走相应终止路径。一次授权只能消费一次；模型、用途、问题、选择或相关 Memory 状态变化后，旧绑定失效，需要重新授权。

## Acceptance Evidence

四份正式人工 Acceptance 均记录为 **PASS**，结论限定于各文档说明的实验范围：

- [ACCEPTANCE_TEST_001.md](ACCEPTANCE_TEST_001.md) — Allow / Manual Cross-Model Portability。
- [ACCEPTANCE_TEST_002.md](ACCEPTANCE_TEST_002.md) — Explicit Denial。
- [ACCEPTANCE_TEST_003.md](ACCEPTANCE_TEST_003.md) — Pre-Consumption Revoke。
- [ACCEPTANCE_TEST_004.md](ACCEPTANCE_TEST_004.md) — Post-Consumption Boundary。

这些是用户真实操作与观察的记录，不是安全认证、渗透测试或自动回归测试；外部模型回答也不证明远程数据保留、删除或遗忘行为。

## Data and Privacy

当前运行数据目录：

- `data/memories/`：用户本地 Memory，每条一个 JSON。
- `data/authorizations/`：授权决定与撤销事件审计。

Authorization decision audit 可能包含 question、purpose、完整 Context preview 和 Memory state snapshot。未来真实使用时，两类目录都可能包含敏感个人信息。**不要把真实个人运行数据直接提交到公开仓库。**

### Public Data Boundary

`data/memories/` 和 `data/authorizations/` 属于本地运行数据，其内容由根目录 `.gitignore` 默认排除，不应提交到公开仓库；当前 fictional 测试数据也按运行数据处理。

`.gitignore` 只影响未来 Git 对未跟踪文件的默认处理，不会删除、移动或修改本机现有数据，也不会自动取消已跟踪文件或清除历史提交中的数据。

新 clone 默认不包含历史 `data/memories/` 与 `data/authorizations/` runtime 内容，可在无数据状态下启动，但不能直接复现依赖原本地数据的“小星”演示。当前已有独立、经过整理的 [林晓 fictional example](examples/linxiao/README.md)，位于 `examples/linxiao/`；Runtime 不会自动加载这些示例，当前没有新增 import/load 功能。不得为了让公开证据链接可用而复制 runtime JSON；示例与运行数据边界保持分离。

Authorization audit 可能包含问题、用途、Context Preview 和 Memory snapshot，即使是拒绝记录，也应按潜在个人数据处理。这一发布边界不是完整隐私保护、安全认证或数据擦除机制。

Deny 阻止本次正常模型使用路径，但授权决定仍会作为本地 audit 保存，包括当时的预览；拒绝不等于本地完全没有记录。Revoke 撤销使用权，不删除 Memory。Audit JSON 是历史记录，不是恢复 grant 的权限凭证。

数据目前为明文，不提供加密或进程间安全隔离。用户人工向外部模型提供 Context 后，本地 Revoke 无法远程追回文本、强制删除或保证模型遗忘。

## Current Limitations

以下是 v0.1 的 scope boundary：

- Manual Context transfer only；没有自动模型 API 调用或切换。
- Single local user、localhost only；没有生产级多用户或远程部署能力。
- 没有加密层、DID 或云同步。
- Runtime 仅在内存中；没有跨进程 grant 恢复或持久化消费账本。
- 没有披露后的 remote recall；无法控制用户复制文本的实际去向。
- 未验证大规模 Memory、长期稳定性或全部并发/崩溃边界。
- 没有安全认证或渗透测试，不作生产部署或绝对隐私保证。

## Project Status

**YueYun Demo v0.1 — Status: FEATURE FROZEN**

- 4 formal manual Acceptance tests：**PASS**。
- 历史 Read-only Freeze Audit verdict：**READY FOR FEATURE FREEZE AFTER MINOR CLEANUP**；所需 cleanup 已完成。
- 已于 2026-10-06 正式 Feature Freeze，依据见 [FEATURE_FREEZE_v0.1.md](FEATURE_FREEZE_v0.1.md)。

v0.1.0 已作为 YueYun Demo 的首个 frozen research prototype 正式公开发布，FEATURE FROZEN 仍然成立。Feature Freeze 仅锁定已验证的功能范围，不等于成熟/最终产品意义的 Final Release、安全认证、生产就绪或项目结束；这不否认 v0.1.0 已经公开发布。main 可以继续包含经过记录的 post-freeze bugfix / documentation improvements，而不改写 v0.1.0 release anchor。
