# Source Adapters

The HICE framework uses an adapter pattern to remain source-agnostic. Any dataset with a free-text narrative column can be plugged in by implementing the `SourceAdapter` interface.

**File:** `hice_framework/_adapter.py`

## Interface: `SourceAdapter`

```python
class SourceAdapter(ABC):
    @abstractmethod
    def get_notes(self, df: pd.DataFrame) -> pd.Series:
        """Return the free-text narrative column (lowercased)."""

    @abstractmethod
    def get_structure_mask(self, df: pd.DataFrame) -> pd.Series:
        """Return boolean mask: True for kinetic events."""

    def get_event_type_col(self, df: pd.DataFrame) -> pd.Series:
        """Optional: event-type column for calculate_hice_intensity()."""
```

## Built-in Adapters

### `ACLEDAdapter`

For the Armed Conflict Location and Event Data Project format.

**Expected columns:** `notes`, `event_type`, `sub_event_type`

```python
class ACLEDAdapter(SourceAdapter):
    ATTACK_SUB_TYPES = [
        "Attack", "Shelling/artillery/missile attack", "Air/drone strike",
        "Abduction/forced disappearance", "Arrests", "Looting/property destruction",
    ]
    VIOLENT_EVENT_TYPES = [
        "Violence against civilians", "Battles", "Explosions/Remote violence",
    ]

    def get_notes(self, df):
        return df["notes"].fillna("").str.lower()

    def get_structure_mask(self, df):
        return (
            df["sub_event_type"].isin(self.ATTACK_SUB_TYPES)
            | df["event_type"].isin(self.VIOLENT_EVENT_TYPES)
        )

    def get_event_type_col(self, df):
        return df["sub_event_type"]
```

- **Layer 1 gate:** Passes events where `sub_event_type` matches attack types OR `event_type` matches violent types
- **Notes:** Uses the ACLED `notes` column directly

### `UCDPGEDAdapter`

For the UCDP Georeferenced Event Dataset format.

**Expected columns:** `source_article`, `type_of_violence`

```python
class UCDPGEDAdapter(SourceAdapter):
    def get_notes(self, df):
        return df["source_article"].fillna("").str.lower()

    def get_structure_mask(self, df):
        return pd.Series(True, index=df.index)  # All UCDP events are kinetic

    def get_event_type_col(self, df):
        return df["type_of_violence"].map(
            {1: "state-based", 2: "non-state", 3: "one-sided"}
        )
```

- **Layer 1 gate:** All events pass (UCDP GED only contains violent events)
- **Notes:** Extracted from `source_article` column containing "Source,Date,Headline" triples
- **Event type:** Maps `type_of_violence` codes to readable labels

## Usage

```python
from hice_framework import ACLEDAdapter, detect_hice_from_source

df = pd.read_csv("data.csv")
mask = detect_hice_from_source(df, ACLEDAdapter())
hice_df = df[mask].copy()
```

## Creating a Custom Adapter

To use the HICE framework with a different data source (e.g., ICEWS, GDELT, local datasets):

```python
from hice_framework import SourceAdapter, detect_hice_from_source

class MyCustomAdapter(SourceAdapter):
    def get_notes(self, df):
        return df["narrative"].fillna("").str.lower()

    def get_structure_mask(self, df):
        # Define which rows are kinetic events
        return df["event_type"].isin(["Battle", "Explosion", "Attack"])

mask = detect_hice_from_source(my_df, MyCustomAdapter())
```
