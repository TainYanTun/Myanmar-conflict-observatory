# Research Pipeline Notebook
## Author: Gemini

This notebook implements a 5-stage research pipeline for analyzing conflict data.


```python
appName = "researchPipeline"
import pandas as pd
import numpy as np
import os
```

## Stage 1: Ingestion

In this stage, we load the raw ACLED data into the notebook.


```python
data_path = "data/ACLED Data Feb 14 2026.csv"
df = pd.read_csv(data_path)
print(f"Loaded {len(df)} rows.")
df.head()
```

    Loaded 91441 rows.





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>event_id_cnty</th>
      <th>event_date</th>
      <th>year</th>
      <th>time_precision</th>
      <th>disorder_type</th>
      <th>event_type</th>
      <th>sub_event_type</th>
      <th>actor1</th>
      <th>assoc_actor_1</th>
      <th>inter1</th>
      <th>...</th>
      <th>location</th>
      <th>latitude</th>
      <th>longitude</th>
      <th>geo_precision</th>
      <th>source</th>
      <th>source_scale</th>
      <th>notes</th>
      <th>fatalities</th>
      <th>tags</th>
      <th>timestamp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>MMR16462</td>
      <td>2021-05-05</td>
      <td>2021</td>
      <td>1</td>
      <td>Strategic developments</td>
      <td>Strategic developments</td>
      <td>Looting/property destruction</td>
      <td>Military Forces of Myanmar (2021-)</td>
      <td>NaN</td>
      <td>State forces</td>
      <td>...</td>
      <td>Tha Min Chan</td>
      <td>22.3606</td>
      <td>94.8957</td>
      <td>1</td>
      <td>Democratic Voice of Burma</td>
      <td>National</td>
      <td>Looting: On 5 May 2021, in Tha Min Chan villag...</td>
      <td>0</td>
      <td>NaN</td>
      <td>1620765673</td>
    </tr>
    <tr>
      <th>1</th>
      <td>MMR16496</td>
      <td>2021-05-05</td>
      <td>2021</td>
      <td>1</td>
      <td>Strategic developments</td>
      <td>Strategic developments</td>
      <td>Looting/property destruction</td>
      <td>RCSS/SSA-S: Restoration Council of Shan State/...</td>
      <td>PSLF/TNLA: Palaung State Liberation Front/Ta'a...</td>
      <td>Rebel group</td>
      <td>...</td>
      <td>Yae Oe</td>
      <td>22.8118</td>
      <td>97.3299</td>
      <td>1</td>
      <td>Irrawaddy</td>
      <td>National</td>
      <td>Property destruction: On 5 May 2021, in Yae Oe...</td>
      <td>0</td>
      <td>NaN</td>
      <td>1753971383</td>
    </tr>
    <tr>
      <th>2</th>
      <td>MMR16128</td>
      <td>2021-05-05</td>
      <td>2021</td>
      <td>1</td>
      <td>Political violence</td>
      <td>Battles</td>
      <td>Armed clash</td>
      <td>Military Forces of Myanmar (2021-)</td>
      <td>NaN</td>
      <td>State forces</td>
      <td>...</td>
      <td>Hpapun</td>
      <td>18.0650</td>
      <td>97.4449</td>
      <td>2</td>
      <td>Karen Information Center News</td>
      <td>Subnational</td>
      <td>On 5 May 2021, between Hpapun and Khapu, Hpapu...</td>
      <td>7</td>
      <td>NaN</td>
      <td>1753971383</td>
    </tr>
    <tr>
      <th>3</th>
      <td>PHL12117</td>
      <td>2021-05-05</td>
      <td>2021</td>
      <td>1</td>
      <td>Demonstrations</td>
      <td>Protests</td>
      <td>Peaceful protest</td>
      <td>Protesters (Philippines)</td>
      <td>LIPI: Liga Independencia Pilipinas; LPP: Leagu...</td>
      <td>Protesters</td>
      <td>...</td>
      <td>Makati</td>
      <td>14.5502</td>
      <td>121.0326</td>
      <td>1</td>
      <td>Philippine News Agency</td>
      <td>National</td>
      <td>On 5 May 2021, anti-communist groups led by th...</td>
      <td>0</td>
      <td>crowd size=no report</td>
      <td>1628035296</td>
    </tr>
    <tr>
      <th>4</th>
      <td>IDN5951</td>
      <td>2021-05-05</td>
      <td>2021</td>
      <td>1</td>
      <td>Demonstrations</td>
      <td>Protests</td>
      <td>Peaceful protest</td>
      <td>Protesters (Indonesia)</td>
      <td>NaN</td>
      <td>Protesters</td>
      <td>...</td>
      <td>Purworejo</td>
      <td>-7.7141</td>
      <td>110.0082</td>
      <td>1</td>
      <td>Detik</td>
      <td>National</td>
      <td>On 5 May 2021, a group of people held a peacef...</td>
      <td>0</td>
      <td>crowd size=no report</td>
      <td>1759789823</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 31 columns</p>
</div>



### Reflection - Stage 1
* **What I learned:** I learned how to efficiently load large CSV datasets using pandas and the importance of verifying the file path relative to the notebook location.
* **Challenge faced:** The dataset contains many columns, making it difficult to visualize the entire structure at once.
* **How I solved it:** I used `df.head()` and `df.columns` to inspect the most relevant fields first.

## Stage 2: Validation & Cleaning

This stage involves detecting and fixing incorrect or missing values to ensure data quality.


```python
# Convert event_date to datetime
df['event_date'] = pd.to_datetime(df['event_date'])

# Handle missing fatalities by filling with 0
df['fatalities'] = df['fatalities'].fillna(0)

# Drop duplicates
df = df.drop_duplicates()

print("Data cleaned and validated.")
```

    Data cleaned and validated.


### Reflection - Stage 2
* **What I learned:** I learned that real-world data often has inconsistent date formats and missing numerical values that can break analysis.
* **Challenge faced:** Determining whether a missing 'fatalities' value meant zero or 'unknown'.
* **How I solved it:** I decided to fill with 0 to maintain numerical consistency while noting that it represents a conservative estimate.

## Stage 3: Transformation

Creating new features to enhance the dataset for deeper analysis.


```python
# Extract temporal features
df['month'] = df['event_date'].dt.month
df['day_of_week'] = df['event_date'].dt.day_name()

# Create high_fatality indicator
df['high_fatality'] = df['fatalities'] > 10

print("Transformation complete. New features added.")
```

    Transformation complete. New features added.


### Reflection - Stage 3
* **What I learned:** I learned how to use the `.dt` accessor in pandas to extract granular time information from datetime objects.
* **Challenge faced:** Creating meaningful categorical groups from continuous fatality numbers.
* **How I solved it:** I implemented a binary 'high_fatality' threshold to quickly identify significant events.

## Stage 4: Aggregation

Summarizing data to compute insights.


```python
# Group by event type and compute stats
summary_stats = df.groupby('event_type').agg({
    'event_id_cnty': 'count',
    'fatalities': ['sum', 'mean']
}).reset_index()

summary_stats.columns = ['event_type', 'event_count', 'total_fatalities', 'average_fatalities']
print("Aggregation complete.")
summary_stats
```

    Aggregation complete.





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>event_type</th>
      <th>event_count</th>
      <th>total_fatalities</th>
      <th>average_fatalities</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Battles</td>
      <td>18880</td>
      <td>53009</td>
      <td>2.807680</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Explosions/Remote violence</td>
      <td>19313</td>
      <td>17963</td>
      <td>0.930099</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Protests</td>
      <td>25573</td>
      <td>24</td>
      <td>0.000938</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Riots</td>
      <td>1056</td>
      <td>277</td>
      <td>0.262311</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Strategic developments</td>
      <td>16059</td>
      <td>168</td>
      <td>0.010461</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Violence against civilians</td>
      <td>10560</td>
      <td>10249</td>
      <td>0.970549</td>
    </tr>
  </tbody>
</table>
</div>



### Reflection - Stage 4
* **What I learned:** I learned how to use multi-index aggregations to calculate multiple statistics for the same group in one pass.
* **Challenge faced:** The resulting multi-index columns were difficult to work with for downstream tasks.
* **How I solved it:** I flattened the column headers immediately after aggregation for better readability.

## Stage 5: Output

Exporting the results for analysis or machine learning.


```python
output_file = "data/processed_research_data.csv"
summary_stats.to_csv(output_file, index=False)
print(f"Final results saved to {output_file}")
```

    Final results saved to data/processed_research_data.csv


### Reflection - Stage 5
* **What I learned:** I learned the importance of disabling index saving in `to_csv` to avoid adding redundant columns to the final file.
* **Challenge faced:** Ensuring the output directory exists before saving.
* **How I solved it:** I verified the directory structure manually, but in a production script, I would use `os.makedirs(exist_ok=True)`.
