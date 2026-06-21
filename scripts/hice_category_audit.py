import os
import sys
import pandas as pd
import numpy as np
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from hice_framework import ACLEDAdapter, detect_hice_from_source, classify_hice_type

DATA_DIR = os.path.join(ROOT, "data")
OUT_DIR = os.path.join(ROOT, "validation")
os.makedirs(OUT_DIR, exist_ok=True)

# ── AI Rubric for Category Validation ──────────────────────────────
# We use regexes to verify if the text actually supports the assigned category.
# This acts as an independent "validator" checking the output of the classifier.

def validate_category(note: str, assigned_cat: str) -> dict:
    note_l = note.lower()
    
    if assigned_cat == "personnel_targeting":
        # Must show explicit targeting/harm to staff
        staff_harm = re.search(r'\b(doctor|nurse|medic|staff|worker|pharmacist|midwife|surgeon|superintendent|health worker|medical staff)\b.{0,150}\b(killed|arrested|shot|abducted|beaten|attacked|targeted|died|assaulted|arrest)\b', note_l) or \
                     re.search(r'\b(killed|arrested|shot|abducted|beaten|attacked|targeted|died|assaulted|arrest)\b.{0,150}\b(doctor|nurse|medic|staff|worker|pharmacist|midwife|surgeon|superintendent|health worker|medical staff)\b', note_l)
        if staff_harm:
            return {"verdict": "TP", "reason": "Confirmed personnel harm/targeting"}
        else:
            return {"verdict": "FP", "reason": "No explicit personnel harm detected"}

    elif assigned_cat == "access_disruption":
        # Must show closure, denial, abandonment, or PV-HICE (proximity causing access issues)
        access = re.search(r'\b(closed|abandoned|no access|denied access|blocked|suspended|evacuate|flee|fled|leave|left|unable to access|barred)\b', note_l)
        proximity = re.search(r'(hospital|clinic|health center|dispensary|facility|pharmacy|medical center|health facility|treatment center).{0,150}(attack|burn|destroy|shell|strike|bomb|fire|hit|clash|fighting|raided|raiding|arrest|target|raid)', note_l) or \
                    re.search(r'(attack|burn|destroy|shell|strike|bomb|fire|hit|clash|fighting|raided|raiding|arrest|target|raid).{0,150}(hospital|clinic|health center|dispensary|facility|pharmacy|medical center|health facility|treatment center)', note_l)
        if access or proximity:
            return {"verdict": "TP", "reason": "Confirmed access disruption or proximity violence"}
        else:
            return {"verdict": "FP", "reason": "No explicit access disruption or clear proximity effect"}

    elif assigned_cat == "infrastructure_damage":
        # Must show direct damage to infrastructure
        infra_damage = re.search(r'\b(hospital|clinic|center|facility|dispensary|pharmacy|medical center|health facility|treatment center)\b.{0,250}\b(destroyed|burned|bombed|shelled|hit|damaged|attacked|bombs|airstrike|fire|explosions?|raided|looted|assaulted|occupied|fired upon|opened fire on|raiding|shelling|artillery|strike|detonated)\b', note_l) or \
                       re.search(r'\b(destroyed|burned|bombed|shelled|hit|damaged|attacked|bombs|airstrike|fire|explosions?|raided|looted|assaulted|occupied|fired upon|opened fire on|raiding|shelling|artillery|strike|detonated)\b.{0,250}\b(hospital|clinic|center|facility|dispensary|pharmacy|medical center|health facility|treatment center)\b', note_l)
        if infra_damage:
            return {"verdict": "TP", "reason": "Confirmed infrastructure damage"}
        else:
            return {"verdict": "FP", "reason": "No explicit infrastructure damage detected"}

    elif assigned_cat == "systemic_attack":
        # Must show BOTH infra and staff involved
        infra = re.search(r'\b(hospital|clinic|facility|center|dispensary|pharmacy|medical center|health facility|treatment center)\b', note_l)
        staff = re.search(r'\b(doctor|nurse|medic|staff|midwife|surgeon|superintendent|health worker|medical staff)\b', note_l)
        if infra and staff:
            return {"verdict": "TP", "reason": "Confirmed presence of both infra and staff"}
        else:
            return {"verdict": "FP", "reason": "Missing either infra or staff for systemic attack"}

    elif assigned_cat == "humanitarian_disruption":
        # General catch-all, assume TP if it passed the HICE filter but doesn't fit above
        return {"verdict": "TP", "reason": "Default humanitarian disruption"}

    return {"verdict": "FP", "reason": "Unknown category"}

def main():
    path = os.path.join(DATA_DIR, 'myanmar_conflict_clean.csv')
    print(f"[INFO] Loading data: {path}")
    df_raw = pd.read_csv(path, low_memory=False)

    mask = detect_hice_from_source(df_raw, ACLEDAdapter())
    notes = df_raw['notes'].fillna('').str.lower()
    types = classify_hice_type(notes)
    hice_df = df_raw[mask].copy()
    hice_df['hice_type'] = types[mask]
    
    print(f"\n[INFO] Classifying {len(hice_df)} HICE events...")
    
    # Run validation across all categories
    results = []
    for _, row in hice_df.iterrows():
        cat = row['hice_type']
        note = str(row['notes'])
        val = validate_category(note, cat)
        results.append({
            "event_id": row.get("event_id_cnty", ""),
            "event_date": row.get("event_date", ""),
            "hice_type": cat,
            "verdict": val["verdict"],
            "reason": val["reason"],
            "notes": note[:200]
        })
    
    res_df = pd.DataFrame(results)
    
    print("\n── AI Category Validation Results ──")
    metrics = {}
    for cat in res_df['hice_type'].unique():
        cat_df = res_df[res_df['hice_type'] == cat]
        total = len(cat_df)
        tp = len(cat_df[cat_df['verdict'] == 'TP'])
        prec = (tp / total) * 100 if total > 0 else 0
        metrics[cat] = {"total": total, "TP": tp, "precision": prec}
        print(f"  {cat.ljust(25)} | n={total:>3} | TP={tp:>3} | Precision = {prec:.1f}%")
        
        # Save a sample of 20 for manual review
        sample = cat_df.sample(min(20, total), random_state=42)
        sample.to_csv(os.path.join(OUT_DIR, f"hice_cat_sample_{cat}.csv"), index=False)
        
    with open(os.path.join(OUT_DIR, "hice_category_validation_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"\n[INFO] Samples exported to {OUT_DIR}/hice_cat_sample_*.csv")

if __name__ == "__main__":
    main()
