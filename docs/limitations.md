# Limitations
This document outlines the known limitations and assumptions of the developed prototype.

> **🔬 Research software notice**: This document is part of a research prototype (v2025.11) and serves as implementation guidance. Scientific references are included for contextual understanding and further reading only. The peer-reviewed scientific contribution can only be found in the published article.


## Table of Contents
- [1. Testing & Validation](#1-testing--validation)
- [2. Technical Limitations](#2-technical-limitations)
- [3. Assumptions](#3-assumptions)
- [4. Known Issues](#4-known-issues)

<br>

---

<br>

## 1. Testing & Validation

The repository includes comprehensive tests to validate core functionality.

**Table 1.1.** Test Coverage (Total: 116 tests)

<table>
<thead>
<tr><th width="20%">Component</th><th width="40%">Test Coverage</th></tr>
</thead>
<tbody>
<tr><td>Module 1 (18 tests)</td><td>Indicator calculations, formula evaluation, variable lookups</td></tr>
<tr><td>Module 2 (23 tests)</td><td>Aggregation, threshold filtering, normalization</td></tr>
<tr><td>Module 3 (22 tests)</td><td>Weighting, scoring, and ranking</td></tr>
<tr><td>Module 4 (5 tests)</td><td>Grouping logic, statistics calculation, multi-level grouping</td></tr>
<tr><td>Module 5 (6 tests)</td><td>Cumulative calculation, component aggregation, profit analysis</td></tr>
<tr><td>Module 6 (8 tests)</td><td>Matplotlib, data preparation, pivot tables</td></tr>
<tr><td>Config validation (21 tests)</td><td>Configuration structure, weight validation, threshold consistency</td></tr>
<tr><td>Integration tests (13 tests)</td><td>Module compatibility, pipeline consistency, data preservation</td></tr>
</tbody>
</table>


The framework has been validated with the following experimental setup:

**Experiments:**
- 96 full-factorial experiments (4 systems × 6 product portfolios × 4 automation levels)
- Feasibility distribution: 61 feasible (63.5%), 35 infeasible (36.5%)

**Indicators (6 KPIs):**
- Direction: 3 minimize (IND01, IND03, IND04), 3 maximize (IND02, IND05, IND06)
- Calculation level: Process/Component (IND01, IND03, IND05, IND06), Resource (IND02), Product (IND04)
- Aggregation: Sum (IND01, IND03, IND05, IND06), Mean (IND02, IND04)

**Groups (7 configurations):**
- Single-factor: 5 groups (by system, product, etc.)
- Two-factor: 1 group (system × product)
- Three-factor: 1 group (full interaction)
- Derived variables: 1 (automation level: manual/low/medium/high)

**Visualizations (16 charts):**
- Types: bar (4), spider (2), heatmap (4), boxplot (3), line (3)
- Data sources: experiments, groups, disassembly depth analysis

<br>

---

<br>

## 2. Technical Limitations

**Input format:**
- The framework requires preprocessed simulation outputs in a specific CSV format
- Column names must match the expected schema (see [`preprocessing/preprocessing.py`](../preprocessing/preprocessing.py))
- No automatic schema validation is performed (missing columns can cause runtime failures)
- Missing attribute lookups default to 0, which may produce incorrect calculations

**Processing constraints:**
- All data is loaded into memory with no streaming support
- No incremental or resume capability is available for interrupted processing
- The framework has been tested with up to 96 experiments; larger datasets may require chunked processing


**Indicator formulas:**
- Formulas use Python `eval()` with restricted context (arithmetic operations only)
- No conditional logic or complex functions are supported
- Workaround: define separate indicators with different filters

**Indicator weighting:**
- AHP weights currently sum to 0.996 (not exactly 1.0)
- No automatic weight normalization is performed
- Manual adjustments are required when adding or removing indicators

**Visualization:**
- Chart types are fixed and defined in [`modules/module6_visualizations.py`](../modules/module6_visualizations.py)
- Adding new chart types requires code modification

<br>

---

<br>

## 3. Assumptions

**Threshold design:**
- Each indicator has a single threshold per direction (minimum for maximize, maximum for minimize)
- No support is provided for acceptable ranges (e.g., 40% to 50%)
- Workaround: Define separate upper and lower bound indicators

**Normalization:**
- Framework uses only linear functions for the normalization
- Weighting is applied within normalized ranges

**Independence:**
- Indicators are assumed to be independent (no interaction effects are considered)
- Users must ensure that indicators measure distinct aspects

**Binary classification:**
- Experiments are classified as either "feasible" (all thresholds met) or "infeasible" as soon as one threshold is not met
- (Threshold violations result in negative normalized scores)


**Aggregation level:**
- Statistics are calculated bottom-up from the component-level and product-level data (requires detailed experiment data)


<br>

---

<br>

## 4. Known Issues

**Preprocessing scalability:**
- Event logs are loaded entirely into memory
- Experiments with many events may require a more efficient approach

**Precision loss:**
- Fixed 2-decimal rounding is applied throughout the pipeline
- Errors may accumulate in multi-stage calculations


**The framework represents a domain-specific implementation with hardcoded elements specific to the disassembly domain:**
- Component naming: comp_XXX_ prefixes, specific activity types (BOSP, BAT, RT, FAX, RAX)
- Output structure: Module prefixes (M0_, M1_, M2_, etc.)
- Quality defaults: Fixed quality = 1.0 for missing values
- Display formatting: Specific rounding, color schemes, and plot dimensions

**Note:** Adapting the framework to different domains requires reviewing these conventions. Product types can be configured via [`config_mappings.json`](../data/config/config_mappings.json).