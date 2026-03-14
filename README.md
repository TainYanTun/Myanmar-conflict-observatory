[မြန်မာဘာသာဖြင့် ဖတ်ရန်](docs/myanmar_translation.md)

# Myanmar Conflict Observatory (MCO)

This project serves as an analytical toolkit and visualization hub for conflict data in Myanmar. The primary focus is to transform raw, complex datasets into structured insights and accessible visualizations.
The core dataset is sourced from ACLED (Armed Conflict Location & Event Data Project), specifically focusing on the timeframe following the military takeover on February 1, 2021.

The goal is to provide researchers, journalists, and analysts with a clear picture of conflict trends, geographical hotspots, and actor dynamics, updated through a robust technical framework.

### Project Status & Data Infrastructure

     Start Date: February 1, 2021 (Coup d'état).
     End Date: Current Date (Rolling update).
     Update Mechanism: Automated ETL pipeline via PostgreSQL database ingestion. 
     Database: PostgreSQL with SQLAlchemy ORM for scalable and performant data retrieval.
     Architecture: Modularized directory structure (src, docs, notebooks, scripts) for enterprise-grade maintainability.
              
This project utilizes data from the Armed Conflict Location & Event Data Project (ACLED).

     Provider: ACLED 
     Location: Myanmar
     Timeframe: Feb 1, 2021 – Present
     License: The analysis code in this repository is open source. However, ACLED data is proprietary. Users must register with ACLED to access the raw data files. This repository does not redistribute the raw proprietary data files.
     
### Possibilities & Scope

Below are the core analytical components currently implemented or in the advanced roadmap:

1. Temporal Analysis
     - Conflict Frequency: Time-series evaluations tracking the number of conflict events per day/week/month.
     - Fatality Trends: Analysis of reported fatalities over time to identify spikes in violence.
     - Event Typology: Breakdown of event types (e.g., Battles, Violence against civilians, Protests, Riots).

2. Geospatial Analysis
     - Conflict Hotspots: Mapping events to identify high-risk regions at State/Region and Township levels.
     - Temporal Expansion: Animated visualizations showing the expansion of conflict over time.
     - Regional Severity: Quantification of instability through a custom Severity Index (Fatalities/Events ratio).

3. Actor Dynamics
     - Actor Interaction: Interactive network graphs mapping engagements between State Forces, Resistance (PDFs), and EAOs.
     - Engagement Composition: Sunburst visualizations of event types and sub-event categories.

4. SDG 3: Health & Well-being (Hackathon Special)
     - Health Infrastructure Impact: Tracking kinetic incidents specifically affecting hospitals, clinics, and medical staff.
     - Humanitarian Trend Monitoring: Analyzing narrative event notes to identify regional health-related vulnerabilities.

5. Advanced Insights (Roadmap)
     The following Natural Language Processing (NLP) components are currently being integrated:
     - Topic Modeling: Categorical classification of events through latent theme discovery in ACLED narratives.
     - Named Entity Recognition (NER): Extraction of specific military units and localized militia names from event notes.
     - Semantic Search: Vector-based search capabilities for qualitative event descriptions.

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
