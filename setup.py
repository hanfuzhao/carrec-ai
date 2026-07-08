"""
Setup script for CarRec AI.

Prepares the data, runs evaluation, and verifies the installation.
Run with: python setup.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def build_data():
    """Generate processed car catalog from source data."""
    print("[1/3] Building car catalog...")
    from scripts.car_data import save_catalog, get_brand_stats

    output = Path(__file__).parent / "data" / "processed" / "cars.json"
    save_catalog(str(output))

    brands = get_brand_stats()
    mainstream = sum(1 for b in brands.values() if b["mainstream"])
    niche = len(brands) - mainstream
    print(f"  Catalog: {output}")
    print(f"  Brands: {len(brands)} ({mainstream} mainstream, {niche} niche)")


def run_evaluation():
    """Run the evaluation harness and generate metrics/plots."""
    print("[2/3] Running evaluation...")
    from scripts.evaluator import run_evaluation, save_results, plot_comparison

    result = run_evaluation(top_k=5)

    base = Path(__file__).parent
    output_dir = base / "data" / "outputs"
    plots_dir = output_dir / "plots"

    save_results(result, str(output_dir / "evaluation.json"))
    plot_comparison(result, str(plots_dir))

    print(f"  Evaluation: {output_dir / 'evaluation.json'}")
    print(f"  Plots: {plots_dir}")

    for metric in ["budget_compliance", "brand_diversity", "type_diversity", "niche_exposure", "relevance"]:
        n = result["summary"]["naive"][metric]["mean"]
        s = result["summary"]["smart"][metric]["mean"]
        print(f"    {metric:25s}  naive={n:.3f}  smart={s:.3f}")


def verify_app():
    """Verify the Flask app can start."""
    print("[3/3] Verifying installation...")
    try:
        from scripts.car_data import CAR_CATALOG
        from scripts.recommender import recommend

        result = recommend("family SUV under $50k", mode="smart", top_k=3)
        assert len(result["recommendations"]) > 0
        assert result["metrics"]["budget_compliance"] == 1.0

        print(f"  Catalog: {len(CAR_CATALOG)} cars loaded")
        print(f"  Test query: '{result['query']}'")
        print(f"  Recommendations: {len(result['recommendations'])}")
        print(f"  Budget compliance: {result['metrics']['budget_compliance']}")
        print("  All checks passed.")
    except Exception as e:
        print(f"  Verification failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    base = Path(__file__).parent
    os.chdir(str(base))

    build_data()
    run_evaluation()
    verify_app()

    print("\nSetup complete. Run 'python main.py' to start the web app.")
