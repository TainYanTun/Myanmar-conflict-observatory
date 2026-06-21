"""
Source adapter interface and built-in implementations.

The HICE framework is source-agnostic. To use it with a new data source,
implement the ``SourceAdapter`` ABC and pass it to ``detect_hice_from_source()``.
"""

import pandas as pd
from abc import ABC, abstractmethod


class SourceAdapter(ABC):
    """Abstract base adapter for plugging in any conflict event data source."""

    @abstractmethod
    def get_notes(self, df: pd.DataFrame) -> pd.Series:
        """
        Return the free-text narrative column (lowercased).
        Used by Layer 2 as input to all NLP signals.
        """

    @abstractmethod
    def get_structure_mask(self, df: pd.DataFrame) -> pd.Series:
        """
        Return a boolean mask: True for kinetic events that can plausibly
        impact health infrastructure (battles, explosions, attacks, etc.).
        Used by Layer 1 as the structural gate.
        """

    def get_event_type_col(self, df: pd.DataFrame) -> pd.Series:
        """
        Optional: return an event-type column for ``calculate_hice_intensity()``.
        """
        raise NotImplementedError(
            "get_event_type_col() not implemented; "
            "calculate_hice_intensity() will not be available."
        )


class ACLEDAdapter(SourceAdapter):
    """
    Adapter for the Armed Conflict Location and Event Data Project (ACLED).

    Expected columns: ``notes``, ``event_type``, ``sub_event_type``.
    """

    ATTACK_SUB_TYPES = [
        "Attack", "Shelling/artillery/missile attack", "Air/drone strike",
        "Abduction/forced disappearance", "Arrests", "Looting/property destruction",
    ]
    VIOLENT_EVENT_TYPES = [
        "Violence against civilians", "Battles", "Explosions/Remote violence",
    ]

    def get_notes(self, df: pd.DataFrame) -> pd.Series:
        return df["notes"].fillna("").str.lower()

    def get_structure_mask(self, df: pd.DataFrame) -> pd.Series:
        return (
            df["sub_event_type"].isin(self.ATTACK_SUB_TYPES)
            | df["event_type"].isin(self.VIOLENT_EVENT_TYPES)
        )

    def get_event_type_col(self, df: pd.DataFrame) -> pd.Series:
        return df["sub_event_type"]


class UCDPGEDAdapter(SourceAdapter):
    """
    Adapter for UCDP Georeferenced Event Dataset (UCDP GED).

    Expected columns: ``source_article``, ``type_of_violence``.
    All UCDP GED events are kinetic by definition.
    The ``source_article`` column contains semicolon-separated
    ``"Source,Date,Headline"`` triples providing narrative signal.
    """

    def get_notes(self, df: pd.DataFrame) -> pd.Series:
        return df["source_article"].fillna("").str.lower()

    def get_structure_mask(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(True, index=df.index)

    def get_event_type_col(self, df: pd.DataFrame) -> pd.Series:
        return df["type_of_violence"].map(
            {1: "state-based", 2: "non-state", 3: "one-sided"}
        )
