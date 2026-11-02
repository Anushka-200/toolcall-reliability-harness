import json, pathlib
from tcr.evaluate import evaluate_trace, evaluate_suite

DATA = json.loads((pathlib.Path(__file__).parent.parent / "data/traces.json").read_text())
by_id = {t["id"]: t for t in DATA}

def kinds(tid):
    return {f["kind"] for f in evaluate_trace(by_id[tid])["findings"]}

def test_clean_traces_pass():
    assert evaluate_trace(by_id["good-search"])["passed"]
    assert evaluate_trace(by_id["send-with-approval"])["passed"]

def test_unapproved_write_flagged():
    assert kinds("send-no-approval") == {"unapproved_write"}

def test_unknown_tool_flagged():
    assert "unknown_tool" in kinds("hallucinated-tool")

def test_schema_errors_and_ignored_error():
    assert {"bad_type", "extra_arg", "ignored_error"} <= kinds("bad-args")

def test_loop_detected():
    assert "loop" in kinds("retry-loop")

def test_suite_metrics():
    rep = evaluate_suite(DATA)
    assert rep["traces"] == 6 and rep["pass_rate"] == round(2 / 6, 3)
    assert rep["by_kind"]["unapproved_write"] == 2  # send-no-approval and bad-args (crm write)
