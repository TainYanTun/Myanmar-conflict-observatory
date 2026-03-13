# RESEARCH PROPOSAL

**Title of Research Proposal:**  
**Myanmar Conflict Observatory: A Big Data Analytics Framework for Post-Coup Stability Assessment**

**Student Name:** Tain Yan Tun  
**Research Area:** Big Data Visualization and Conflict Analytics  

---

# ABSTRACT

Following the military takeover on **February 1, 2021**, the political and social landscape of Myanmar has undergone significant upheaval, resulting in a complex and evolving conflict environment. Understanding the dynamics of this conflict requires analysing massive volumes of heterogeneous data, including event-based records, geospatial coordinates, and temporal logs.

This project proposes the development of the **Myanmar Conflict Observatory**, an open-source analytical framework designed to ingest, curate, and visualize data from the **Armed Conflict Location & Event Data Project (ACLED)**.

By leveraging **big data engineering techniques**, this research aims to transform raw conflict logs into actionable intelligence through interactive dashboards. The proposed system will address challenges in data curation and manual updates, providing researchers and analysts with tools to identify conflict hotspots, actor dynamics, and temporal trends.

Ultimately, this project seeks to bridge the gap between raw datasets and accessible knowledge, facilitating deeper academic and humanitarian understanding of the ongoing crisis.

**Keywords:**  
Big Data Visualization, Conflict Analytics, ACLED, Geospatial Analysis, Myanmar, Data Science

---

# 1. INTRODUCTION

The political instability in Myanmar following the **February 1, 2021 coup d'état** has resulted in a widespread humanitarian and security crisis. In such a volatile environment, the ability to track and analyze conflict events in real-time is crucial for researchers, policymakers, and humanitarian organizations.

However, the data describing these events, sourced from the **Armed Conflict Location & Event Data Project (ACLED)**, exists as massive raw tabular datasets that are difficult to interpret without specialized tools.

The execution of conflict events leaves digital traces across various dimensions:

- Time
- Location
- Actors involved
- Event types

To analyze this process data effectively, it is necessary to collect the data into a structured repository and leverage visualization tools to analyze the data along multiple dimensions:

- Geographic
- Temporal
- Categorical

The big data challenge in this context is characterized by:

- **Volume** – continuous accumulation of event data  
- **Variety** – multiple event types and actors  
- **Velocity** – need for timely updates  

Currently, manual analysis of these datasets is time-consuming and prone to error, creating a barrier to rapid insight generation.

To address these challenges, this proposal presents a **data science approach** for systematically organizing Myanmar conflict data and preparing it for interactive analytics.

The proposed framework has the potential to serve as a critical resource for the academic community by transforming raw ACLED logs into a **Knowledge Observatory** that reveals patterns in violence, protest, and territorial control.

### Unique Contributions

- **Advancement in understanding conflict dynamics**  
  Analysis of patterns in Myanmar conflict data to reveal trends in violence and resistance.

- **A platform for organizing and curating conflict metadata**  
  Focus on geospatial and temporal metadata to enable visualization of conflict hotspots and actor movements.

- **A digital dashboard for conflict entity analysis**  
  Visualization tools that support analysis of actors, event frequencies, and regional stability.

---

# 2. LITERATURE REVIEW

## 2.1 Conflict Data and Event Analysis

The study of political violence relies heavily on **event-based datasets**. The **ACLED project** has become the gold standard for coding and analysing conflict events, providing high-resolution geospatial data.

While ACLED provides the raw foundation for analysis, a significant research gap exists in the **curation and contextualization** of this data for dynamic conflict environments like Myanmar.

Standard analytical models often struggle to adapt to:

- Rapid proliferation of armed actors (e.g., People's Defence Forces)
- Fluidity of territorial control

This challenge has been identified in recent conflict literature.

Furthermore, generic visualization tools frequently fail to address the **data islands** created by Myanmar's fragmented information landscape.

Consequently, there is a lack of **specialized open-source frameworks** that automate the transformation of raw logs into a structured **Knowledge Observatory** for post-coup Myanmar.

---

## 2.2 Big Data Visualization in Humanitarian Contexts

Visualizing big data in humanitarian contexts presents challenges related to:

- Data veracity
- Privacy
- Reliability

Previous research demonstrates the effectiveness of **web-based dashboards** for crisis mapping. These systems often utilize a **Data Lake architecture** to ingest raw logs before applying transformation layers for visualization.

---

## 2.3 Geospatial Analytics and Knowledge Graphs

Graph databases and geospatial tools are increasingly used to map relationships between entities.

Research shows that representing **conflict actors as nodes in a knowledge graph** allows the discovery of hidden alliances and conflict chains.

This project proposes adapting these techniques to map the complex web of actors in **post-2021 Myanmar**.

---

# 3. RESEARCH OBJECTIVES

The anticipated outcome of this project is the development of a framework and techniques for contextualizing conflict data.

### Objectives

1. **Develop a unified data ingestion framework**

   - Automatically curate raw ACLED data (Excel/CSV)
   - Prepare it for structured database storage
   - Address data quality and formatting issues

2. **Design analytical components for conflict analytics**

   - **Temporal Component** – time-series analysis of event frequency  
   - **Geospatial Component** – heatmaps and regional breakdowns  
   - **Actor Component** – network analysis of conflict participants  

3. **Build a digital dashboard**

   - Interactive filters
   - Geospatial maps
   - Analytical charts

---

# 4. PROPOSED METHODOLOGY

## 4.1 Research Design

This research adopts a **mixed-methods approach** combining:

- Quantitative data analysis
- Qualitative evaluation

The study follows four phases:

1. Data collection and integration  
2. Data curation and knowledge extraction  
3. Framework development and implementation  
4. Evaluation and validation  

---

## 4.2 Data Collection and Sources

The primary dataset is the **ACLED Myanmar dataset**.

**Scope**

- February 1, 2021 (Military Takeover)
- To Current Date

**Update Mechanism**

- Semi-automated script for manual upload of ACLED Excel files
- ETL pipeline updates the database automatically

**Attributes**

- Event Date
- Event Type
- Sub-Event Type
- Actor 1
- Actor 2
- Location
- Latitude
- Longitude
- Fatalities
- Notes

---

## 4.3 Tools and Technologies

| Component | Technology | Purpose |
|---|---|---|
| Language | Python | Data processing and backend |
| Data Processing | Pandas / NumPy | ETL operations and manipulation |
| Geospatial Analysis | GeoPandas / Folium / Plotly | Mapping and spatial analysis |
| Database | SQLite / PostgreSQL / MySQL | Structured data storage |
| Visualization | Streamlit / Dash | Interactive dashboard |
| Version Control | GitHub | Open-source code management |

---

## 4.4 Analysis Techniques

### Temporal Analysis
Aggregating events by date to identify trends and spikes in conflict intensity.

### Geospatial Clustering
Identifying conflict hotspots using heatmaps.

### Network Analysis
Creating relationship graphs between actors  
(e.g., **Military vs. People's Defence Forces** engagements).

### Descriptive Statistics
Summarizing:

- Fatalities
- Event types
- Regional distribution

---

# 5. EXPECTED OUTCOMES

- A functional **open-source repository** containing the source code.
- A **cleaned dataset** structured for time-series and geospatial queries.
- A **deployable web dashboard** allowing filtering by:
  - Date
  - Region
  - Actor
- Documentation explaining how to update ACLED datasets.
- A **final research paper** documenting the methodology and findings.

---

# 6. PROJECT TIMELINE

| Phase | Activity | Duration | Deliverable |
|---|---|---|---|
| Phase 1 | Literature Review & Data Study | Weeks 1–3 | ACLED schema report |
| Phase 2 | Data Pipeline Development (ETL) | Weeks 4–6 | Python data cleaning scripts |
| Phase 3 | Component Implementation | Weeks 7–10 | Functional dashboard components |
| Phase 4 | Integration & Testing | Weeks 11–13 | Integrated dashboard prototype |
| Phase 5 | Documentation & Final Report | Weeks 14–16 | Final paper & GitHub repository |

---

# 7. CONCLUSION

The ongoing crisis in Myanmar presents a significant challenge for **data-driven decision-making** due to the complexity and volume of conflict data.

This proposal outlines a framework for transforming raw event data into a **structured interactive Observatory**.

By bridging the gap between raw ACLED data and end-user analysis, this project empowers researchers with tools to:

- Monitor conflict dynamics
- Understand actor behaviours
- Generate transparent insights about the Myanmar crisis

The **open-source nature** of the project ensures that it can be extended and used by the broader academic and humanitarian community.

---

# REFERENCES

[1] C. Raleigh, A. Linke, H. Hegre, and J. Karlsen,  
"Introducing ACLED—Armed Conflict Location & Event Data,"  
*Journal of Peace Research*, vol. 47, no. 5, pp. 651–660, 2010.

[2] S. P. O’Brien,  
"Crisis Early Warning and Decision Support,"  
*International Studies Review*, vol. 12, no. 1, pp. 87–104, 2010.

[3] J. D. Fearon and D. D. Laitin,  
"Ethnicity, Insurgency, and Civil War,"  
*American Political Science Review*, vol. 97, no. 1, pp. 75–90, 2003.

[4] A. Slingsby, J. Dykes, and J. Wood,  
"Using Treemaps for Variable Selection in Spatio-Temporal Visualisation,"  
*Information Visualization*, vol. 7, pp. 210–224, 2008.

[5] A. M. Al-Deen,  
"Big Data Analytics in Crisis Management,"  
*IEEE International Conference on Big Data*, 2019.

[6] R. K. L. Ko,  
"Web-based Geovisualization for Crisis Data,"  
*IEEE Transactions on Visualization and Computer Graphics*, vol. 20, no. 1, 2014.

[7] Y. Htung,  
"Conflict Analysis of the Kachin Independence Organization and Myanmar Army,"  
*Thammasat Review*, vol. 21, no. 2, 2018.

[8] Z. T. Khan,  
"The Dynamics and Implications of the Myanmar Civil War,"  
*Academia Journal of Humanities & Social Sciences*, 2025.
