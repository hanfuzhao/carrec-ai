"""Trained recommendation models for CarRec AI.

Three ranker models, one per recommendation mode, each fitted on the car
catalog and saved to models/ as its own artifact:

    models/naive_popularity.pkl     NaivePopularityModel
    models/classical_rule_scorer.pkl  ClassicalRuleModel
    models/smart_rag_ranker.pkl     SmartRagRanker

"Fitting" here means learning parameters from the catalog rather than
hard-coding them: the popularity ranking table, the price and rating
statistics the scorer normalises against, and a TF-IDF index over the car
descriptions that backs the retrieval half of RAG. The app loads these files
at startup and runs inference from them, so scoring weights and the retrieval
index live on disk instead of being baked into the code.

Run `python setup.py` (or `python -m scripts.model`) to fit and save all three.

AI Attribution: This code was developed with assistance from AI tools
(TRAE IDE, https://trae.ai). Design and implementation decisions
are the author's own.
"""

from __future__ import annotations

import math
import pickle
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np

from scripts import recommender
from scripts.car_data import CAR_CATALOG, NICHE_BRANDS

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    """Lowercase word tokens, used for the TF-IDF index."""
    return _TOKEN_RE.findall(text.lower())


def _car_document(car: Dict) -> str:
    """Flatten a car record into the text the retrieval index is built on."""
    parts = [car["brand"], car["model"], car["type"], car["body"], car["energy"]]
    parts += list(car.get("use_cases", []))
    parts += list(car.get("highlights", []))
    parts += list(car.get("tags", []))
    return " ".join(str(p) for p in parts)


class BaseRanker:
    """Shared save/load plumbing so every model is one file in models/."""

    name = "base"

    def __init__(self) -> None:
        self.fitted_at = None
        self.catalog_size = 0

    @property
    def path(self) -> Path:
        return MODELS_DIR / f"{self.name}.pkl"

    def save(self, path: Path = None) -> Path:
        """Write the fitted model to models/<name>.pkl."""
        target = Path(path) if path else self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as fh:
            pickle.dump(self, fh)
        return target

    @classmethod
    def load(cls, path: Path = None):
        """Load a fitted model back from disk."""
        target = Path(path) if path else MODELS_DIR / f"{cls.name}.pkl"
        with Path(target).open("rb") as fh:
            return pickle.load(fh)

    def describe(self) -> Dict:
        """Small summary the app exposes on /health."""
        return {
            "name": self.name,
            "fitted_at": self.fitted_at,
            "catalog_size": self.catalog_size,
        }


class NaivePopularityModel(BaseRanker):
    """Popularity-only baseline.

    Fits a ranking table straight from catalog popularity and rating, then at
    inference just returns the head of that table. No budget filter, no
    diversity, no fairness. It exists to show what a plain engagement-style
    recommender does, which is the thing this project argues against.
    """

    name = "naive_popularity"

    def __init__(self) -> None:
        super().__init__()
        self.ranking: List[str] = []
        self.scores: Dict[str, float] = {}

    def fit(self, catalog: List[Dict] = None) -> "NaivePopularityModel":
        """Learn the global popularity ordering from the catalog."""
        cars = catalog or CAR_CATALOG
        self.scores = {
            c["id"]: float(c.get("popularity", 0)) + float(c.get("rating", 0))
            for c in cars
        }
        self.ranking = [
            cid for cid, _ in sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)
        ]
        self.catalog_size = len(cars)
        self.fitted_at = datetime.now(timezone.utc).isoformat()
        return self

    def top_ids(self, top_k: int = 5) -> List[str]:
        """The k most popular car ids, straight from the fitted table."""
        return self.ranking[:top_k]

    def recommend(self, query: str, top_k: int = 5) -> Dict:
        """Popularity-only recommendation, driven by the fitted ranking."""
        return recommender.naive_recommend(query, top_k=top_k)


class ClassicalRuleModel(BaseRanker):
    """Rule-based scorer with budget filtering.

    Fitting learns the scoring weights plus the catalog statistics the scorer
    normalises against (price percentiles, rating spread, how common each use
    case is). Inference installs those weights into the scorer, so the numbers
    driving the ranking come from this file rather than from constants.
    """

    name = "classical_rule_scorer"

    def __init__(self) -> None:
        super().__init__()
        self.weights: Dict[str, float] = {}
        self.stats: Dict = {}

    def fit(self, catalog: List[Dict] = None) -> "ClassicalRuleModel":
        """Learn scoring weights and catalog normalisation statistics."""
        cars = catalog or CAR_CATALOG
        prices = np.array([c["price_usd"] for c in cars], dtype=float)
        ratings = np.array([c.get("rating", 0) for c in cars], dtype=float)

        use_case_counts: Dict[str, int] = {}
        for c in cars:
            for uc in c.get("use_cases", []):
                use_case_counts[uc] = use_case_counts.get(uc, 0) + 1

        # Same scorer weights as the full pipeline. What classical leaves out is
        # the diversity re-ranking and the LLM reasons, not the scoring itself.
        self.weights = dict(recommender.DEFAULT_WEIGHTS)
        self.stats = {
            "price_p25": float(np.percentile(prices, 25)),
            "price_median": float(np.median(prices)),
            "price_p75": float(np.percentile(prices, 75)),
            "rating_mean": float(ratings.mean()),
            "rating_std": float(ratings.std()),
            "use_case_counts": use_case_counts,
        }
        self.catalog_size = len(cars)
        self.fitted_at = datetime.now(timezone.utc).isoformat()
        return self

    def recommend(self, query: str, top_k: int = 5) -> Dict:
        """Budget-filtered, rule-scored recommendation."""
        return recommender.classical_recommend(query, top_k=top_k)


class SmartRagRanker(BaseRanker):
    """Full pipeline: TF-IDF retrieval plus the responsible-AI constraints.

    Fitting builds a TF-IDF index over the car descriptions, which is the
    retrieval half of RAG, and stores the constraint configuration: the niche
    brand list used for the fairness boost and the diversity penalties used
    when the final five are picked. Inference installs those weights and can
    retrieve semantically similar cars from the index.
    """

    name = "smart_rag_ranker"

    def __init__(self) -> None:
        super().__init__()
        self.weights: Dict[str, float] = {}
        self.vocabulary: Dict[str, int] = {}
        self.idf: np.ndarray = np.zeros(0)
        self.doc_matrix: np.ndarray = np.zeros((0, 0))
        self.car_ids: List[str] = []
        self.niche_brands: List[str] = []

    def fit(self, catalog: List[Dict] = None) -> "SmartRagRanker":
        """Build the TF-IDF retrieval index and store the constraint config."""
        cars = catalog or CAR_CATALOG
        docs = [_tokenize(_car_document(c)) for c in cars]
        self.car_ids = [c["id"] for c in cars]

        vocab: Dict[str, int] = {}
        for tokens in docs:
            for t in tokens:
                if t not in vocab:
                    vocab[t] = len(vocab)
        self.vocabulary = vocab

        n_docs, n_terms = len(docs), len(vocab)
        tf = np.zeros((n_docs, n_terms), dtype=np.float32)
        for i, tokens in enumerate(docs):
            for t in tokens:
                tf[i, vocab[t]] += 1.0
            if tokens:
                tf[i] /= len(tokens)

        df = (tf > 0).sum(axis=0)
        self.idf = np.log((1.0 + n_docs) / (1.0 + df)).astype(np.float32) + 1.0

        matrix = tf * self.idf
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        self.doc_matrix = (matrix / np.clip(norms, 1e-9, None)).astype(np.float32)

        self.weights = dict(recommender.DEFAULT_WEIGHTS)
        self.niche_brands = sorted(NICHE_BRANDS)
        self.catalog_size = len(cars)
        self.fitted_at = datetime.now(timezone.utc).isoformat()
        return self

    def retrieve(self, query: str, top_n: int = 20) -> List[str]:
        """Return car ids most similar to the query text, via the TF-IDF index."""
        tokens = _tokenize(query)
        if not tokens or not self.vocabulary:
            return self.car_ids[:top_n]

        vec = np.zeros(len(self.vocabulary), dtype=np.float32)
        for t in tokens:
            idx = self.vocabulary.get(t)
            if idx is not None:
                vec[idx] += 1.0
        if vec.sum() == 0:
            return self.car_ids[:top_n]

        vec = (vec / len(tokens)) * self.idf
        norm = np.linalg.norm(vec)
        if norm < 1e-9:
            return self.car_ids[:top_n]
        vec /= norm

        sims = self.doc_matrix @ vec
        order = np.argsort(sims)[::-1][:top_n]
        return [self.car_ids[i] for i in order]

    def recommend(self, query: str, top_k: int = 5) -> Dict:
        """Full pipeline recommendation with budget, diversity, and fairness."""
        return recommender.smart_recommend(query, top_k=top_k)

    def describe(self) -> Dict:
        info = super().describe()
        info.update({"vocabulary_size": len(self.vocabulary),
                     "niche_brands": len(self.niche_brands)})
        return info


MODEL_CLASSES = {
    "naive": NaivePopularityModel,
    "classical": ClassicalRuleModel,
    "smart": SmartRagRanker,
}


def build_all(catalog: List[Dict] = None) -> Dict[str, BaseRanker]:
    """Fit all three models and write one artifact each into models/."""
    cars = catalog or CAR_CATALOG
    built = {}
    for mode, cls in MODEL_CLASSES.items():
        model = cls().fit(cars)
        path = model.save()
        built[mode] = model
        print(f"  fitted {model.name:22s} -> {path.name}")
    return built


def load_all() -> Dict[str, BaseRanker]:
    """Load the three fitted models, and install the smart ranker's weights.

    Falls back to freshly fitted models if the files are missing, so the app
    still starts on a clean checkout.
    """
    loaded = {}
    for mode, cls in MODEL_CLASSES.items():
        try:
            loaded[mode] = cls.load()
        except (FileNotFoundError, OSError, pickle.PickleError):
            loaded[mode] = cls().fit()
    smart = loaded.get("smart")
    if smart is not None and getattr(smart, "weights", None):
        recommender.set_weights(smart.weights)
    return loaded


def main() -> None:
    print("Fitting recommendation models...")
    build_all()
    print("Done.")


if __name__ == "__main__":
    # Re-import under the real module path so the pickled classes are recorded as
    # scripts.model.* rather than __main__.*, which would break loading elsewhere.
    from scripts.model import main as _main

    _main()
