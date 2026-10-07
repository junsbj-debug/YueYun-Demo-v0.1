# YueYun Demo v0.1

**English** | [简体中文](README.zh-CN.md)

Project start date: 2026-10-05

The first runnable engineering prototype of the YueYun Personal Continuity system.

## What is YueYun Demo v0.1?

YueYun is a minimal, local-first engineering research prototype for personal continuity. It explores whether long-term personal Memory can remain independent of a specific AI model, under user control for storage, retrieval, selection, authorization, and reuse with different models.

The current local workflow is:

`Local Memory → Retrieval → User Selection → Permission → Context`

The runtime coordinates each user request as an in-memory run, tracking its state and when it ends. A model does not own Memory. The user explicitly authorizes Context prepared for a particular request and manually provides that text to the model.

## What v0.1 validates

- **Local Long-Term Memory**: explicitly confirmed information is stored in local JSON and can be read, retrieved, and selected again. Minimal append-only Correction / Evolution preserves the original records.
- **Manual Model Portability**: the same user-side Memory was independently authorized and manually provided to ChatGPT and Claude; both used the Context correctly. This does not establish automatic API interoperability or compatibility with all models.
- **Permission Boundary**: manual acceptance supports Deny, pre-consumption Revoke, prevention of repeated generation after consumption, and the distinction between local generation and external delivery through the normal UI workflow.

`Memory ≠ Permission`

`Approve ≠ Consume`

`Consume ≠ External Disclosure`

`Pre-consumption Revoke ≠ Post-consumption Recall`

Validation is limited to a small amount of fictional/demo data and manual workflows. It does not establish a complete Personal AI, a personality replica, or production-grade security.

## Architecture

| File | Current responsibility |
| --- | --- |
| [memory_store.py](memory_store.py) | Stores explicitly confirmed memories, reads records, and supports append-only updates. |
| [retrieval.py](retrieval.py) | Keyword matching and current / historical / evolution / audit queries. |
| [permissions.py](permissions.py) | The sole authorization boundary: preview, approve/deny, revoke, invalidate, snapshot validation, and one-time consumption. |
| [model_adapters.py](model_adapters.py) | Consumes a Permission-approved object and returns plain-text Context for manual use. |
| [runtime.py](runtime.py) | In-memory Runs, drafts, event summaries, and workflow coordination; does not restore grants. |
| [app.py](app.py) | Localhost HTTP service, module integration, and startup entry point. |
| [ui/index.html](ui/index.html) | Single-page browser UI with embedded JavaScript / CSS. |

## Requirements

- Python **3.10+**, with `python` in the terminal pointing to that version.
- Python standard library only; no third-party Python packages are required.
- A browser with JavaScript enabled.
- Development and manual Acceptance were performed on Windows. This does not establish acceptance on other operating systems or imply that the code can run only on Windows.

## Run locally

In Windows PowerShell, enter the project directory and start the service:

```powershell
Set-Location 'E:\YueYun\Demo-v0.1'
python app.py
```

Replace the path if your project is elsewhere. Keep the terminal running and open:

**http://127.0.0.1:8765/**

The service listens only on `127.0.0.1:8765`. Stop it with **Ctrl+C** in the startup terminal. Closing the browser neither stops the background service nor reliably revokes authorization. After a service restart, old Runs and runtime grants are not restored; authorization must be obtained again.

There is currently no double-click startup script or automatic browser opening.

## Minimal Demo Flow

The original local experiment environment contains fictional test records. A manual demo can use the keyword “游泳” (swimming), the question “小星周日喜欢做什么？” (What does Xiaoxing like doing on Sundays?), and the purpose “回答当前问题” (answer the current question). A fresh clone does not include these historical runtime records and cannot directly reproduce that Xiaoxing demo.

1. Retrieve local Memory and explicitly select the records needed.
2. Enter Target model (for example, `chatgpt`), Purpose, and Current question.
3. Review the complete Authorization Preview.
4. Click “仅本次授权” (authorize this request only) or “拒绝授权” (deny authorization). Denial does not generate authorized Context for this request.
5. After approval, the workflow enters Approved-Unconsumed. Before generation, “撤销本次授权” (revoke this authorization) remains available.
6. To continue, click “生成 Context” (generate Context), consume the authorization once, and inspect the final text.
7. The user decides whether to click “复制 Context” (copy Context) and manually provide it to the target model. This is manual external disclosure.
8. Switching models requires a new preview and independent authorization. To end the local Run, click “结束／取消本次运行” (end/cancel this Run).

YueYun v0.1 does not automatically call ChatGPT / Claude APIs, send Context, or save model responses.

## Runtime and Authorization Workflow States

These are **Runtime states**. They describe the workflow and are not credentials that can restore or manufacture permission.

| State | Meaning |
| --- | --- |
| Preparing | The user forms a draft, queries, and selects; no authorization preview has been established. |
| Awaiting Decision | A preview exists and awaits explicit approval or denial. |
| Approved-Unconsumed | Approved but not consumed; revocation is available. |
| Denied | Authorization was denied; the Run terminates. |
| Revoked | Unconsumed authorization was revoked; the Run terminates. |
| Context Ready | Local Context was generated and Permission was consumed; this does not mean it was sent to an external model. |
| Completed | The user ended a local Run after Context generation; this does not mean the model received it or answered. |
| Invalidated / Cancelled / Error | A binding change, cancellation, or error terminates the Run; old permissions are not restored. |

The normal path is `Preparing → Awaiting Decision → Approved-Unconsumed → Context Ready → Completed`. Denial or revocation takes the corresponding terminal path. Authorization can be consumed only once. Changes to the model, purpose, question, selection, or relevant Memory state invalidate the old binding and require new authorization.

## Acceptance Evidence

Four formal manual Acceptance records report **PASS**, limited to the experimental scope described in each document:

- [ACCEPTANCE_TEST_001.md](ACCEPTANCE_TEST_001.md) — Allow / Manual Cross-Model Portability.
- [ACCEPTANCE_TEST_002.md](ACCEPTANCE_TEST_002.md) — Explicit Denial.
- [ACCEPTANCE_TEST_003.md](ACCEPTANCE_TEST_003.md) — Pre-Consumption Revoke.
- [ACCEPTANCE_TEST_004.md](ACCEPTANCE_TEST_004.md) — Post-Consumption Boundary.

These record actual user operations and observations. They are not security certification, penetration testing, or automated regression tests. External model responses do not prove remote data retention, deletion, or forgetting behavior.

## Data and Privacy

Current runtime data directories:

- `data/memories/`: user-local Memory, one JSON file per record.
- `data/authorizations/`: authorization decisions and revocation audit events.

Authorization decision audits may contain the question, purpose, complete Context preview, and Memory state snapshot. Both directories may contain sensitive personal information in future real use. **Do not submit real personal runtime data directly to a public repository.**

### Public Data Boundary

`data/memories/` and `data/authorizations/` contain local runtime data. The root `.gitignore` excludes their contents by default; they should not be committed to a public repository. Current fictional test records are also treated as runtime data.

`.gitignore` only affects Git's default handling of untracked files going forward. It does not delete, move, or modify existing local data, untrack already tracked files, or remove data from commit history.

A fresh clone does not include historical runtime contents from these directories. It can start with no data, but cannot directly reproduce the Xiaoxing demo that depends on the original local records. An independently curated [Linxiao fictional example](examples/linxiao/README.md) is available in `examples/linxiao/`. Runtime does not automatically load these examples; no import/load feature has been added. Do not copy runtime JSON to make public evidence links work. Examples and runtime data remain separate.

Even denied authorization audits may contain questions, purposes, Context Previews, and Memory snapshots and must be treated as potentially personal data. This publication boundary is not complete privacy protection, security certification, or a data-erasure mechanism.

Deny blocks the normal model-use path for that request, but the decision and its preview are still stored in a local audit. Denial does not mean no local record exists. Revoke terminates usage permission; it does not delete Memory. Audit JSON is historical evidence, not a credential for restoring grants.

Data is currently plaintext, with no encryption or inter-process security isolation. After a user manually provides Context to an external model, local Revoke cannot remotely recall the text, force deletion, or guarantee that the model forgets it.

## Current Limitations

The v0.1 scope boundaries are:

- Manual Context transfer only; no automatic model API calls or switching.
- A single local user and localhost only; no production-grade multi-user or remote deployment capability.
- No encryption layer, DID, or cloud synchronization.
- In-memory Runtime only; no cross-process grant restoration or persistent consumption ledger.
- No remote recall after disclosure; the destination of user-copied text is outside the program's control.
- Large-scale Memory, long-term stability, and all concurrency/crash boundaries have not been validated.
- No security certification or penetration testing; no production-deployment or absolute-privacy guarantees.

## Project Status

**YueYun Demo v0.1 — Status: FEATURE FROZEN**

- 4 formal manual Acceptance tests: **PASS**.
- Historical read-only Freeze Audit verdict: **READY FOR FEATURE FREEZE AFTER MINOR CLEANUP**; the required cleanup was completed.
- Feature Freeze was declared on 2026-10-06; see [FEATURE_FREEZE_v0.1.md](FEATURE_FREEZE_v0.1.md).
- v0.1.0 has been publicly released as YueYun Demo's first frozen research prototype. **FEATURE FROZEN** remains in effect.

Feature Freeze locks the validated functional scope. It does not mean a mature/final product release, security certification, production readiness, or the end of the project; v0.1.0 is a published research-prototype release, not a finished or production-ready product. The `main` branch may contain documented post-freeze bugfixes and documentation improvements without changing the v0.1.0 release anchor.
