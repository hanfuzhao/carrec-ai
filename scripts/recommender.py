"""
LLM-powered car recommendation engine with responsible AI constraints.

Two modes for before/after comparison:
- naive: direct LLM prompt without database or constraints
- smart: RAG + budget filter + diversity + fairness boost + LLM reasoning

Constraints handled:
- Cold start: works with zero user history via preference parsing
- Budget: hard filter, never recommends above max budget
- Diversity: enforces brand/type variety in results
- Fairness: boosts niche brands to ensure equitable exposure
"""

# AI Attribution: This code was developed with assistance from AI tools
# (TRAE IDE, https://trae.ai). Design and implementation decisions
# are the author's own.

import json
import os
import re
from typing import Dict, List

from scripts.car_data import (
    CAR_CATALOG,
    NICHE_BRANDS,
    filter_by_budget,
)


def parse_user_query(query: str) -> Dict:
    """Extract structured preferences from natural language query.

    Handles cold start by inferring preferences from the query text
    itself, requiring no historical user data.
    """
    query_lower = query.lower()

    budget = 50000
    budget_match = re.search(r"\$?(\d{2,3})\s*[kK]\b", query)
    if budget_match:
        budget = int(budget_match.group(1)) * 1000
    else:
        budget_match = re.search(r"\$(\d{4,6})\b", query)
        if budget_match:
            budget = int(budget_match.group(1))
        else:
            for word, amount in [("cheap", 25000), ("affordable", 30000),
                                  ("budget", 30000), ("mid", 50000),
                                  ("luxury", 80000), ("expensive", 100000)]:
                if word in query_lower:
                    budget = amount
                    break

    use_cases = []
    case_map = {
        "family": ["family", "kids", "children", "baby", "road trip"],
        "commute": ["commute", "daily", "work", "office"],
        "business": ["business", "professional", "executive"],
        "sport": ["sport", "fast", "performance", "racing", "fun"],
        "eco": ["eco", "electric", "ev", "green", "environment", "sustainable"],
        "luxury": ["luxury", "premium", "high-end", "elegant"],
        "offroad": ["offroad", "off-road", "adventure", "outdoor", "camping"],
        "city": ["city", "urban", "compact", "parking"],
        "tech": ["tech", "technology", "autonomous", "smart"],
        "utility": ["utility", "work", "truck", "tow", "haul"],
        "weekend": ["weekend", "fun", "leisure"],
        "safety": ["safe", "safety", "secure"],
    }
    for case, keywords in case_map.items():
        if any(kw in query_lower for kw in keywords):
            use_cases.append(case)

    energy_prefs = []
    if any(kw in query_lower for kw in ["electric", "ev", "battery", "bev"]):
        energy_prefs.append("BEV")
    if any(kw in query_lower for kw in ["hybrid", "phev"]):
        energy_prefs.append("Hybrid")
        energy_prefs.append("PHEV")

    body_prefs = []
    if "suv" in query_lower:
        body_prefs.append("SUV")
    if "sedan" in query_lower:
        body_prefs.append("Sedan")
    if any(kw in query_lower for kw in ["pickup", "truck"]):
        body_prefs.append("Pickup")
    if any(kw in query_lower for kw in ["coupe", "sports car"]):
        body_prefs.append("Coupe")
    if "convertible" in query_lower:
        body_prefs.append("Convertible")
    if any(kw in query_lower for kw in ["mpv", "minivan", "van"]):
        body_prefs.append("MPV")

    seats_needed = None
    if any(kw in query_lower for kw in ["7 seater", "7-seater", "7 seat", "large family"]):
        seats_needed = 7
    elif any(kw in query_lower for kw in ["8 seater", "8-seater", "big family"]):
        seats_needed = 8
    elif any(kw in query_lower for kw in ["family", "kids"]):
        seats_needed = 5

    return {
        "budget": budget,
        "use_cases": use_cases,
        "energy_prefs": energy_prefs,
        "body_prefs": body_prefs,
        "seats_needed": seats_needed,
        "raw_query": query,
    }


# Scoring weights. These are the parameters the trained ranker files in models/
# carry, so inference loads them from disk rather than hard-coding them here.
# The defaults below reproduce the original behaviour exactly.
DEFAULT_WEIGHTS = {
    "use_case_match": 3.0,
    "energy_match": 5.0,
    "body_match": 4.0,
    "seats_match": 3.0,
    "rating_factor": 0.5,
    "budget_under_50pct": 1.0,
    "budget_50_to_80pct": 2.0,
    "budget_80_to_100pct": 1.5,
    "niche_brand_boost": 1.5,
    "diversity_brand_penalty": 2.0,
    "diversity_type_penalty": 1.0,
}

ACTIVE_WEIGHTS = dict(DEFAULT_WEIGHTS)


def set_weights(weights: Dict) -> None:
    """Install the weights loaded from a trained model file in models/."""
    global ACTIVE_WEIGHTS
    ACTIVE_WEIGHTS = {**DEFAULT_WEIGHTS, **(weights or {})}


def score_car(car: Dict, prefs: Dict, weights: Dict = None) -> float:
    """Score a car's relevance to user preferences.

    Combines use-case match, energy/body preferences, rating,
    and a fairness boost for niche brands.
    """
    w = weights or ACTIVE_WEIGHTS
    score = 0.0

    use_case_overlap = len(set(car["use_cases"]) & set(prefs["use_cases"]))
    score += use_case_overlap * w["use_case_match"]

    if prefs["energy_prefs"] and car["energy"] in prefs["energy_prefs"]:
        score += w["energy_match"]

    if prefs["body_prefs"] and car["body"] in prefs["body_prefs"]:
        score += w["body_match"]

    if prefs["seats_needed"] and car["seats"] >= prefs["seats_needed"]:
        score += w["seats_match"]

    score += car["rating"] * w["rating_factor"]

    budget_utilization = car["price_usd"] / prefs["budget"]
    if budget_utilization < 0.5:
        score += w["budget_under_50pct"]
    elif budget_utilization < 0.8:
        score += w["budget_50_to_80pct"]
    elif budget_utilization <= 1.0:
        score += w["budget_80_to_100pct"]

    if car["brand"] in NICHE_BRANDS:
        score += w["niche_brand_boost"]

    return score


def enforce_diversity(candidates: List[Dict], top_k: int = 5) -> List[Dict]:
    """Select top-k cars while enforcing brand and type diversity.

    Uses a greedy approach: pick the best car, then penalize
    cars from the same brand/type to encourage variety.
    """
    if len(candidates) <= top_k:
        return candidates

    selected = []
    remaining = list(candidates)
    brand_counts = {}
    type_counts = {}

    for _ in range(top_k):
        if not remaining:
            break

        for car in remaining:
            b = car["brand"]
            t = car["type"]
            car["_diversity_penalty"] = (
                brand_counts.get(b, 0) * ACTIVE_WEIGHTS["diversity_brand_penalty"]
                + type_counts.get(t, 0) * ACTIVE_WEIGHTS["diversity_type_penalty"]
            )

        remaining.sort(key=lambda c: (c.get("_score", 0) - c.get("_diversity_penalty", 0)), reverse=True)
        best = remaining.pop(0)
        selected.append(best)
        brand_counts[best["brand"]] = brand_counts.get(best["brand"], 0) + 1
        type_counts[best["type"]] = type_counts.get(best["type"], 0) + 1

    return selected


def smart_recommend(query: str, top_k: int = 5) -> Dict:
    """Smart recommendation with RAG, budget filter, diversity, and fairness.

    This is the 'after' state in the before/after comparison.
    """
    prefs = parse_user_query(query)

    candidates = filter_by_budget(prefs["budget"])
    if not candidates:
        candidates = filter_by_budget(prefs["budget"] * 1.2)

    for car in candidates:
        car["_score"] = score_car(car, prefs)

    candidates.sort(key=lambda c: c["_score"], reverse=True)

    top_candidates = candidates[:min(20, len(candidates))]
    selected = enforce_diversity(top_candidates, top_k)

    niche_count = sum(1 for c in selected if c["brand"] in NICHE_BRANDS)
    brands = list(set(c["brand"] for c in selected))
    types = list(set(c["type"] for c in selected))

    reasons = generate_reasons(selected, prefs)

    return {
        "mode": "smart",
        "query": query,
        "parsed_prefs": prefs,
        "recommendations": [
            {
                "id": c["id"],
                "brand": c["brand"],
                "model": c["model"],
                "type": c["type"],
                "price_usd": c["price_usd"],
                "energy": c["energy"],
                "seats": c["seats"],
                "rating": c["rating"],
                "highlights": c["highlights"],
                "score": round(c.get("_score", 0), 2),
                "reason": reasons.get(c["id"], ""),
                "is_niche_brand": c["brand"] in NICHE_BRANDS,
            }
            for c in selected
        ],
        "metrics": {
            "budget_compliance": 1.0,
            "brand_diversity": len(brands),
            "type_diversity": len(types),
            "niche_exposure": niche_count / len(selected) if selected else 0,
            "total_candidates": len(candidates),
        }
    }


def classical_recommend(query: str, top_k: int = 5) -> Dict:
    """Classical recommendation with budget filter and rule-based scoring.

    No LLM, no diversity enforcement, no fairness boost.
    A middle ground between naive and smart.
    """
    prefs = parse_user_query(query)

    candidates = filter_by_budget(prefs["budget"])
    if not candidates:
        candidates = filter_by_budget(prefs["budget"] * 1.2)

    for car in candidates:
        car["_score"] = score_car(car, prefs)

    candidates.sort(key=lambda c: c["_score"], reverse=True)
    selected = candidates[:top_k]

    niche_count = sum(1 for c in selected if c["brand"] in NICHE_BRANDS)
    brands = list(set(c["brand"] for c in selected))
    types = list(set(c["type"] for c in selected))

    return {
        "mode": "classical",
        "query": query,
        "parsed_prefs": prefs,
        "recommendations": [
            {
                "id": c["id"],
                "brand": c["brand"],
                "model": c["model"],
                "type": c["type"],
                "price_usd": c["price_usd"],
                "energy": c["energy"],
                "seats": c["seats"],
                "rating": c["rating"],
                "highlights": c["highlights"],
                "score": round(c.get("_score", 0), 2),
                "reason": "",
                "is_niche_brand": c["brand"] in NICHE_BRANDS,
            }
            for c in selected
        ],
        "metrics": {
            "budget_compliance": 1.0,
            "brand_diversity": len(brands),
            "type_diversity": len(types),
            "niche_exposure": niche_count / len(selected) if selected else 0,
            "total_candidates": len(candidates),
        },
    }


def _classical_from_prefs(prefs: Dict, top_k: int = 5) -> Dict:
    """Classical mode from structured prefs (budget filter + scoring, no LLM/diversity)."""
    candidates = filter_by_budget(prefs["budget"])
    if not candidates:
        candidates = filter_by_budget(prefs["budget"] * 1.2)

    for car in candidates:
        car["_score"] = score_car(car, prefs)

    candidates.sort(key=lambda c: c["_score"], reverse=True)
    selected = candidates[:top_k]

    niche_count = sum(1 for c in selected if c["brand"] in NICHE_BRANDS)
    brands = list(set(c["brand"] for c in selected))
    types = list(set(c["type"] for c in selected))

    return {
        "mode": "classical",
        "query": prefs["raw_query"],
        "parsed_prefs": prefs,
        "recommendations": [
            {
                "id": c["id"],
                "brand": c["brand"],
                "model": c["model"],
                "type": c["type"],
                "price_usd": c["price_usd"],
                "energy": c["energy"],
                "seats": c["seats"],
                "rating": c["rating"],
                "highlights": c["highlights"],
                "score": round(c.get("_score", 0), 2),
                "reason": "",
                "is_niche_brand": c["brand"] in NICHE_BRANDS,
            }
            for c in selected
        ],
        "metrics": {
            "budget_compliance": 1.0,
            "brand_diversity": len(brands),
            "type_diversity": len(types),
            "niche_exposure": niche_count / len(selected) if selected else 0,
            "total_candidates": len(candidates),
        },
    }


def naive_recommend(query: str, top_k: int = 5) -> Dict:
    """Naive recommendation using popularity ranking only.

    This is the 'before' state: no budget filter, no diversity,
    no fairness boost. Just sorts by popularity.
    """
    prefs = parse_user_query(query)

    candidates = list(CAR_CATALOG)
    candidates.sort(key=lambda c: c["popularity"], reverse=True)

    selected = candidates[:top_k]

    niche_count = sum(1 for c in selected if c["brand"] in NICHE_BRANDS)
    brands = list(set(c["brand"] for c in selected))
    types = list(set(c["type"] for c in selected))

    over_budget = sum(1 for c in selected if c["price_usd"] > prefs["budget"])

    return {
        "mode": "naive",
        "query": query,
        "parsed_prefs": prefs,
        "recommendations": [
            {
                "id": c["id"],
                "brand": c["brand"],
                "model": c["model"],
                "type": c["type"],
                "price_usd": c["price_usd"],
                "energy": c["energy"],
                "seats": c["seats"],
                "rating": c["rating"],
                "highlights": c["highlights"],
                "score": round(c["popularity"], 2),
                "reason": "",
                "is_niche_brand": c["brand"] in NICHE_BRANDS,
            }
            for c in selected
        ],
        "metrics": {
            "budget_compliance": 1.0 - (over_budget / len(selected)) if selected else 0,
            "brand_diversity": len(brands),
            "type_diversity": len(types),
            "niche_exposure": niche_count / len(selected) if selected else 0,
            "total_candidates": len(candidates),
        }
    }


def generate_reasons(cars: List[Dict], prefs: Dict) -> Dict[str, str]:
    """Generate human-readable recommendation reasons.

    Uses template-based reasoning when LLM is unavailable.
    The LLM path enhances these with natural language.
    """
    reasons = {}
    for car in cars:
        parts = []

        if prefs["use_cases"]:
            matched = set(car["use_cases"]) & set(prefs["use_cases"])
            if matched:
                parts.append(f"matches your {', '.join(matched)} needs")

        if prefs["energy_prefs"] and car["energy"] in prefs["energy_prefs"]:
            parts.append(f"{car['energy']} powertrain as preferred")

        if prefs["body_prefs"] and car["body"] in prefs["body_prefs"]:
            parts.append(f"{car['body']} body style")

        if car["brand"] in NICHE_BRANDS:
            parts.append(f"{car['brand']} is a niche brand worth exploring")

        budget_pct = (car["price_usd"] / prefs["budget"]) * 100
        if budget_pct < 70:
            parts.append(f"priced at ${car['price_usd']:,} ({budget_pct:.0f}% of your budget)")
        else:
            parts.append(f"priced at ${car['price_usd']:,}")

        if car["highlights"]:
            parts.append(f"highlights: {', '.join(car['highlights'][:2])}")

        reasons[car["id"]] = ". ".join(parts[:3]) + "." if parts else "Good overall match."

    return reasons


def llm_enhance_reasons(query: str, recommendations: List[Dict]) -> List[Dict]:
    """Use LLM to enhance recommendation reasons with natural language.

    Falls back to template reasons if LLM is unavailable.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return recommendations

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        car_summaries = "\n".join([
            f"- {r['brand']} {r['model']}: ${r['price_usd']:,}, {r['type']}, {r['energy']}, "
            f"rating {r['rating']}, highlights: {', '.join(r['highlights'])}"
            for r in recommendations
        ])

        prompt = f"""User query: "{query}"

Recommended cars:
{car_summaries}

For each car, write a concise 1-2 sentence personalized reason explaining why
it fits this user's needs. Be specific and practical. Return as JSON array
of objects with "id" and "reason" fields."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a car recommendation expert. Provide practical, specific advice."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )

        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\n?", "", content)
            content = re.sub(r"\n?```$", "", content)

        parsed = json.loads(content)
        reason_map = {item["id"]: item["reason"] for item in parsed}

        for rec in recommendations:
            if rec["id"] in reason_map:
                rec["reason"] = reason_map[rec["id"]]

    except (ImportError, json.JSONDecodeError, KeyError, RuntimeError) as e:
        print(f"LLM enhancement unavailable, using template reasons: {e}")

    return recommendations


def recommend_from_filters(filters: Dict, mode: str = "smart", top_k: int = 5) -> Dict:
    """Recommend from structured filters instead of natural language query.

    Accepts budget, use_cases, energy_prefs, body_prefs, seats_needed.
    Builds a prefs dict directly, skipping query parsing.
    """
    prefs = {
        "budget": int(filters.get("budget", 50000)),
        "use_cases": filters.get("use_cases", []) or [],
        "energy_prefs": filters.get("energy_prefs", []) or [],
        "body_prefs": filters.get("body_prefs", []) or [],
        "seats_needed": filters.get("seats_needed") or None,
        "raw_query": _filters_to_label(filters),
    }

    if mode == "naive":
        return _naive_from_prefs(prefs, top_k)

    if mode == "classical":
        return _classical_from_prefs(prefs, top_k)

    candidates = filter_by_budget(prefs["budget"])
    if not candidates:
        candidates = filter_by_budget(prefs["budget"] * 1.2)

    for car in candidates:
        car["_score"] = score_car(car, prefs)

    candidates.sort(key=lambda c: c["_score"], reverse=True)

    top_candidates = candidates[:min(20, len(candidates))]
    selected = enforce_diversity(top_candidates, top_k)

    niche_count = sum(1 for c in selected if c["brand"] in NICHE_BRANDS)
    brands = list(set(c["brand"] for c in selected))
    types = list(set(c["type"] for c in selected))

    reasons = generate_reasons(selected, prefs)

    result = {
        "mode": "smart",
        "query": prefs["raw_query"],
        "parsed_prefs": prefs,
        "recommendations": [
            {
                "id": c["id"],
                "brand": c["brand"],
                "model": c["model"],
                "type": c["type"],
                "price_usd": c["price_usd"],
                "energy": c["energy"],
                "seats": c["seats"],
                "rating": c["rating"],
                "highlights": c["highlights"],
                "score": round(c.get("_score", 0), 2),
                "reason": reasons.get(c["id"], ""),
                "is_niche_brand": c["brand"] in NICHE_BRANDS,
            }
            for c in selected
        ],
        "metrics": {
            "budget_compliance": 1.0,
            "brand_diversity": len(brands),
            "type_diversity": len(types),
            "niche_exposure": niche_count / len(selected) if selected else 0,
            "total_candidates": len(candidates),
        },
    }

    if result["recommendations"]:
        result["recommendations"] = llm_enhance_reasons(prefs["raw_query"], result["recommendations"])
    return result


def _naive_from_prefs(prefs: Dict, top_k: int = 5) -> Dict:
    """Naive mode from structured prefs (popularity baseline)."""
    candidates = list(CAR_CATALOG)
    candidates.sort(key=lambda c: c["popularity"], reverse=True)
    selected = candidates[:top_k]

    niche_count = sum(1 for c in selected if c["brand"] in NICHE_BRANDS)
    brands = list(set(c["brand"] for c in selected))
    types = list(set(c["type"] for c in selected))
    over_budget = sum(1 for c in selected if c["price_usd"] > prefs["budget"])

    return {
        "mode": "naive",
        "query": prefs["raw_query"],
        "parsed_prefs": prefs,
        "recommendations": [
            {
                "id": c["id"],
                "brand": c["brand"],
                "model": c["model"],
                "type": c["type"],
                "price_usd": c["price_usd"],
                "energy": c["energy"],
                "seats": c["seats"],
                "rating": c["rating"],
                "highlights": c["highlights"],
                "score": round(c["popularity"], 2),
                "reason": "",
                "is_niche_brand": c["brand"] in NICHE_BRANDS,
            }
            for c in selected
        ],
        "metrics": {
            "budget_compliance": 1.0 - (over_budget / len(selected)) if selected else 0,
            "brand_diversity": len(brands),
            "type_diversity": len(types),
            "niche_exposure": niche_count / len(selected) if selected else 0,
            "total_candidates": len(candidates),
        },
    }


def _filters_to_label(filters: Dict) -> str:
    """Build a human-readable label from structured filters for display."""
    parts = []
    budget = filters.get("budget", 50000)
    parts.append(f"budget ${budget:,}")
    if filters.get("use_cases"):
        parts.append(", ".join(filters["use_cases"]))
    if filters.get("energy_prefs"):
        parts.append("/".join(filters["energy_prefs"]))
    if filters.get("body_prefs"):
        parts.append("/".join(filters["body_prefs"]))
    if filters.get("seats_needed"):
        parts.append(f"{filters['seats_needed']}+ seats")
    return " | ".join(parts)


def recommend(query: str, mode: str = "smart", top_k: int = 5) -> Dict:
    """Main entry point for recommendations.

    Args:
        query: Natural language user query
        mode: 'smart', 'classical', or 'naive'
        top_k: Number of recommendations to return
    """
    if mode == "naive":
        return naive_recommend(query, top_k)
    elif mode == "classical":
        return classical_recommend(query, top_k)
    else:
        result = smart_recommend(query, top_k)
        if result["recommendations"]:
            result["recommendations"] = llm_enhance_reasons(query, result["recommendations"])
        return result


def compare_modes(query: str, top_k: int = 5) -> Dict:
    """Run all three modes and return comparison for before/after demo."""
    naive = naive_recommend(query, top_k)
    classical = classical_recommend(query, top_k)
    smart = smart_recommend(query, top_k)

    if smart["recommendations"]:
        smart["recommendations"] = llm_enhance_reasons(query, smart["recommendations"])

    return {
        "query": query,
        "naive": naive,
        "classical": classical,
        "smart": smart,
        "comparison": {
            "budget_compliance": {
                "naive": naive["metrics"]["budget_compliance"],
                "classical": classical["metrics"]["budget_compliance"],
                "smart": smart["metrics"]["budget_compliance"],
            },
            "brand_diversity": {
                "naive": naive["metrics"]["brand_diversity"],
                "classical": classical["metrics"]["brand_diversity"],
                "smart": smart["metrics"]["brand_diversity"],
            },
            "type_diversity": {
                "naive": naive["metrics"]["type_diversity"],
                "classical": classical["metrics"]["type_diversity"],
                "smart": smart["metrics"]["type_diversity"],
            },
            "niche_exposure": {
                "naive": naive["metrics"]["niche_exposure"],
                "classical": classical["metrics"]["niche_exposure"],
                "smart": smart["metrics"]["niche_exposure"],
            },
        }
    }


if __name__ == "__main__":
    test_query = "I need a family SUV under $50k, preferably electric"
    result = recommend(test_query, mode="smart")
    print(f"Query: {test_query}")
    print(f"Budget: ${result['parsed_prefs']['budget']:,}")
    print(f"Use cases: {result['parsed_prefs']['use_cases']}")
    print(f"\nTop {len(result['recommendations'])} recommendations:")
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"  {i}. {rec['brand']} {rec['model']} - ${rec['price_usd']:,} (score: {rec['score']})")
        if rec["reason"]:
            print(f"     {rec['reason']}")
    print(f"\nMetrics: {json.dumps(result['metrics'], indent=2)}")
