# Linux Foundation Leaderboards Analysis

> [!Note]
> **Data Attribution:** This project provides an independent analysis derived from [LFX Insights Leaderboards](https://insights.linuxfoundation.org/leaderboards). This project is an independent effort and is not officially affiliated with the Linux Foundation.

## 🌐 Live Data Stories

Explore the interactive data stories: **[View Data Stories](https://pythonicvarun.github.io/LinuxFoundation-Leaderboards-Analysis/)**

## 📊 Beyond the Leaderboards

This project digs deeper into the Linux Foundation's open source ecosystem data. Instead of just ranking projects by size or activity, we analyze **health**, **efficiency**, and **sustainability**.

Using **Marimo**, **Pandas**, and **Altair**, this tool transforms raw JSON datasets into interactive data stories.

### 🔍 Key Analyses

1.  **🚀 Efficiency (David vs. Goliath)**: Identifying small, elite teams that outperform massive armies of contributors.
2.  **🔥 Burnout Risk**: Spotting "Focused Teams" that are experiencing a critical loss of momentum (>90% drop).
3.  **💎 Hidden Gems**: Finding projects with high corporate backing but low individual contributor counts (often critical infrastructure libraries).
4.  **🔄 The "Churn" Trap**: Distinguishing between projects that are growing (feature work) vs. those that are spinning their wheels (heavy refactoring).
5.  **🚌 Bus Factor Watchlist**: Highlighting projects with massive output but a dangerously small number of contributors.
6.  **📚 Libraries vs. Apps**: Segmenting projects to avoid penalizing stable libraries for having fewer contributors than end-user apps.

### 🛠️ Getting Started

This project uses `uv` for dependency management and `marimo` for interactive notebooks.

#### Prerequisites
- Python 3.12+
- `uv` installed

#### Running the Analysis

**Option 1: Interactive Notebook (Recommended)**
Explore the charts and data interactively in your browser.
```bash
uv run marimo edit analysis.py
```

**Option 2: Terminal Output**
Run the script to see the calculated insights and top 10 lists in your terminal.
```bash
uv run analysis.py
```

### 📂 Project Structure

```
├── analysis.py              # Main Marimo app with analysis & visualizations
├── scraper.py               # Utility for fetching fresh data from LFX
├── pyproject.toml           # Project dependencies
├── datasets/                # Raw JSON datasets from LFX Leaderboards
│   ├── active-contributors_full.json
│   ├── commit-activity_full.json
│   ├── contributors_full.json
│   ├── focused-teams_full.json
│   ├── small-teams-massive-output_full.json
│   └── ...
└── datastory/               # Generated data stories (GitHub Pages)
    ├── index.html                  # Landing page for all stories
    ├── PROMPTS.md                  # Prompts used for generating stories
    ├── report_data.json            # Processed analysis data
    ├── animated-style/             # Adventure-themed story
    ├── malcolm-gladwell-style/     # Narrative journalism style
    ├── polygraph-style/            # Interactive scrollytelling
    ├── shirley-wu-style/           # Artistic D3.js visualizations
    └── wall-street-journal-style/  # Financial journalism style
```
