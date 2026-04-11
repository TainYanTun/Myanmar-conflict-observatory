[မြန်မာဘာသာဖြင့် ဖတ်ရန်](docs/myanmar_translation.md)

# Myanmar Conflict Observatory (MCO)

[![Kaggle Dataset](https://img.shields.io/badge/Kaggle-Dataset-blue?logo=kaggle)](https://www.kaggle.com/datasets/tainyantun/acled-dataset-for-myanmar)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/TainYanTun/Myanmar-conflict-observatory)

This project serves as an analytical toolkit and visualization hub for conflict data in Myanmar. The primary focus is to transform raw, complex datasets into structured insights and accessible visualizations.
The core dataset is sourced from ACLED (Armed Conflict Location & Event Data Project), specifically focusing on the timeframe following the military takeover on February 1, 2021.

The goal is to provide researchers, journalists, and analysts with a clear picture of conflict trends, geographical hotspots, and actor dynamics, updated through a robust technical framework.

## System Architecture

The Myanmar Conflict Observatory is built on a robust, multi-layered data pipeline designed for high availability and forensic accuracy.

```mermaid
graph TD
    subgraph SDG_2030_Goal ["0. STRATEGIC ALIGNMENT (UN SDG 2030)"]
        SDG3["SDG 3.d: Early Warning & Risk Management"]
        SDG16["SDG 16.1: Reduce All Forms of Violence"]
    end

    subgraph Data_Ingestion_Layer ["1. DATA INGESTION & RESILIENCE"]
        GHA[GitHub Actions: Daily Sync] -->|Trigger| Sync[Data Sync Engine]
        DB[(PostgreSQL Live)] -->|Primary| Sync
        Local[Local CSV Data] -->|Secondary| Sync
        Kaggle[KaggleHub Cloud] -->|Cloud Fallback| Sync
    end

    subgraph Processing_Engine ["2. INTELLIGENCE ENGINE (Python/Pandas)"]
        Sync --> Logic[Actor Normalization Protocol]
        Logic --> NLP[NLP-Lite: SDG 3 Extraction]
        NLP --> Clean[Verified Forensic Dataset]
    end

    subgraph Analytical_Models ["3. ANALYTICAL MODELS"]
        Clean --> Geo[Geospatial Heatmapping]
        Clean --> Temp[Temporal Trend Analysis]
        Clean --> Net[Actor Interaction Networks]
        Clean --> Stat[Z-Score Anomaly Detection]
    end

    subgraph Presentation_Layer ["4. MISSION UI (Streamlit)"]
        Geo & Temp & Net & Stat --> Dashboard[Bilingual Dashboard: EN/MM]
        Dashboard --> CSS[Custom Forensic CSS]
        Dashboard --> Export[High-Res Export Engine: 3x Scale]
    end

    SDG3 -.-> Stat
    SDG3 -.-> NLP
    SDG16 -.-> Geo
    
    style Dashboard fill:#10b981,stroke:#059669,stroke-width:4px,color:#fff
    style DB fill:#1e293b,color:#fff
    style NLP fill:#3b82f6,color:#fff
    style GHA fill:#24292e,color:#fff
    style SDG_2030_Goal fill:#f8fafc,stroke:#cbd5e1,stroke-dasharray: 5 5
```

## UN SDG 2030 Strategic Alignment

This project is purpose-built to support the **United Nations 2030 Agenda for Sustainable Development**, specifically focusing on the intersection of conflict and health.

### **Primary Goal: SDG 3 (Good Health & Well-being)**
*   **Target 3.d:** *Strengthen the capacity of all countries... for early warning, risk reduction and management of national and global health risks.*
    *   **Our Contribution:** The **Early Warning (SDG 3.D)** tab uses Z-Score anomaly detection to identify surges in violence that threaten medical infrastructure, acting as a real-time risk assessment tool for humanitarian responders.
*   **Target 3.8:** *Achieve universal health coverage... access to quality essential health-care services.*
    *   **Our Contribution:** By mapping conflict "Hotspots" against medical infrastructure narratives, we identify regions where health coverage is being systemically disrupted by kinetic engagements.

### **Secondary Goal: SDG 16 (Peace, Justice & Strong Institutions)**
*   **Target 16.1:** *Significantly reduce all forms of violence and related death rates everywhere.*
    *   **Our Contribution:** Through the **Actor Interaction Network**, we provide a transparent, data-driven record of violence, supporting the "Peace & Justice" mandate by documenting the human cost of conflict with forensic clarity.

---

### Project Status & Data Infrastructure

     Start Date: February 1, 2021 (Coup d'état).
     End Date: Current Date (Rolling update).
     Update Mechanism: Automated daily API ingestion via GitHub Actions and ACLED OAuth2. 
     Database: PostgreSQL (Supabase) with SQLAlchemy ORM for scalable retrieval.
     Architecture: Modularized directory structure (src, docs, notebooks, scripts) for enterprise-grade maintainability.
              
This project utilizes live data from the Armed Conflict Location & Event Data Project (ACLED) API.

## Setup & Installation

To run this project locally or in a containerized environment, you must configure your ACLED credentials:

1. **Register with ACLED:** Obtain an account at [acleddata.com](https://acleddata.com/).
2. **Configure Environment:** Create a `.env` file in the root directory (refer to `.env.example`):
   ```env
   ACLED_EMAIL=your_email@example.com
   ACLED_PASSWORD=your_password
   DB_URL=postgresql://admin:secure_password@localhost:5432/conflict_db
   ```
3. **Automated Data Update:** Run the extraction script to fetch the latest conflict logs:
   ```bash
   python update_data.py
   ```
4. **Launch Dashboard:**
   ```bash
   streamlit run app.py
   ```

### Possibilities & Scope

Below are the core analytical components currently implemented:

1. Temporal Analysis
     - Conflict Frequency: Time-series evaluations tracking the number of conflict events per day/week/month.
     - Fatality Trends: Analysis of reported fatalities over time to identify spikes in violence.

2. Geospatial Analysis
     - Conflict Hotspots: Mapping events to identify high-risk regions at State/Region and Township levels.
     - Temporal Expansion: Animated visualizations showing the expansion of conflict over time.
     - Regional Severity: Quantification of instability through a custom Severity Index (Fatalities/Events ratio).

3. Actor Dynamics
     - Actor Interaction: Interactive network graphs mapping engagements between State Forces, Resistance (PDFs), and EAOs.
     - Semantic Normalization: Automated clustering of fragmented local groups into high-level taxonomies.

4. SDG 3: Health & Well-being (Hackathon Special)
     - Health Infrastructure Impact: Tracking kinetic incidents specifically affecting hospitals, clinics, and medical staff.
     - Social Impact Analysis: NLP extraction of gender-specific targeting (women and girls) and systemic well-being indicators.
     - Early Warning System: Z-Score anomaly detection for proactive risk management (SDG Target 3.d).

### Project Organization

The repository has been restructured to support professional development standards:

     app.py: Main Streamlit dashboard interface with SDG 3 focus.
     db_manager.py: Data ingestion and PostgreSQL management pipeline.
     src/: Shared processing logic including actor categorization, health impact extraction, and data cleaning.
     docs/: Formal research documentation, proposals, and NLP strategy.
     notebooks/: Environment for experimental EDA and research-driven analysis.
     scripts/: Data ingestion and database management utilities.

### Collaborators

- **Tain Yan Tun** - Data Engineer (Undergraduate)
- **Kyaw Zay Aung** - Data Analyst (Undergraduate)

### Disclaimer & Ethics

     The data analyzed involves real-world violence and human rights issues. The goal of this project is to provide objective clarity for research purposes, not to sensationalize.
     ACLED data is derived from multiple reports and represents a "Verified Floor"—a conservative confirmed minimum of fatalities.
     Visualizations are only as accurate as the underlying data source. All credit for the raw data belongs to ACLED. 
     

### License

The code in this repository is licensed under the [MIT License](LICENSE).
Information on political violence and protest events is sourced from the Armed Conflict Location & Event Data Project (ACLED).