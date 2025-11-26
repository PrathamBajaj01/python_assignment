#!/usr/bin/env python3
import re, json, sys
from pathlib import Path

RE_CREATE = re.compile(r"""(?:/\*.*?\*/\s*)?(CREATE\s+(?:OR\s+REPLACE\s+)?(PROCEDURE|FUNCTION|VIEW)\s+(?P<name>["\w\.]+))\s*(\((?P<params>.*?)\))?(?:\s*RETURNS\s+(?P<returns>[^\s;]+))?""", re.IGNORECASE | re.DOTALL | re.VERBOSE)
RE_STATEMENTS = re.compile(r"""(?P<stmt>(?:SELECT\b.*?(?=(?:;|\n\S|\Z)))|(?:INSERT\s+INTO\b.*?(?=(?:;|\n\S|\Z)))|(?:UPDATE\b.*?(?=(?:;|\n\S|\Z)))|(?:DELETE\s+FROM\b.*?(?=(?:;|\n\S|\Z)))|(?:MERGE\b.*?(?=(?:;|\n\S|\Z))))""", re.IGNORECASE | re.DOTALL | re.VERBOSE)
RE_TABLES = re.compile(r"""(?:(?:FROM|JOIN|INTO|UPDATE|DELETE\s+FROM|MERGE\s+INTO)\s+)(?P<table>["\w\.]+)""", re.IGNORECASE | re.VERBOSE)
RE_SELECT_LIST = re.compile(r"SELECT\s+(?P<select>.*?)\s+FROM\b", re.IGNORECASE | re.DOTALL)
RE_PARAM_SPLIT = re.compile(r",\s*(?![^()]*\))")
RE_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
RE_LINE_COMMENT = re.compile(r"--.*?$", re.MULTILINE)

def clean_comments(sql: str) -> str:
    return RE_BLOCK_COMMENT.sub("", RE_LINE_COMMENT.sub("", sql))

def first_comments(sql: str) -> str:
    m = re.match(r"\s*((?:/\*.*?\*/\s*)|(?:(?:--.*\n)+))+", sql, re.DOTALL | re.IGNORECASE)
    return m.group(0).strip() if m else ""

def parse_params(params_text: str):
    params = []
    if not params_text:
        return params
    ptext = params_text.strip()
    parts = RE_PARAM_SPLIT.split(ptext)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        pm = re.match(r"(?:(IN|OUT|INOUT)\s+)?([\"\w]+)\s+(.+)", part, re.IGNORECASE)
        if pm:
            mode = pm.group(1) or ""
            name = pm.group(2)
            rest = pm.group(3).strip()
            default = None
            mdef = re.search(r"\bDEFAULT\b\s+(.+)$", rest, re.IGNORECASE)
            if mdef:
                default = mdef.group(1).strip()
                dtype = re.sub(r"\bDEFAULT\b\s+(.+)$", "", rest, flags=re.IGNORECASE).strip()
            else:
                dtype = rest
            params.append({"name": name, "mode": mode.upper(), "datatype": dtype, "default": default})
        else:
            params.append({"raw": part})
    return params

def extract_tables(sql: str):
    tables = set()
    for m in RE_TABLES.finditer(sql):
        t = m.group("table")
        if t:
            tables.add(t.strip())
    return sorted(tables)

def extract_select_columns(sql: str):
    cols = set()
    for m in RE_SELECT_LIST.finditer(sql):
        select_part = m.group("select").strip()
        items = RE_PARAM_SPLIT.split(select_part)
        for it in items:
            it = it.strip()
            if not it:
                continue
            it = re.sub(r"\s+AS\s+[\w\"]+$", "", it, flags=re.IGNORECASE)
            it = re.sub(r"\s+[" r'"\w]+' r"$", "", it)
            cols.add(it)
    return sorted(cols)

def extract_statements(sql: str):
    stmts = []
    for m in RE_STATEMENTS.finditer(sql):
        stmt = m.group("stmt").strip()
        if stmt:
            stmts.append(stmt)
    return stmts

def main(path):
    p = Path(path)
    if not p.exists():
        print("File not found:", path, file=sys.stderr); sys.exit(2)
    raw = p.read_text(encoding="utf-8")
    leading_comments = first_comments(raw)
    cleaned = clean_comments(raw)
    m = RE_CREATE.search(cleaned)
    obj_type = "UNKNOWN"
    name = None
    params_text = None
    returns = None
    if m:
        obj_type = m.group(2).upper() if m.group(2) else "UNKNOWN"
        name = m.group("name")
        params_text = m.group("params") or ""
        returns = m.group("returns")
    if obj_type == "UNKNOWN":
        if re.search(r"\bCREATE\s+VIEW\b", cleaned, re.IGNORECASE):
            obj_type = "VIEW"
            vm = re.search(r"CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+([\"\w\.]+)", cleaned, re.IGNORECASE)
            if vm:
                name = vm.group(1)
    params = parse_params(params_text) if params_text else []
    statements = extract_statements(cleaned)
    tables = extract_tables(cleaned)
    select_columns = extract_select_columns(cleaned)
    body = ""
    if m:
        body_start = m.end()
        body = cleaned[body_start:].strip()
    else:
        body = cleaned.strip()
    queries = [{"sql": (s if len(s) < 5000 else s[:5000] + "..."), "length": len(s)} for s in statements]
    out = {
        "source_file": str(p),
        "object_type": obj_type,
        "object_name": name,
        "parameters": params,
        "returns": returns,
        "leading_comments": leading_comments,
        "tables": tables,
        "select_columns": select_columns,
        "queries": queries,
        "body_excerpt": (body[:2000] + "...") if len(body) > 2000 else body,
        "full_body_length": len(body),
    }
    out_name = p.with_suffix(".json")
    out_name.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Wrote:", out_name)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extraction.py sample_stored_procedure.sql", file=sys.stderr); sys.exit(1)
    main(sys.argv[1])
