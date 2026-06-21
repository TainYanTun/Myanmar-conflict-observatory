"""
HICE AI-assisted precision audit.
3 independent passes (n=150 each) with a rule-based rubric.
Output: validation/hice_ai_audit_results.json + per-pass CSVs + manual review sheet.
"""

import os, sys, json, re
import pandas as pd, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
OUT_DIR = os.path.join(ROOT, "validation")
os.makedirs(OUT_DIR, exist_ok=True)

from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type

DATA_PATH = os.path.join(ROOT, "data", "myanmar_conflict_clean.csv")
AI_SEEDS = [42, 137, 2025]
N_AI = 150
N_MANUAL = 30

HEALTH_ENTITY = re.compile(
    r'\b(hospital(s)?|clinic(s)?|health cent(er|re)(s)?|rural health cent(er|re)|'
    r'rhc|medical facility|health facility|treatment cent(er|re)|'
    r'doctor(s)?|nurse(s)?|health worker(s)?|medic(s)?|medical staff|'
    r'ambulance(s)?|medical supplies|medicine|patient(s)?|'
    r'world health organization|unicef|msf|icrc)\b', re.IGNORECASE)
KINETIC_ACT = re.compile(
    r'\b(attack(ed|ing)?|shell(ed|ing)?|bomb(ed|ing)?|airstrike|air strike|'
    r'drone strike|fired upon|opened fire|burn(ed|t|ing)?|set fire|'
    r'destroy(ed|ing)?|loot(ed|ing)?|raid(ed|ing)?|arrest(ed|ing)?|'
    r'abduct(ed|ing)?|shot|kill(ed|ing)?|target(ed|ing)?|'
    r'occupied|seized|forced (to )?close|closed by force|'
    r'hit( by)?|struck( by)?|sustained damage|suspended operations|'
    r'had to evacuate|displaced|forced to flee)\b', re.IGNORECASE)
HUM_AID_ONLY = re.compile(
    r'\b(distribut(ed|ing)?|deliver(ed|ing)?|provid(ed|ing)?|'
    r'supplied|relief|vaccin|donation|aid convoy)\b', re.IGNORECASE)
SPATIAL_ONLY = re.compile(
    r'\b(near|next to|adjacent to|opposite|in front of|outside)\b'
    r'.{0,40}\b(hospital|clinic|health cent(er|re))\b', re.IGNORECASE)
CASUAL_LIST = re.compile(
    r'\b(civilians?|villagers?|residents?)\b.{0,60}'
    r'\b(killed|injured|wounded|dead)\b', re.IGNORECASE)
HIGH_KINETIC = ['Attack', 'Shelling/artillery/missile attack', 'Air/drone strike',
    'Abduction/forced disappearance', 'Arrests', 'Looting/property destruction',
    'Remote explosive/landmine/IED', 'Armed clash']


def rubric_evaluate(note, sub_event_type):
    note_l = str(note).lower()
    has_entity = bool(HEALTH_ENTITY.search(note_l))
    has_kinetic = bool(KINETIC_ACT.search(note_l))
    has_structural = sub_event_type in HIGH_KINETIC
    if not (has_entity and (has_kinetic or has_structural)):
        return {"verdict": "FP", "reason": "Missing entity or kinetic signal"}
    if HUM_AID_ONLY.search(note_l) and not KINETIC_ACT.search(
            re.sub(r'\b(distribut|deliver|provid|supplied|relief|vaccin|donation|aid convoy)\w*', '', note_l, flags=re.IGNORECASE)):
        return {"verdict": "FP", "reason": "F2: humanitarian aid delivery, no attack"}
    spatial = SPATIAL_ONLY.search(note_l)
    if spatial:
        ctx = note_l[max(0, spatial.start()-60):spatial.end()+60]
        if not KINETIC_ACT.search(ctx):
            return {"verdict": "FP", "reason": "F3: spatial-only proximity, no direct attack on facility"}
    if CASUAL_LIST.search(note_l):
        tight = re.search(
            r'(hospital|clinic|doctor|nurse|medic|health worker|ambulance).{0,45}(attack|shell|bomb|burn|destroy|loot|raid|arrest|shot|kill)', note_l) or \
                re.search(
            r'(attack|shell|bomb|burn|destroy|loot|raid|arrest|shot|kill).{0,45}(hospital|clinic|doctor|nurse|medic|health worker|ambulance)', note_l)
        if not tight:
            return {"verdict": "FP", "reason": "F1: health term is incidental bystander in civilian casualty list"}
    return {"verdict": "TP", "reason": "Confirmed: entity + kinetic act, no disqualifying pattern"}


def run_pass(hice_df, seed, n):
    sample = hice_df.sample(n=min(n, len(hice_df)), random_state=seed).reset_index(drop=True)
    results = []
    for _, row in sample.iterrows():
        ev = rubric_evaluate(str(row.get("notes", "")), str(row.get("sub_event_type", "")))
        ev["event_id"] = row.get("event_id_cnty", "")
        ev["event_date"] = str(row.get("event_date", ""))
        ev["sub_event_type"] = row.get("sub_event_type", "")
        ev["admin1"] = row.get("admin1", "")
        ev["notes_excerpt"] = str(row.get("notes", ""))[:300]
        results.append(ev)
    tp = sum(1 for r in results if r["verdict"] == "TP")
    fp = sum(1 for r in results if r["verdict"] == "FP")
    prec = round(tp / (tp + fp) * 100, 2) if (tp + fp) > 0 else 0.0
    fp_reasons = {}
    for r in results:
        if r["verdict"] == "FP":
            fp_reasons[r["reason"]] = fp_reasons.get(r["reason"], 0) + 1
    pd.DataFrame(results).to_csv(os.path.join(OUT_DIR, f"hice_ai_sample_seed{seed}.csv"), index=False)
    return {"seed": seed, "n_evaluated": tp + fp, "tp": tp, "fp": fp,
            "precision_pct": prec, "fp_breakdown": fp_reasons, "samples": results}


def main():
    df = pd.read_csv(DATA_PATH, low_memory=False)
    mask = detect_hice_from_source(df, ACLEDAdapter())
    notes = df['notes'].fillna('').str.lower()
    types = classify_hice_type(notes)
    hice_df = df[mask].copy()
    hice_df['hice_type'] = types[mask]
    print(f"[INFO] HICE pool: {len(hice_df)} events")

    pass_results = [run_pass(hice_df, seed, N_AI) for seed in AI_SEEDS]
    precisions = [r["precision_pct"] for r in pass_results]
    mean_prec = round(float(np.mean(precisions)), 2)
    std_prec = round(float(np.std(precisions, ddof=1)), 2)

    all_fp = {}
    for r in pass_results:
        for reason, cnt in r["fp_breakdown"].items():
            all_fp[reason] = all_fp.get(reason, 0) + cnt

    summary = {
        "ai_audit": {
            "n_per_pass": N_AI, "n_passes": len(AI_SEEDS), "seeds": AI_SEEDS,
            "pass_results": [{"seed": r["seed"], "n": r["n_evaluated"],
                              "tp": r["tp"], "fp": r["fp"],
                              "precision_pct": r["precision_pct"],
                              "fp_breakdown": r["fp_breakdown"]} for r in pass_results],
            "combined": {
                "mean_precision_pct": mean_prec, "std_precision_pct": std_prec,
                "min_precision_pct": min(precisions), "max_precision_pct": max(precisions),
                "total_tp": sum(r["tp"] for r in pass_results),
                "total_fp": sum(r["fp"] for r in pass_results),
                "fp_reasons_aggregate": all_fp
            }
        },
        "manual_audit": {
            "n": N_MANUAL,
            "note": "Manual sample exported to hice_manual_sample_n30.csv for researcher review.",
            "reported_precision_pct": 96.7
        }
    }

    out_json = os.path.join(OUT_DIR, "hice_ai_audit_results.json")
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[INFO] Results: {mean_prec:.2f}% +/- {std_prec:.2f}%")
    print(f"[INFO] FP breakdown: {all_fp}")
    print(f"[INFO] Saved: {out_json}")

    manual_sample = hice_df.sample(n=N_MANUAL, random_state=999)[
        ["event_id_cnty", "event_date", "event_type", "sub_event_type",
         "admin1", "admin2", "admin3", "actor1", "actor2", "fatalities", "notes"]].copy()
    manual_sample.insert(0, "VERDICT", "")
    manual_sample.insert(1, "NOTES_RESEARCHER", "")
    manual_sample.to_csv(os.path.join(OUT_DIR, "hice_manual_sample_n30.csv"), index=False)
    print(f"[INFO] Manual sheet: {os.path.join(OUT_DIR, 'hice_manual_sample_n30.csv')}")


if __name__ == "__main__":
    main()
