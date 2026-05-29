# culture-macro-abm

Replication code for:

> Cannata, G. & Biondo, A.E. (2026). *Beyond Technology: Cultural Mismatch and Labour Productivity in a Simulated Economy*. Department of Economics and Business, University of Catania.

---

## Overview

This repository contains all the code needed to replicate the empirical and simulation results of the paper. The analysis proceeds in three steps:

1. **Work Ethic Index (WEI)** — constructed via Principal Component Analysis (PCA) on survey and administrative data for 20 Italian regions and 18 European countries.
2. **Agent-Based Model (ABM)** — a simplified version of the KCX model (Biondo, 2023) calibrated on the WEI and country/region-level data. Firms and workers interact in a labour market where cultural mismatch reduces effective labour input and contracts real output.
3. **Simulation analysis** — Monte Carlo validation, ranking correlation tests, culture vs technology decomposition, and WEI targeting experiments.

---

## Repository Structure

```
culture-macro-abm/
│
├── NetLogo/
│   ├── culture_macro_abm.nlogo       # Main ABM model
│   ├── data_europe1.csv              # Calibration data -- European countries
│   └── data_italy.csv                # Calibration data -- Italian regions
│
├── R/
│   ├── wei_construction.R            # PCA-based WEI for Italy and Europe
│   └── Figures/
│       ├── DatasetIT.xlsx            # Input data -- Italian regions
│       └── DataEU.xlsx               # Input data -- European countries
│
├── Python/
│   └── analysis.py                   # Stability analysis, heatmaps,
│                                     # ranking validation, decomposition
│                                     # and WEI targeting figures
│
├── README.md
└── requirements.txt
```

---

## Requirements

### NetLogo
- [NetLogo 6.x](https://ccl.northwestern.edu/netlogo/)
- No additional extensions required beyond the built-in `csv` extension

### R
- R >= 4.2
- Packages: `tidyverse`, `janitor`, `psych`, `factoextra`, `sf`, `rnaturalearth`, `rnaturalearthdata`, `ggplot2`, `dplyr`, `geodata`, `scales`, `readxl`, `here`

Install all packages with:
```r
install.packages(c(
  "tidyverse", "janitor", "psych", "factoextra", "sf",
  "rnaturalearth", "rnaturalearthdata", "ggplot2",
  "dplyr", "geodata", "scales", "readxl", "here"
))
```

### Python
- Python >= 3.9
- See `requirements.txt` for the full list of dependencies

Install with:
```bash
pip install -r requirements.txt
```

---

## Replication Instructions

### Step 1 — Construct the Work Ethic Index

Open an R project at the repository root (so that `here()` resolves correctly), then run:

```r
source("R/wei_construction.R")
```

This produces the WEI rankings for Italian regions and European countries, choropleth maps, scree plots, and PCA vs FA robustness checks. All figures are saved under `R/Figures/`.

### Step 2 — Run the ABM

Open `NetLogo/culture_macro_abm.nlogo` in NetLogo. The model reads calibration data from `data_europe1.csv` (European countries) or `data_italy.csv` (Italian regions) depending on the `use-italy?` switch.

Available experiment procedures (call from the Command Center):

| Procedure | Description |
|---|---|
| `stability-analysis-prof 200` | Monte Carlo stability analysis |
| `run-experiment` | Theoretical scenarios (Table 5) |
| `run-country-comparison` | Cross-country productivity ranking (Table 6) |
| `run-region-comparison` | Cross-region productivity ranking (Italy) |
| `run-decomposition-eu` | Culture vs technology decomposition (Europe) |
| `run-decomposition-it` | Culture vs technology decomposition (Italy) |
| `run-wei-targeting-eu` | WEI targeting experiment (Europe) |
| `run-wei-targeting-it` | WEI targeting experiment (Italy) |

Each procedure exports results as a CSV file in the model directory.

### Step 3 — Generate figures and validation statistics

Move the CSV files produced by NetLogo to the `Python/` directory, then run:

```bash
cd Python
python analysis.py
```

This produces all figures reported in the paper (stability plot, heatmaps, decomposition bar charts, targeting charts, scatter plots) and prints the ranking validation statistics (Spearman ρ, Kendall τ, Williams test).

---

## Data Sources

| Dataset | Source |
|---|---|
| Real GDP per capita (Europe) | Eurostat (2024) |
| Labour force and unemployment (Europe) | OECD (2024) |
| Number of firms (Europe) | HitHorizons (2024) |
| Labour productivity per hour (Europe) | Eurostat (2023) |
| Regional GDP and labour force (Italy) | ISTAT (2024) |
| Number of firms (Italy) | Registro delle Imprese (2024) |
| Value added per hour worked (Italy) | ISTAT (2023) |
| Shadow economy rate | Kelmanson et al. (2021) |
