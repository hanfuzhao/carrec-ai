"""
Evaluation harness for the CarRec recommendation system.

Computes metrics across diverse test queries to demonstrate how
the smart recommender balances relevance with responsible AI
constraints compared to the naive baseline.

Metrics:
- Budget compliance: fraction of recommendations within user budget
- Brand diversity: unique brands in top-k
- Type diversity: unique body types in top-k
- Niche exposure: fraction of recommendations from niche brands
- Relevance: average use-case match score
"""

# AI Attribution: This code was developed with assistance from AI tools
# (TRAE IDE, https://trae.ai). Design and implementation decisions
# are the author's own.

import json
import os
from pathlib import Path
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from scripts.recommender import naive_recommend, classical_recommend, smart_recommend
from scripts.car_data import CAR_CATALOG, NICHE_BRANDS, MAINSTREAM_BRANDS


TEST_QUERIES = [
    {"query": "I need a family SUV under $50k, preferably electric",
     "expected_budget": 50000, "expected_use_cases": ["family", "eco"],
     "expected_types": ["SUV"]},
    {"query": "Looking for a cheap commute car around $25k",
     "expected_budget": 25000, "expected_use_cases": ["commute"],
     "expected_types": []},
    {"query": "Want a luxury sedan for business, budget $60k",
     "expected_budget": 60000, "expected_use_cases": ["business", "luxury"],
     "expected_types": ["Sedan"]},
    {"query": "Need a 7 seater family car under $50k",
     "expected_budget": 50000, "expected_use_cases": ["family"],
     "expected_types": []},
    {"query": "Looking for an affordable electric car for city driving",
     "expected_budget": 30000, "expected_use_cases": ["city", "eco"],
     "expected_types": []},
    {"query": "Want a sports car for weekend fun, around $40k",
     "expected_budget": 40000, "expected_use_cases": ["sport", "weekend"],
     "expected_types": []},
    {"query": "Need a reliable family car under $30k",
     "expected_budget": 30000, "expected_use_cases": ["family"],
     "expected_types": []},
    {"query": "Looking for a luxury SUV, can spend up to $80k",
     "expected_budget": 80000, "expected_use_cases": ["luxury"],
     "expected_types": ["SUV"]},
    {"query": "Want an eco-friendly car for daily commute, $45k budget",
     "expected_budget": 45000, "expected_use_cases": ["commute", "eco"],
     "expected_types": []},
    {"query": "Need a pickup truck for work and offroad, under $50k",
     "expected_budget": 50000, "expected_use_cases": ["utility", "offroad"],
     "expected_types": ["Pickup"]},
    {"query": "Looking for a safe family SUV around $45k",
     "expected_budget": 45000, "expected_use_cases": ["family", "safety"],
     "expected_types": ["SUV"]},
    {"query": "Want a tech-loaded electric sedan, budget $50k",
     "expected_budget": 50000, "expected_use_cases": ["tech", "eco"],
     "expected_types": ["Sedan"]},
    {"query": "Need an affordable hybrid for family use, $30k",
     "expected_budget": 30000, "expected_use_cases": ["family", "eco"],
     "expected_types": []},
    {"query": "Looking for a premium business sedan, $55k",
     "expected_budget": 55000, "expected_use_cases": ["business", "luxury"],
     "expected_types": ["Sedan"]},
    {"query": "Want a spacious family car for road trips, under $40k",
     "expected_budget": 40000, "expected_use_cases": ["family", "road_trip"],
     "expected_types": []},
]


def compute_relevance(recommendations: List[Dict], expected_use_cases: List[str]) -> float:
    """Compute average relevance score based on use-case overlap."""
    if not recommendations or not expected_use_cases:
        return 0.0

    total = 0.0
    for rec in recommendations:
        car = next((c for c in CAR_CATALOG if c["id"] == rec["id"]), None)
        if car:
            overlap = len(set(car["use_cases"]) & set(expected_use_cases))
            total += overlap / max(len(expected_use_cases), 1)

    return total / len(recommendations)


def evaluate_single(query_info: Dict, top_k: int = 5) -> Dict:
    """Evaluate all three modes on a single query."""
    query = query_info["query"]
    expected_budget = query_info["expected_budget"]
    expected_use_cases = query_info["expected_use_cases"]

    naive = naive_recommend(query, top_k)
    classical = classical_recommend(query, top_k)
    smart = smart_recommend(query, top_k)

    naive_budget_ok = sum(1 for r in naive["recommendations"] if r["price_usd"] <= expected_budget)
    classical_budget_ok = sum(1 for r in classical["recommendations"] if r["price_usd"] <= expected_budget)
    smart_budget_ok = sum(1 for r in smart["recommendations"] if r["price_usd"] <= expected_budget)

    naive_relevance = compute_relevance(naive["recommendations"], expected_use_cases)
    classical_relevance = compute_relevance(classical["recommendations"], expected_use_cases)
    smart_relevance = compute_relevance(smart["recommendations"], expected_use_cases)

    return {
        "query": query,
        "expected_budget": expected_budget,
        "naive": {
            "budget_compliance": naive_budget_ok / top_k,
            "brand_diversity": naive["metrics"]["brand_diversity"],
            "type_diversity": naive["metrics"]["type_diversity"],
            "niche_exposure": naive["metrics"]["niche_exposure"],
            "relevance": naive_relevance,
        },
        "classical": {
            "budget_compliance": classical_budget_ok / top_k,
            "brand_diversity": classical["metrics"]["brand_diversity"],
            "type_diversity": classical["metrics"]["type_diversity"],
            "niche_exposure": classical["metrics"]["niche_exposure"],
            "relevance": classical_relevance,
        },
        "smart": {
            "budget_compliance": smart_budget_ok / top_k,
            "brand_diversity": smart["metrics"]["brand_diversity"],
            "type_diversity": smart["metrics"]["type_diversity"],
            "niche_exposure": smart["metrics"]["niche_exposure"],
            "relevance": smart_relevance,
        },
    }


def run_evaluation(top_k: int = 5) -> Dict:
    """Run evaluation across all test queries."""
    results = [evaluate_single(q, top_k) for q in TEST_QUERIES]

    metrics = ["budget_compliance", "brand_diversity", "type_diversity", "niche_exposure", "relevance"]

    summary = {"naive": {}, "classical": {}, "smart": {}}
    for metric in metrics:
        for mode in ("naive", "classical", "smart"):
            vals = [r[mode][metric] for r in results]
            summary[mode][metric] = {
                "mean": round(np.mean(vals), 3),
                "std": round(np.std(vals), 3),
                "min": round(np.min(vals), 3),
                "max": round(np.max(vals), 3),
            }

    improvements = {}
    for metric in metrics:
        n_mean = summary["naive"][metric]["mean"]
        s_mean = summary["smart"][metric]["mean"]
        if n_mean > 0:
            improvements[metric] = round(((s_mean - n_mean) / n_mean) * 100, 1)
        else:
            improvements[metric] = float("inf") if s_mean > 0 else 0.0

    return {
        "num_queries": len(results),
        "top_k": top_k,
        "per_query": results,
        "summary": summary,
        "improvements_pct": improvements,
        "catalog_stats": {
            "total_cars": len(CAR_CATALOG),
            "mainstream_brands": len(MAINSTREAM_BRANDS),
            "niche_brands": len(NICHE_BRANDS),
            "total_brands": len(MAINSTREAM_BRANDS) + len(NICHE_BRANDS),
        },
    }


def plot_comparison(eval_result: Dict, output_dir: str):
    """Generate comparison plots."""
    os.makedirs(output_dir, exist_ok=True)

    metrics = ["budget_compliance", "brand_diversity", "type_diversity", "niche_exposure", "relevance"]
    labels = ["Budget\nCompliance", "Brand\nDiversity", "Type\nDiversity", "Niche\nExposure", "Relevance"]

    naive_means = [eval_result["summary"]["naive"][m]["mean"] for m in metrics]
    classical_means = [eval_result["summary"]["classical"][m]["mean"] for m in metrics]
    smart_means = [eval_result["summary"]["smart"][m]["mean"] for m in metrics]

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(11, 5))
    bars1 = ax.bar(x - width, naive_means, width, label="Naive (Popularity)", color="#e74c3c", alpha=0.85)
    bars2 = ax.bar(x, classical_means, width, label="Classical (Rule-based)", color="#f39c12", alpha=0.85)
    bars3 = ax.bar(x + width, smart_means, width, label="Smart (RAG+Constraints)", color="#2ecc71", alpha=0.85)

    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Recommendation Quality: Naive vs Classical vs Smart", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.legend(fontsize=10)
    ax.set_ylim(0, max(max(naive_means), max(classical_means), max(smart_means)) * 1.3)

    for bar in bars1 + bars2 + bars3:
        height = bar.get_height()
        ax.annotate(f"{height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "metric_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.flatten()

    for i, metric in enumerate(metrics):
        naive_vals = [r["naive"][metric] for r in eval_result["per_query"]]
        classical_vals = [r["classical"][metric] for r in eval_result["per_query"]]
        smart_vals = [r["smart"][metric] for r in eval_result["per_query"]]

        ax = axes[i]
        x = np.arange(len(naive_vals))
        ax.bar(x - 0.25, naive_vals, 0.25, label="Naive", color="#e74c3c", alpha=0.85)
        ax.bar(x, classical_vals, 0.25, label="Classical", color="#f39c12", alpha=0.85)
        ax.bar(x + 0.25, smart_vals, 0.25, label="Smart", color="#2ecc71", alpha=0.85)
        ax.set_title(metric.replace("_", " ").title(), fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([f"Q{i+1}" for i in range(len(naive_vals))], fontsize=8)
        ax.legend(fontsize=8)

    axes[5].axis("off")
    axes[5].text(0.1, 0.5, f"Catalog: {eval_result['catalog_stats']['total_cars']} cars\n"
                           f"Brands: {eval_result['catalog_stats']['total_brands']} "
                           f"({eval_result['catalog_stats']['mainstream_brands']} mainstream, "
                           f"{eval_result['catalog_stats']['niche_brands']} niche)\n"
                           f"Queries: {eval_result['num_queries']}",
                 fontsize=12, verticalalignment="center")

    plt.suptitle("Per-Query Breakdown (3 Models)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "per_query_breakdown.png"), dpi=150, bbox_inches="tight")
    plt.close()

    niche_exposure = eval_result["summary"]["smart"]["niche_exposure"]["mean"]
    mainstream_exposure = 1.0 - niche_exposure

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie([mainstream_exposure, niche_exposure],
           labels=["Mainstream Brands", "Niche Brands"],
           autopct="%1.1f%%", colors=["#3498db", "#e67e22"],
           startangle=90, textprops={"fontsize": 12})
    ax.set_title("Brand Exposure Distribution (Smart Mode)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fairness_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()


def _to_native(obj):
    """Convert numpy types to native Python for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_native(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def save_results(eval_result: Dict, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(_to_native(eval_result), f, indent=2)


if __name__ == "__main__":
    base = Path(__file__).parent.parent
    output_dir = base / "data" / "outputs"
    plots_dir = output_dir / "plots"

    print("Running evaluation...")
    result = run_evaluation(top_k=5)

    save_results(result, str(output_dir / "evaluation.json"))
    print(f"Saved evaluation to {output_dir / 'evaluation.json'}")

    plot_comparison(result, str(plots_dir))
    print(f"Saved plots to {plots_dir}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for metric in ["budget_compliance", "brand_diversity", "type_diversity", "niche_exposure", "relevance"]:
        n = result["summary"]["naive"][metric]["mean"]
        c = result["summary"]["classical"][metric]["mean"]
        s = result["summary"]["smart"][metric]["mean"]
        imp = result["improvements_pct"][metric]
        print(f"  {metric:25s}  naive={n:.3f}  classical={c:.3f}  smart={s:.3f}  improvement={imp:+.1f}%")
