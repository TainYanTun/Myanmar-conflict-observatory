"""
Run all HICE validation checks sequentially.
Outputs summary to console + validation/validation_summary.json
"""

import os, sys, json, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
OUT_DIR = os.path.join(ROOT, "validation")


def run_script(name):
    path = os.path.join(os.path.dirname(__file__), name)
    print(f"\n{'=' * 60}")
    print(f"RUNNING: {name}")
    print(f"{'=' * 60}")
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[:500])
    return result.returncode == 0


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ok = True
    ok &= run_script("run_audit.py")
    ok &= run_script("run_sensitivity.py")
    ok &= run_script("run_category_audit.py")

    summary = {"all_passed": ok}
    for fname in ["hice_ai_audit_results.json", "hice_category_validation_metrics.json"]:
        fpath = os.path.join(OUT_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath) as f:
                summary[fname.replace(".json", "")] = json.load(f)

    out_path = os.path.join(OUT_DIR, "validation_summary.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'=' * 60}")
    status = "ALL VALIDATIONS PASSED" if ok else "SOME VALIDATIONS FAILED"
    print(f"  {status}")
    print(f"  Summary: {out_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
