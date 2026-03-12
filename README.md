[မြန်မာဘာသာဖြင့် ဖတ်ရန်](myanmar_translation.md)

# Myanmar Conflict Insight Project

Intially as planned, this project will serves as an analytical toolkit and visualization hub for conflict data in Myanmar. The primary focus is to transform raw, complex datasets into insights and accessible visualizations. 
The current core dataset is sourced from ACLED (Armed Conflict Location & Event Data Project), specifically focusing on the timeframe following the military takeover on February 1, 2021. 

The goal is to and will be provided to researchers, journalists, and analysts with a clear picture of conflict trends, geographical hotspots, and actor dynamics, updated regularly to reflect the evolving situation on the ground. 

### Project Status & Data Update 

     Start Date: February 1, 2021 (Coup d'état).
     End Date: Current Date (Rolling update).
     Update Mechanism: Currently, the dataset is updated manually to ensure data integrity and curation. The system is designed to allow easy injection of new dated data.
         Future Goal: Develop a script to automate the fetching and cleaning of ACLED data via API or scraper to ensure real-time accuracy.
              
This project utilizes data from the Armed Conflict Location & Event Data Project (ACLED). 

     Provider: ACLED 
     Location: Myanmar
     Timeframe: Feb 1, 2021 – Present
     License: The analysis code in this repository is open source. However, ACLED data is proprietary. Users must register with ACLED to access the raw data files. This repository does not redistribute the raw proprietary data files.
     
### Possibilities & Scope 

It intends to expand beyond simple data aggregation. Below are the core analytical possibilities currently being explored or implemented: 

1. Temporal Analysis 

     - Conflict Frequency: Time-series graphs tracking the number of conflict events per day/week/month.
     - Fatality Trends: Analysis of reported fatalities over time to identify spikes in violence.
     - Event Typology: Breakdown of event types (e.g., Battles, Violence against civilians, Protests, Riots).
     

2. Geospatial Analysis 

     - Conflict Hotspots: Mapping events to identify high-risk regions (State/Region, Township level).
     - Displacement Correlation: (Potential) Overlaying conflict data with IDP (Internally Displaced Persons) camp data to visualize movement triggers.
     - Actor Control Zones: Visualizing areas of influence for different armed groups (Military/SAC, EAOs, PDFs).

3. Actor Dynamics 

     - Actor Interaction: Network graphs showing which actors are fighting whom.
     - Most Active Actors: Ranked lists of groups involved in the highest number of conflict events.
     

4. Advanced Insights (Roadmap) 

     Although it is not confirmed, it is pretty much expected with some foundational Machine Learning integrated in the system possibly
     - Natural Language Processing (NLP): Analyzing the "Notes" section of ACLED data to extract keywords and sentiment regarding specific incidents.
     - Predictive Modeling: Experimenting with basic time-series forecasting to estimate near-future conflict intensity in specific regions.
     
### Collaborators

- **Tain Yan Tun** - Data Engineer (Undergraduate)
- **Kyaw Zay Aung** - Data Analyst (Undergraduate)

### Disclaimer & Ethics 

     The data analyzed involves real-world violence, suffering, and human rights issues. The goal of this project is to provide objective clarity for research purposes, not to sensationalize.
     ACLED data is derived from media reports and may not capture every incident. Visualizations are only as accurate as the underlying data source.
     All credit for the raw data belongs to ACLED. The analysis and code produced in this repository are provided under the MIT License.
     

### License 

The code in this repository is licensed under the [MIT License](LICENSE). 
Information on political violence and protest events is sourced from the Armed Conflict Location & Event Data Project (ACLED). 
