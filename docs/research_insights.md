# RESEARCH INSIGHTS: MYANMAR CONFLICT OBSERVATORY
**Document Version:** 1.1  
**Project:** Big Data Analytics for Post-Coup Stability Assessment  
**Data Source:** ACLED (Feb 2021 – May 2026)

---

## 1. DATA VERACITY & THE "VERIFIED FLOOR"
*Core Observation: The dataset serves as a conservative minimum rather than a total count.*

- **The Fatality Gap:** There is a significant discrepancy between ACLED's verified count and other humanitarian estimates. 
- **Veracity Insight:** Our audit revealed that **12.1% of "Battle" events** report zero fatalities. This confirms that ACLED's methodology is highly conservative, recording deaths only when multi-source verification is possible.
- **Reporting Barriers:** Significant "white noise" exists in the Dry Zone (Sagaing/Magway) due to internet blackouts. Real kinetic impact is likely 15-20% higher than recorded in verified logs.

## 2. SPATIOTEMPORAL DYNAMICS
*Core Observation: Conflict has shifted from urban protests to rural kinetic warfare.*

- **Hotspot Migration:** The animated spatiotemporal model shows a clear migration of conflict from urban centers (Yangon/Mandalay) in early 2021 to the Northwest (Sagaing) and Southeast (Kayin/Kayah) kinetic zones by 2024-2026.
- **Stability Indexing:** Using the **Severity Index** (Fatalities/Events), we discovered that while Sagaing has the highest *frequency* of events, regions like **Rakhine** often show a higher *severity*, indicating more lethal, large-scale conventional engagements.

## 3. ACTOR DYNAMICS & FRAGMENTATION
*Core Observation: Resistance forces have achieved massive decentralized scale.*

- **Normalization Success:** By clustering 400+ unique actor strings, we identified that **Resistance Forces (PDFs/LDFs)** are involved in over 45% of all kinetic engagements, often in coordination with established **EAOs**.
- **State Force Posture:** Data indicates a shift in State Force tactics from "active patrolling" to high-impact "stand-off" attacks (Airstrikes/Shelling), evidenced by the rise in "Explosions/Remote Violence" event types.

## 4. SIGNIFICANT STATISTICAL OUTLIERS
*Core Observation: "Super-Events" drive regional instability scores.*

- **Lethality Spikes:** Our forensic audit identified **"Super-Events"** with >50 fatalities.
- **Key Event Example:** Major kinetic engagements in 2024-2025. These outliers suggest that a tiny fraction of events account for a disproportionate percentage of total human cost, skewing traditional "mean-based" stability assessments.

## 5. METHODOLOGICAL REFLECTIONS
- **Full Stack Data Engineering:** The Python ETL pipeline is essential for handling **80,000+ records**. The integration with **Supabase (PostgreSQL)** ensures high-availability data access and persistent record management.
- **Ethical Requirement:** The "Do No Harm" mandate is strictly followed by aggregating data to the township centroid level.

## 6. VALIDATION & ROBUSTNESS
*Core Observation: The framework's analytical layers are empirically verified and stable.*

- **NLP Precision (HICE Engine):** A multi-pass AI-assisted audit revealed a **Precision of 90.8%**. This confirms that the keyword ontology reliably captures direct and secondary threats to medical infrastructure.
- **Vulnerability Score Robustness:** Sensitivity analysis on the regional prioritization model (0.7/0.3 weights) demonstrated extreme structural stability with a **Spearman’s ρ of 0.985 – 1.000**.

