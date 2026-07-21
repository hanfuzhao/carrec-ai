# CarRec AI

Recommendations that actually matter. An LLM-powered car recommendation system that balances relevance with responsible AI constraints.

Live demo: https://carrec-ai.onrender.com

## What It Does

CarRec AI recommends cars based on natural language queries like "I need a family SUV under $50k, preferably electric." Unlike popularity-based recommenders, it enforces four real-world constraints:

- **Budget compliance**: never recommends a car above the user's stated budget
- **Brand diversity**: ensures recommendations span multiple brands rather than clustering around one
- **Fairness**: boosts niche brands (BYD, NIO, Polestar, Rivian, etc.) so they get equitable exposure alongside mainstream names like Toyota and Tesla
- **Cold start**: works with zero user history by parsing preferences directly from the query

## Why This Is More Than Convenience

Buying a car is the second-largest purchase most households ever make, and it is one of the
biggest personal decisions people make about energy use. A recommender that optimizes for
clicks in this setting does real damage, not just mild annoyance. Four concrete stakes:

**Financial harm.** A popularity-ranked list happily shows cars people cannot afford. Our
naive baseline scores 0.84 on budget compliance, meaning roughly one in six of its picks blows
past the stated budget. Treating budget as a hard constraint rather than a ranking feature
takes that to 1.00. Nobody gets nudged toward a loan they should not sign.

**Who gets seen.** Recommenders decide which brands exist in a buyer's mind. Popularity
feedback loops entrench incumbents: the naive baseline gives niche brands 0 percent exposure,
so 26 of the 42 brands in the catalog are effectively invisible no matter how well they fit.
The fairness boost lifts that to 85 percent, which matters both for market competition and for
buyers who would otherwise never discover a better-value or cleaner option.

**Energy choices.** The catalog spans gasoline, hybrid, PHEV, and battery electric. Honoring a
stated preference for an efficient vehicle, instead of defaulting to whatever is popular, is a
small lever on a decision that determines a household's emissions for the next decade.

**Privacy by default.** The system cold-starts from what the user says they want. It needs no
behavioral profile, no tracking history, and no cross-site data to make a good recommendation.

That is the argument for the whole design: relevance and responsibility are not a trade-off
here. The evaluation below shows relevance more than doubling at the same time as fairness and
diversity improve.

## How It Works

Three recommendation modes provide a progressive comparison:

**Naive mode** (baseline): sorts the entire catalog by popularity and returns the top 5. No budget filtering, no diversity enforcement, no fairness boost.

**Classical mode** (middle): adds budget filtering and rule-based scoring on use-case match, energy/body preferences, and budget utilization. No LLM, no diversity enforcement, no fairness boost.

**Smart mode** (full): uses retrieval-augmented generation (RAG) with an LLM. The pipeline is:
1. Parse the query to extract budget, use cases, energy preferences, body style, and seating needs
2. Filter the catalog by budget (hard constraint)
3. Score each car on use-case match, preference alignment, and a fairness boost for niche brands
4. Enforce brand/type diversity through a greedy selection with diversity penalties
5. Use GPT-4o-mini to generate personalized recommendation reasons

When no OpenAI API key is available, the system falls back to template-based reasons, so the app still works without external dependencies.

## Catalog

422 vehicles across 42 brands, covering sedans, SUVs, MPVs, coupes, hatchbacks, wagons, pickups, and convertibles. Price range from $16,000 to $28,000,000. Energy types include gasoline, hybrid, PHEV, and BEV.

16 mainstream brands: Toyota, Honda, Tesla, BMW, Mercedes-Benz, Audi, Volkswagen, Ford, Chevrolet, Hyundai, Kia, Nissan, Acura, Infiniti, Lincoln, Cadillac.

26 niche brands: BYD, NIO, Xpeng, Li Auto, Polestar, Rivian, Lucid, Genesis, Mini, Subaru, Mazda, Volvo, Porsche, Lexus, Buick, Land Rover, Jaguar, Ferrari, Lamborghini, McLaren, Aston Martin, Maserati, Bentley, Rolls-Royce, VinFast, Fisker.

## Models

Each mode is a fitted ranker saved as its own file in `models/`, built by
`scripts/model.py` and loaded by the app at startup. Fitting means the parameters are learned
from the catalog rather than hard-coded, so inference reads them from disk.

| File | Class | What was fitted |
|------|-------|-----------------|
| `models/naive_popularity.pkl` | `NaivePopularityModel` | Global popularity ranking table over all 422 cars |
| `models/classical_rule_scorer.pkl` | `ClassicalRuleModel` | Scoring weights plus catalog statistics (price percentiles, rating spread, use-case frequencies) |
| `models/smart_rag_ranker.pkl` | `SmartRagRanker` | TF-IDF retrieval index (422 x 538 term matrix) plus the constraint config: fairness boost and diversity penalties |

The smart ranker's TF-IDF index is the retrieval half of RAG, built with numpy so the deployed
image stays small. `GET /health` reports which models are loaded. Rebuild them any time with:

```bash
python -m scripts.model     # or: python setup.py
```

## Evaluation Results

Across 15 diverse test queries, all three modes are compared:

| Metric | Naive | Classical | Smart | Improvement (N→S) |
|--------|-------|-----------|-------|-------------------|
| Budget compliance | 0.840 | 1.000 | 1.000 | +19.0% |
| Brand diversity | 3.000 | 3.667 | 5.000 | +66.7% |
| Type diversity | 2.000 | 1.733 | 2.067 | +3.4% |
| Niche exposure | 0.000 | 0.867 | 0.853 | from zero to 85% |
| Relevance | 0.380 | 0.880 | 0.893 | +135.0% |

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
│   ├── car_data.py         # Car catalog (422 cars, 42 brands)
│   ├── model.py            # The three rankers: fit, save, load, predict
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
├── models/                 # trained model files, one per mode
│   ├── naive_popularity.pkl
│   ├── classical_rule_scorer.pkl
│   └── smart_rag_ranker.pkl
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
| `/api/plots/<filename>` | GET | Serve evaluation plot images |
| `/health` | GET | Health check |

## Deployment

The app is deployed on Render using Docker. To deploy your own instance:

1. Fork the repository on GitHub
2. Create a new Web Service on Render, connecting the GitHub repo
3. Render will auto-detect the Dockerfile and build the image
4. Set `OPENAI_API_KEY` as an environment variable (optional)
5. The app will be available at `https://<your-service-name>.onrender.com`

## Tech Stack

- Python 3.11
- Flask
- NumPy (TF-IDF retrieval index, evaluation math)
- OpenAI GPT-4o-mini (optional, for enhanced reasons)
- Matplotlib (evaluation plots)
- Vanilla JavaScript, CSS (frontend)

## AI Attribution

This project was developed with assistance from AI tools (TRAE IDE, https://trae.ai). The
per-file attribution notes are at the top of each source file. The problem framing, the
constraint design, the evaluation protocol, and all final decisions are my own.
