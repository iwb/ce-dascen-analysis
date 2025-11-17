# Disassembly Scenario Analysis Framework (DASCEN-ANALYSIS)

> **⚠️ Note**
> The associated research article for this repository is currently under review. Information such as DOI, citation format, and license will be updated after the article is published.

![Version](https://img.shields.io/badge/version-2025.11-blue)
![Status](https://img.shields.io/badge/status-research%20prototype-orange)
![Experiments](https://img.shields.io/badge/experiments-96-green)
![Indicators](https://img.shields.io/badge/indicators-6-green)

This repository provides a configuration-driven analytics framework for the multi-criteria decision analysis in tactical disassembly planning. The framework processes simulation outputs of various experiments to compare different disassembly scenarios.

> **🔬 Research software notice**
>
> This is a **research prototype** (v2025.11) developed for academic purposes. The prototype has been verified with a full-factorial experimental design. See [`docs/experiment-configuration.md`](docs/experiment-configuration.md) for the specific use case implementation. This repository provides supplementary materials to facilitate the practical application and reproduction of the prototype described in the associated scientific publication. The content of this guide is intended to provide an implementation guidance and a technical documentation for users. While scientific references are included in some documents, they are solely intended to provide contextual understanding and sources for further reading. The peer-reviewed scientific contribution can only be found in the published article. For an overview of the scientific outcomes and contributions, please refer to the publication.

## Table of Contents
- [Contact](#contact)
- [1. Introduction](#1-introduction)
  - [1.1 Framework Documentation](#11-framework-documentation)
  - [1.2 Related Research Work and Repositories](#12-related-research-work-and-repositories)
- [2. System Architecture](#2-system-architecture)
- [3. Usage Instructions](#3-usage-instructions)
  - [3.1 Quick Start](#31-quick-start)
  - [3.2 Customization](#32-customization)
  - [3.3 Running Tests](#33-running-tests)
- [4. Configuration and Output](#4-configuration-and-output)
- [5. Project Structure](#5-project-structure)
- [Citation](#citation)
- [License](#license)

<br>

---

<br>


## Contact
### Contact Details
Corresponding author: Patrick Jordan  
Institutional email: patrick.jordan@iwb.tum.de  
Personal profile: [patrick-jordan.github.io](https://patrick-jordan.github.io/) (for future correspondence)


### Useful Links
- **[Visit our other repositories](https://iwb.github.io)**
Explore more tools and resources from our research institute.

- **[Visit our institute for more information](https://www.mec.ed.tum.de/en/iwb/homepage/)**
Learn more about our research and ongoing projects.

<br>

---

<!-- ================================================== -->
<!-- INTRODUCTION SECTION -->
<!-- ================================================== -->

<br>

## 1. Introduction
This framework provides a tool for the multi-criteria decision analysis of disassembly scenarios. Each **disassembly scenario** is defined by a distinct **system design scenario** (i.e., layout and workstation configurations) and a **product scenario** (i.e., incoming products and disassembly depths). Its development was inspired by the research  of [Jordan et al. (2024)](#jordan-et-al-2024) and aims to assist in decision-making processes of tactical disassembly planning.  

The model can be used to analyze experiments across multiple dimensions such as:
- different workstation configurations (manual vs. automated processing),
- system configurations (number of stations, division strategies), and
- product portfolio variations (product mix, disassembly depth).

Key capabilities include:
- a multi-criteria ranking system with weighted indicators and a threshold-based feasibility assessment,
- a configuration-driven architecture using JSON definitions for indicators, groups, and visualizations,
- statistical group analysis with aggregations across configurable experimental dimensions,
- the cost-benefit evaluation of the disassembly depth, and
- various visualizations including spider charts, heatmaps, and boxplots.

**Use case context:**<br>
This framework was verified using a use case from the Smart Production Lab (SPL), a learning factory at the Institute for Machine Tools and Industrial Management (*iwb*) at the Technical University of Munich (https://iwb-spl.de/). A dataset from six disassembly runs of remotely controlled electric buggies (https://github.com/iwb/ce-dascen-lf-data) was used for the verification and scaled to resemble real-world disassembly operations. A full factorial experimental design combining four system configurations, six product portfolios, and four automation levels produced **96 disassembly scenarios** and 96 experiments. See [`docs/experiment-configuration.md`](docs/experiment-configuration.md) for the detailed experimental design.


### 1.1 Framework Documentation
Table 1.1 provides an overview of the relevant documents, including their main content.

<br>

**Table 1.1.** Framework documentation overview

<table>
  <thead>
    <tr>
      <th width="30%">Document</th>
      <th width="70%">Content</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="docs/experiment-configuration.md">Experiment configuration</a></td>
      <td>Data basis for the 96 experiments: 4 systems × 6 portfolios × 4 automation levels, product structures, process times</td>
    </tr>
    <tr>
      <td><a href="docs/indicator_selection.md">Indicator selection</a></td>
      <td>Selection process to identify six indicators</td>
    </tr>
    <tr>
      <td><a href="docs/feature-groups.md">Feature groups</a></td>
      <td>Feature groups to support the exploration of the solution space</td>
    </tr>
    <tr>
      <td><a href="docs/visualizations.md">Visualizations</a></td>
      <td>Information about the visualizations and examples for their possible usage</td>
    </tr>
    <tr>
      <td><a href="docs/limitations.md">Limitations</a></td>
      <td>Framework assumptions and limitations</td>
    </tr>
  </tbody>
</table>

<br>

### 1.2 Related Research Work and Repositories
Table 1.2 provides an overview of the resources used in this framework, including their associated GitHub repositories and publications.

<br>

**Table 1.2.** Related research work and repositories

<table>
  <thead>
    <tr>
      <th width="18%">Resource</th>
      <th width="35%">Purpose</th>
      <th width="20%">Results/data location</th>
      <th width="17%">Repository</th>
      <th width="10%">Publication</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Simulation model</td>
      <td>Used to generate the simulation data for the 96 experiments</td>
      <td><a href="experiment_data/">experiment_data/</a></td>
      <td><a href="https://github.com/iwb/ce-dascen-sim">View repository</a></td>
      <td>TBA<sup>†</sup></td>
    </tr>
    <tr>
      <td>Learning factory dataset</td>
      <td>Provided the empirical disassembly data for the experiment configuration</td>
      <td><a href="docs/experiment-configuration.md">experiment-configuration.md</a></td>
      <td><a href="https://github.com/iwb/ce-dascen-lf-data">View repository</a></td>
      <td>-</td>
    </tr>
    <tr>
      <td>Sustainability indicator selection tool</td>
      <td>Applied to select the six performance indicators using a structured methodology</td>
      <td><a href="docs/indicator_selection.md">indicator_selection.md</a></td>
      <td><a href="https://github.com/iwb/sus-kpi-sel">View repository</a></td>
      <td><a href="https://doi.org/10.1016/j.procir.2025.04.001">Jordan et al. (2025)</a></td>
    </tr>
    <tr>
      <td>Research article</td>
      <td>Main publication describing the framework methodology and validation</td>
      <td>—</td>
      <td>—</td>
      <td>TBA<sup>†</sup></td>
    </tr>
  </tbody>
</table>

> **⚠️ Note:** <sup>†</sup> Details will be updated after publication

<br>

---

<!-- ================================================== -->
<!-- SYSTEM ARCHITECTURE -->
<!-- ================================================== -->

<br>

## 2. System Architecture
The framework has a modular architecture with seven processing modules (modules 0-6) that execute sequentially from data loading to visualization generation:

1. **Module 0: Data loader** ([`module0_data_loader.py`](modules/module0_data_loader.py))
   - Loads the design of experiments (DoE) table and simulation outputs from [`experiment_data/`](experiment_data/)
   - Combines the data into consolidated dataframes
   - Loads the attribute tables (product, process, system) from [`data/attributes/`](data/attributes/)

2. **Module 1: Indicator calculation** ([`module1_step_indicators.py`](modules/module1_step_indicators.py))
   - Calculates six indicators using the formulas from [`config_indicators.json`](data/config/config_indicators.json)
   - Performs the attribute lookups from [`data/attributes/`](data/attributes/), including quality-dependent values (component value, circularity ratings)
   - Generates supporting values for the disassembly depth analysis of Module 5 (revenue, costs, profit)

3. **Module 2: Aggregation & normalization** ([`module2_experiment_aggregation.py`](modules/module2_experiment_aggregation.py))
   - Aggregates indicators to the experiment level
   - Applies threshold-based feasibility filters as set in [`config_indicators.json`](data/config/config_indicators.json)
   - Normalizes indicators using ALL experiments (enables negative scores for indicators violating thresholds)

4. **Module 3: Multi-criteria ranking (SAW with AHP weights)** ([`module3_ranking.py`](modules/module3_ranking.py))
   - Applies the defined indicator weights set in [`config_indicators.json`](data/config/config_indicators.json) to the normalized indicators
   - Calculates total weighted scores using Simple Additive Weighting (SAW) method
   - Creates a dual ranking system of experiments (all + feasible only)

5. **Module 4: Group statistics** ([`module4_grouping.py`](modules/module4_grouping.py))
   - Calculates statistics (mean, std, min, max) for the groups defined in [`config_groups.json`](data/config/config_groups.json)
   - Supports the translation of variables (e.g., automation_level 0-6 → manual/low/medium/high)
   - Handles the multi-dimensional group analysis (e.g., system × product_mix, system × automation × stations)

6. **Module 5: Depth analysis** ([`module5_depth_analysis.py`](modules/module5_depth_analysis.py))
   - Calculates profits on the component level using settings from [`config_disassembly_depth.json`](data/config/config_disassembly_depth.json)
   - Creates cumulative profits including the fixed costs of the system
   - Enables the product-specific disassembly depth analysis

7. **Module 6: Visualizations** ([`module6_visualizations.py`](modules/module6_visualizations.py))
   - Generates SVG visualizations that are exported to [`output/visualizations/`](output/visualizations/)
   - Types: bar charts, spider charts, heatmaps, boxplots, line charts (defined in [`config_visualizations.json`](data/config/config_visualizations.json))


**Data flow:**<br>
The data processing follows a sequential pipeline, where the output of each module becomes the input for the next module:

```
    ↓ (simulation data, i.e. case tables, event logs)
Preprocessing: Transform simulation outputs*
    ↓ (structured CSVs)
Module 0: Load data
    ↓ (df_process, df_product, df_resource, df_system, doe)
Module 1: Calculate indicators
    ↓ (configured indicators + supporting values)
Module 2: Aggregate & normalize
    ↓ (df_experiments with normalized indicators, feasibility status)
Module 3: Apply weights & rank
    ↓ (rank_all, rank, total_weighted_score)
Module 4: Group statistics**
    ↓ (df_groups with mean, std, min, max by groups)
Module 5: Depth analysis
    ↓ (component aggregates, cumulative profit trajectories)
Module 6: Visualizations
    ↓ (SVG charts and plots)
```

\* The preprocessing step transforms the raw experiment data from [`experiment_data/outputs/`](experiment_data/outputs/) into an analytics-ready format. The results are stored in the [`data/processed/`](data/processed/) folder

<br>

---

<!-- ================================================== -->
<!-- USAGE INSTRUCTIONS -->
<!-- ================================================== -->

<br>

## 3. Usage Instructions
> Before running the framework, please review the [docs/limitations.md](docs/limitations.md) file to understand the assumptions and tested configurations.

### 3.1 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the complete pipeline:**
```bash
python main.py
```

3. **Check results:**
```bash
# View the experiment rankings in
output/dataframes/df_experiments_ranked_feasible.csv

# View the visualizations in
output/visualizations/

# Expected results
Total experiments: 96
Feasible experiments: 61 (63.5%)
Infeasible experiments: 35 (36.5%)
Top ranked experiment: exp004 (score: 0.7072)
Visualizations generated: 16
```


Table 2.1 shows the basic commands for running the framework.

<br>

**Table 2.1.** Basic usage commands

| Task | Command | Description |
|------|---------|-------------|
| Run full pipeline | `python main.py` | Execute all 6 modules sequentially |
| Test single module | `cd modules && python module3_ranking.py` | Run modules 0-3 only |
| Preprocess raw data | `cd preprocessing && python preprocessing.py` | Convert raw simulation data to structured CSVs |

**Usage examples:**
```bash
# Preprocess the experiment data
cd preprocessing && python preprocessing.py

# Run the complete analysis
python main.py

# View the module 2 summary (normalization statistics)
cat output/reports/module2_summary.txt

# View the module 3 summary (ranking results)
cat output/reports/module3_summary.txt

# Check the group statistics
cat output/groups/M4_01_df_groups_all.csv
```

### 3.2 Customization
The framework has a configuration-driven architecture for evaluating use-case-specific disassembly scenarios. Users can adapt the framework to different experiments, indicators, groups, and visualizations with minimal or no modifications to the modules. All customization takes place via JSON configuration files.

The framework supports the customization for various purposes, including:
- the number of experiments in the analysis,
- the indicator definitions with custom formulas and parameters,
- the visualization types and their combinations,
- the feasibility thresholds for each indicator, and
- the weights for the multi-criteria ranking.

**Example: Adding a new KPI**<br>
The following steps are required to add a new indicator:

1. Edit [`config/config_indicators.json`](data/config/config_indicators.json) to add the new indicator definition with its formula, threshold, weight, and variable sources.
2. Add the required attribute data to the [`data/attributes/`](data/attributes/) directory.
3. Adjust the weights of existing indicators to a sum of 1.0.



### 3.3 Running Tests
The repository includes 116 tests covering all modules.

**Basic test execution:**
```bash
# Run all tests
python -m pytest tests/

# Run with detailed output
python -m pytest tests/ -v --tb=short

# Run specific test module
python -m pytest tests/test_module1_step_indicators.py -v
```

**Test coverage:**
- Module tests (1-6): Indicator calculation, aggregation, ranking, grouping, depth analysis, and visualizations
- Configuration validation: JSON structure, weights, thresholds, and consistency checks
- Integration tests: Module compatibility and full pipeline execution

See [`docs/limitations.md`](docs/limitations.md) for the detailed test coverage breakdown.


<br>

---

<br>

## 4. Configuration and Output
The framework uses a JSON-based configuration architecture that enables the adaptation to different experimental setups. It generates structured outputs for the experiment analysis and visualizations.

**Configuration files:**<br>
The configuration files define the parameters, the calculation formulas, and the analysis dimensions. Modifications to weights, thresholds, or indicators require edits in the following JSON files:
```
data/config/
├── config_disassembly_depth.json   # Aggregation rules for component-level profit analysis
├── config_formatting.json          # Output formatting specifications for visualization
├── config_groups.json              # Analysis group definitions for statistical aggregation
├── config_indicators.json          # Performance indicators with formulas, weights, and thresholds
├── config_mappings.json            # Variable transformations (e.g., automation levels, product types)
├── config_values.json              # Economic value calculations (costs, revenue, profit)
└── config_visualizations.json      # Chart specifications and data mappings
```





**Attribute Files**<br>
The attribute files contain the reference data for the component specifications and resource parameters. These attributes serve as "lookup values" during indicator calculations and are defined in the following files:
```
data/attributes/
├── attributes_disassembly_paths.json  # Component extraction sequences and dependencies
├── attributes_product.json            # Component weights, values, and circularity ratings
├── attributes_resource.json           # Labor rates, power consumption, and fixed costs
└── attributes_system.json             # Energy rates and system-level parameters
```

See [docs/experiment-configuration.md](docs/experiment-configuration.md) for more information about the configuration and attribute files.


**Output Files**<br>
The output files provide experiment rankings, statistical aggregations, and visualizations:
```
output/dataframes/
├── M0_*_df_*.csv                       # Module 0: Loaded dataframes (process, product, resource, system)
├── M2_*_df_experiments_*.csv           # Module 2: Aggregated and feasible experiments
├── M3_*_df_experiments_ranked_*.csv    # Module 3: Ranked experiments (all and feasible)
└── M5_*_depth_*.csv                    # Module 5: Disassembly depth analysis results

output/groups/
├── M4_01_df_groups_all.csv             # Aggregated statistics for all analysis groups
└── M4_*_df_groups_G*.csv               # Group-specific statistical summaries

output/visualizations/
├── M6_*_viz_*.svg                      # Performance rankings and comparisons
└── M6_*_figure_*.svg                   # Figures used in publication

output/reports/
├── module2_summary.txt                 # Normalization statistics and threshold violations
└── module3_summary.txt                 # Ranking results and score distributions
```

See [docs/visualizations.md](docs/visualizations.md) for more information about the visualizations.

<br>

---

<br>

## 5. Project Structure

```
ce-disassembly-decision-framework/
├── data/                    # Input data and configurations
│   ├── attributes/
│   ├── config/
│   └── processed/
├── docs/                    # Documentation
│   └── figures/             # Documentation visualizations
├── experiment_data/         # Experiment inputs and outputs
│   ├── config/
│   └── outputs/
├── modules/                 # Core processing modules (0-6)
│   └── visualizations/      # Visualization utilities
├── output/                  # Analysis results
│   ├── dataframes/
│   ├── groups/
│   ├── reports/
│   └── visualizations/
├── preprocessing/           # Data transformation scripts
├── tests/                   # Test suite
├── main.py                  # Pipeline orchestrator
├── pytest.ini               # Test configuration
└── requirements.txt         # Python dependencies
```

<br>

---

<!-- ================================================== -->
<!-- CITATION SECTION -->
<!-- ================================================== -->

<br>

## Citation
If you use this repository for your research or industry projects, please cite the following article:

> **⚠️ Note** Updated after the publication of the research article
```bibtex
@article{tba.,
}
```

<br>

---

<br>

## License
This repository and its contents are licensed under the [MIT License](./LICENSE).

### Acknowledgements
This research was funded by the Federal Ministry for Economic Affairs and Energy (BMWE) as part of the “SmartMan” project (13IK033J).


## References


#### Jordan et al. 2024
Jordan, P., Kroeger, S., Streibel, L., Vernim, S., Zaeh, M.F., 2024. Concept for a data-based approach to support decision-making in tactical tasks for planning disassembly systems. Procedia CIRP, 122, 288–293. https://doi.org/10.1016/j.procir.2024.01.042


---
For questions, suggestions, or collaboration opportunities, please contact the corresponding author or visit our [institute website](https://www.mec.ed.tum.de/en/iwb/homepage/).
