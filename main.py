"""
CarRec AI - Flask web application for LLM-powered car recommendations.

Endpoints:
- GET  /            : Main UI
- POST /api/recommend : Get recommendations (smart or naive mode)
- POST /api/compare  : Before/after comparison
- GET  /api/catalog  : List all cars in catalog
- GET  /api/evaluation : Return evaluation metrics
- GET  /api/stats    : Catalog statistics
- GET  /health       : Health check
"""

# AI Attribution: This code was developed with assistance from AI tools
# (TRAE IDE, https://trae.ai). Design and implementation decisions
# are the author's own.

import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from scripts.car_data import (
    CAR_CATALOG,
    MAINSTREAM_BRANDS,
    NICHE_BRANDS,
    get_brand_stats,
    get_catalog,
)
from scripts.model import load_all
from scripts.recommender import compare_modes, recommend, recommend_from_filters


app = Flask(__name__, static_folder="static", template_folder="templates")

# Load the three trained rankers from models/ once at startup. This also installs
# the smart ranker's scoring weights, so every request is scored with parameters
# read from the model files rather than constants in the code.
MODELS = load_all()


@app.route("/")
def index():
    """Render the main web UI."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Return service health, catalog size, and the loaded models."""
    return jsonify({
        "status": "healthy",
        "catalog_size": len(CAR_CATALOG),
        "brands": len(MAINSTREAM_BRANDS) + len(NICHE_BRANDS),
        "models_loaded": len(MODELS),
        "models": {mode: m.describe() for mode, m in MODELS.items()},
    })


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """Return recommendations from structured filters or natural language query."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    mode = data.get("mode", "smart")
    top_k = min(data.get("top_k", 5), 10)

    if mode not in ("smart", "classical", "naive"):
        return jsonify({"error": "mode must be 'smart', 'classical', or 'naive'"}), 400

    try:
        if "filters" in data and data["filters"]:
            result = recommend_from_filters(data["filters"], mode=mode, top_k=top_k)
        elif "query" in data and data["query"]:
            result = recommend(data["query"], mode=mode, top_k=top_k)
        else:
            return jsonify({"error": "Provide 'filters' or 'query' field"}), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compare", methods=["POST"])
def api_compare():
    """Run both naive and smart modes and return side-by-side comparison."""
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' field"}), 400

    query = data["query"]
    top_k = min(data.get("top_k", 5), 10)

    try:
        result = compare_modes(query, top_k=top_k)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/catalog")
def api_catalog():
    """Browse the catalog with optional brand, type, energy, and price filters."""
    brand_filter = request.args.get("brand")
    type_filter = request.args.get("type")
    energy_filter = request.args.get("energy")
    max_price = request.args.get("max_price", type=float)

    cars = get_catalog()

    if brand_filter:
        cars = [c for c in cars if c["brand"].lower() == brand_filter.lower()]
    if type_filter:
        cars = [c for c in cars if c["type"].lower() == type_filter.lower()]
    if energy_filter:
        cars = [c for c in cars if c["energy"].lower() == energy_filter.lower()]
    if max_price:
        cars = [c for c in cars if c["price_usd"] <= max_price]

    return jsonify({
        "count": len(cars),
        "cars": cars,
    })


@app.route("/api/stats")
def api_stats():
    """Return catalog statistics: brand counts, type counts, energy counts, price ranges."""
    brands = get_brand_stats()
    types = {}
    energy = {}
    price_ranges = {"under_30k": 0, "30k_50k": 0, "50k_80k": 0, "over_80k": 0}

    for car in CAR_CATALOG:
        t = car["type"]
        types[t] = types.get(t, 0) + 1

        e = car["energy"]
        energy[e] = energy.get(e, 0) + 1

        p = car["price_usd"]
        if p < 30000:
            price_ranges["under_30k"] += 1
        elif p < 50000:
            price_ranges["30k_50k"] += 1
        elif p < 80000:
            price_ranges["50k_80k"] += 1
        else:
            price_ranges["over_80k"] += 1

    return jsonify({
        "total_cars": len(CAR_CATALOG),
        "total_brands": len(brands),
        "mainstream_brands": len(MAINSTREAM_BRANDS),
        "niche_brands": len(NICHE_BRANDS),
        "brands": brands,
        "types": types,
        "energy": energy,
        "price_ranges": price_ranges,
    })


@app.route("/api/evaluation")
def api_evaluation():
    """Return the full evaluation results from data/outputs/evaluation.json."""
    eval_path = Path(__file__).parent / "data" / "outputs" / "evaluation.json"
    if eval_path.exists():
        with open(eval_path) as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Evaluation not run yet. Run scripts/evaluator.py first."}), 404


@app.route("/api/plots/<path:filename>")
def api_plots(filename):
    """Serve evaluation plot images from data/outputs/plots/."""
    plots_dir = Path(__file__).parent / "data" / "outputs" / "plots"
    if plots_dir.exists():
        return send_from_directory(str(plots_dir), filename)
    return jsonify({"error": "Plots not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)
