"""Grade a recorded agent trace against the tool registry.

Checks (each is a typed Finding so a failed run is explainable, not just a score):
  unknown_tool, missing_arg, bad_type, extra_arg, unapproved_write, loop, ignored_error
"""
from dataclasses import dataclass
from .registry import REGISTRY

@dataclass
class Finding:
    step: int
    kind: str
    detail: str

def evaluate_trace(trace, registry=REGISTRY, max_repeat=2):
    findings, seen = [], {}
    approved = set()
    steps = trace["steps"]
    for i, s in enumerate(steps):
        if s.get("type") == "approval":
            approved.add(s["tool"])
            continue
        if s.get("type") != "call":
            continue
        tool = registry.get(s["tool"])
        if tool is None:
            findings.append(Finding(i, "unknown_tool", s["tool"]))
            continue
        args = s.get("args", {})
        for k, typ in tool.required.items():
            if k not in args:
                findings.append(Finding(i, "missing_arg", f"{s['tool']}.{k}"))
            elif not isinstance(args[k], typ):
                findings.append(Finding(i, "bad_type", f"{s['tool']}.{k} expected {typ.__name__}"))
        for k in args:
            if k not in tool.required and k not in tool.optional:
                findings.append(Finding(i, "extra_arg", f"{s['tool']}.{k}"))
        if tool.needs_approval and s["tool"] not in approved:
            findings.append(Finding(i, "unapproved_write", s["tool"]))
        key = (s["tool"], tuple(sorted((k, str(v)) for k, v in args.items())))
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > max_repeat:
            findings.append(Finding(i, "loop", f"{s['tool']} repeated {seen[key]}x with same args"))
        if s.get("result", {}).get("error") and i + 1 < len(steps):
            nxt = steps[i + 1]
            if nxt.get("type") == "final" and "success" in nxt.get("text", "").lower():
                findings.append(Finding(i, "ignored_error", "final answer claims success after a tool error"))
    return {"id": trace["id"], "passed": not findings, "findings": [f.__dict__ for f in findings]}

def evaluate_suite(traces, **kw):
    results = [evaluate_trace(t, **kw) for t in traces]
    n = len(results)
    ok = sum(r["passed"] for r in results)
    by_kind = {}
    for r in results:
        for f in r["findings"]:
            by_kind[f["kind"]] = by_kind.get(f["kind"], 0) + 1
    return {"traces": n, "pass_rate": round(ok / n, 3) if n else 0.0, "by_kind": by_kind, "results": results}
