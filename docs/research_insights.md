# RESEARCH INSIGHTS: MYANMAR CONFLICT OBSERVATORY
**Document Version:** 1.0  
**Project:** Big Data Analytics for Post-Coup Stability Assessment  
**Data Source:** ACLED (Feb 2021 – Feb 2026)

---

## 1. DATA VERACITY & THE "VERIFIED FLOOR"
*Core Observation: The dataset serves as a conservative minimum rather than a total count.*

- **The Fatality Gap:** There is a significant discrepancy between ACLED's verified count (~77,560) and other humanitarian estimates (~89,200). 
- **Veracity Insight:** Our audit revealed that **12.1% of "Battle" events (8,485 records)** report zero fatalities. This confirms that ACLED's methodology is highly conservative, recording deaths only when multi-source verification is possible.
- **Reporting Barriers:** Significant "white noise" exists in the Dry Zone (Sagaing/Magway) due to internet blackouts. Real kinetic impact is likely 15-20% higher than recorded in verified logs.

## 2. SPATIOTEMPORAL DYNAMICS
*Core Observation: Conflict has shifted from urban protests to rural kinetic warfare.*

- **Hotspot Migration:** The animated spatiotemporal model shows a clear migration of conflict from urban centers (Yangon/Mandalay) in early 2021 to the Northwest (Sagaing) and Southeast (Kayin/Kayah) kinetic zones by 2024.
- **Stability Indexing:** Using the **Severity Index** (Fatalities/Events), we discovered that while Sagaing has the highest *frequency* of events, regions like **Rakhine** often show a higher *severity*, indicating more lethal, large-scale conventional engagements.

## 3. ACTOR DYNAMICS & FRAGMENTATION
*Core Observation: Resistance forces have achieved massive decentralized scale.*

- **Normalization Success:** By clustering 300+ unique actor strings, we identified that **Resistance Forces (PDFs/LDFs)** are involved in over 45% of all kinetic engagements, often in coordination with established **EAOs**.
- **State Force Posture:** Data indicates a shift in State Force tactics from "active patrolling" to high-impact "stand-off" attacks (Airstrikes/Shelling), evidenced by the rise in "Explosions/Remote Violence" event types.

## 4. SIGNIFICANT STATISTICAL OUTLIERS
*Core Observation: "Super-Events" drive regional instability scores.*

- **Lethality Spikes:** Our forensic audit identified **48 "Super-Events"** with >50 fatalities.
- **Key Event Example:** Sept 5, 2024, in Maung Shwe Lay (400 fatalities). These outliers suggest that a tiny fraction of events (0.06%) account for a disproportionate percentage of total human cost, skewing traditional "mean-based" stability assessments.

## 5. METHODOLOGICAL REFLECTIONS
- **Big Data Utility:** Traditional spreadsheet analysis failed to reveal the spatiotemporal "bloom" of the conflict. The Python ETL pipeline was essential for handling the **69,000+ records**.
- **Ethical Requirement:** The "Do No Harm" mandate is not just legal; it is analytical. Aggregating data into 1-month clusters (ME) is necessary to provide strategic insights without creating tactical risks for local reporters.

---
**Researcher Signature:** Tain Yan Tun  
**Date:** March 13, 2026
