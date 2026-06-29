# Research Proposal: A Framework for Detecting Healthcare Interference in Conflict Zones

**Student:** Tain Yan Tun
**Department:** Faculty of Information Technology
**Institution:** Asia Pacific International University

---

## Introduction

In armed conflicts around the world, healthcare facilities, medical workers, and patients often become targets of violence. Hospitals are bombed, doctors are arrested, and clinics are forced to shut down. These incidents are documented by organizations that track conflict events, but the information is usually recorded in written narratives rather than structured categories. This means that when someone searches for attacks on healthcare, many incidents go unnoticed simply because they were never labeled as such.

The problem is not a lack of data but a lack of the right tools to interpret it. Current methods for tracking attacks on healthcare rely either on manual reading — which cannot keep up with the volume of information — or on pre-assigned categories that often miss the full picture. There is no existing system specifically designed to automatically identify healthcare interference from conflict reports in a way that is both reliable and transparent.

This research proposes a new framework that fills this gap. The framework itself is the primary contribution: a method that can identify when healthcare has been affected in conflict narratives and classify the type of interference. It is designed to be transparent, meaning every decision it makes can be traced back to clear rules. It does not require training data or black-box algorithms, making it suitable for humanitarian contexts where accountability matters. The framework is demonstrated through a case study of Myanmar, one of the most dangerous conflict zones for healthcare delivery today.

## The Problem

When an artillery shell hits a building, conflict databases record the event type, location, and number of casualties. But they often do not record that the building was a clinic, that the person killed was a nurse, or that an entire community lost access to maternal care. These details exist only in the written description of the event — details that are invisible to standard queries.

International organizations document thousands of attacks on healthcare every year. Their work is valuable, but it relies on structured tags and manual verification, meaning incidents described only in narrative form fall through the cracks. Meanwhile, modern artificial intelligence approaches require large amounts of pre-labeled examples that do not exist for conflict zones, and their decision-making process is often opaque, making them unsuitable where lives are at stake.

## The Framework

The proposed framework addresses these limitations through a transparent, rule-based approach. Instead of learning from examples, it uses clearly defined criteria to analyze written text. This makes it fully verifiable, any decision it makes can be examined by a human reviewer.

The framework processes conflict narratives through multiple stages to identify when healthcare has been affected. It connects healthcare-related language with indicators of violence, and filters out cases where healthcare appears only as background context rather than the subject of interference. When an incident is identified, it is classified by the type of impact whether it involves damage to facilities, targeting of personnel, disruption of access, or interference with supplies. The framework also produces vulnerability scores that rank regions by the severity of healthcare interference, supporting evidence-based humanitarian decision-making.

The framework itself is the central contribution of this research. It is a new method for extracting meaningful information from unstructured text — one that can be adapted to other conflict zones, other types of infrastructure, and other humanitarian concerns.

## Demonstration: Myanmar

To demonstrate the framework, it is applied to conflict data from Myanmar, where wides.pread violence following the 2021 military takeover has created one of the most dangerous environments for healthcare delivery in the world. Over 80,000 conflict events have been recorded in the country between 2021 and 2025.

Applying the framework reveals the scale and nature of healthcare interference that structured records alone would miss. It identifies hundreds of verified incidents, shows which types of interference are most common, which regions are most affected, and how patterns have changed over time. These findings are compiled into vulnerability rankings that highlight where humanitarian resources are most needed.

This case study serves two purposes: it validates that the framework works on real-world data, and it provides actionable insights for organizations working to protect healthcare in Myanmar.

## Validation

The framework is validated through multiple methods. A sample of detected incidents is manually reviewed. An automated verification process checks a larger sample across multiple rounds. The classification of incidents by type is validated separately. A sensitivity analysis confirms that regional rankings remain stable when scoring weights are adjusted, ensuring the results are robust.

## Expected Outcomes

This research produces three main outcomes. First, a fully documented framework for detecting healthcare interference from conflict narratives, designed to be transparent, reproducible, and adaptable. Second, a detailed analysis of healthcare interference in Myanmar based on the application of this framework, including regional vulnerability rankings. Third, an open-source implementation and an interactive dashboard for exploring the findings.

## Conclusion

Attacks on healthcare in conflict zones are a documented reality, but current methods of tracking them miss a significant portion of incidents hidden in unstructured text. This research addresses that gap by building a framework specifically designed to detect healthcare interference from conflict narratives. The framework itself is the central contribution — a transparent, rule-based method that does not require training data and can be verified by human reviewers. Its application to Myanmar demonstrates its value in practice, revealing patterns of healthcare interference that would otherwise remain invisible.
