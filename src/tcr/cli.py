import json, sys
from .evaluate import evaluate_suite

def main(argv=None):
    path = (argv or sys.argv[1:] or ["data/traces.json"])[0]
    rep = evaluate_suite(json.load(open(path)))
    print(f"traces={rep['traces']} pass_rate={rep['pass_rate']}")
    for k, v in sorted(rep["by_kind"].items()):
        print(f"  {k}: {v}")
    for r in rep["results"]:
        if not r["passed"]:
            print(f"- {r['id']}: " + "; ".join(f"[{f['kind']}] {f['detail']}" for f in r["findings"]))
    return 0 if rep["pass_rate"] == 1.0 else 1

if __name__ == "__main__":
    sys.exit(main())
