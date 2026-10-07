"""Local Memory UI; writes require an explicit, previously previewed confirmation."""

import base64
import hashlib
import json
import secrets
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer

import memory_store
import runtime
import retrieval


HOST = "127.0.0.1"
PORT = 8765
PAGE = memory_store.PROJECT_DIR / "ui" / "index.html"
PREVIEW_TOKEN = secrets.token_urlsafe(32)
UI_SESSIONS = {}
UI_RUNS = {}
UI_QUERIES = {}
UI_UPDATES = {}


def clear_authorization(session, *, source="app.clear_authorization", clear_query=False):
    run = UI_RUNS.get(session)
    if run is not None:
        run.clear_preview(source=source, clear_query=clear_query)


def preparing_run(session):
    run = UI_RUNS.get(session)
    if run is None or run.summary()["status"] != "Preparing":
        clear_authorization(session, source="app.preparing_run")
        run = runtime.Run()
        UI_RUNS[session] = run
    query = UI_QUERIES.get(session)
    if query is not None:
        current = run.summary()
        metadata = {key: query.get(key) for key in ("mode", "query_date", "keyword", "memory_id")}
        if current["query"] != metadata or current["selectable_memory_ids"] != query["ids"]:
            run.set_query(query, query["ids"])
    return run


def memory_cards(records, views, mode):
    """Add display capabilities; Permission remains the fact-eligibility boundary."""
    cards = []
    for record in records:
        view = views[record["id"]]
        cards.append({**record, **view,
                      "selectable": mode in ("current", "historical") and view["status"] == "current_valid",
                      "can_update": view["next_memory_id"] is None and view["status"] != "corrected"})
    return cards


def prepare_update(data):
    """Validate a proposed append without saving or creating an authorization."""
    previous_id = data.get("previous_memory_id")
    memory_store._validate_id(previous_id)
    relation = data.get("relationship_type")
    if relation not in ("correction", "evolution"):
        raise ValueError("请明确选择纠正原记录或情况发生变化。")
    content, tags, source = (data.get(key) for key in ("content", "tags", "source"))
    memory_store._validate_fields(content, tags, source, True)
    records = retrieval._load_records()
    if previous_id not in records:
        raise ValueError("原 Memory 不存在。")
    views = retrieval._views(records, date.today().isoformat())
    if views[previous_id]["next_memory_id"] is not None:
        raise ValueError("此记录已有后继，请查看并更新最新记录。")
    previous = records[previous_id]
    effective = data.get("effective_from")
    if relation == "correction":
        if effective is not None:
            raise ValueError("纠正只能继承原记录的生效日期。")
        effective = previous.get("effective_from")
    else:
        if effective is None:
            raise ValueError("变化必须明确填写生效日期。")
        memory_store._validate_date(effective)
        previous_date = previous.get("effective_from")
        if previous_date is not None and effective <= previous_date:
            raise ValueError("变化日期必须晚于前序状态的生效日期。")
    return {"previous_memory_id": previous_id, "previous_memory": previous,
            "relationship_type": relation, "content": content,
            "tags": tags, "source": source, "effective_from": effective}


def render_page():
    query_date = date.today().isoformat()
    records = retrieval._load_records()
    views = retrieval._views(records, query_date)
    current = [record for ident, record in records.items() if views[ident]["status"] == "current_valid"]
    cards = memory_cards(current, views, "current")
    template = PAGE.read_text(encoding="utf-8")
    session = secrets.token_urlsafe(32)
    UI_SESSIONS[session] = None
    UI_QUERIES[session] = {"mode": "current", "query_date": query_date,
                           "ids": [record["id"] for record in current]}
    run = preparing_run(session)
    initial = json.dumps({"results": cards, "mode": "current", "query_date": query_date, "run": run.summary()}, ensure_ascii=False).replace("<", "\\u003c")
    return template.replace("__INITIAL_MEMORIES__", initial).replace("__PREVIEW_TOKEN__", PREVIEW_TOKEN).replace("__PAGE_SESSION__", session)


class MemoryHandler(BaseHTTPRequestHandler):
    def _json_response(self, status, data):
        session = self.headers.get("X-Page-Session")
        if session in UI_RUNS:
            data = {**data, "run": UI_RUNS[session].summary()}
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        origin = f"http://{HOST}:{self.server.server_port}"
        if (self.headers.get("Host") != origin.removeprefix("http://")
                or self.headers.get("Origin") != origin
                or self.headers.get("X-Preview-Token") != PREVIEW_TOKEN):
            self._json_response(403, {"error": "拒绝非本地页面请求。"})
            return
        session = self.headers.get("X-Page-Session")
        if session not in UI_SESSIONS:
            self._json_response(403, {"error": "页面会话已失效，请刷新。"})
            return
        if self.path not in ("/preview", "/decision", "/invalidate", "/context", "/search", "/update-preview", "/update-save", "/revoke", "/run-end", "/draft"):
            self._json_response(404, {"error": "不存在的接口。"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16384 or self.headers.get("Content-Type") != "application/json":
                raise ValueError("请求格式或大小不正确。")
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("请求必须是 JSON 对象。")
            if self.path == "/draft":
                run = UI_RUNS.get(session)
                if run is None:
                    raise ValueError("没有本次运行，请刷新页面。")
                result = run.update_draft(data)
                self._json_response(200, {"status": result["status"]})
                return
            if self.path == "/run-end":
                if data:
                    raise ValueError("结束运行不接受客户端 ID 或权限对象。")
                run = UI_RUNS.get(session)
                if run is None:
                    raise ValueError("没有本次运行。")
                result = run.finish(source="/run-end")
                UI_UPDATES.pop(session, None)
                self._json_response(200, {"status": result["status"]})
                return
            if self.path == "/revoke":
                if data:
                    raise ValueError("撤销请求不接受客户端 authorization ID 或批准快照。")
                run = UI_RUNS.get(session)
                if run is None:
                    raise ValueError("没有可撤销的本次运行。")
                result = run.revoke()
                self._json_response(200, result)
                return
            if self.path == "/search":
                clear_authorization(session, source="/search", clear_query=True)
                UI_QUERIES[session] = None
                run = preparing_run(session)
                mode = data.get("mode", "current")
                query_date = data.get("query_date")
                if mode == "current":
                    if query_date not in (None, "", date.today().isoformat()):
                        raise ValueError("当前状态使用本地今天；指定日期请使用历史状态。")
                    query_date = date.today().isoformat()
                if mode == "evolution":
                    results = run.search(mode=mode, memory_id=data.get("memory_id"))
                else:
                    keyword = data.get("keyword")
                    if not isinstance(keyword, str) or not keyword.strip():
                        raise ValueError("请输入检索关键词。")
                    results = run.search(keyword=keyword.strip(), mode=mode, query_date=query_date or None)
                query_date = results[0]["query_date"] if results else retrieval._query_date(query_date or None, mode)
                cards = [{**record,
                          "selectable": mode in ("current", "historical") and record["status"] == "current_valid" and query_date <= date.today().isoformat(),
                          "can_update": record["next_memory_id"] is None and record["status"] != "corrected"}
                         for record in results]
                UI_QUERIES[session] = {"mode": mode, "query_date": query_date,
                                       "ids": [record["id"] for record in cards if record["selectable"]],
                                       "keyword": data.get("keyword"), "memory_id": data.get("memory_id")}
                self._json_response(200, {"results": cards, "mode": mode, "query_date": query_date})
                return
            if self.path == "/invalidate":
                reasons = {"query_changed", "update_draft_changed", "page_restored", "context_error",
                           "revoke_error", "run_end_error", "memory_saved", "preview_cleanup"}
                reason = data.get("reason")
                source = "/invalidate:" + reason if isinstance(reason, str) and reason in reasons else "/invalidate"
                clear_authorization(session, source=source, clear_query=data.get("clear_query") is True)
                if data.get("clear_query") is True:
                    UI_QUERIES[session] = None
                if data.get("clear_update") is True:
                    UI_UPDATES.pop(session, None)
                run = UI_RUNS.get(session)
                self._json_response(200, {"status": run.summary()["status"] if run else "no_run"})
                return
            if self.path == "/update-preview":
                clear_authorization(session, source="/update-preview")
                UI_UPDATES.pop(session, None)
                plan = prepare_update(data)
                update_id = secrets.token_urlsafe(32)
                UI_UPDATES[session] = (update_id, plan)
                self._json_response(200, {"update_id": update_id, **plan})
                return
            if self.path == "/update-save":
                preview = UI_UPDATES.get(session)
                if preview is None or data.get("update_id") != preview[0] or data.get("user_confirmed") is not True:
                    raise ValueError("必须先查看更新预览，再明确确认保存。")
                plan = preview[1]
                expected = {key: plan[key] for key in ("previous_memory_id", "relationship_type", "content", "tags", "source")}
                expected["effective_from"] = plan["effective_from"] if plan["relationship_type"] == "evolution" else None
                if any(data.get(key) != value for key, value in expected.items()) or prepare_update(data) != plan:
                    UI_UPDATES.pop(session, None)
                    raise ValueError("输入或原 Memory 已变化，请重新查看更新预览。")
                UI_UPDATES.pop(session, None)
                record = memory_store.update_memory(
                    plan["previous_memory_id"], plan["content"], plan["tags"], plan["source"],
                    relationship_type=plan["relationship_type"], user_confirmed=True,
                    effective_from=expected["effective_from"],
                )
                # Other open pages must re-retrieve too; their old snapshots remain audit history.
                for page_session in UI_SESSIONS:
                    clear_authorization(page_session, source="/update-save", clear_query=True)
                    UI_QUERIES[page_session] = None
                UI_UPDATES.clear()
                query_date = date.today().isoformat()
                records = retrieval._load_records()
                views = retrieval._views(records, query_date)
                current = [r for ident, r in records.items() if views[ident]["status"] == "current_valid"]
                UI_QUERIES[session] = {"mode": "current", "query_date": query_date, "ids": [r["id"] for r in current]}
                preparing_run(session)
                self._json_response(200, {"memory_id": record["id"], "status": "saved",
                                          "results": memory_cards(current, views, "current"),
                                          "mode": "current", "query_date": query_date})
                return
            if self.path == "/context":
                run = UI_RUNS.get(session)
                if run is None:
                    raise ValueError("没有本次运行，请重新预览并授权。")
                context = run.generate(data)
                self._json_response(200, {"context": context})
                return
            if self.path == "/decision":
                run = UI_RUNS.get(session)
                if run is None:
                    raise ValueError("没有本次运行，请重新生成预览。")
                result = run.decide(data)
                self._json_response(200, result)
                return
            missing = []
            selected = data.get("selected_memory_ids")
            if not isinstance(selected, list) or not selected:
                missing.append("至少选择 1 条 Memory")
            for key, label in (("target_model", "目标模型"), ("purpose", "本次用途"), ("user_question", "当前问题")):
                if not isinstance(data.get(key), str) or not data[key].strip():
                    missing.append(label)
            if missing:
                raise ValueError("请填写或选择：" + "、".join(missing))
            run = preparing_run(session)
            query = UI_QUERIES.get(session)
            if query is None or query["mode"] not in ("current", "historical"):
                raise ValueError("审计/变化历史不能直接授权，请重新检索当前或历史状态。")
            if (data.get("selection_mode") != query["mode"] or data.get("query_date") != query["query_date"]
                    or any(ident not in query["ids"] for ident in selected)):
                raise ValueError("选择或查询条件不匹配，请重新检索并选择。")
            request = run.preview(data)
            states = json.loads(request.memory_state_snapshot)
            records = [{**state["memory"], **state["state_at_query"]} for state in states]
            self._json_response(200, {
                "authorization_id": request.authorization_id,
                "status": request.status, "user_approved": request.user_approved,
                "target_model": request.target_model, "purpose": request.purpose,
                "user_question": request.user_question, "memories": records,
                "selection_mode": request.selection_mode, "query_date": request.query_date,
                "context_preview": request.context_preview,
            })
        except (ValueError, OSError, UnicodeError) as error:
            run = UI_RUNS.get(session)
            if run is not None and run.summary()["status"] != "Context Ready":
                run.fail(error, source=self.path)
            self._json_response(400, {"error": "操作未完成：" + str(error)})

    def do_GET(self):
        expected_host = f"{HOST}:{self.server.server_port}"
        if self.headers.get("Host") != expected_host:
            self.send_error(403, "Invalid host")
            return
        if self.path != "/":
            self.send_error(404)
            return
        try:
            body = render_page().encode("utf-8")
        except (OSError, ValueError):
            self.send_error(500, "Unable to read local memory records")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        script = body.decode("utf-8").split("<script>", 1)[1].split("</script>", 1)[0]
        script_hash = base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii")
        self.send_header("Content-Security-Policy", f"default-src 'none'; script-src 'sha256-{script_hash}'; connect-src http://{HOST}:{self.server.server_port}; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)


def main():
    with HTTPServer((HOST, PORT), MemoryHandler) as server:
        print(f"YueYun Demo v0.1: http://{HOST}:{PORT}/", flush=True)
        print("Updates require explicit preview and confirmation. Stop with Ctrl+C.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
