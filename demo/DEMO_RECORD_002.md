# DEMO RECORD 002 — Cross-Model Personal Continuity

- **Experiment date:** 2026-10-07
- **System:** YueYun Demo v0.1
- **Status:** FEATURE FROZEN
- **Experiment type:** Post-freeze manual demonstration and validation

## 1. Objective

Evaluate whether the same user-controlled local memories can be independently authorized for different target models, generated as Context through one-time authorization consumption, and manually provided to ChatGPT and Claude.

The experiment also checks whether a retrieved but unselected Memory remains outside the authorized Context.

This is a manual workflow demonstration. It does not involve automatic cross-model transfer or model API integration.

## 2. Test Data

All records are **fictional demo data** about the fictional person **Linxiao**.

The retrieval results contained three memories:

### A — Kyoto Travel Plan

**Memory ID:** `27082d6e-f6fa-412d-8405-bf5afd1cb297`

> Fictional demo data: Linxiao plans to visit Kyoto on November 15, 2026.

### B — Travel Preference

**Memory ID:** `47bcf429-fe55-43b5-b146-39945eed8fd9`

> Fictional demo data: Linxiao prefers relaxed travel itineraries with free time each day.

### C — Unrelated Coffee Preference

**Memory ID:** `726256d7-7302-4da1-b396-7bdc78642ccc`

> Fictional demo data: Linxiao prefers unsweetened black coffee.

The user selected **A + B** for both target models. **C** was retrieved but not selected and did not enter either approved Context preview.

## 3. Shared Request

| Field | Value |
|---|---|
| Purpose | `Plan a relaxed Kyoto visit` |
| Question | `Using only the authorized memories, suggest a relaxed plan for Linxiao's Kyoto visit.` |
| Selection mode | `current` |
| Query date | `2026-10-07` |
| Selected memories | A + B |

## 4. ChatGPT Run

| Field | Value |
|---|---|
| Observed Run ID | `8af4aa13-85d6-487b-be7f-0577edc523b8` |
| Authorization ID | `c7c9b795-12f6-4b66-b564-b566a3b6099e` |
| Target model | `chatgpt` |
| Persisted decision | `approved` |
| User approval | `true` |

The user independently approved the ChatGPT request with exactly A + B selected. The coffee Memory was excluded.

Local Context generation and the Runtime/UI transitions to **Context Ready** and **Completed** were manually observed. The user manually copied the Context and pasted it into ChatGPT. A ChatGPT response was manually observed.

The persisted authorization audit does **not** contain the Run ID or a separate consumption event. It therefore does not independently prove exact Run linkage or consumption.

## 5. Claude Run

| Field | Value |
|---|---|
| Observed Run ID | `b8ae7e24-8506-4cf7-b321-70c5a9538f99` |
| Authorization ID | `ce632013-2530-4832-980a-7091459e549f` |
| Target model | `claude` |
| Persisted decision | `approved` |
| User approval | `true` |

The user created a separate, independently approved Claude request with exactly A + B selected. The ChatGPT authorization was not reused. The coffee Memory was excluded.

Local Context generation and the Runtime/UI transitions to **Context Ready** and **Completed** were manually observed. The user manually copied the Context and pasted it into Claude. A Claude response was manually observed.

The persisted authorization audit does **not** contain the Run ID or a separate consumption event. It therefore does not independently prove exact Run linkage or consumption.

## 6. Cross-Model Result

The observed workflow was:

```text
Same local memories
→ separate target-specific authorization
→ Context bounded to the same selected memories
→ manual reuse with ChatGPT and Claude
```

The two authorization records have different authorization IDs and different target models, while retaining the same purpose, question, and selected Memory IDs.

A ChatGPT authorization cannot simply be treated as a Claude authorization. Each target required a separate approval. The Contexts shared the same Memory scope; their target-specific metadata differed.

This result concerns the two tested manual workflows and does not establish universal model compatibility.

## 7. Scope Exclusion Result

**The coffee Memory was retrieved but not selected.**

Read-only inspection confirmed that its ID and content were absent from both approved Context previews. Its ID was also absent from both:

- `selected_memory_ids`
- authorization state snapshots

This demonstrates the tested scope boundary:

```text
Retrieval ≠ Selection
Selection ≠ Authorization
Authorization scope is explicit.
```

Retrieval made the coffee Memory available for user consideration; it did not automatically include that Memory in either authorization.

## 8. Evidence Layers

### A. Persisted Audit Evidence

The two local authorization audits record:

- Separate authorization IDs.
- Target models `chatgpt` and `claude`.
- The matching purpose and question.
- Decisions of `approved` with `user_approved = true`.
- Exactly A + B as the selected Memory IDs.
- Selection mode `current` and query date `2026-10-07`.
- Approved Context previews and authorization state snapshots excluding C.

These records support the recorded approval and scope facts. They do not independently prove consumption, external delivery, or model responses.

The audit JSON files are local runtime evidence and are not supplied with the public repository. They must not be copied, reconstructed, or fabricated to repair public evidence references.

### B. Runtime/UI Manual Observation

The operator manually observed local Context generation and the states **Context Ready** and **Completed** for each Run.

Code inspection shows that successful Adapter consumption removes the live grant, preventing repeated consumption. Runtime enters Context Ready after successful Context generation through that path.

The observed UI states therefore support successful local consumption and generation within the tested workflow. They are not a persisted consumption ledger, an independent replay test, or evidence of external delivery.

Completed indicates that the local Run ended.

### C. External-Model Manual Observation

The operator manually copied and pasted the Context into ChatGPT and Claude and observed their responses.

External submission, apparent receipt, and responses are **manual observation evidence**. They are not independently established by YueYun’s authorization audits or Runtime state names.

These three evidence layers must not be combined into a claim of automatic system proof.

## 9. Known Evidence Limitations

- Authorization audits do not persist `run_id`.
- Approval audits do not persist a separate consumption event.
- Exact Run-to-Authorization linkage therefore relies partly on matching request fields and timing, together with manual observation.
- External delivery and responses are not independently proven by YueYun audit records.
- The experiment does not establish remote-model retention, deletion, recall, or other server-side data-processing behavior.
- This demonstration does not constitute adversarial testing, security certification, penetration testing, or cryptographic proof.

More explicit Run linkage and consumption evidence could be considered in later research or engineering work. This record makes no implementation commitment and does not change v0.1.

## 10. Boundary Statements

Approve ≠ Consume ≠ External Disclosure

Context Ready ≠ External Model Received

Completed ≠ External Model Answered

## 11. Conclusion

Within the tested manual workflow, this experiment supports:

- Target-specific, independent authorization for ChatGPT and Claude.
- Context bounded to explicitly selected local memories.
- Manual cross-model reuse of user-controlled Context.
- Exclusion of a retrieved but unselected Memory.

The combined evidence consists of persisted approval records, local Runtime/UI manual observations, and external-model manual observations, each with the limitations stated above.

It does not establish automatic interoperability, automatic cross-model transfer, universal model compatibility, security certification, production readiness, cryptographic guarantees, or external deletion/recall capabilities. It does not demonstrate AGI or a personality replica.

## 12. Freeze Note

This record documents an experiment performed with the frozen YueYun Demo v0.1.

It does not add a new v0.1 feature or change the frozen semantics.
