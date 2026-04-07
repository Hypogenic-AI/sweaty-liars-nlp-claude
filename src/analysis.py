"""
Sweaty Liars: Analysis script.
Loads experiment results and produces statistical tests + visualizations.
"""

import json
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ── Load Results ─────────────────────────────────────────────────────────────
def load_results(filepath="results/all_results.json"):
    with open(filepath) as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} results")
    print(f"Models: {df['model'].unique()}")
    print(f"Framings: {df['framing'].unique()}")
    print(f"Probe types: {df['probe_type'].unique()}")
    print(f"Items: {df['item_id'].nunique()}")
    print(f"Runs: {df['run'].nunique()}")
    return df


# ── Summary Statistics ───────────────────────────────────────────────────────
def summary_stats(df):
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)

    # Overall ASR by framing
    print("\n--- Overall Attack Success Rate (ASR) by Framing ---")
    asr = df.groupby("framing")["leaked"].mean()
    for framing, rate in asr.items():
        n = df[df["framing"] == framing].shape[0]
        ci = 1.96 * np.sqrt(rate * (1 - rate) / n)
        print(f"  {framing:15s}: {rate:.4f} ({rate*100:.1f}%) [95% CI: {rate-ci:.4f} - {rate+ci:.4f}]  (n={n})")

    # ASR by framing x probe_type
    print("\n--- ASR by Framing x Probe Type ---")
    pivot = df.groupby(["framing", "probe_type"])["leaked"].agg(["mean", "count"]).reset_index()
    pivot.columns = ["framing", "probe_type", "asr", "n"]
    for _, row in pivot.iterrows():
        ci = 1.96 * np.sqrt(row["asr"] * (1 - row["asr"]) / row["n"])
        print(f"  {row['framing']:15s} x {row['probe_type']:15s}: {row['asr']:.4f} ({row['asr']*100:.1f}%)  [CI: {row['asr']-ci:.4f}-{row['asr']+ci:.4f}]  (n={int(row['n'])})")

    # ASR by framing x model
    print("\n--- ASR by Framing x Model ---")
    pivot2 = df.groupby(["framing", "model"])["leaked"].agg(["mean", "count"]).reset_index()
    pivot2.columns = ["framing", "model", "asr", "n"]
    for _, row in pivot2.iterrows():
        ci = 1.96 * np.sqrt(row["asr"] * (1 - row["asr"]) / row["n"])
        print(f"  {row['framing']:15s} x {row['model']:20s}: {row['asr']:.4f} ({row['asr']*100:.1f}%)  [CI: {row['asr']-ci:.4f}-{row['asr']+ci:.4f}]")

    # Refusal rate by framing
    print("\n--- Refusal Rate by Framing ---")
    ref = df.groupby("framing")["refused"].mean()
    for framing, rate in ref.items():
        print(f"  {framing:15s}: {rate:.4f} ({rate*100:.1f}%)")

    # Mean leakage score by framing
    print("\n--- Mean Leakage Score by Framing ---")
    ls = df.groupby("framing")["leakage_score"].mean()
    for framing, score in ls.items():
        print(f"  {framing:15s}: {score:.4f}")

    return pivot


# ── Statistical Tests ────────────────────────────────────────────────────────
def statistical_tests(df):
    print("\n" + "=" * 60)
    print("STATISTICAL TESTS")
    print("=" * 60)

    results = {}

    # 1. Overall: Chi-squared test for independence (framing vs leaked)
    print("\n--- 1. Chi-squared test: Framing vs Leaked (overall) ---")
    ct = pd.crosstab(df["framing"], df["leaked"])
    chi2, p, dof, expected = stats.chi2_contingency(ct)
    n_total = len(df)
    cramers_v = np.sqrt(chi2 / n_total)
    print(f"  chi2 = {chi2:.4f}, p = {p:.6f}, dof = {dof}, Cramer's V = {cramers_v:.4f}")
    print(f"  Contingency table:\n{ct}")
    results["overall_chi2"] = {"chi2": chi2, "p": p, "cramers_v": cramers_v}

    # 2. Per probe type: Chi-squared tests
    print("\n--- 2. Chi-squared tests per probe type ---")
    probe_types = df["probe_type"].unique()
    for pt in probe_types:
        sub = df[df["probe_type"] == pt]
        ct_sub = pd.crosstab(sub["framing"], sub["leaked"])
        if ct_sub.shape == (2, 2):
            chi2, p, dof, _ = stats.chi2_contingency(ct_sub)
            cramers_v = np.sqrt(chi2 / len(sub))
            # Odds ratio
            a, b = ct_sub.iloc[0, 1], ct_sub.iloc[0, 0]  # concealment: leaked, not-leaked
            c, d = ct_sub.iloc[1, 1], ct_sub.iloc[1, 0]  # neutral: leaked, not-leaked
            or_val = (a * d) / (b * c) if b * c > 0 else float('inf')
            print(f"  {pt:15s}: chi2={chi2:.4f}, p={p:.6f}, V={cramers_v:.4f}, OR={or_val:.3f}")
            results[f"chi2_{pt}"] = {"chi2": chi2, "p": p, "odds_ratio": or_val}
        else:
            print(f"  {pt:15s}: insufficient variation in one condition")

    # 3. Per model: Chi-squared tests
    print("\n--- 3. Chi-squared tests per model ---")
    for model in df["model"].unique():
        sub = df[df["model"] == model]
        ct_sub = pd.crosstab(sub["framing"], sub["leaked"])
        if ct_sub.shape == (2, 2):
            chi2, p, dof, _ = stats.chi2_contingency(ct_sub)
            a, b = ct_sub.iloc[0, 1], ct_sub.iloc[0, 0]
            c, d = ct_sub.iloc[1, 1], ct_sub.iloc[1, 0]
            or_val = (a * d) / (b * c) if b * c > 0 else float('inf')
            print(f"  {model:20s}: chi2={chi2:.4f}, p={p:.6f}, OR={or_val:.3f}")
            results[f"chi2_{model}"] = {"chi2": chi2, "p": p, "odds_ratio": or_val}

    # 4. Mann-Whitney U for continuous leakage score
    print("\n--- 4. Mann-Whitney U for leakage score ---")
    neutral_scores = df[df["framing"] == "neutral"]["leakage_score"]
    conceal_scores = df[df["framing"] == "concealment"]["leakage_score"]
    u_stat, p_mw = stats.mannwhitneyu(conceal_scores, neutral_scores, alternative="greater")
    # Effect size: rank-biserial correlation
    n1, n2 = len(conceal_scores), len(neutral_scores)
    r_rb = 1 - 2 * u_stat / (n1 * n2)
    print(f"  U = {u_stat:.1f}, p = {p_mw:.6f}, rank-biserial r = {r_rb:.4f}")
    results["mannwhitney_leakage"] = {"U": u_stat, "p": p_mw, "r_rb": r_rb}

    # 5. McNemar's test (paired by item): for each item, compare framing outcomes
    print("\n--- 5. McNemar-like paired analysis ---")
    # Aggregate: for each (model, run, item_id, probe_type, probe_text), compare framing
    paired = df.pivot_table(
        index=["model", "run", "item_id", "probe_type", "probe_text"],
        columns="framing",
        values="leaked",
        aggfunc="first"
    ).reset_index()

    if "neutral" in paired.columns and "concealment" in paired.columns:
        # Count discordant pairs
        both_leak = ((paired["neutral"] == True) & (paired["concealment"] == True)).sum()
        neither = ((paired["neutral"] == False) & (paired["concealment"] == False)).sum()
        only_neutral = ((paired["neutral"] == True) & (paired["concealment"] == False)).sum()
        only_conceal = ((paired["neutral"] == False) & (paired["concealment"] == True)).sum()

        print(f"  Both leak: {both_leak}")
        print(f"  Neither leak: {neither}")
        print(f"  Only neutral leaks: {only_neutral}")
        print(f"  Only concealment leaks: {only_conceal}")

        # McNemar's test on discordant pairs
        if only_neutral + only_conceal > 0:
            # Use exact binomial test for small samples
            n_discord = only_neutral + only_conceal
            p_mcnemar = stats.binomtest(only_conceal, n_discord, 0.5).pvalue
            print(f"  McNemar p-value (exact binomial): {p_mcnemar:.6f}")
            print(f"  Ratio: concealment-only / neutral-only = {only_conceal}/{only_neutral} = {only_conceal/max(only_neutral,1):.2f}")
            results["mcnemar"] = {
                "only_conceal": int(only_conceal),
                "only_neutral": int(only_neutral),
                "p": p_mcnemar,
            }

    # 6. ASR by information category
    print("\n--- 6. ASR by Information Category x Framing ---")
    cat_pivot = df.groupby(["item_category", "framing"])["leaked"].mean().unstack()
    print(cat_pivot.to_string())

    # Save statistical results
    # Convert numpy types to Python native for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    serializable = {}
    for k, v in results.items():
        serializable[k] = {kk: convert(vv) for kk, vv in v.items()}

    with open("results/statistical_tests.json", "w") as f:
        json.dump(serializable, f, indent=2)

    return results


# ── Visualizations ───────────────────────────────────────────────────────────
def create_visualizations(df):
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)

    sns.set_theme(style="whitegrid", font_scale=1.2)

    # 1. Overall ASR by framing (bar chart)
    fig, ax = plt.subplots(figsize=(6, 5))
    asr = df.groupby("framing")["leaked"].mean().reset_index()
    asr.columns = ["Framing", "ASR"]
    colors = {"neutral": "#4C72B0", "concealment": "#DD8452"}
    bars = ax.bar(asr["Framing"], asr["ASR"], color=[colors[f] for f in asr["Framing"]])
    ax.set_ylabel("Attack Success Rate (ASR)")
    ax.set_title("Overall Leakage Rate by Framing Condition")
    ax.set_ylim(0, 1)
    for bar, val in zip(bars, asr["ASR"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.1%}", ha="center", fontweight="bold")
    plt.tight_layout()
    plt.savefig("figures/01_overall_asr.png", dpi=150)
    plt.close()
    print("  Saved figures/01_overall_asr.png")

    # 2. ASR by framing x probe type (grouped bar chart)
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot = df.groupby(["probe_type", "framing"])["leaked"].mean().reset_index()
    pivot.columns = ["Probe Type", "Framing", "ASR"]
    probe_order = ["benign", "indirect", "direct", "adversarial"]
    pivot["Probe Type"] = pd.Categorical(pivot["Probe Type"], categories=probe_order, ordered=True)
    pivot = pivot.sort_values("Probe Type")
    sns.barplot(data=pivot, x="Probe Type", y="ASR", hue="Framing",
                palette=colors, ax=ax)
    ax.set_ylabel("Attack Success Rate (ASR)")
    ax.set_title("Leakage Rate by Probe Type and Framing")
    ax.set_ylim(0, 1)
    ax.legend(title="Framing")
    plt.tight_layout()
    plt.savefig("figures/02_asr_by_probe_type.png", dpi=150)
    plt.close()
    print("  Saved figures/02_asr_by_probe_type.png")

    # 3. ASR by framing x model (grouped bar chart)
    fig, ax = plt.subplots(figsize=(8, 5))
    pivot2 = df.groupby(["model", "framing"])["leaked"].mean().reset_index()
    pivot2.columns = ["Model", "Framing", "ASR"]
    sns.barplot(data=pivot2, x="Model", y="ASR", hue="Framing",
                palette=colors, ax=ax)
    ax.set_ylabel("Attack Success Rate (ASR)")
    ax.set_title("Leakage Rate by Model and Framing")
    ax.set_ylim(0, 1)
    ax.legend(title="Framing")
    plt.tight_layout()
    plt.savefig("figures/03_asr_by_model.png", dpi=150)
    plt.close()
    print("  Saved figures/03_asr_by_model.png")

    # 4. ASR by framing x information category (heatmap)
    fig, ax = plt.subplots(figsize=(8, 5))
    heat_data = df.groupby(["item_category", "framing"])["leaked"].mean().unstack()
    heat_data = heat_data[["neutral", "concealment"]]
    sns.heatmap(heat_data, annot=True, fmt=".2f", cmap="RdYlGn_r", vmin=0, vmax=1, ax=ax)
    ax.set_title("ASR by Information Category and Framing")
    ax.set_ylabel("Information Category")
    ax.set_xlabel("Framing Condition")
    plt.tight_layout()
    plt.savefig("figures/04_asr_heatmap_category.png", dpi=150)
    plt.close()
    print("  Saved figures/04_asr_heatmap_category.png")

    # 5. Refusal rate by framing x probe type
    fig, ax = plt.subplots(figsize=(10, 6))
    ref_pivot = df.groupby(["probe_type", "framing"])["refused"].mean().reset_index()
    ref_pivot.columns = ["Probe Type", "Framing", "Refusal Rate"]
    ref_pivot["Probe Type"] = pd.Categorical(ref_pivot["Probe Type"], categories=probe_order, ordered=True)
    ref_pivot = ref_pivot.sort_values("Probe Type")
    sns.barplot(data=ref_pivot, x="Probe Type", y="Refusal Rate", hue="Framing",
                palette=colors, ax=ax)
    ax.set_ylabel("Refusal Rate")
    ax.set_title("Refusal Rate by Probe Type and Framing")
    ax.set_ylim(0, 1)
    ax.legend(title="Framing")
    plt.tight_layout()
    plt.savefig("figures/05_refusal_rate.png", dpi=150)
    plt.close()
    print("  Saved figures/05_refusal_rate.png")

    # 6. Leakage score distribution by framing (violin plot)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.violinplot(data=df, x="framing", y="leakage_score", palette=colors, ax=ax)
    ax.set_ylabel("Leakage Score (0-1)")
    ax.set_xlabel("Framing Condition")
    ax.set_title("Distribution of Leakage Scores by Framing")
    plt.tight_layout()
    plt.savefig("figures/06_leakage_score_violin.png", dpi=150)
    plt.close()
    print("  Saved figures/06_leakage_score_violin.png")

    # 7. Detailed: ASR by framing x probe type x model (faceted)
    fig, axes = plt.subplots(1, df["model"].nunique(), figsize=(14, 5), sharey=True)
    if df["model"].nunique() == 1:
        axes = [axes]
    for ax, model in zip(axes, sorted(df["model"].unique())):
        sub = df[df["model"] == model]
        pivot_m = sub.groupby(["probe_type", "framing"])["leaked"].mean().reset_index()
        pivot_m.columns = ["Probe Type", "Framing", "ASR"]
        pivot_m["Probe Type"] = pd.Categorical(pivot_m["Probe Type"], categories=probe_order, ordered=True)
        pivot_m = pivot_m.sort_values("Probe Type")
        sns.barplot(data=pivot_m, x="Probe Type", y="ASR", hue="Framing",
                    palette=colors, ax=ax)
        ax.set_title(model)
        ax.set_ylim(0, 1)
        if ax != axes[0]:
            ax.set_ylabel("")
            ax.legend().remove()
        else:
            ax.legend(title="Framing", fontsize=9)
    plt.suptitle("ASR by Probe Type and Framing (per Model)", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig("figures/07_asr_faceted_model.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved figures/07_asr_faceted_model.png")

    # 8. Effect size (difference: concealment - neutral) by probe type
    fig, ax = plt.subplots(figsize=(8, 5))
    diff_data = []
    for pt in probe_order:
        sub = df[df["probe_type"] == pt]
        c_rate = sub[sub["framing"] == "concealment"]["leaked"].mean()
        n_rate = sub[sub["framing"] == "neutral"]["leaked"].mean()
        diff = c_rate - n_rate
        # Bootstrap CI
        diffs = []
        for _ in range(1000):
            c_sample = sub[sub["framing"] == "concealment"]["leaked"].sample(frac=1, replace=True).mean()
            n_sample = sub[sub["framing"] == "neutral"]["leaked"].sample(frac=1, replace=True).mean()
            diffs.append(c_sample - n_sample)
        ci_low, ci_high = np.percentile(diffs, [2.5, 97.5])
        diff_data.append({"Probe Type": pt, "Difference": diff, "CI_low": ci_low, "CI_high": ci_high})

    diff_df = pd.DataFrame(diff_data)
    ax.barh(diff_df["Probe Type"], diff_df["Difference"], color="#DD8452", height=0.6)
    ax.errorbar(diff_df["Difference"], diff_df["Probe Type"],
                xerr=[diff_df["Difference"] - diff_df["CI_low"],
                      diff_df["CI_high"] - diff_df["Difference"]],
                fmt="none", color="black", capsize=5)
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Difference in ASR (Concealment - Neutral)")
    ax.set_title("Effect of Concealment Framing on Leakage\n(Positive = concealment leaks MORE)")
    plt.tight_layout()
    plt.savefig("figures/08_effect_size.png", dpi=150)
    plt.close()
    print("  Saved figures/08_effect_size.png")


# ── Error Analysis ───────────────────────────────────────────────────────────
def error_analysis(df):
    print("\n" + "=" * 60)
    print("ERROR ANALYSIS")
    print("=" * 60)

    # Leakage methods breakdown
    print("\n--- Leakage Detection Method Breakdown ---")
    leaked_only = df[df["leaked"] == True]
    if len(leaked_only) > 0:
        method_counts = leaked_only["leakage_method"].value_counts()
        for method, count in method_counts.items():
            print(f"  {method}: {count} ({100*count/len(leaked_only):.1f}%)")

    # Sample leaked responses (concealment condition)
    print("\n--- Sample Leaked Responses (Concealment Condition) ---")
    conceal_leaked = df[(df["framing"] == "concealment") & (df["leaked"] == True)]
    if len(conceal_leaked) > 0:
        samples = conceal_leaked.sample(min(5, len(conceal_leaked)), random_state=42)
        for _, row in samples.iterrows():
            print(f"\n  Item: {row['item_label']} = {row['item_value']}")
            print(f"  Probe ({row['probe_type']}): {row['probe_text'][:80]}...")
            print(f"  Response: {row['response'][:200]}...")
            print(f"  Method: {row['leakage_method']}, Score: {row['leakage_score']:.2f}")

    # Sample non-leaked responses (neutral condition, direct probe)
    print("\n--- Sample Non-Leaked Responses (Neutral, Direct Probe) ---")
    neutral_noleak = df[(df["framing"] == "neutral") & (df["leaked"] == False) & (df["probe_type"] == "direct")]
    if len(neutral_noleak) > 0:
        samples2 = neutral_noleak.sample(min(3, len(neutral_noleak)), random_state=42)
        for _, row in samples2.iterrows():
            print(f"\n  Item: {row['item_label']} = {row['item_value']}")
            print(f"  Probe: {row['probe_text'][:80]}")
            print(f"  Response: {row['response'][:200]}...")

    # Items with highest concealment leakage
    print("\n--- Items with Highest Concealment Leakage ---")
    item_asr = df[df["framing"] == "concealment"].groupby("item_id")["leaked"].mean().sort_values(ascending=False)
    for item_id, asr in item_asr.items():
        print(f"  {item_id}: {asr:.2%}")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = load_results()
    summary_stats(df)
    statistical_tests(df)
    create_visualizations(df)
    error_analysis(df)
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
