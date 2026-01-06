import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell(hide_code=True)
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 📊 LFX Leaderboard Analysis: Beyond the Rankings

    Welcome to a deeper dive into the Linux Foundation's open source ecosystem. While standard leaderboards tell us *who* is on top, this analysis asks *why* and *how*.

    We aren't just looking for the biggest projects; we're looking for the **healthiest**, the **most efficient**, and the **hidden gems** that are powering the industry quietly.

    ### 🎯 Our Mission
    We will slice and dice these datasets to uncover:
    - **Hidden Gems**: Small projects with massive corporate backing.
    - **Burnout Risks**: Teams that are running hot but slowing down.
    - **Efficiency Monsters**: Small teams outperforming armies of developers.
    - **The "Churn" Trap**: Projects that are spinning their wheels (refactoring) vs. those that are actually growing.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Datasets Info:

    - **contributors**: Developers ranked by volume of contributions over the last 12 months, highlighting the most active and influential individuals.
    - **organizations**: Most influential organizations based on the total number of contributions made over the last 12 months.
    - **active-contributors**: These projects attracted the highest number of unique contributors over the past 12 months.
    - **active-organizations**: These projects brought together the largest number of distinct contributing organizations in the past 12 months.
    - **commit-activity**: These projects recorded the most commits during the past 12 months, showing high development momentum.
    - **codebase-size**: These projects maintain the largest codebases measured by total source lines of code.
    - **fastest-responders**: These projects achieve the shortest median time to first response on issues over the past 12 months.
    - **fastest-mergers**: These projects merge pull requests the fastest over the past 12 months.
    - **focused-teams**: These projects show the highest productivity per contributor.
    - **resolution-rate**: These projects keep development flowing, with most pull requests merged relative to issues opened.
    - **small-teams-massive-output**: These projects demonstrate exceptional productivity, achieving the highest commit volumes with 50 or fewer contributors.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 📂 The Data Landscape

    We have access to a rich set of metrics. Here's what we're working with:

    - **People Power**: `contributors`, `active-contributors`, `focused-teams` (productivity per person).
    - **Corporate Clout**: `organizations`, `active-organizations` (who is paying the bills?).
    - **Velocity & Health**: `commit-activity`, `fastest-responders`, `fastest-mergers`, `resolution-rate`.
    - **Scale**: `codebase-size`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. 🧹 Data Loading & Prep
    First, let's load the raw JSON data into Pandas. We'll normalize project names so we can join these different datasets together. Think of this as assembling our "Project 360" view.
    """)
    return


@app.cell
def _():
    import json
    import os

    import altair as alt
    import pandas as pd

    dataset_path = "datasets"
    files = [f for f in os.listdir(dataset_path) if f.endswith("_full.json")]

    dfs = {}
    for file in files:
        key = file.replace("_full.json", "")
        with open(os.path.join(dataset_path, file), "r") as f:
            data = json.load(f)
            # The data is a list of dictionaries
            dfs[key] = pd.DataFrame(data)
            print(f"Loaded {key} with {len(dfs[key])} records")
    return alt, dfs, json, os, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. 🚀 Efficiency: David vs. Goliath

    **Question:** Do you need a massive army to move fast?

    We're calculating the **Commits per Contributor** ratio.
    - **High Ratio**: A small, elite team (or highly automated bots) doing massive work.
    - **Low Ratio**: A large community where each person contributes a little (the "Bazaar" model).

    *Note: The `focused-teams` dataset is the official leaderboard for this metric. We will calculate it manually here to verify and visualize the distribution.*

    *Let's see who the "Special Forces" of open source are.*
    """)
    return


@app.cell
def _(alt, dfs, pd):
    # Merge active-contributors and commit-activity on project name/slug
    if "active-contributors" in dfs and "commit-activity" in dfs:
        _ac_df = dfs["active-contributors"][["name", "slug", "value"]].rename(
            columns={"value": "active_contributors"}
        )
        _ca_df = dfs["commit-activity"][["slug", "value"]].rename(
            columns={"value": "commits"}
        )
        merged_df = pd.merge(_ac_df, _ca_df, on="slug", how="inner")
        merged_df["commits_per_contributor"] = (
            merged_df["commits"] / merged_df["active_contributors"]
        )
        top_efficient = merged_df.sort_values(
            "commits_per_contributor", ascending=False
        ).head(10)

        print("Top 10 Most Efficient Projects (Commits per Contributor):")
        print(
            top_efficient[
                [
                    "name",
                    "active_contributors",
                    "commits",
                    "commits_per_contributor",
                ]
            ]
        )

        chart1 = (
            alt.Chart(merged_df)
            .mark_circle()
            .encode(
                x=alt.X(
                    "active_contributors",
                    scale=alt.Scale(type="log"),
                    title="Active Contributors",
                ),
                y=alt.Y("commits", scale=alt.Scale(type="log"), title="Commits"),
                size=alt.Size(
                    "commits_per_contributor", title="Commits per Contributor"
                ),
                tooltip=[
                    "name",
                    "active_contributors",
                    "commits",
                    "commits_per_contributor",
                ],
            )
            .properties(title="Active Contributors vs. Commit Activity")
            .interactive()
        )

    else:
        print("Required datasets not found.")
        chart1 = None
    chart1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. ⏱️ The "Triage Trap": Speed vs. Quality

    **Hypothesis:** If a project responds instantly to issues, they probably fix them faster too, right?

    We're correlating **Response Time** (how fast they say "Hello") with **Resolution Rate** (how often they actually close the issue).

    *Spoiler Alert: We found a correlation of **0.03**. That's basically zero. Fast bots saying "Thanks for your issue!" doesn't mean the bug gets fixed.*
    """)
    return


@app.cell
def _(alt, dfs, pd):
    if "fastest-responders" in dfs and "resolution-rate" in dfs:
        fr_df = dfs["fastest-responders"][["name", "slug", "value"]].rename(
            columns={"value": "response_time_hours"}
        )  # Assuming hours or similar unit

        rr_df = dfs["resolution-rate"][["slug", "value"]].rename(
            columns={"value": "resolution_rate"}
        )

        merged_rr_fr = pd.merge(fr_df, rr_df, on="slug", how="inner")

        correlation = merged_rr_fr["response_time_hours"].corr(
            merged_rr_fr["resolution_rate"]
        )
        print(
            f"Correlation between Response Time and Resolution Rate: {correlation:.2f}"
        )

        base = alt.Chart(merged_rr_fr).encode(
            x=alt.X("response_time_hours", title="Response Time (Hours)"),
            y=alt.Y("resolution_rate", title="Resolution Rate"),
        )

        points = base.mark_circle().encode(
            tooltip=["name", "response_time_hours", "resolution_rate"]
        )

        line = base.transform_regression(
            "response_time_hours", "resolution_rate"
        ).mark_line(color="red")

        chart2 = (
            (points + line)
            .properties(
                title=f"Response Time vs. Resolution Rate (Correlation: {correlation:.2f})"
            )
            .interactive()
        )

    else:
        print("Required datasets not found.")
        chart2 = None
    chart2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. 🏗️ Growth vs. Maintenance

    **Question:** Is the project building a skyscraper or just painting the walls?

    We compare **Commit Activity** against **Codebase Size**.
    - **High Commits + Low Size**: High Maintenance/Refactoring. The team is working hard to keep things running or cleaning up technical debt.
    - **High Commits + High Size**: Massive expansion.

    *Projects like **Model Context Protocol (MCP)** appeared here with huge activity but small size-classic signs of a new, rapidly iterating standard or heavy refactoring.*
    """)
    return


@app.cell
def _(alt, dfs, pd):
    if "codebase-size" in dfs and "commit-activity" in dfs:
        cs_df = dfs["codebase-size"][["name", "slug", "value"]].rename(
            columns={"value": "codebase_size"}
        )
        _ca_df = dfs["commit-activity"][["slug", "value"]].rename(
            columns={"value": "commits"}
        )
        merged_cs_ca = pd.merge(cs_df, _ca_df, on="slug", how="inner")

        chart3 = (
            alt.Chart(merged_cs_ca)
            .mark_circle()
            .encode(
                x=alt.X("commits", scale=alt.Scale(type="log"), title="Commits"),
                y=alt.Y(
                    "codebase_size",
                    scale=alt.Scale(type="log"),
                    title="Codebase Size (LOC)",
                ),
                tooltip=["name", "commits", "codebase_size"],
            )
            .properties(title="Commit Activity vs. Codebase Size")
            .interactive()
        )

        merged_cs_ca["maintenance_ratio"] = (
            merged_cs_ca["commits"] / merged_cs_ca["codebase_size"]
        )
        top_maintenance = merged_cs_ca.sort_values(
            "maintenance_ratio", ascending=False
        ).head(10)
        print(
            "Top 10 High Maintenance/Refactoring Projects (Commits per Line of Code):"
        )
        print(
            top_maintenance[
                ["name", "commits", "codebase_size", "maintenance_ratio"]
            ]
        )  # Identify high maintenance projects (High commits, low size)
    else:  # We can define a ratio: commits / codebase_size
        print("Required datasets not found.")
        chart3 = None
    chart3
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. 💎 Finding "Hidden Gems" (Corporate Darlings)

    **Question:** Which projects have huge corporate buy-in but relatively small contributor circles?

    We look for a high **Organizational Diversity Ratio** (Organizations / Contributors).
    - **High Ratio**: Many companies care about this, but few people write the code. These are often critical infrastructure libraries (like **Numcodecs** or **ko**).
    - **Low Ratio**: A massive community project (like Kubernetes) where the contributor count dwarfs the org count.

    *These "Hidden Gems" are often the safest bets for enterprise adoption-stable, backed by many, but not chaotic.*
    """)
    return


@app.cell
def _(alt, dfs, pd):
    if "active-organizations" in dfs and "active-contributors" in dfs:
        ao_df = dfs["active-organizations"][["name", "slug", "value"]].rename(
            columns={"value": "active_organizations"}
        )
        _ac_df = dfs["active-contributors"][["slug", "value"]].rename(
            columns={"value": "active_contributors"}
        )
        merged_org_cont = pd.merge(ao_df, _ac_df, on="slug", how="inner")
        merged_org_cont["org_diversity_ratio"] = (
            merged_org_cont["active_organizations"]
            / merged_org_cont["active_contributors"]
        )
        filtered_org_cont = merged_org_cont[
            merged_org_cont["active_contributors"] > 50
        ]
        top_diversity = filtered_org_cont.sort_values(
            "org_diversity_ratio", ascending=False
        ).head(10)
        print(
            "Top 10 Projects with High Organizational Diversity (Orgs per Contributor):"
        )
        print(
            top_diversity[
                [
                    "name",
                    "active_organizations",
                    "active_contributors",
                    "org_diversity_ratio",
                ]
            ]
        )  # Filter for projects with at least a decent number of contributors to avoid noise

        chart4 = (
            alt.Chart(filtered_org_cont)
            .mark_circle()
            .encode(
                x=alt.X(
                    "active_contributors",
                    scale=alt.Scale(type="log"),
                    title="Active Contributors",
                ),
                y=alt.Y(
                    "active_organizations",
                    scale=alt.Scale(type="log"),
                    title="Active Organizations",
                ),
                size=alt.Size("org_diversity_ratio", title="Diversity Ratio"),
                tooltip=[
                    "name",
                    "active_contributors",
                    "active_organizations",
                    "org_diversity_ratio",
                ],
            )
            .properties(title="Active Contributors vs. Active Organizations")
            .interactive()
        )

    else:
        print("Required datasets not found.")
        chart4 = None
    chart4
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. 🚌 The "Bus Factor" Watchlist: Small Teams, Massive Output

    **Question:** Which projects are punching way above their weight (and thus have the highest "Bus Factor" risk)?

    We are looking at the **Small Teams, Massive Output** dataset.
    - These projects have **<= 50 contributors** but are generating massive commit volumes.
    - **Risk**: High output from a small group means if one key person leaves, the project could stall.

    *These are the "David" projects of the ecosystem. Impressive, but fragile.*
    """)
    return


@app.cell
def _(alt, dfs):
    if "small-teams-massive-output" in dfs:
        st_df = dfs["small-teams-massive-output"][
            ["name", "slug", "value", "collectionsSlugs"]
        ].rename(columns={"value": "commits"})

        # We don't have exact contributor counts for all of these in this dataset,
        # but we know they are <= 50.
        # Let's visualize the top 15 by commit volume.

        top_small_teams = st_df.sort_values("commits", ascending=False).head(15)

        print("Top 15 Small Teams (<=50 Contributors) with Massive Output:")
        print(top_small_teams[["name", "commits"]])

        chart5 = (
            alt.Chart(top_small_teams)
            .mark_bar()
            .encode(
                x=alt.X("commits", title="Commit Volume (Last 12 Months)"),
                y=alt.Y("name", sort="-x", title="Project Name"),
                tooltip=["name", "commits"],
                color=alt.Color("commits", scale=alt.Scale(scheme="viridis")),
            )
            .properties(
                title="Small Teams, Massive Output: The 'Bus Factor' Watchlist"
            )
            .interactive()
        )

    else:
        print("Required datasets not found.")
        chart5 = None
    chart5
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. 🔥 Burnout Risk: The "Red Alert" List

    **Question:** Who is running out of steam?

    We looked at projects with **High Productivity Scores** (the `focused-teams` dataset) that have seen a **massive drop in momentum** (commits plummeting compared to the previous period).

    *We found alarming drops in projects like **Islet** and **CheriBSD** (>97% drop). These teams were running hot (high productivity) but are now stalling. If you depend on these, check on them.*
    """)
    return


@app.cell
def _(alt, dfs, pd):
    if "focused-teams" in dfs and "commit-activity" in dfs:
        _ft_df_burnout = dfs["focused-teams"][["name", "slug", "value"]].rename(
            columns={"value": "productivity_score"}
        )
        _ca_df_burnout = dfs["commit-activity"][
            ["slug", "value", "previousPeriodValue"]
        ].rename(
            columns={"value": "commits", "previousPeriodValue": "prev_commits"}
        )

        _merged_burnout = pd.merge(
            _ft_df_burnout, _ca_df_burnout, on="slug", how="inner"
        )

        # Calculate Momentum (Percentage Change)
        # Handle division by zero
        _merged_burnout["momentum"] = _merged_burnout.apply(
            lambda row: (
                (row["commits"] - row["prev_commits"]) / row["prev_commits"]
                if row["prev_commits"] > 0
                else 0
            ),
            axis=1,
        )

        # Filter for projects with negative momentum (slowing down)
        # We focus on projects that have at least some significant activity to avoid noise
        _declining_projects = _merged_burnout[
            (_merged_burnout["momentum"] < -0.1)
            & (_merged_burnout["commits"] > 100)
        ].sort_values("momentum", ascending=True)

        print(
            "Top 10 'Focused Team' Projects with Dropping Momentum (Burnout Risk?):"
        )
        print(
            _declining_projects[
                [
                    "name",
                    "productivity_score",
                    "commits",
                    "prev_commits",
                    "momentum",
                ]
            ].head(10)
        )

        chart6 = (
            alt.Chart(_merged_burnout)
            .mark_circle()
            .encode(
                x=alt.X(
                    "productivity_score",
                    scale=alt.Scale(type="log"),
                    title="Productivity Score (Commits/Contributor)",
                ),
                y=alt.Y("momentum", title="Momentum (Activity Change)"),
                color=alt.condition(
                    alt.datum.momentum < 0,
                    alt.value("red"),  # Red for negative momentum
                    alt.value("green"),  # Green for positive
                ),
                tooltip=[
                    "name",
                    "productivity_score",
                    "commits",
                    "prev_commits",
                    alt.Tooltip("momentum", format=".1%"),
                ],
            )
            .properties(title="Project Momentum vs. Productivity Score")
            .interactive()
        )

        # Add a horizontal line at 0 momentum
        rule = (
            alt.Chart(pd.DataFrame({"y": [0]}))
            .mark_rule(color="black")
            .encode(y="y")
        )
        chart6 = chart6 + rule

    else:
        print("Required datasets not found.")
        chart6 = None
    chart6
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. 📚 Libraries vs. Apps: The "Free Rider" Problem

    **Question:** Is a low contributor count always bad?

    We segmented our "Hidden Gems" into **Libraries** and **Apps**.
    - **Libraries (e.g., Resolve, MarkupSafe)**: High corporate use + low contributors = **Healthy**. Stable APIs don't need a thousand cooks in the kitchen.
    - **Apps (e.g., E4S)**: High corporate use + low contributors = **Warning**. Companies are using the app but not giving back.

    *This distinction saves us from flagging a perfectly healthy library as "stagnant".*
    """)
    return


@app.cell
def _(alt, dfs, pd):
    if "active-organizations" in dfs and "active-contributors" in dfs:
        _ao_df_seg = dfs["active-organizations"][
            ["name", "slug", "value", "collectionsSlugs"]
        ].rename(columns={"value": "active_organizations"})
        _ac_df_seg = dfs["active-contributors"][["slug", "value"]].rename(
            columns={"value": "active_contributors"}
        )
        _merged_seg = pd.merge(_ao_df_seg, _ac_df_seg, on="slug", how="inner")
        _merged_seg["org_diversity_ratio"] = (
            _merged_seg["active_organizations"]
            / _merged_seg["active_contributors"]
        )

        # Simple classifier function
        def classify_project(row):
            slugs = (
                " ".join(row["collectionsSlugs"]).lower()
                if isinstance(row["collectionsSlugs"], list)
                else ""
            )
            name = row["name"].lower()
            text = slugs + " " + name

            library_keywords = [
                "library",
                "sdk",
                "framework",
                "toolkit",
                "plugin",
                "module",
                "api",
                "standard",
                "spec",
                "protocol",
                "connector",
                "driver",
            ]
            app_keywords = [
                "platform",
                "application",
                "server",
                "client",
                "dashboard",
                "system",
                "database",
                "service",
                "desktop",
                "mobile",
                "app",
            ]

            is_lib = any(k in text for k in library_keywords)
            is_app = any(k in text for k in app_keywords)

            if is_lib and not is_app:
                return "Library/Tool"
            elif is_app and not is_lib:
                return "End-User App"
            elif is_lib and is_app:
                return "Hybrid/Platform"  # e.g. a platform that also has an SDK
            else:
                return "Unclassified"

        _merged_seg["type"] = _merged_seg.apply(classify_project, axis=1)

        # Filter for high diversity ratio (> 0.5) and reasonable org count (> 5)
        _hidden_gems = _merged_seg[
            (_merged_seg["org_diversity_ratio"] > 0.5)
            & (_merged_seg["active_organizations"] > 5)
        ].copy()

        print("Top 'Hidden Gems' Segmented by Type:")
        print(
            _hidden_gems[
                [
                    "name",
                    "type",
                    "active_organizations",
                    "active_contributors",
                    "org_diversity_ratio",
                ]
            ]
            .sort_values("org_diversity_ratio", ascending=False)
            .head(15)
        )

        chart7 = (
            alt.Chart(_hidden_gems)
            .mark_circle()
            .encode(
                x=alt.X(
                    "active_contributors",
                    scale=alt.Scale(type="log"),
                    title="Active Contributors",
                ),
                y=alt.Y(
                    "active_organizations",
                    scale=alt.Scale(type="log"),
                    title="Active Organizations",
                ),
                color="type",
                size="org_diversity_ratio",
                tooltip=[
                    "name",
                    "type",
                    "active_organizations",
                    "active_contributors",
                    "org_diversity_ratio",
                ],
            )
            .properties(title="Hidden Gems Segmentation: Libraries vs. Apps")
            .interactive()
        )

    else:
        print("Required datasets not found.")
        chart7 = None
    chart7
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. 🔄 The "Churn" Trap: Motion vs. Progress

    **Question:** Are they building new features or just rewriting the same code forever?

    We calculated a **Churn Ratio**: Commits per Net Line of Code Change.
    - **Low Ratio (~1.0)**: Every commit adds value (Growth).
    - **High Ratio (>100)**: Hundreds of commits to change 5 lines of code.

    *We found **Model Context Protocol (MCP)** and **EVerest** with ratios > 2000. This indicates massive refactoring, stabilization, or non-code work. They are spinning their wheels (or polishing the engine) rather than driving forward.*
    """)
    return


@app.cell
def _(alt, dfs, pd):
    if "codebase-size" in dfs and "commit-activity" in dfs:
        _cs_df_churn = dfs["codebase-size"][
            ["name", "slug", "value", "previousPeriodValue"]
        ].rename(
            columns={"value": "current_loc", "previousPeriodValue": "prev_loc"}
        )
        _ca_df_churn = dfs["commit-activity"][["slug", "value"]].rename(
            columns={"value": "commits"}
        )

        _merged_churn = pd.merge(
            _cs_df_churn, _ca_df_churn, on="slug", how="inner"
        )

        # Calculate Net Line Change
        _merged_churn["net_line_change"] = (
            _merged_churn["current_loc"] - _merged_churn["prev_loc"]
        ).abs()

        # Avoid division by zero
        _merged_churn["churn_ratio_proxy"] = _merged_churn.apply(
            lambda row: (
                row["commits"] / row["net_line_change"]
                if row["net_line_change"] > 0
                else row["commits"]
            ),  # If 0 change, ratio is infinite (just use commits as score)
            axis=1,
        )

        # Filter for significant activity
        _high_churn = (
            _merged_churn[_merged_churn["commits"] > 100]
            .sort_values("churn_ratio_proxy", ascending=False)
            .head(10)
        )

        print("Top 10 Projects with High Churn (Refactoring/Instability?):")
        print(
            _high_churn[
                ["name", "commits", "net_line_change", "churn_ratio_proxy"]
            ]
        )

        chart8 = (
            alt.Chart(_merged_churn[_merged_churn["commits"] > 100])
            .mark_circle()
            .encode(
                x=alt.X(
                    "net_line_change",
                    scale=alt.Scale(type="log"),
                    title="Net Line Change (Growth)",
                ),
                y=alt.Y(
                    "commits",
                    scale=alt.Scale(type="log"),
                    title="Commits (Activity)",
                ),
                color=alt.Color(
                    "churn_ratio_proxy",
                    scale=alt.Scale(scheme="viridis", reverse=True),
                    title="Churn Proxy",
                ),
                tooltip=[
                    "name",
                    "commits",
                    "net_line_change",
                    "churn_ratio_proxy",
                ],
            )
            .properties(title="Activity vs. Growth (Churn Analysis)")
            .interactive()
        )

    else:
        print("Required datasets not found.")
        chart8 = None
    chart8
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. 📦 Generating a Complete Report Data for Data Story

    **Purpose:** Export all our analysis insights into a structured JSON format.

    We're consolidating all the metrics we've calculated into a single `report_data.json` file that can power interactive data stories and visualizations.

    This includes:
    - **Efficiency Rankings**: Commits per contributor for all projects.
    - **Response vs. Resolution**: Correlation data showing the disconnect between speed and quality.
    - **Growth vs. Maintenance**: Projects categorized by their development patterns.
    - **Hidden Gems**: High organizational diversity projects.
    - **Bus Factor Watchlist**: Small teams with massive output.
    - **Burnout Risk Indicators**: Projects with declining momentum.
    - **Churn Analysis**: Motion vs. progress metrics.
    - **Library vs. App Segmentation**: Categorized project types.

    *This JSON export enables downstream dashboards and data journalism pieces.*
    """)
    return


@app.cell
def _(dfs, pd):
    def generate_report():
        report_data = {}

        # 1. Efficiency data (matches Section 2: David vs. Goliath)
        if "active-contributors" in dfs and "commit-activity" in dfs:
            _ac_df = dfs["active-contributors"][["name", "slug", "value"]].rename(
                columns={"value": "active_contributors"}
            )
            _ca_df = dfs["commit-activity"][["slug", "value"]].rename(
                columns={"value": "commits"}
            )
            merged_df = pd.merge(_ac_df, _ca_df, on="slug", how="inner")
            merged_df["commits_per_contributor"] = (
                merged_df["commits"] / merged_df["active_contributors"]
            )
            report_data["efficiency"] = merged_df.nlargest(
                50, "commits_per_contributor"
            ).to_dict(orient="records")
            report_data["efficiency_all"] = merged_df.to_dict(orient="records")

        # 2. Response vs Resolution (matches Section 3: The "Triage Trap")
        if "fastest-responders" in dfs and "resolution-rate" in dfs:
            fr_df = dfs["fastest-responders"][["name", "slug", "value"]].rename(
                columns={"value": "response_time_hours"}
            )
            rr_df = dfs["resolution-rate"][["slug", "value"]].rename(
                columns={"value": "resolution_rate"}
            )
            merged_rr_fr = pd.merge(fr_df, rr_df, on="slug", how="inner")
            report_data["response_resolution"] = merged_rr_fr.to_dict(
                orient="records"
            )
            report_data["correlation"] = float(
                merged_rr_fr["response_time_hours"].corr(
                    merged_rr_fr["resolution_rate"]
                )
            )

        # 3. Growth vs Maintenance (matches Section 4: Growth vs. Maintenance)
        if "codebase-size" in dfs and "commit-activity" in dfs:
            cs_df = dfs["codebase-size"][["name", "slug", "value"]].rename(
                columns={"value": "codebase_size"}
            )
            _ca_df = dfs["commit-activity"][["slug", "value"]].rename(
                columns={"value": "commits"}
            )
            merged_cs_ca = pd.merge(cs_df, _ca_df, on="slug", how="inner")
            merged_cs_ca["maintenance_ratio"] = (
                merged_cs_ca["commits"] / merged_cs_ca["codebase_size"]
            )
            report_data["growth_maintenance"] = merged_cs_ca.to_dict(
                orient="records"
            )
            report_data["top_maintenance"] = merged_cs_ca.nlargest(
                15, "maintenance_ratio"
            ).to_dict(orient="records")

        # 4. Hidden Gems (matches Section 5: Finding "Hidden Gems")
        if "active-organizations" in dfs and "active-contributors" in dfs:
            ao_df = dfs["active-organizations"][["name", "slug", "value"]].rename(
                columns={"value": "active_organizations"}
            )
            _ac_df = dfs["active-contributors"][["slug", "value"]].rename(
                columns={"value": "active_contributors"}
            )
            merged_org_cont = pd.merge(ao_df, _ac_df, on="slug", how="inner")
            merged_org_cont["org_diversity_ratio"] = (
                merged_org_cont["active_organizations"]
                / merged_org_cont["active_contributors"]
            )
            filtered_org_cont = merged_org_cont[
                merged_org_cont["active_contributors"] > 50
            ]
            report_data["hidden_gems"] = filtered_org_cont.nlargest(
                20, "org_diversity_ratio"
            ).to_dict(orient="records")
            report_data["org_diversity_all"] = filtered_org_cont.to_dict(
                orient="records"
            )

        # 5. Bus Factor (matches Section 6: Small Teams, Massive Output)
        if "small-teams-massive-output" in dfs:
            st_df = dfs["small-teams-massive-output"][
                ["name", "slug", "value", "collectionsSlugs"]
            ].rename(columns={"value": "commits"})
            report_data["bus_factor"] = st_df.nlargest(20, "commits").to_dict(
                orient="records"
            )

        # 6. Burnout Risk (matches Section 7: The "Red Alert" List)
        if "focused-teams" in dfs and "commit-activity" in dfs:
            _ft_df_burnout = dfs["focused-teams"][["name", "slug", "value"]].rename(
                columns={"value": "productivity_score"}
            )
            _ca_df_burnout = dfs["commit-activity"][
                ["slug", "value", "previousPeriodValue"]
            ].rename(
                columns={"value": "commits", "previousPeriodValue": "prev_commits"}
            )
            _merged_burnout = pd.merge(
                _ft_df_burnout, _ca_df_burnout, on="slug", how="inner"
            )
            _merged_burnout["momentum"] = _merged_burnout.apply(
                lambda row: (
                    (row["commits"] - row["prev_commits"]) / row["prev_commits"]
                    if row["prev_commits"] > 0
                    else 0
                ),
                axis=1,
            )
            _declining_projects = _merged_burnout[
                (_merged_burnout["momentum"] < -0.1)
                & (_merged_burnout["commits"] > 100)
            ].nsmallest(15, "momentum")
            report_data["burnout_risk"] = _declining_projects.to_dict(
                orient="records"
            )
            report_data["burnout_all"] = _merged_burnout.to_dict(orient="records")

        # 7. Churn Analysis (matches Section 9: The "Churn" Trap)
        if "codebase-size" in dfs and "commit-activity" in dfs:
            _cs_df_churn = dfs["codebase-size"][
                ["name", "slug", "value", "previousPeriodValue"]
            ].rename(
                columns={"value": "current_loc", "previousPeriodValue": "prev_loc"}
            )
            _ca_df_churn = dfs["commit-activity"][["slug", "value"]].rename(
                columns={"value": "commits"}
            )
            _merged_churn = pd.merge(
                _cs_df_churn, _ca_df_churn, on="slug", how="inner"
            )
            _merged_churn["net_line_change"] = (
                _merged_churn["current_loc"] - _merged_churn["prev_loc"]
            ).abs()
            _merged_churn["churn_ratio_proxy"] = _merged_churn.apply(
                lambda row: (
                    row["commits"] / row["net_line_change"]
                    if row["net_line_change"] > 0
                    else row["commits"]
                ),
                axis=1,
            )
            _churn_filtered = _merged_churn[_merged_churn["commits"] > 100]
            report_data["churn_high"] = _churn_filtered.nlargest(
                15, "churn_ratio_proxy"
            ).to_dict(orient="records")
            report_data["churn_all"] = _churn_filtered.to_dict(orient="records")

        # 8. Libraries vs Apps segmentation (matches Section 8)
        if "active-organizations" in dfs and "active-contributors" in dfs:
            _ao_df_seg = dfs["active-organizations"][
                ["name", "slug", "value", "collectionsSlugs"]
            ].rename(columns={"value": "active_organizations"})
            _ac_df_seg = dfs["active-contributors"][["slug", "value"]].rename(
                columns={"value": "active_contributors"}
            )
            _merged_seg = pd.merge(_ao_df_seg, _ac_df_seg, on="slug", how="inner")
            _merged_seg["org_diversity_ratio"] = (
                _merged_seg["active_organizations"]
                / _merged_seg["active_contributors"]
            )

            def classify_project(row):
                slugs = (
                    " ".join(row["collectionsSlugs"]).lower()
                    if isinstance(row["collectionsSlugs"], list)
                    else ""
                )
                name = row["name"].lower()
                text = slugs + " " + name
                library_keywords = [
                    "library",
                    "sdk",
                    "framework",
                    "toolkit",
                    "plugin",
                    "module",
                    "api",
                    "standard",
                    "spec",
                    "protocol",
                    "connector",
                    "driver",
                ]
                app_keywords = [
                    "platform",
                    "application",
                    "server",
                    "client",
                    "dashboard",
                    "system",
                    "database",
                    "service",
                    "desktop",
                    "mobile",
                    "app",
                ]
                is_lib = any(k in text for k in library_keywords)
                is_app = any(k in text for k in app_keywords)
                if is_lib and not is_app:
                    return "Library/Tool"
                elif is_app and not is_lib:
                    return "End-User App"
                elif is_lib and is_app:
                    return "Hybrid/Platform"
                else:
                    return "Unclassified"

            _merged_seg["type"] = _merged_seg.apply(classify_project, axis=1)
            _hidden_gems = _merged_seg[
                (_merged_seg["org_diversity_ratio"] > 0.5)
                & (_merged_seg["active_organizations"] > 5)
            ].copy()

            _hidden_gems["collectionsSlugs"] = _hidden_gems[
                "collectionsSlugs"
            ].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            report_data["segmented_gems"] = _hidden_gems.nlargest(
                30, "org_diversity_ratio"
            ).to_dict(orient="records")

        return report_data
    return (generate_report,)


@app.cell
def _(generate_report, json, os):
    os.makedirs("datastory/", exist_ok=True)

    # Save to JSON file
    report_data = generate_report()
    with open("datastory/report_data.json", "w") as _f:
        json.dump(report_data, _f)

    print(f"Exported {len(report_data)} datasets to datastory/report_data.json")
    print("Keys:", list(report_data.keys()))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Conclusion

    ### Key Findings:

    1.  **Contributor Efficiency**: Projects like **CBT Tape**, **Mushroom Observer**, and **SmokeDetector** show incredibly high commits per contributor ratios. This suggests highly automated workflows or extremely prolific core maintainers.
    2.  **Response Time vs. Resolution Rate**: There is **no significant correlation (0.03)** between how fast a project responds to an issue and its resolution rate. Faster response doesn't guarantee a fix.
    3.  **Codebase Growth vs. Activity**: Projects like **Model Context Protocol (MCP)** and **EVerest** show massive commit activity relative to their codebase size, indicating intense development, refactoring, or a repository structure where commits don't always equal lines of code (e.g., configuration, documentation updates).
    4.  **Organizational Diversity**: **ko**, **Infection**, and **Numcodecs** stand out as projects with high organizational diversity relative to their contributor count, suggesting broad industry adoption and support.
    5.  **Bus Factor Watchlist**: Projects like **Mushroom Observer** and **SOAJS** are the "Davids" of the ecosystem—generating over 20,000 commits with <= 50 contributors. They are impressive but carry higher risk if key maintainers leave.
    6.  **Burnout Risk**: We identified projects like **Islet** and **CheriBSD** that had high productivity scores but are now experiencing a >97% drop in commit activity. These teams may be facing burnout or resource constraints.
    7.  **Hidden Gems Segmentation**: We distinguished between healthy Libraries like **Resolve** and **MarkupSafe** (high corporate use, focused team) versus Apps like **E4S** that might need more community support.
    8.  **Churn Analysis**: **Model Context Protocol (MCP)** and **EVerest** show extremely high churn ratios (>2000 commits per net line change), indicating heavy refactoring or stabilization phases rather than pure feature growth.

    ### 🏁 Final Verdict

    We've gone beyond the vanity metrics. Here is the pulse of the ecosystem:

    1.  **Don't trust the "Fastest Responders"**: Speed does not equal quality (0.03 correlation).
    2.  **Watch out for Burnout**: **Islet** and **CheriBSD** are flashing red warning lights.
    3.  **Respect the Libraries**: **MarkupSafe** and **Resolve** are quiet pillars of the industry.
    4.  **Question the Activity**: **MCP** is churning hard-is it stabilizing or stuck?

    *Data doesn't lie, but it does whisper. You just have to listen closely.*
    """)
    return


if __name__ == "__main__":
    app.run()
