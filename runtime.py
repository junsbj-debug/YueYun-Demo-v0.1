"""In-memory request coordination. Permission alone owns export authority.

No run files, memory copies, context cache, audit loading or model I/O.
Private handles are the original objects issued by Permission, never IDs.
"""

from copy import deepcopy
from datetime import date, datetime, timezone
from threading import RLock
from uuid import uuid4

import permissions
import retrieval
import model_adapters


TERMINAL = frozenset({"Completed", "Denied", "Revoked", "Invalidated", "Cancelled", "Error"})


def _now():
    return datetime.now(timezone.utc).isoformat()


class Run:
    """One server-owned run; summary/status/IDs are not export credentials."""

    def __init__(self):
        self._lock = RLock()
        self._request = None
        self._approval = None
        self._data = {
            "run_id": str(uuid4()), "created_at": _now(),
            "current_question": "", "target_model": "", "purpose": "",
            "query": None, "selectable_memory_ids": [],
            "selected_memory_ids": [], "authorization_id": None,
            "status": "Preparing", "events": [], "error": None,
        }
        self._event("created")

    def _event(self, action, source="runtime", reason=None):
        event = {"created_at": _now(), "action": action,
                 "status": self._data["status"], "source": source}
        if reason is not None:
            event["reason"] = reason
        self._data["events"].append(event)

    def summary(self):
        with self._lock:
            return deepcopy(self._data)

    def _require(self, status):
        if self._data["status"] != status:
            raise ValueError("Run is not " + status + "; start a new request.")

    def _cleanup(self):
        # End real pending/grant authority before forgetting the references.
        if self._request is not None:
            permissions.invalidate_authorization(self._request)
        if self._approval is not None:
            permissions.invalidate_authorization(self._approval)
        self._request = self._approval = None

    def _end(self, status, error=None, *, source="runtime", reason="operation_ended"):
        self._cleanup()
        self._data["status"] = status
        self._data["error"] = error
        self._event(status.lower(), source, reason)

    def invalidate(self, *, source="runtime.invalidate", reason="explicit_invalidation"):
        with self._lock:
            if self._data["status"] not in TERMINAL:
                self._end("Invalidated", source=source, reason=reason)
            return self.summary()

    def clear_preview(self, *, source="runtime.clear_preview", clear_query=False):
        """Ordinary cleanup preserves an unbound Preparing run, on the server.

        Actual bound handles take precedence over a status label. This is not
        explicit cancellation and never creates or recovers Permission objects.
        """
        with self._lock:
            if (self._data["status"] == "Preparing"
                    and self._request is None and self._approval is None):
                if clear_query:
                    self._data.update(query=None, selectable_memory_ids=[], selected_memory_ids=[])
                self._event("preview_cleared", source, "unbound_preparing")
                return self.summary()
            return self.invalidate(source=source, reason="bound_preview_cleanup")

    def finish(self, *, source="runtime.finish"):
        with self._lock:
            if self._data["status"] not in TERMINAL:
                self._end("Completed" if self._data["status"] == "Context Ready" else "Cancelled",
                          source=source, reason="user_requested_end")
            return self.summary()

    def fail(self, error, *, source="runtime.fail"):
        with self._lock:
            if self._data["status"] not in TERMINAL:
                self._end("Error", str(error), source=source, reason="operation_failed")
            return self.summary()

    def set_query(self, query, selectable_ids):
        with self._lock:
            self._require("Preparing")
            # Explicit metadata only; never retain Retrieval's memory content.
            self._data["query"] = {key: deepcopy(query.get(key)) for key in
                                   ("mode", "query_date", "keyword", "memory_id")}
            self._data["selectable_memory_ids"] = list(selectable_ids)
            self._event("query_ready")

    def update_draft(self, data):
        """Accept unbound inputs; changes to a real preview/grant end its run.

        The server-held state and handles decide the boundary, never a client
        claim that it is still Preparing. This method creates no authority.
        """
        with self._lock:
            query = self._data["query"] or {}
            fields = {
                "selected_memory_ids": data.get("selected_memory_ids"),
                "target_model": data.get("target_model"),
                "purpose": data.get("purpose"),
                "current_question": data.get("user_question"),
            }
            if (self._request is not None or self._approval is not None
                    or self._data["status"] in ("Awaiting Decision", "Approved-Unconsumed", "Context Ready")):
                changed = any(value != self._data[key] for key, value in fields.items())
                changed = changed or data.get("selection_mode") != query.get("mode") or data.get("query_date") != query.get("query_date")
                if changed:
                    self.invalidate(source="/draft", reason="binding_inputs_changed")
                return self.summary()
            if self._data["status"] in TERMINAL:
                return self.summary()
            self._require("Preparing")
            ids = fields["selected_memory_ids"]
            if (not isinstance(ids, list) or any(not isinstance(ident, str) for ident in ids)
                    or len(set(ids)) != len(ids)
                    or any(ident not in self._data["selectable_memory_ids"] for ident in ids)):
                raise ValueError("草稿只能选择当前服务器查询中的候选 Memory IDs。")
            if ids and (data.get("selection_mode") != query.get("mode")
                        or data.get("query_date") != query.get("query_date")):
                raise ValueError("草稿选择与服务器查询条件不一致。")
            if any(not isinstance(fields[key], str) for key in ("target_model", "purpose", "current_question")):
                raise ValueError("草稿模型、用途和问题必须是文本，可以暂时为空。")
            changed = [key for key, value in fields.items() if self._data[key] != value]
            self._data.update(deepcopy(fields))
            for key in changed:
                self._event("selection_changed" if key == "selected_memory_ids" else key + "_changed")
            return self.summary()

    def search(self, *, keyword=None, mode="current", query_date=None, memory_id=None):
        with self._lock:
            self._require("Preparing")
            try:
                results = (retrieval.search_memories(mode=mode, memory_id=memory_id)
                           if mode == "evolution" else
                           retrieval.search_memories(keyword, mode=mode, query_date=query_date))
                effective_date = results[0]["query_date"] if results else retrieval._query_date(query_date, mode)
                ids = [r["id"] for r in results if mode in ("current", "historical")
                       and r["status"] == "current_valid" and effective_date <= date.today().isoformat()]
                self.set_query({"mode": mode, "query_date": effective_date,
                                "keyword": keyword, "memory_id": memory_id}, ids)
                return results
            except (ValueError, OSError, UnicodeError) as error:
                self._end("Error", str(error), source="runtime.search", reason="retrieval_failed")
                raise

    def preview(self, data):
        with self._lock:
            self._require("Preparing")
            query = self._data["query"]
            selected = data.get("selected_memory_ids")
            if (query is None or query["mode"] not in ("current", "historical")
                    or not isinstance(selected, list) or not selected
                    or data.get("selection_mode") != query["mode"]
                    or data.get("query_date") != query["query_date"]
                    or any(ident not in self._data["selectable_memory_ids"] for ident in selected)):
                self._end("Invalidated", "Query/selection mismatch.", source="runtime.preview", reason="query_selection_mismatch")
                raise ValueError("选择或查询条件不匹配，请重新检索并选择。")
            try:
                request = permissions.create_authorization_request(
                    data.get("target_model"), data.get("purpose"), selected,
                    user_question=data.get("user_question"),
                    selection_mode=query["mode"], query_date=query["query_date"],
                )
            except (ValueError, OSError, UnicodeError) as error:
                self._end("Invalidated" if isinstance(error, ValueError) else "Error", str(error), source="runtime.preview", reason="permission_preview_failed")
                raise
            self._request = request
            self._data.update(current_question=request.user_question, target_model=request.target_model,
                              purpose=request.purpose, selected_memory_ids=list(request.selected_memory_ids),
                              authorization_id=request.authorization_id, status="Awaiting Decision")
            self._event("preview_ready")
            return request

    def _check_inputs(self, data):
        query = self._data["query"] or {}
        expected = {"authorization_id": self._data["authorization_id"],
                    "target_model": self._data["target_model"], "purpose": self._data["purpose"],
                    "user_question": self._data["current_question"],
                    "selected_memory_ids": self._data["selected_memory_ids"],
                    "selection_mode": query.get("mode"), "query_date": query.get("query_date")}
        if any(data.get(key) != value for key, value in expected.items()):
            self._end("Invalidated", "Inputs differ from the preview/approval.", source="runtime._check_inputs", reason="binding_mismatch")
            raise ValueError("输入与批准快照不一致，请重新预览并授权。")

    def decide(self, data):
        with self._lock:
            self._require("Awaiting Decision")
            self._check_inputs(data)
            try:
                result = permissions.decide_authorization(
                    self._request, user_approved=data.get("user_approved"), defer_export=True)
            except (ValueError, OSError, UnicodeError) as error:
                self._end("Invalidated" if isinstance(error, ValueError) else "Error", str(error), source="runtime.decide", reason="permission_decision_failed")
                raise
            self._request = None
            if result["authorization"]["status"] == "approved":
                self._approval = result
                self._data["status"] = "Approved-Unconsumed"
                self._event("approved")
            else:
                self._end("Denied", source="runtime.decide", reason="user_denied")
            return {"status": result["authorization"]["status"],
                    "authorization_id": self._data["authorization_id"]}

    def generate(self, data):
        with self._lock:
            self._require("Approved-Unconsumed")
            self._check_inputs(data)
            try:
                context = model_adapters.export_manual_context(
                    self._data["current_question"], self._approval,
                    target_model=self._data["target_model"], purpose=self._data["purpose"],
                    selected_memory_ids=self._data["selected_memory_ids"])
            except (ValueError, OSError, UnicodeError) as error:
                self._end("Invalidated" if isinstance(error, ValueError) else "Error", str(error), source="runtime.generate", reason="permission_consume_failed")
                raise
            self._approval = None
            self._data["status"] = "Context Ready"
            self._event("context_generated_not_sent")
            return context  # Transient output; not retained by Runtime.

    def revoke(self):
        with self._lock:
            self._require("Approved-Unconsumed")
            try:
                result = permissions.revoke_authorization(self._approval)
            except (ValueError, OSError, UnicodeError) as error:
                self._end("Invalidated" if isinstance(error, ValueError) else "Error", str(error), source="runtime.revoke", reason="permission_revoke_failed")
                raise
            self._end("Revoked", result.get("error"), source="runtime.revoke", reason="user_requested_revoke")
            return result
