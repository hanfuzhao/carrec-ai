# CarRec AI

Recommendations that actually matter. An LLM-powered car recommendation system that balances relevance with responsible AI constraints.

Live demo: https://carrec-ai.onrender.com

## What It Does

CarRec AI recommends cars based on natural language queries like "I need a family SUV under $50k, preferably electric." Unlike popularity-based recommenders, it enforces four real-world constraints:

- **Budget compliance**: never recommends a car above the user's stated budget
- **Brand diversity**: ensures recommendations span multiple brands rather than clustering around one
- **Fairness**: boosts niche brands (BYD, NIO, Polestar, Rivian, etc.) so they get equitable exposure alongside mainstream names like Toyota and Tesla
- **Cold start**: works with zero user history by parsing preferences directly from the query

## How It Works

Two recommendation modes provide a before/after comparison:

**Naive mode** (before): sorts the entire catalog by popularity and returns the top 5. No budget filtering, no diversity enforcement, no fairness boost.

**Smart mode** (after): uses retrieval-augmented generation (RAG) with an LLM. The pipeline is:
1. Parse the query to extract budget, use cases, energy preferences, body style, and seating needs
2. Filter the catalog by budget (hard constraint)
3. Score each car on use-case match, preference alignment, and a fairness boost for niche brands
4. Enforce brand/type diversity through a greedy selection with diversity penalties
5. Use GPT-4o-mini to generate personalized recommendation reasons

When no OpenAI API key is available, the system falls back to template-based reasons, so the app still works without external dependencies.

## Catalog

70 vehicles across 27 brands, covering sedans, SUVs, MPVs, coupes, hatchbacks, wagons, pickups, and convertibles. Price range from $23,000 to $115,000. Energy types include gasoline, hybrid, PHEV, and BEV.

12 mainstream brands: Toyota, Honda, Tesla, BMW, Mercedes-Benz, Audi, Volkswagen, Ford, Chevrolet, Hyundai, Kia, Nissan.

15 niche brands: BYD, NIO, Xpeng, Li Auto, Polestar, Rivian, Lucid, Genesis, Mini, Subaru, Mazda, Volvo, Porsche, Lexus, Buick.

## Evaluation Results

Across 15 diverse test queries, the smart mode outperforms the naive baseline:

| Metric | Naive | Smart | Improvement |
|--------|-------|-------|-------------|
| Budget compliance | 0.840 | 1.000 | +19.0% |
| Brand diversity | 3.000 | 4.933 | +64.4% |
| Type diversity | 2.000 | 2.533 | +26.6% |
| Niche exposure | 0.000 | 0.600 | from zero to 60% |
| Relevance | 0.380 | 0.793 | +108.7% |

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Build data and run evaluation
python setup.py

# Start the web app
python main.py
```

The app runs on http://localhost:7860.

To enable LLM-enhanced recommendation reasons, set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-key-here"
```

Without the key, the app uses template-based reasons and still works fully.

## Project Structure

```
Module3_Hackathon/
├── README.md
├── requirements.txt
├── requirements-deploy.txt
├── Makefile
├── setup.py
├── main.py                 # Flask web app
├── Dockerfile
├── scripts/
│   ├── __init__.py
│   ├── car_data.py         # Car catalog (70 cars, 27 brands)
│   ├── recommender.py      # LLM recommendation engine
│   └── evaluator.py        # Evaluation harness
├── data/
│   ├── raw/
│   ├── processed/
│   │   └── cars.json
│   └── outputs/
│       ├── evaluation.json
│       └── plots/
│           ├── metric_comparison.png
│           ├── per_query_breakdown.png
│           └── fairness_distribution.png
├── models/
├── notebooks/
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   └── index.html
└── .github/
    ├── pull_request_template.md
    └── workflows/keep-alive.yml
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/api/recommend` | POST | Get recommendations (`{"query": "...", "mode": "smart"}`) |
| `/api/compare` | POST | Before/after comparison (`{"query": "..."}`) |
| `/api/catalog` | GET | Browse catalog with filters |
| `/api/stats` | GET | Catalog statistics |
| `/api/evaluation` | GET | Evaluation metrics |
| `/health` | GET | Health check |

## Deployment

The app is deployed on HuggingFace Space using Docker. To deploy your own instance:

1. Create a new Space on HuggingFace
2. Set `OPENAI_API_KEY` as a secret (optional)
3. Push the code to the Space repository

## Tech Stack

- Python 3.11
- Flask
- OpenAI GPT-4o-mini (optional, for enhanced reasons)
- Matplotlib (evaluation plots)
- Vanilla JavaScript, CSS (frontend)
