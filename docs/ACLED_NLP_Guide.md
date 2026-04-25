# How to Analyze ACLED’s Notes Column using Natural Language Processing (NLP)

*Source: ACLED Documentation*

Explore how to use NLP to analyze ACLED's ‘Notes’ column for extracting insights beyond the structured variables.

---

## Understanding the ACLED ‘Notes’ Column

The ‘Notes’ column provides a brief summary of the main features of the event, typically two sentences long. While the notes reflect the variables coded in other ACLED columns, they can also provide additional information regarding the events not captured in the structured variables.

| Category | Information in the ‘Notes’ Column | What can be Extracted with Keyword Searches |
| :--- | :--- | :--- |
| **Who** | Actors involved (sometimes providing more details beyond coded actors). | Identify additional actors involved not captured in coded fields. |
| **What** | Narrative version of event details describing actor activity and interaction. | Identify additional tactics, weapons, or multiple forms of violence. |
| **Where** | Precise location details beyond the coded village/town level. | Extract granular location details (e.g., “market”, “school”). |
| **Why** | The immediate cause or motive of the event. | Identify motives (e.g., election-related, protest motivations). |
| **Fatalities** | Details on injuries, varying fatality estimates, or affiliations. | Extract injury counts and ranges of reported fatalities. |

### Examples of ‘Notes’ Entries

*   **Example 1 – Event Type: Explosions/Remote Violence**
    > “On 28 May 2024, an Algerian army drone targeted Saharawi and Mauritanian gold miners operating near Dakhla refugee camp (Tindouf, Tindouf). Between 10 and 12 people were killed.“

*   **Example 2 – Event Type: Battles**
    > “On 30 May 2024, JNIM militants ambushed a patrol of gendarmes near the village of Gassel (Bani, Seno). Nine gendarmes were killed, 22 were injured, and one was reported missing.“

---

## Extracting Information from ‘Notes’ Using NLP

Because the ‘Notes’ column is free-text, systematic analysis requires keyword searches and Natural Language Processing (NLP). These methods help:
1. Filter events by keywords (e.g., “injured,” “landmine”).
2. Extract specific details (e.g., neighborhood locations, protest motivations).
3. Classify events automatically using machine learning.

### 1. Keyword-Based Search

Keyword searches are best suited for extracting information beyond the coded variables.

**Example Use Cases:**
*   **Targeting Infrastructure:** Identifying events near educational infrastructure using keywords like “school”, “university”, “academic”.
*   **Specific Weapons:** Identifying events involving “missile”, “rocket”, or “Katyusha”.
*   **Landmarks:** Identifying events near a “market”.

#### Building an Effective Keyword List

*   **Step 1: Review Sample Notes.** Scan notes for regional phrasing variations and localized terms.
*   **Step 2: Apply Standardization.**

| Technique | Purpose | Example |
| :--- | :--- | :--- |
| **Lowercasing** | Standardizes capitalization. | “Election” → “election” |
| **Stemming** | Reduces words to their root form. | “Voting”, “voter” → “vot” |
| **Lemmatization** | Uses linguistic rules to find base forms. | “elected” → “elect”, “children” → “child” |

---

## Model-Based Approaches

ACLED uses model-based approaches like **SetFit (Few-Shot)** for high accuracy with minimal training data (~100 examples per category).

### Choosing the Right Model

| Model Type | Best Use Case | Challenges |
| :--- | :--- | :--- |
| **BERT / RoBERTa** | High-accuracy for large datasets. | Requires hundreds of training examples. |
| **Few-Shot (SetFit)** | Works well with small datasets. | Requires some manual labeling. |
| **Zero-Shot** | Classify without training data. | Often too inaccurate for ACLED data. |

---

## Best Practices

### ✅ Do’s
*   Normalize text (lowercasing, stemming) before searching.
*   Use fuzzy matching to catch variations (e.g., “poll” matching “polling”).
*   Manually review a sample of notes before finalizing a keyword list.
*   Consider classification models if keyword searches produce too many false positives.

### ❌ Don’ts
*   Avoid exact keyword matches for all variations; use normalization instead.
*   Don’t assume uniform phrasing; wording varies by region and researcher.
*   Don’t overcomplicate keyword searches with excessive regex; use NLP models for complex cases.

---

## Annex: Code Snippets (Python)

### Fuzzy Matching
```python
import pandas as pd

keywords = ["polling", "poll", "vote", "ballot", "voting", "voter", "voters", "election", "elections"]
pattern = '|'.join(keywords)

# Case-insensitive search
df['contains_election'] = df['notes'].str.contains(pattern, case=False)
df_elections = df[df['contains_election'] == True]
```

### Exact Matching (Word Boundaries)
```python
import pandas as pd

keywords = ["poll", "vote", "ine"]
pattern = r'\b(' + '|'.join(keywords) + r')\b'

df['contains_election'] = df['notes'].str.contains(pattern, case=False)
```

### Stemming Pre-processing
```python
from nltk.stem import PorterStemmer
import pandas as pd

stemmer = PorterStemmer()
keywords = ["voting", "election"]
stemmed_keywords = [stemmer.stem(word) for word in keywords]
pattern = '|'.join(stemmed_keywords)

df['stemmed_notes'] = df['notes'].apply(lambda x: ' '.join([stemmer.stem(word) for word in x.split()]))
df['contains_election'] = df['stemmed_notes'].str.contains(pattern, case=False)
```

### SetFit Model Application
```python
from setfit import SetFitModel

# Load a pre-trained model
model = SetFitModel.from_pretrained("trained_model")

# Apply and get probabilities
results = model.predict_proba(df["notes"].to_list())
probs, preds = results.max(dim=1)
df["pred_prob"] = probs
df["pred"] = preds
```
