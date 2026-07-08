# CarRec AI: Recommendations That Actually Matter

## The Problem

Car recommendation platforms like Dongchedi (DongCheDi) and Edmunds optimize for engagement. They push popular models because popular models get clicks, and clicks drive ad revenue. But a first-time buyer asking for "a family SUV under $50k" does not need to see five Teslas. They need options that fit their budget, match their use case, and expose them to brands they might not have considered.

The core problem with engagement-optimized recommenders is that they create feedback loops. Popular cars get more exposure, become more popular, and crowd out alternatives. Niche brands, including innovative EV makers like BYD, NIO, and Rivian, get buried even when they might be a better fit for the user.

## What I Built

CarRec AI is a car recommendation system that uses an LLM (GPT-4o-mini) with retrieval-augmented generation to provide recommendations that balance relevance with responsibility.

The system enforces four real-world constraints:

1. **Budget compliance** - a hard filter that never recommends above the user's stated budget
2. **Brand diversity** - a greedy selection algorithm that penalizes repeated brands to ensure variety
3. **Fairness** - a scoring boost for niche brands to ensure equitable exposure
4. **Cold start** - preference parsing from natural language that works with zero user history

## LLM Strategy

I used GPT-4o-mini from OpenAI, applied through prompt engineering and retrieval-augmented generation rather than weight-based fine-tuning. The strategy has three layers:

**Layer 1: Structured retrieval.** The LLM never sees the raw user query alone. Instead, the system first parses the query to extract budget, use cases, energy preferences, body style, and seating needs. It then filters a structured catalog of 70 cars across 27 brands. Only the filtered, relevant candidates are passed to the LLM.

**Layer 2: Constraint-aware scoring.** Before the LLM generates reasons, each car is scored on use-case match, preference alignment, budget utilization, and a fairness boost for niche brands. A diversity-aware selection algorithm ensures the top 5 recommendations span multiple brands and types.

**Layer 3: LLM reasoning.** The LLM receives the user query and the pre-selected candidates, then generates a personalized 1-2 sentence reason for each recommendation explaining why it fits this specific user.

When no API key is available, the system falls back to template-based reasons and still produces correct recommendations with full constraint enforcement. The LLM enhances the user experience but is not a dependency for correctness.

## Before/After Comparison

I evaluated both modes across 15 diverse test queries covering family cars, luxury sedans, electric vehicles, pickups, and budget options.

| Metric | Naive (Before) | Smart (After) | Change |
|--------|---------------|---------------|--------|
| Budget compliance | 84% | 100% | +19% |
| Brand diversity | 3.0 brands | 4.93 brands | +64% |
| Type diversity | 2.0 types | 2.53 types | +27% |
| Niche brand exposure | 0% | 60% | from zero to 60% |
| Use-case relevance | 0.38 | 0.79 | +109% |

**Example query:** "I need a family SUV under $50k, preferably electric"

**Before (naive):** Returns the 5 most popular cars overall (Tesla Model Y, Tesla Model 3, Toyota RAV4, Ford F-150, Honda CR-V). Two of these exceed the $50k budget. All are mainstream brands. No niche brands appear.

**After (smart):** Returns BYD Atto 3 ($28k), NIO ES6 ($42k), Volvo XC40 Recharge ($42k), Volkswagen ID.4 ($39k), Hyundai Ioniq 5 ($42k). All within budget. All electric SUVs. Three niche brands get exposure. Each comes with a personalized reason.

## Reflection: Risks, Ethics, and Evaluation Challenges

**Risk of bias in the catalog.** My catalog of 70 cars is curated, not comprehensive. I chose which brands count as "niche" and which cars to include. A real deployment would need a much larger, continuously updated catalog, and the niche/mainstream classification should be data-driven rather than manually assigned.

**Fairness is not neutral.** The 1.5-point boost I give to niche brands is an explicit editorial choice. It favors newer EV brands over established Japanese sedans. This is defensible, given the goal of expanding user consideration sets, but it is a value judgment, not an objective optimization. Different stakeholders might disagree on the right boost amount.

**Cold start works, but at a cost.** Parsing preferences from a single query means the system has no learning loop. It cannot improve from user feedback. A production system would need to track outcomes, did the user actually buy the recommended car, and feed that back into the scoring model.

**Evaluation is limited.** My relevance metric measures use-case overlap, which is a proxy for actual user satisfaction. The ideal evaluation would be A/B testing with real car buyers, which is beyond the scope of a hackathon. The 15 test queries are also my own design and may not represent the full distribution of user needs.

**LLM dependency.** The LLM generates reasons but does not make the recommendation decision. This is deliberate. I wanted the constraint enforcement to be deterministic and auditable. If the LLM hallucinates a feature, the underlying recommendation is still correct. But the reasons could mislead users if the LLM invents attributes. A production system would validate LLM output against the structured car data before displaying it.

## Limitations

- Catalog is static and manually curated (70 cars). A real system would integrate live inventory and pricing data.
- No user accounts or history. Every session is a cold start.
- LLM enhancement requires an OpenAI API key. Without it, reasons are templated.
- No image support. Recommendations are text-only.
- The niche brand classification is binary. Reality is more nuanced.

## Links

- Live app: https://hanfuzhao781-carrec-ai.hf.space
- GitHub: (to be added after push)
