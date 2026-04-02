# NLP Integration Strategy: Myanmar Conflict Observatory

This document outlines the strategic framework for incorporating **Natural Language Processing (NLP)** into the Myanmar Conflict Observatory, as discussed for the project's analytical roadmap.
## 1. Overview
The ACLED dataset provides a rich `notes` column containing detailed qualitative descriptions of each conflict event. By applying NLP techniques, we have already begun transforming these unstructured narratives into structured insights, revealing patterns that traditional categorical data (e.g., event types) may overlook.

---

## 2. Core NLP Analytical Pillars (Implemented & Future)

### 2.1 Keyword-Based Feature Extraction (Implemented)
Specialized regex-based NLP engines to identify specific impacts.
- **SDG 3 Health Impacts:** Automated extraction of incidents impacting medical infrastructure (hospitals, clinics) and personnel.
- **Social Vulnerability:** Extraction of indicators such as "Women Targeted," "Girls," and "Political Party" involvement.
- **Status:** Integrated into `src/processing.py` and visualized in the **SDG 3** and **SOCIAL IMPACT** tabs.

### 2.2 Topic Modeling (Theme Extraction - Roadmap)
...

Extract specific sub-entities mentioned in event narratives.
- **Objective:** Identify specific military units (e.g., "Light Infantry Battalion 77"), local PDF group names, specific commanders, or key landmarks.
- **Techniques:** spaCy (rule-based and statistical), HuggingFace Transformers (BERT-based models).
- **Visualization:** Most frequent "Specific Units Involved" list or regional entity maps.

### 2.3 Narrative Intensity (Sentiment & Severity Analysis)
Quantify the descriptive severity of an event beyond fatality counts.
- **Objective:** Distinguish between "brief exchanges of fire" and "prolonged artillery assaults" or "systematic raids."
- **Techniques:** VADER, TextBlob, or fine-tuned Transformer models for conflict-specific sentiment.
- **Visualization:** A "Narrative Severity Index" that maps the intensity of violence described in notes.

### 2.4 Semantic Search & Clustering
Enable researchers to find related events based on meaning rather than keywords.
- **Objective:** Find events involving "human shields" or "extortion" even if those exact terms aren't used, by using vector embeddings.
- **Techniques:** Sentence-Transformers (SBERT), Vector Databases (ChromaDB or pgvector).
- **Visualization:** Interactive clustering maps (t-SNE/UMAP) of related incident narratives.

---

## 3. Implementation Roadmap

### Phase 1: Preprocessing & Keyword Extraction (Short-term)
- **Action:** Update `db_manager.py` to clean and tokenize the `notes` column.
- **Goal:** Extract top 5 keywords per event and store them in the PostgreSQL database.
- **Visual:** Add a "Trending Keywords" section to the dashboard.

### Phase 2: Theme Classification (Medium-term)
- **Action:** Implement a Topic Modeling pipeline to categorize every event into one of 10-15 "Conflict Themes."
- **Goal:** Enable filtering the dashboard by "Thematic Focus" (e.g., "Economic Impact," "Civic Repression").

### Phase 3: Entity Mapping (Long-term)
- **Action:** Use a fine-tuned NER model to map specific actors to locations.
- **Goal:** Create a "Unit Tracker" to see where specific battalions or PDF groups have been most active.

---

## 4. Recommended Tech Stack
- **spaCy:** For high-speed tokenization, POS tagging, and NER.
- **scikit-learn:** For baseline Topic Modeling (LDA).
- **HuggingFace Transformers:** For deep-learning-based sentiment and semantic embeddings.
- **pgvector:** To store NLP embeddings directly within the existing PostgreSQL database.
