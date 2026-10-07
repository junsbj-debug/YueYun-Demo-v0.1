"""Manual model adapter: one approved plain-text export, with no external I/O."""

import permissions


def export_manual_context(user_question, approved_authorization, *,
                          target_model=None, purpose=None, selected_memory_ids=None):
    """Return the exact approved text once, without reading memory or sending it.

    First create a request with this question, then explicitly decide it using
    user_approved=True and defer_export=True. Pass that live decision here.
    Optional expected model/purpose/IDs must match the approval. Changed inputs
    require a new preview and approval. Audit JSON is not an export credential.
    Denied, pending, copied, modified and already used decisions are rejected.
    No clipboard, browser, network, file export or model-reply storage occurs.
    """
    return permissions.consume_approved_context(
        approved_authorization, user_question=user_question,
        target_model=target_model, purpose=purpose,
        selected_memory_ids=selected_memory_ids,
    )
