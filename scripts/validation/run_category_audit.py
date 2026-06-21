"""
HICE Category-level validation.
Validates assigned HICE type against narrative content using an independent rubric.
Output: validation/hice_category_validation_metrics.json + per-category sample CSVs.
"""

import os, sys, json, re
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
OUT_DIR = os.path.join(ROOT, "validation")
os.makedirs(OUT_DIR, exist_ok=True)

from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type

DATA_PATH = os.path.join(ROOT, "data", "myanmar_conflict_clean.csv")


def validate_category(note, assigned_cat):
    note_l = note.lower()
    if assigned_cat == "personnel_targeting":
        staff_harm = re.search(
            r'\b(doctor|nurse|medic|staff|worker|pharmacist|midwife|surgeon|superintendent|health worker|medical staff)\b.{0,150}\b(killed|arrested|shot|abducted|beaten|attacked|targeted|died|assaulted)\b', note_l) or \
            re.search(
            r'\b(killed|arrested|shot|abducted|beaten|attacked|targeted|died|assaulted)\b.{0,150}\b(doctor|nurse|medic|staff|worker|pharmacist|midwife|surgeon|superintendent|health worker|medical staff)\b', note_l)
        if staff_harm:
            return {"verdict": "TP", "reason": "Confirmed personnel harm/targeting"}
        return {"verdict": "FP", "reason": "No explicit personnel harm detected"}
    elif assigned_cat == "access_disruption":
        access = re.search(
            r'\b(closed|abandoned|no access|denied access|blocked|suspended|evacuate|flee|fled|leave|left|unable to access|barred)\b', note_l)
        proximity = re.search(
            r'(hospital|clinic|health center|dispensary|facility|pharmacy|medical center|health facility|treatment center).{0,150}(attack|burn|destroy|shell|strike|bomb|fire|hit|clash|fighting|raided|raiding|arrest|target|raid)', note_l) or \
            re.search(
            r'(attack|burn|destroy|shell|strike|bomb|fire|hit|clash|fighting|raided|raiding|arrest|target|raid).{0,150}(hospital|clinic|health center|dispensary|facility|pharmacy|medical center|health facility|treatment center)', note_l)
        if access or proximity:
            return {"verdict": "TP", "reason": "Confirmed access disruption or proximity violence"}
        return {"verdict": "FP", "reason": "No explicit access disruption or clear proximity effect"}
    elif assigned_cat == "infrastructure_damage":
        infra_damage = re.search(
            r'\b(hospital|clinic|center|facility|dispensary|pharmacy|medical center|health facility|treatment center)\b.{0,250}\b(destroyed|burned|bombed|shelled|hit|damaged|attacked|bombs|airstrike|fire|explosions?|raided|looted|assaulted|occupied|fired upon|opened fire on|raiding|shelling|artillery|strike|detonated)\b', note_l) or \
            re.search(
            r'\b(destroyed|burned|bombed|shelled|hit|damaged|attacked|bombs|airstrike|fire|explosions?|raided|looted|assaulted|occupied|fired upon|opened fire on|raiding|shelling|artillery|strike|detonated)\b.{0,250}\b(hospital|clinic|center|facility|dispensary|pharmacy|medical center|health facility|treatment center)\b', note_l)
        if infra_damage:
            return {"verdict": "TP", "reason": "Confirmed infrastructure damage"}
        return {"verdict": "FP", "reason": "No explicit infrastructure damage detected"}
    elif assigned_cat == "systemic_attack":
        infra = re.search(r'\b(hospital|clinic|facility|center|dispensary|pharmacy|medical center|health facility|treatment center)\b', note_l)
        staff = re.search(r'\b(doctor|nurse|medic|staff|midwife|surgeon|superintendent|health worker|medical staff)\b', note_l)
        if infra and staff:
            return {"verdict": "TP", "reason": "Confirmed presence of both infra and staff"}
        return {"verdict": "FP", "reason": "Missing either infra or staff for systemic attack"}
    elif assigned_cat == "humanitarian_disruption":
        return {"verdict": "TP", "reason": "Default humanitarian disruption"}
    return {"verdict": "FP", "reason": "Unknown category"}


def main():
    df = pd.read_csv(DATA_PATH, low_memory=False)
    mask = detect_hice_from_source(df, ACLEDAdapter())
    notes = df['notes'].fillna('').str.lower()
    types = classify_hice_type(notes)
    hice_df = df[mask].copy()
    hice_df['hice_type'] = types[mask]
    print(f"[INFO] HICE pool: {len(hice_df)} events")

    results = []
    for _, row in hice_df.iterrows():
        val = validate_category(str(row.get('notes', '')), row['hice_type'])
        results.append({"event_id": row.get("event_id_cnty", ""), "hice_type": row['hice_type'],
                        "verdict": val["verdict"], "reason": val["reason"],
                        "notes": str(row.get("notes", ""))[:200]})
    res_df = pd.DataFrame(results)

    print("\nCategory-level precision:")
    metrics = {}
    for cat in res_df['hice_type'].unique():
        cat_df = res_df[res_df['hice_type'] == cat]
        total, tp = len(cat_df), len(cat_df[cat_df['verdict'] == 'TP'])
        prec = round(tp / total * 100, 1) if total > 0 else 0
        metrics[cat] = {"total": total, "TP": tp, "precision": prec}
        print(f"  {cat:30s} n={total:3d}  TP={tp:3d}  prec={prec:.1f}%")
        sample = cat_df.sample(min(20, total), random_state=42)
        sample.to_csv(os.path.join(OUT_DIR, f"hice_cat_sample_{cat}.csv"), index=False)

    with open(os.path.join(OUT_DIR, "hice_category_validation_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)
    print(f"[INFO] Saved to validation/hice_category_validation_metrics.json")


if __name__ == "__main__":
    main()
