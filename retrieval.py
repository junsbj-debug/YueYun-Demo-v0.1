"""Read-only keyword/date retrieval over explicitly linked local memories.

No natural-language date parsing, selection, authorization or context export.
"""

from datetime import date

import memory_store


def _normalize_keywords(keywords):
    if isinstance(keywords, str):
        keywords = [keywords]
    if not isinstance(keywords, (list, tuple)):
        raise ValueError("Keywords must be a string or a list/tuple of strings.")
    normalized = []
    seen = set()
    for keyword in keywords:
        if not isinstance(keyword, str):
            raise ValueError("Each keyword must be a string.")
        keyword = keyword.strip()
        folded = keyword.casefold()
        if keyword and folded not in seen:
            normalized.append(keyword)
            seen.add(folded)
    return normalized


def _query_date(value, mode):
    if value is None:
        if mode == "historical":
            raise ValueError("Historical mode requires query_date in YYYY-MM-DD.")
        return date.today().isoformat()
    memory_store._validate_date(value)
    return value


def _load_records():
    """Validate every record and the whole graph; any damage aborts retrieval."""
    directory = memory_store.MEMORIES_DIR
    if not directory.resolve().is_relative_to(memory_store.PROJECT_DIR):
        raise ValueError("Memory storage must remain inside the project directory.")
    records = {}
    for path in sorted(directory.glob("*.json")):
        try:
            record = memory_store.load_memory(path.stem)
            memory_store._validate_relationship(record)
        except (ValueError, OSError) as error:
            raise ValueError(f"Cannot retrieve memory {path.name}: {error}") from error
        records[record["id"]] = record
    memory_store._validate_links(records)
    return records


def _views(records, query_date):
    """Derive states from linear chains; corrections never count as true history.

    Missing effective_from remains unknown; created_at is never a substitute.
    A null start is accepted as an undated current fact, but cannot prove a
    historical date. Each evolution boundary starts a new temporal state.
    """
    successors = {r["previous_memory_id"]: r["id"] for r in records.values()
                  if r.get("relationship_type") in ("correction", "evolution")}
    views = {}
    for root in records.values():
        if root.get("previous_memory_id"):
            continue
        chain = []
        current = root["id"]
        while current is not None:
            chain.append(current)
            current = successors.get(current)
        valid = [ident for ident in chain if ident not in successors
                 or records[successors[ident]]["relationship_type"] != "correction"]
        ends = {ident: (records[valid[index + 1]].get("effective_from")
                        if index + 1 < len(valid) else None)
                for index, ident in enumerate(valid)}
        for position, ident in enumerate(chain):
            record = records[ident]
            start = record.get("effective_from")
            end = ends.get(ident)
            if ident not in ends:
                status, label = "corrected", "已纠正"
            elif start is not None and start > query_date:
                status, label = "future", "尚未生效"
            elif end is not None and query_date >= end:
                status, label = "historical_valid", "历史有效"
            else:
                status, label = "current_valid", "当前有效"
            views[ident] = {
                "relationship_type": record.get("relationship_type") or None,
                "previous_memory_id": record.get("previous_memory_id") or None,
                "effective_from": start,
                "effective_until": end,
                "effective_from_known": start is not None,
                "status": status, "status_label": label,
                "chain_id": root["id"], "chain_position": position,
                "next_memory_id": successors.get(ident), "query_date": query_date,
            }
    if len(views) != len(records):
        raise ValueError("Cannot determine all memory chains.")
    return views


def search_memories(keywords=None, *, mode="current", query_date=None, memory_id=None):
    """Search current/historical/audit facts, or display one evolution chain.

    Old search_memories(keywords) calls remain valid: default current mode uses
    the local date, returned as query_date for inspection. Historical requires
    an explicit ISO date and excludes undated facts rather than inventing dates.
    Audit searches all records including corrected/future facts. Evolution
    requires memory_id, accepts no keywords, and returns the entire explicit
    chain in order (including clearly marked corrected audit records).

    Matching is the original case-insensitive substring OR rule on content/tags,
    applied AFTER candidate filtering. No matching ancestor substitutes for a
    nonmatching descendant. Dates refer to asserted fact validity, not what the
    system knew at that time. Intervals are start-inclusive/end-exclusive.
    Statuses are relative to query_date. Broken records/chains raise ValueError;
    no records are repaired, selected, authorized or written.
    """
    if mode not in ("current", "historical", "evolution", "audit"):
        raise ValueError("Unknown retrieval mode.")
    query_date = _query_date(query_date, mode)
    if mode == "evolution":
        memory_store._validate_id(memory_id)
        if keywords is not None:
            raise ValueError("Evolution takes memory_id, not keywords.")
        normalized = []
    else:
        if memory_id is not None:
            raise ValueError("memory_id is only used in evolution mode.")
        normalized = _normalize_keywords(keywords)
        if not normalized:
            return []
    records = _load_records()
    views = _views(records, query_date)
    if mode == "evolution":
        if memory_id not in records:
            raise ValueError(f"Missing memory: {memory_id}")
        chain_id = views[memory_id]["chain_id"]
        candidates = sorted(
            (r for r in records.values() if views[r["id"]]["chain_id"] == chain_id),
            key=lambda r: views[r["id"]]["chain_position"],
        )
    else:
        candidates = [r for r in records.values()
                      if mode == "audit" or (
                          views[r["id"]]["status"] == "current_valid"
                          and (mode != "historical" or r.get("effective_from") is not None))]
    results = []
    for record in candidates:
        content = record["content"].casefold()
        tags = [tag.casefold() for tag in record["tags"]]
        matches = []
        for keyword in normalized:
            folded = keyword.casefold()
            fields = []
            if folded in content:
                fields.append("content")
            if any(folded in tag for tag in tags):
                fields.append("tags")
            if fields:
                matches.append({"keyword": keyword, "fields": fields})
        if matches or mode == "evolution":
            results.append({
                "id": record["id"],
                "content": record["content"],
                "tags": record["tags"],
                "source": record["source"],
                "created_at": record["created_at"],
                "matched_keywords": [match["keyword"] for match in matches],
                "matched_fields": [
                    field for field in ("content", "tags")
                    if any(field in match["fields"] for match in matches)
                ],
                "matches": matches,
                "mode": mode,
                **views[record["id"]],
            })
    return results
