# =============================================================================
# CULTURE AND MACROECONOMIC PERFORMANCE
# Cannata & Biondo (2026)
# Simulation Analysis and Figures
#
# This script reads CSV outputs from NetLogo and produces:
#   Part I   -- Monte Carlo stability analysis
#   Part II  -- Ranking validation (Spearman, Kendall, Williams)
#   Part III -- Culture vs technology decomposition and WEI targeting figures
#
# All CSV files are expected in the working directory (project root).
# Output figures are saved as PNG (300 dpi) in the same directory.
# =============================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import geopandas as gpd
from adjustText import adjust_text
from scipy import stats
from pathlib import Path

# Working directory: root of the project repository
ROOT = Path(__file__).resolve().parent


# =============================================================================
# PART I: MONTE CARLO STABILITY ANALYSIS
# =============================================================================
# Reads stability_prof_NW4300_NF700_random.csv produced by NetLogo's
# stability-analysis-prof procedure and plots the cumulative mean and
# standard deviation of labour productivity per hour.

def plot_stability():
    df = pd.read_csv(ROOT / "stability_prof_NW4300_NF700_random.csv")

    final_mean = df["cumulative_mean_productivity"].iloc[-1]
    final_std  = df["cumulative_std_productivity"].iloc[-1]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.errorbar(
        df["run"],
        df["cumulative_mean_productivity"],
        yerr=df["cumulative_std_productivity"],
        fmt="o", color="darkgreen", markersize=3,
        ecolor="gray", elinewidth=0.8, capsize=2,
        label="Cumulative mean productivity"
    )
    ax.axhline(final_mean + final_std, color="gray",
               linestyle="--", linewidth=0.8)
    ax.axhline(final_mean - final_std, color="gray",
               linestyle="--", linewidth=0.8)

    ax.set_xlabel("Replications", fontsize=12)
    ax.set_ylabel("Mean Productivity per Hour", fontsize=12)
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(False)

    plt.tight_layout()
    plt.savefig(ROOT / "stability_analysis.png", dpi=300)
    plt.show()
    print("Saved: stability_analysis.png")


# =============================================================================
# PART II: HEATMAPS -- EMPIRICAL VS SIMULATED PRODUCTIVITY
# =============================================================================

def plot_heatmaps_eu():
    """Side-by-side choropleth maps for European countries."""

    empirical = {
        "Austria": 118.9, "Belgium": 134.0, "Bulgaria": 56.3,
        "Denmark": 141.2, "Finland": 108.2, "France": 117.7,
        "Germany": 121.5, "Greece": 56.2,   "Hungary": 70.1,
        "Italy": 97.7,    "Netherlands": 124.2, "Poland": 65.7,
        "Portugal": 71.2, "Slovenia": 84.3, "Slovakia": 78.7,
        "Spain": 95.4,    "Switzerland": 129.3, "Türkiye": 50.5
    }

    df_sim = pd.read_csv(ROOT / "table6_results.csv")
    df_sim["country"] = df_sim["country"].replace({"Turkey": "Türkiye"})
    simulated = dict(zip(df_sim["country"], df_sim["productivity_with_WEI"]))

    world = gpd.read_file(
        "https://naciscdn.org/naturalearth/110m/cultural/"
        "ne_110m_admin_0_countries.zip"
    )
    europe = world[
        (world["CONTINENT"] == "Europe") | (world["NAME"] == "Türkiye")
    ].copy()
    europe["empirical"] = europe["NAME"].map(empirical)
    europe["simulated"] = europe["NAME"].map(simulated)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    europe.plot(
        column="empirical", ax=ax1, legend=True,
        legend_kwds={"label": "Empirical", "shrink": 0.5},
        cmap="GnBu",
        missing_kwds={"color": "lightgrey", "edgecolor": "white"},
        edgecolor="white", linewidth=0.5
    )
    ax1.set_xlim(-12, 45)
    ax1.set_ylim(34, 72)
    ax1.set_title("Empirical", fontsize=14, fontweight="bold")
    ax1.axis("off")

    europe.plot(
        column="simulated", ax=ax2, legend=True,
        legend_kwds={"label": "Simulated", "shrink": 0.5},
        cmap="Reds",
        missing_kwds={"color": "lightgrey", "edgecolor": "white"},
        edgecolor="white", linewidth=0.5
    )
    ax2.set_xlim(-12, 45)
    ax2.set_ylim(34, 72)
    ax2.set_title("Simulated", fontsize=14, fontweight="bold")
    ax2.axis("off")

    plt.tight_layout()
    plt.savefig(ROOT / "figure2_heatmaps.png", dpi=300, bbox_inches="tight")
    plt.show()
    print("Saved: figure2_heatmaps.png")


def plot_heatmaps_it():
    """Side-by-side choropleth maps for Italian regions."""

    empirical = {
        "Piemonte": 43.362, "Valle d'Aosta": 47.691,
        "Lombardia": 51.184, "Trentino-Alto Adige": 52.395,
        "Veneto": 43.893, "Friuli-Venezia Giulia": 42.940,
        "Liguria": 45.796, "Emilia-Romagna": 46.006,
        "Toscana": 42.696, "Umbria": 37.471, "Marche": 37.729,
        "Lazio": 46.842, "Abruzzo": 37.935, "Molise": 37.198,
        "Campania": 36.239, "Puglia": 32.475, "Basilicata": 36.350,
        "Calabria": 31.521, "Sicilia": 35.487, "Sardegna": 34.770
    }

    df_sim = pd.read_csv(ROOT / "table_italy_results.csv")
    df_sim["region"] = df_sim["region"].replace(
        {"Trentino Alto Adige": "Trentino-Alto Adige"}
    )
    simulated = dict(zip(df_sim["region"], df_sim["productivity_with_WEI"]))

    italy = gpd.read_file(
        "https://naciscdn.org/naturalearth/10m/cultural/"
        "ne_10m_admin_1_states_provinces.zip"
    )
    italy = italy[italy["admin"] == "Italy"].copy()

    region_mapping = {
        "Valle d'Aosta": "Valle d'Aosta", "Piemonte": "Piemonte",
        "Lombardia": "Lombardia", "Trentino-Alto Adige": "Trentino-Alto Adige",
        "Veneto": "Veneto", "Friuli-Venezia Giulia": "Friuli-Venezia Giulia",
        "Liguria": "Liguria", "Emilia-Romagna": "Emilia-Romagna",
        "Toscana": "Toscana", "Umbria": "Umbria", "Marche": "Marche",
        "Lazio": "Lazio", "Abruzzo": "Abruzzo", "Molise": "Molise",
        "Campania": "Campania", "Apulia": "Puglia",
        "Basilicata": "Basilicata", "Calabria": "Calabria",
        "Sicily": "Sicilia", "Sardegna": "Sardegna"
    }

    italy["region_name"] = italy["region"].map(region_mapping)
    italy_regions = italy.dissolve(by="region_name").reset_index()
    italy_regions["empirical"] = italy_regions["region_name"].map(empirical)
    italy_regions["simulated"] = italy_regions["region_name"].map(simulated)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))

    italy_regions.plot(
        column="empirical", ax=ax1, legend=True,
        legend_kwds={"label": "Value added per hour (€)", "shrink": 0.5},
        cmap="YlGn",
        missing_kwds={"color": "lightgrey", "edgecolor": "white"},
        edgecolor="white", linewidth=0.5
    )
    ax1.set_xlim(6, 19)
    ax1.set_ylim(36, 48)
    ax1.set_title("Empirical", fontsize=14, fontweight="bold")
    ax1.axis("off")

    italy_regions.plot(
        column="simulated", ax=ax2, legend=True,
        legend_kwds={"label": "Simulated productivity", "shrink": 0.5},
        cmap="PuRd",
        missing_kwds={"color": "lightgrey", "edgecolor": "white"},
        edgecolor="white", linewidth=0.5
    )
    ax2.set_xlim(6, 19)
    ax2.set_ylim(36, 48)
    ax2.set_title("Simulated", fontsize=14, fontweight="bold")
    ax2.axis("off")

    plt.tight_layout()
    plt.savefig(ROOT / "figure3_heatmaps_italy.png", dpi=300, bbox_inches="tight")
    plt.show()
    print("Saved: figure3_heatmaps_italy.png")


# =============================================================================
# PART III: RANKING VALIDATION
# =============================================================================

def make_ranks(values):
    return stats.rankdata([-v for v in values], method="average")


def permutation_spearman(x, y, B=100_000, seed=42):
    rng = np.random.default_rng(seed)
    rho_obs, _ = stats.spearmanr(x, y)
    y = np.array(y)
    count = sum(
        abs(stats.spearmanr(x, rng.permutation(y))[0]) >= abs(rho_obs)
        for _ in range(B)
    )
    return rho_obs, count / B


def bootstrap_ci_spearman(x, y, B=10_000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(x)
    x, y = np.array(x), np.array(y)
    boot = [
        stats.spearmanr(x[idx := rng.integers(0, n, n)], y[idx])[0]
        for _ in range(B)
    ]
    return np.percentile(boot, [2.5, 97.5])


def kendall_cd(x, y):
    tau, p = stats.kendalltau(x, y)
    n = len(x)
    pairs = n * (n - 1) // 2
    C = round((tau * pairs + pairs) / 2)
    D = pairs - C
    return tau, p, C, D, pairs


def williams_test(r12, r13, r23, n):
    """
    Williams (1959) / Steiger (1980) test.
    H0: rho(empirical, with_WEI) = rho(empirical, no_WEI).
    """
    R = 1 - r12**2 - r13**2 - r23**2 + 2 * r12 * r13 * r23
    num = (r12 - r13) * np.sqrt((n - 1) * (1 + r23))
    denom = np.sqrt(
        2 * ((n - 1) / (n - 3)) * R +
        ((r12 + r13)**2 / 4) * (1 - r23)**3
    )
    t = num / denom
    p = 2 * stats.t.sf(abs(t), df=n - 3)
    return t, n - 3, p


def inversions(names, r_emp, r_sim, threshold=2):
    return [
        (name, int(r_emp[i]), int(r_sim[i]), int(r_sim[i] - r_emp[i]))
        for i, name in enumerate(names)
        if abs(r_sim[i] - r_emp[i]) > threshold
    ]


def run_validation(label, names, empirical, sim_with, sim_without):
    r_emp     = make_ranks(empirical)
    r_with    = make_ranks(sim_with)
    r_without = make_ranks(sim_without)

    rho_w,  p_w  = permutation_spearman(r_emp, r_with)
    rho_wo, p_wo = permutation_spearman(r_emp, r_without)
    rho_23, _    = stats.spearmanr(r_with, r_without)

    ci_w  = bootstrap_ci_spearman(r_emp, r_with)
    ci_wo = bootstrap_ci_spearman(r_emp, r_without)

    tau_w,  p_kw,  C_w,  D_w,  pairs = kendall_cd(r_emp, r_with)
    tau_wo, p_kwo, C_wo, D_wo, _     = kendall_cd(r_emp, r_without)

    t_wil, df_wil, p_wil = williams_test(rho_w, rho_wo, rho_23, len(names))

    inv_with    = inversions(names, r_emp, r_with,    threshold=2)
    inv_without = inversions(names, r_emp, r_without, threshold=2)

    sep = "=" * 65
    print(f"\n{sep}\n  {label.upper()}\n{sep}")

    print("\n--- SPEARMAN RHO (permutation test, B = 100,000) ---")
    p_w_str  = "< 0.00001" if p_w  == 0 else f"{p_w:.5f}"
    p_wo_str = "< 0.00001" if p_wo == 0 else f"{p_wo:.5f}"
    print(f"  With WEI:  rho = {rho_w:.4f}  CI95 [{ci_w[0]:.4f}, {ci_w[1]:.4f}]  p = {p_w_str}")
    print(f"  WEI = 0:   rho = {rho_wo:.4f}  CI95 [{ci_wo[0]:.4f}, {ci_wo[1]:.4f}]  p = {p_wo_str}")

    print("\n--- KENDALL TAU ---")
    print(f"  With WEI:  tau = {tau_w:.4f}  p = {p_kw:.5f}  |  C={C_w}, D={D_w} / {pairs} pairs")
    print(f"  WEI = 0:   tau = {tau_wo:.4f}  p = {p_kwo:.5f}  |  C={C_wo}, D={D_wo} / {pairs} pairs")

    print("\n--- WILLIAMS TEST (H0: rho_with = rho_without) ---")
    print(f"  t = {t_wil:.4f}  |  df = {df_wil}  |  p = {p_wil:.4f}")
    sig = "NOT significant" if p_wil >= 0.05 else "SIGNIFICANT"
    print(f"  >> Difference between models: {sig} at 5%")

    print(f"\n--- INVERSIONS |delta| > 2 ---")
    print(f"  Model with WEI ({len(inv_with)} inversions):")
    for name, re, rs, d in inv_with:
        print(f"    {name:<25}  emp={re}  sim={rs}  delta={d:+d}")
    if not inv_with:
        print("    None")

    print(f"  Model WEI=0 ({len(inv_without)} inversions):")
    for name, re, rs, d in inv_without:
        print(f"    {name:<25}  emp={re}  sim={rs}  delta={d:+d}")
    if not inv_without:
        print("    None")


def run_all_validations():
    eu_countries   = [
        "Denmark", "Belgium", "Switzerland", "Netherlands", "Germany",
        "Austria", "France", "Finland", "Italy", "Spain", "Slovenia",
        "Slovakia", "Portugal", "Hungary", "Poland", "Bulgaria",
        "Greece", "Turkey"
    ]
    eu_empirical   = [141.2,134.0,129.3,124.2,121.5,118.9,117.7,108.2,
                       97.7, 95.4, 84.3, 78.7, 71.2, 70.1, 65.7, 56.3,
                       56.2, 50.5]
    eu_sim_with    = [0.463,0.352,0.670,0.432,0.371,0.396,0.351,0.371,
                      0.271,0.274,0.284,0.240,0.256,0.222,0.232,0.169,
                      0.228,0.157]
    eu_sim_without = [0.335,0.281,0.451,0.302,0.284,0.291,0.264,0.279,
                      0.254,0.223,0.215,0.189,0.202,0.178,0.183,0.145,
                      0.197,0.156]

    it_regions     = [
        "Trentino Alto Adige", "Lombardia", "Valle d'Aosta", "Lazio",
        "Emilia-Romagna", "Liguria", "Veneto", "Piemonte",
        "Friuli-Venezia Giulia", "Toscana", "Abruzzo", "Marche",
        "Umbria", "Molise", "Basilicata", "Campania",
        "Sicilia", "Sardegna", "Puglia", "Calabria"
    ]
    it_empirical   = [52.395,51.184,47.691,46.842,46.006,45.796,43.893,
                      43.362,42.940,42.696,37.935,37.729,37.471,37.198,
                      36.350,36.239,35.487,34.770,32.475,31.521]
    it_sim_with    = [0.666,0.590,0.554,0.468,0.523,0.409,0.481,0.408,
                      0.449,0.430,0.312,0.370,0.346,0.255,0.248,0.169,
                      0.167,0.241,0.186,0.148]
    it_sim_without = [0.447,0.412,0.385,0.343,0.357,0.305,0.331,0.295,
                      0.306,0.304,0.240,0.262,0.238,0.201,0.207,0.166,
                      0.165,0.196,0.170,0.146]

    run_validation("European Countries",
                   eu_countries, eu_empirical, eu_sim_with, eu_sim_without)
    run_validation("Italian Regions",
                   it_regions, it_empirical, it_sim_with, it_sim_without)


# =============================================================================
# PART IV: DECOMPOSITION AND WEI TARGETING FIGURES
# =============================================================================

# --- Color palette ---
C_BASELINE = "#2C5F8A"
C_CULTURE  = "#5B9EC9"
C_TECH     = "#A8C8E8"
C_PLUS01   = "#E07B6A"
C_PLUS02   = "#C0392B"
C_PLUS03   = "#7B241C"


def load_experiment_data():
    dec_eu = pd.read_csv(ROOT / "decomposition_eu.csv")
    dec_it = pd.read_csv(ROOT / "decomposition_it.csv")
    tgt_eu = pd.read_csv(ROOT / "wei_targeting_eu.csv")
    tgt_it = pd.read_csv(ROOT / "wei_targeting_it.csv")

    for df in [dec_eu, dec_it]:
        df["contrib_culture"] = df["prod_baseline"] - df["prod_only_technology"]
        df["contrib_tech"]    = df["prod_baseline"] - df["prod_only_culture"]

    for df in [tgt_eu, tgt_it]:
        for delta in ["01", "02", "03"]:
            df[f"gain_{delta}"] = (
                (df[f"prod_wei_plus{delta}"] - df["prod_baseline"])
                / df["prod_baseline"] * 100
            )

    return dec_eu, dec_it, tgt_eu, tgt_it


def valid_decomposition(df, id_col, threshold=0.02):
    mask = (
        (df["contrib_culture"] >= 0) &
        (df["contrib_tech"]    >= 0) &
        (df["contrib_culture"] + df["contrib_tech"] >= threshold)
    )
    out = df[mask].copy()
    out["total_contrib"] = out["contrib_culture"] + out["contrib_tech"]
    out["pct_culture"]   = out["contrib_culture"] / out["total_contrib"] * 100
    out["pct_tech"]      = 100 - out["pct_culture"]
    return out.sort_values("pct_culture", ascending=False)


def print_diagnostics(dec_eu, dec_it, tgt_eu, tgt_it):
    dec_eu_v = valid_decomposition(dec_eu, "country")
    dec_it_v = valid_decomposition(dec_it, "region")
    tgt_eu_s = tgt_eu.sort_values("WEI_real")
    tgt_it_s = tgt_it.sort_values("WEI_real")
    sep = "=" * 70

    for label, df, id_col, valid in [
        ("EUROPE -- all countries", dec_eu, "country", dec_eu_v),
        ("ITALY  -- all regions",   dec_it, "region",  dec_it_v)
    ]:
        print(f"\n{sep}\n  {label}\n{sep}")
        print(df[[id_col, "prod_baseline", "prod_only_culture",
                  "prod_only_technology", "contrib_culture",
                  "contrib_tech"]].round(4).to_string(index=False))
        excl = df[~df[id_col].isin(valid[id_col])][id_col].tolist()
        print(f"\nExcluded (negative or negligible contributions): {excl}")
        print(f"\n  Culture range:    {valid['pct_culture'].min():.1f}% "
              f"-- {valid['pct_culture'].max():.1f}%")
        print(f"  Technology range: {valid['pct_tech'].min():.1f}% "
              f"-- {valid['pct_tech'].max():.1f}%")

    for label, df, id_col in [
        ("WEI TARGETING -- Europe", tgt_eu_s, "country"),
        ("WEI TARGETING -- Italy",  tgt_it_s, "region")
    ]:
        print(f"\n{sep}\n  {label}\n{sep}")
        print(df[[id_col, "WEI_real", "gain_01",
                  "gain_02", "gain_03"]].round(2).to_string(index=False))
        print(f"\n  Gain +0.1 -- min: {df['gain_01'].min():.2f}%  "
              f"max: {df['gain_01'].max():.2f}%")


def plot_decomposition_bars(dec_eu, dec_it):
    width = 0.25
    for df, id_col, rot, fname in [
        (dec_eu, "country", 45, "decomposition_eu.png"),
        (dec_it, "region",  45, "decomposition_it.png")
    ]:
        fig, ax = plt.subplots(figsize=(12, 5))
        x = np.arange(len(df))
        ax.bar(x - width, df["prod_baseline"],        width,
               color=C_BASELINE, label="Baseline ($A$ real, WEI real)")
        ax.bar(x,          df["prod_only_culture"],    width,
               color=C_CULTURE,  label="Only culture ($\\bar{A}$, WEI real)")
        ax.bar(x + width,  df["prod_only_technology"], width,
               color=C_TECH,     label="Only technology ($A$ real, $\\overline{WEI}$)")
        ax.set_xticks(x)
        ax.set_xticklabels(df[id_col], rotation=rot, ha="right", fontsize=9)
        ax.set_ylabel("Labour productivity per hour", fontsize=11)
        ax.legend(fontsize=10, framealpha=0.9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_minor_locator(mticker.AutoMinorLocator())
        plt.tight_layout()
        plt.savefig(ROOT / fname, dpi=300, bbox_inches="tight")
        plt.show()
        print(f"Saved: {fname}")


def plot_targeting_bars(tgt_eu, tgt_it):
    width = 0.25
    for df, id_col, rot, fname in [
        (tgt_eu.sort_values("WEI_real"), "country", 45, "wei_targeting_gains_eu.png"),
        (tgt_it.sort_values("WEI_real"), "region",  45, "wei_targeting_gains_it.png")
    ]:
        fig, ax = plt.subplots(figsize=(12, 5))
        x = np.arange(len(df))
        ax.bar(x - width, df["gain_01"], width, color=C_PLUS01, label="WEI $+0.1$")
        ax.bar(x,          df["gain_02"], width, color=C_PLUS02, label="WEI $+0.2$")
        ax.bar(x + width,  df["gain_03"], width, color=C_PLUS03, label="WEI $+0.3$")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(df[id_col], rotation=rot, ha="right", fontsize=9)
        ax.set_ylabel("Productivity gain vs baseline (%)", fontsize=11)
        ax.legend(fontsize=10, framealpha=0.9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        plt.savefig(ROOT / fname, dpi=300, bbox_inches="tight")
        plt.show()
        print(f"Saved: {fname}")


def plot_scatter_wei_gain(tgt_eu, tgt_it):
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ax, df, id_col, color, title in [
        (axes[0], tgt_eu, "country", C_PLUS02,   "European Countries"),
        (axes[1], tgt_it, "region",  C_BASELINE, "Italian Regions")
    ]:
        ax.scatter(df["WEI_real"], df["gain_01"], color=color, s=80, zorder=3)
        texts = [
            ax.text(row["WEI_real"], row["gain_01"], row[id_col],
                    fontsize=8, color="dimgray")
            for _, row in df.iterrows()
        ]
        adjust_text(texts, ax=ax,
                    arrowprops=dict(arrowstyle="-", color="lightgray", lw=0.8))
        z = np.polyfit(df["WEI_real"], df["gain_01"], 1)
        x_line = np.linspace(df["WEI_real"].min(), df["WEI_real"].max(), 100)
        ax.plot(x_line, np.poly1d(z)(x_line), "--",
                color="gray", linewidth=1.2, alpha=0.7)
        ax.set_xlabel("WEI (observed value)", fontsize=11)
        ax.set_ylabel("Productivity gain from WEI $+0.1$ (%)", fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(ROOT / "scatter_wei_gain.png", dpi=300, bbox_inches="tight")
    plt.show()
    print("Saved: scatter_wei_gain.png")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    print("\n>>> PART I: Stability analysis")
    plot_stability()

    print("\n>>> PART II: Heatmaps")
    plot_heatmaps_eu()
    plot_heatmaps_it()

    print("\n>>> PART III: Ranking validation")
    run_all_validations()

    print("\n>>> PART IV: Decomposition and targeting figures")
    dec_eu, dec_it, tgt_eu, tgt_it = load_experiment_data()
    print_diagnostics(dec_eu, dec_it, tgt_eu, tgt_it)
    plot_decomposition_bars(dec_eu, dec_it)
    plot_targeting_bars(tgt_eu, tgt_it)
    plot_scatter_wei_gain(tgt_eu, tgt_it)

    print("\n=== ALL DONE ===")
