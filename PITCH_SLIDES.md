# CarRec AI Pitch Slides

Slide-by-slide content for the 5-minute video pitch. Each slide includes speaker notes.

## Slide 1: Title

**CarRec AI: Recommendations That Actually Matter**

LLM-powered car recommendation with responsible AI constraints

GitHub: https://github.com/hanfuzhao/carrec-ai
Live app: https://carrec-ai.onrender.com

> Speaker notes: This is CarRec AI, a car recommendation system that uses an LLM to balance relevance with responsibility. The live app and source code are linked on this slide.

## Slide 2: The Problem

Car platforms like Dongchedi and Edmunds optimize for clicks, not outcomes.

- Popular cars get more exposure, become more popular, crowd out alternatives
- Niche brands (BYD, NIO, Rivian) get buried even when they fit better
- Users see five Teslas when they ask for a family SUV
- No budget enforcement, no diversity, no fairness

Engagement optimization creates feedback loops that narrow user choice.

> Speaker notes: Engagement-optimized recommenders create feedback loops. Popular cars get more exposure, become more popular, and crowd out alternatives. A first-time buyer asking for a family SUV does not need to see five Teslas. They need options that fit their budget and expose them to brands they might not have considered.

## Slide 3: What I Built

CarRec AI uses GPT-4o-mini with retrieval-augmented generation.

Four real-world constraints enforced:

1. Budget compliance - hard filter, never exceeds user budget
2. Brand diversity - greedy selection penalizing repeated brands
3. Fairness - scoring boost for niche brands
4. Cold start - preference parsing from natural language, zero user history

> Speaker notes: I built a car recommendation system using GPT-4o-mini from OpenAI, adapted to the car domain through prompt engineering and retrieval-augmented generation. The system enforces four real-world constraints: budget compliance as a hard filter, brand diversity through greedy selection, fairness via a scoring boost for niche brands, and cold start handling by parsing preferences from the query itself with zero user history.

## Slide 4: LLM Strategy

Three-layer architecture:

**Layer 1: Structured retrieval.** Parse query to extract budget, use cases, energy, body, seats. Filter catalog of 70 cars across 27 brands. Only relevant candidates reach the LLM.

**Layer 2: Constraint-aware scoring.** Each car scored on use-case match, preference alignment, budget utilization, and fairness boost. Diversity-aware selection ensures top 5 span multiple brands.

**Layer 3: LLM reasoning.** GPT-4o-mini generates personalized 1-2 sentence reasons for each recommendation.

Falls back to template reasons without API key. Correctness never depends on the LLM.

> Speaker notes: The strategy has three layers. First, structured retrieval. The LLM never sees the raw query alone. The system parses it to extract budget, use cases, and preferences, then filters a catalog of 70 cars. Only relevant candidates move forward. Second, constraint-aware scoring. Each car is scored on use-case match, preference alignment, budget utilization, and a fairness boost for niche brands. A diversity-aware selection ensures variety. Third, LLM reasoning. GPT-4o-mini generates a personalized reason for each recommendation. When no API key is available, the system falls back to templates and still produces correct recommendations. The LLM enhances the experience but is not a dependency for correctness.

## Slide 5: Before/After Comparison

15 test queries covering family, luxury, electric, pickup, and budget use cases.

| Metric | Naive (Before) | Smart (After) | Change |
|--------|---------------|---------------|--------|
| Budget compliance | 84% | 100% | +19% |
| Brand diversity | 3.0 | 4.93 | +64% |
| Type diversity | 2.0 | 2.53 | +27% |
| Niche exposure | 0% | 60% | from zero |
| Relevance | 0.38 | 0.79 | +109% |

> Speaker notes: I evaluated both modes across 15 test queries. The naive mode, which sorts by popularity, achieved 84 percent budget compliance, meaning 16 percent of recommendations exceeded the user's budget. Brand diversity was stuck at 3, and niche brand exposure was zero. The smart mode achieved 100 percent budget compliance, increased brand diversity to nearly 5 unique brands per query, and brought niche exposure from zero to 60 percent. Relevance more than doubled from 0.38 to 0.79.

## Slide 6: Example Query

Query: "I need a family SUV under $50k, preferably electric"

**Before (naive):** Tesla Model Y, Tesla Model 3, Toyota RAV4, Ford F-150, Honda CR-V
- 2 over budget, all mainstream, 0 electric SUVs, 0 niche brands

**After (smart):** BYD Atto 3 ($28k), NIO ES6 ($42k), Volvo XC40 Recharge ($42k), VW ID.4 ($39k), Hyundai Ioniq 5 ($42k)
- All within budget, all electric SUVs, 3 niche brands exposed

> Speaker notes: For the query "family SUV under 50k, preferably electric," the naive mode returns the five most popular cars overall. Two exceed the budget, none are electric SUVs, and all are mainstream brands. The smart mode returns five electric SUVs, all within budget, from three niche brands that the user might not have considered otherwise.

## Slide 7: Risks and Ethics

**Catalog bias.** 70 cars is curated, not comprehensive. Niche classification is manual, should be data-driven.

**Fairness is editorial.** The 1.5-point niche boost is a value judgment, not objective optimization. Different stakeholders may disagree.

**No learning loop.** Cold start means no feedback mechanism. Cannot improve from outcomes.

**LLM hallucination risk.** LLM generates reasons but does not make the decision. Structured data validates the recommendation. Production would validate LLM output against car data.

> Speaker notes: Four risks are worth noting. First, catalog bias. My 70-car catalog is curated, and I chose which brands count as niche. A real system would need a larger, continuously updated catalog with data-driven classification. Second, fairness is not neutral. The 1.5-point boost for niche brands is an editorial choice. Third, there is no learning loop. Every session is a cold start with no feedback mechanism. Fourth, LLM hallucination. The LLM generates reasons but does not make the recommendation decision, which is deterministic and auditable. But the reasons could mislead users if the LLM invents attributes. A production system would validate LLM output against structured data.

## Slide 8: Live Demo

Live app: https://carrec-ai.onrender.com

Try queries like:
- "family SUV under $50k, preferably electric"
- "cheap commute car around $25k"
- "luxury sedan for business, budget $60k"

GitHub: https://github.com/hanfuzhao/carrec-ai

> Speaker notes: The live app is deployed on Render and accepts natural language queries. The GitHub repository contains the full codebase with PRs following git best practices.

## Recording Guide

Target duration: 4-5 minutes (5 min hard stop)

1. Use Loom (free, https://www.loom.com) or YouTube for recording
2. Share screen showing these slides and the live app
3. Spend roughly 30 seconds per slide
4. Slide 6 can include a live demo of the app (extra 30 seconds)
5. Upload and share the link

Slide timing:
- Slide 1 (Title): 20s
- Slide 2 (Problem): 40s
- Slide 3 (What I Built): 40s
- Slide 4 (LLM Strategy): 60s
- Slide 5 (Before/After): 40s
- Slide 6 (Example): 40s
- Slide 7 (Risks): 40s
- Slide 8 (Demo): 20s
- Total: about 4 min 30s
