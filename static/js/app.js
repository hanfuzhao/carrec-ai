/* CarRec AI - Frontend Logic
   Vanilla JS, modularized. Fetch API against Flask backend. */

(function () {
    "use strict";

    /* Config & State */
    const API = {
        recommend: "/api/recommend",
        compare: "/api/compare",
        catalog: "/api/catalog",
        stats: "/api/stats",
        evaluation: "/api/evaluation",
        plots: "/api/plots/",
    };

    const GAUGE_CIRCUMFERENCE = 213.628; // 2 * PI * 34

    const state = {
        mode: "smart",
        lastQuery: "",
        statsLoaded: false,
        evalLoaded: false,
        catalogLoaded: false,
        catalogData: [],
        budget: 50000,
    };

    /* DOM cache */
    const dom = {
        systemStatus: document.getElementById("systemStatus"),
        catalogCount: document.getElementById("catalogCount"),
        brandCount: document.getElementById("brandCount"),
        budgetSlider: document.getElementById("budgetSlider"),
        budgetValue: document.getElementById("budgetValue"),
        useCaseChips: document.getElementById("useCaseChips"),
        energyChips: document.getElementById("energyChips"),
        bodyChips: document.getElementById("bodyChips"),
        seatsChips: document.getElementById("seatsChips"),
        advancedToggle: document.getElementById("advancedToggle"),
        advancedBody: document.getElementById("advancedBody"),
        queryInput: document.getElementById("queryInput"),
        modeToggle: document.querySelector(".mode-toggle"),
        recommendBtn: document.getElementById("recommendBtn"),
        parsedPrefs: document.getElementById("parsedPrefs"),
        prefsGrid: document.getElementById("prefsGrid"),
        resultsPanel: document.getElementById("resultsPanel"),
        resultsSub: document.getElementById("resultsSub"),
        metricsBar: document.getElementById("metricsBar"),
        mBudget: document.getElementById("mBudget"),
        mDiversity: document.getElementById("mDiversity"),
        mNiche: document.getElementById("mNiche"),
        mCandidates: document.getElementById("mCandidates"),
        cardsGrid: document.getElementById("cardsGrid"),
        comparePanel: document.getElementById("comparePanel"),
        runCompareBtn: document.getElementById("runCompareBtn"),
        naiveCards: document.getElementById("naiveCards"),
        smartCards: document.getElementById("smartCards"),
        compareTableWrap: document.getElementById("compareTableWrap"),
        compareTableBody: document.getElementById("compareTableBody"),
        evalToggle: document.getElementById("evalToggle"),
        evalBody: document.getElementById("evalBody"),
        evalSummary: document.getElementById("evalSummary"),
        plotMetric: document.getElementById("plotMetric"),
        plotPerQuery: document.getElementById("plotPerQuery"),
        plotFairness: document.getElementById("plotFairness"),
        catalogToggle: document.getElementById("catalogToggle"),
        catalogBody: document.getElementById("catalogBody"),
        filterBrand: document.getElementById("filterBrand"),
        filterType: document.getElementById("filterType"),
        filterEnergy: document.getElementById("filterEnergy"),
        filterPrice: document.getElementById("filterPrice"),
        priceLabel: document.getElementById("priceLabel"),
        applyFiltersBtn: document.getElementById("applyFiltersBtn"),
        resetFiltersBtn: document.getElementById("resetFiltersBtn"),
        catalogCountDisplay: document.getElementById("catalogCountDisplay"),
        catalogGrid: document.getElementById("catalogGrid"),
        loadingOverlay: document.getElementById("loadingOverlay"),
        loadingText: document.getElementById("loadingText"),
        toast: document.getElementById("toast"),
        footerMode: document.getElementById("footerMode"),
    };

    /* Utility helpers */
    const util = {
        formatPrice(n) {
            if (n >= 1000) return "$" + n.toLocaleString("en-US");
            return "$" + n;
        },
        formatPriceShort(n) {
            if (n >= 1000) return "$" + (n / 1000).toFixed(0) + "k";
            return "$" + n;
        },
        escapeHtml(str) {
            if (str == null) return "";
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#39;");
        },
        energyClass(energy) {
            const e = (energy || "").toLowerCase();
            if (e === "bev") return "is-energy-bev";
            if (e === "hybrid") return "is-energy-hybrid";
            if (e === "phev") return "is-energy-phev";
            if (e === "gasoline") return "is-energy-gasoline";
            return "";
        },
        clampPct(v) {
            v = Number(v) || 0;
            if (v < 0) v = 0;
            if (v > 1) v = 1;
            return v;
        },
    };

    /* Toast + Loading */
    let toastTimer = null;
    function showToast(message, isError) {
        dom.toast.textContent = message;
        dom.toast.classList.toggle("is-error", !!isError);
        dom.toast.hidden = false;
        // force reflow so transition runs
        void dom.toast.offsetWidth;
        dom.toast.classList.add("is-show");
        clearTimeout(toastTimer);
        toastTimer = setTimeout(function () {
            dom.toast.classList.remove("is-show");
            setTimeout(function () { dom.toast.hidden = true; }, 280);
        }, 3200);
    }

    function showLoading(text) {
        dom.loadingText.textContent = text || "PROCESSING";
        dom.loadingOverlay.hidden = false;
    }
    function hideLoading() {
        dom.loadingOverlay.hidden = true;
    }

    /* API layer */
    const REQUEST_TIMEOUT_MS = 20000;

    function fetchWithTimeout(url, options) {
        const controller = new AbortController();
        const timer = setTimeout(function () { controller.abort(); }, REQUEST_TIMEOUT_MS);
        const opts = Object.assign({}, options, { signal: controller.signal });
        return fetch(url, opts).finally(function () { clearTimeout(timer); });
    }

    const api = {
        async getStats() {
            const res = await fetchWithTimeout(API.stats);
            if (!res.ok) throw new Error("stats " + res.status);
            return res.json();
        },
        async recommendQuery(query, mode, topK) {
            const res = await fetchWithTimeout(API.recommend, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, mode: mode, top_k: topK || 5 }),
            });
            const data = await res.json();
            if (!res.ok || data.error) throw new Error(data.error || "recommend failed (" + res.status + ")");
            return data;
        },
        async recommendFilters(filters, mode, topK) {
            const res = await fetchWithTimeout(API.recommend, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ filters: filters, mode: mode, top_k: topK || 5 }),
            });
            const data = await res.json();
            if (!res.ok || data.error) throw new Error(data.error || "recommend failed (" + res.status + ")");
            return data;
        },
        async compare(query, topK) {
            const res = await fetchWithTimeout(API.compare, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, top_k: topK || 5 }),
            });
            const data = await res.json();
            if (!res.ok || data.error) throw new Error(data.error || "compare failed (" + res.status + ")");
            return data;
        },
        async catalog(filters) {
            const params = new URLSearchParams();
            if (filters.brand) params.set("brand", filters.brand);
            if (filters.type) params.set("type", filters.type);
            if (filters.energy) params.set("energy", filters.energy);
            if (filters.max_price) params.set("max_price", filters.max_price);
            const res = await fetchWithTimeout(API.catalog + "?" + params.toString());
            if (!res.ok) throw new Error("catalog " + res.status);
            return res.json();
        },
        async evaluation() {
            const res = await fetchWithTimeout(API.evaluation);
            if (!res.ok) return null;
            return res.json();
        },
        plotUrl(filename) {
            return API.plots + filename;
        },
    };

    /* Bootstrap: load stats + health */
    async function bootstrap() {
        try {
            const stats = await api.getStats();
            state.statsLoaded = true;
            dom.catalogCount.textContent = stats.total_cars;
            dom.brandCount.textContent = stats.total_brands;
            dom.systemStatus.textContent = "ONLINE";
            dom.systemStatus.classList.add("is-online");
            // populate catalog filter options lazily handled on expand
        } catch (err) {
            dom.systemStatus.textContent = "OFFLINE";
            showToast("Backend unreachable. Is Flask running on port 7860?", true);
        }
    }

    /* Mode toggle */
    function initModeToggle() {
        const buttons = dom.modeToggle.querySelectorAll(".mode-btn");
        buttons.forEach(function (btn) {
            btn.addEventListener("click", function () {
                const mode = btn.getAttribute("data-mode");
                if (mode === state.mode) return;
                state.mode = mode;
                buttons.forEach(function (b) {
                    const active = b === btn;
                    b.classList.toggle("active", active);
                    b.setAttribute("aria-checked", active ? "true" : "false");
                });
                dom.footerMode.textContent = mode + " mode";
            });
        });
    }

    /* Filter chips: multi-select toggle, or exclusive for seats */
    function initFilters() {
        dom.budgetSlider.addEventListener("input", function () {
            dom.budgetValue.textContent = util.formatPriceShort(Number(dom.budgetSlider.value));
        });

        function bindChipGroup(container) {
            const exclusive = container.getAttribute("data-exclusive") === "true";
            container.addEventListener("click", function (e) {
                const chip = e.target.closest(".filter-chip");
                if (!chip) return;
                if (exclusive) {
                    container.querySelectorAll(".filter-chip").forEach(function (c) {
                        c.classList.remove("is-active");
                    });
                    chip.classList.add("is-active");
                } else {
                    chip.classList.toggle("is-active");
                }
            });
        }
        bindChipGroup(dom.useCaseChips);
        bindChipGroup(dom.energyChips);
        bindChipGroup(dom.bodyChips);
        bindChipGroup(dom.seatsChips);

        dom.seatsChips.querySelector('[data-value=""]').classList.add("is-active");

        dom.advancedToggle.addEventListener("click", function () {
            const expanded = dom.advancedToggle.getAttribute("aria-expanded") === "true";
            dom.advancedToggle.setAttribute("aria-expanded", !expanded);
            dom.advancedBody.hidden = expanded;
        });

        dom.queryInput.addEventListener("keydown", function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                handleRecommend();
            }
        });
        dom.recommendBtn.addEventListener("click", handleRecommend);
    }

    function collectFilters() {
        const budget = Number(dom.budgetSlider.value);
        const useCases = getActiveValues(dom.useCaseChips);
        const energyPrefs = getActiveValues(dom.energyChips);
        const bodyPrefs = getActiveValues(dom.bodyChips);
        const seatsVal = getActiveValues(dom.seatsChips)[0];
        return {
            budget: budget,
            use_cases: useCases,
            energy_prefs: energyPrefs,
            body_prefs: bodyPrefs,
            seats_needed: seatsVal ? Number(seatsVal) : null,
        };
    }

    function getActiveValues(container) {
        return Array.from(container.querySelectorAll(".filter-chip.is-active"))
            .map(function (c) { return c.getAttribute("data-value"); })
            .filter(function (v) { return v !== ""; });
    }

    async function handleRecommend() {
        const query = dom.queryInput.value.trim();
        showLoading("SCANNING CATALOG");
        dom.recommendBtn.disabled = true;
        try {
            let result;
            if (query) {
                result = await api.recommendQuery(query, state.mode, 5);
                state.lastQuery = query;
            } else {
                const filters = collectFilters();
                result = await api.recommendFilters(filters, state.mode, 5);
                state.lastQuery = result.query || "filter-based";
            }
            renderResults(result);
            dom.comparePanel.hidden = false;
        } catch (err) {
            const msg = err.name === "AbortError"
                ? "Request timed out. The server may be waking up, please try again."
                : err.message;
            showToast(msg, true);
        } finally {
            hideLoading();
            dom.recommendBtn.disabled = false;
        }
    }

    /* Render: parsed preferences */
    function renderParsedPrefs(prefs) {
        if (!prefs) {
            dom.parsedPrefs.hidden = true;
            return;
        }
        dom.parsedPrefs.hidden = false;
        const items = [
            { key: "Budget", val: util.formatPrice(prefs.budget) },
            { key: "Use Cases", val: (prefs.use_cases && prefs.use_cases.length) ? prefs.use_cases.join(", ") : "any" },
            { key: "Energy", val: (prefs.energy_prefs && prefs.energy_prefs.length) ? prefs.energy_prefs.join(", ") : "any" },
            { key: "Body", val: (prefs.body_prefs && prefs.body_prefs.length) ? prefs.body_prefs.join(", ") : "any" },
            { key: "Seats", val: prefs.seats_needed ? ">= " + prefs.seats_needed : "any" },
        ];
        state.budget = prefs.budget || 50000;
        dom.prefsGrid.innerHTML = items.map(function (it) {
            return '<div class="pref-item"><span class="pref-key">' + it.key + '</span>' +
                '<span class="pref-val">' + util.escapeHtml(it.val) + '</span></div>';
        }).join("");
    }

    /* Render: metrics gauges */
    function setGauge(container, value, isPct) {
        const fg = container.querySelector(".gauge-fg");
        const num = container.querySelector(".gauge-num");
        let pct, display;
        if (isPct) {
            pct = util.clampPct(value);
            display = Math.round(pct * 100) + "%";
        } else {
            // count out of 5
            pct = util.clampPct(value / 5);
            display = String(value);
        }
        const offset = GAUGE_CIRCUMFERENCE * (1 - pct);
        if (fg) fg.style.strokeDashoffset = offset;
        if (num) num.textContent = display;
    }

    function renderMetrics(metrics) {
        if (!metrics) return;
        const budgetGauge = dom.metricsBar.querySelector('[data-metric="budget_compliance"]');
        const divGauge = dom.metricsBar.querySelector('[data-metric="brand_diversity"]');
        const nicheGauge = dom.metricsBar.querySelector('[data-metric="niche_exposure"]');
        setGauge(budgetGauge, metrics.budget_compliance, true);
        setGauge(divGauge, metrics.brand_diversity, false);
        setGauge(nicheGauge, metrics.niche_exposure, true);
        dom.mCandidates.textContent = String(metrics.total_candidates || 0);
    }

    /* Render: recommendation cards */
    function buildCarCard(rec, index) {
        const rank = index + 1;
        const nicheBadge = rec.is_niche_brand ? '<span class="niche-badge">NICHE</span>' : "";
        const highlights = (rec.highlights || []).slice(0, 4).map(function (h) {
            return '<span class="highlight-tag">' + util.escapeHtml(h.replace(/_/g, " ")) + '</span>';
        }).join("");
        const reason = rec.reason ? util.escapeHtml(rec.reason) : "Good overall match.";
        // score bar: normalize score to a 0-100 width (smart scores ~ 0-30, naive ~ 0-1)
        let scorePct;
        if (state.mode === "smart") {
            scorePct = Math.min(100, Math.max(8, (rec.score / 30) * 100));
        } else {
            scorePct = Math.min(100, Math.max(8, rec.score * 100));
        }
        return '' +
            '<article class="car-card" style="animation-delay:' + (index * 60) + 'ms">' +
                '<span class="card-rank">' + String(rank).padStart(2, "0") + '</span>' +
                '<div class="card-head">' +
                    '<div class="card-brand-row">' +
                        '<span class="card-brand">' + util.escapeHtml(rec.brand) + '</span>' +
                        nicheBadge +
                    '</div>' +
                    '<h3 class="card-model">' + util.escapeHtml(rec.model) + '</h3>' +
                '</div>' +
                '<div class="card-specs">' +
                    '<div class="spec"><span class="spec-label">Type</span><span class="spec-value">' + util.escapeHtml(rec.type) + '</span></div>' +
                    '<div class="spec"><span class="spec-label">Energy</span><span class="spec-value ' + util.energyClass(rec.energy) + '">' + util.escapeHtml(rec.energy) + '</span></div>' +
                    '<div class="spec"><span class="spec-label">Seats</span><span class="spec-value">' + rec.seats + '</span></div>' +
                    '<div class="spec"><span class="spec-label">Price</span><span class="spec-value is-price">' + util.formatPrice(rec.price_usd) + '</span></div>' +
                    '<div class="spec"><span class="spec-label">Rating</span><span class="spec-value">' + Number(rec.rating).toFixed(1) + '</span></div>' +
                    '<div class="spec"><span class="spec-label">Match</span><span class="spec-value">' + Number(rec.score).toFixed(1) + '</span></div>' +
                '</div>' +
                '<div class="card-score-row">' +
                    '<div class="score-block">' +
                        '<span class="score-label">Score</span>' +
                        '<span class="score-value">' + Number(rec.score).toFixed(2) + '</span>' +
                    '</div>' +
                    '<div class="score-bar"><div class="score-bar-fill" style="width:' + scorePct.toFixed(1) + '%"></div></div>' +
                '</div>' +
                (highlights ? '<div class="card-highlights">' + highlights + '</div>' : '') +
                '<p class="card-reason">' + reason + '</p>' +
            '</article>';
    }

    function renderResults(result) {
        renderParsedPrefs(result.parsed_prefs);
        renderMetrics(result.metrics);
        const recs = result.recommendations || [];
        dom.cardsGrid.innerHTML = recs.length
            ? recs.map(buildCarCard).join("")
            : '<p style="padding:22px;color:var(--text-muted);grid-column:1/-1">No recommendations returned.</p>';
        dom.resultsSub.textContent = result.mode.toUpperCase() + " mode / " + recs.length + " results / query: \"" + result.query + "\"";
        dom.resultsPanel.hidden = false;
        // smooth scroll results into view
        dom.resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    /* Compare (before/after) */
    function initCompare() {
        dom.runCompareBtn.addEventListener("click", handleCompare);
    }

    async function handleCompare() {
        const query = dom.queryInput.value.trim();
        const compareQuery = query || buildCompareQueryFromFilters();
        if (!compareQuery) {
            showToast("Set some filters or enter a query to compare.", true);
            return;
        }
        state.lastQuery = compareQuery;
        showLoading("RUNNING A/B TEST");
        dom.runCompareBtn.disabled = true;
        try {
            const result = await api.compare(compareQuery, 5);
            renderCompare(result);
        } catch (err) {
            const msg = err.name === "AbortError"
                ? "Request timed out. The server may be waking up, please try again."
                : err.message;
            showToast(msg, true);
        } finally {
            hideLoading();
            dom.runCompareBtn.disabled = false;
        }
    }

    function buildCompareQueryFromFilters() {
        const filters = collectFilters();
        if (!filters.use_cases.length && !filters.energy_prefs.length &&
            !filters.body_prefs.length && !filters.seats_needed &&
            filters.budget === 50000) {
            return "";
        }
        const parts = [];
        parts.push("budget $" + filters.budget);
        if (filters.use_cases.length) parts.push(filters.use_cases.join(" "));
        if (filters.body_prefs.length) parts.push(filters.body_prefs.join(" ").toLowerCase());
        if (filters.energy_prefs.length) {
            const e = filters.energy_prefs.join(" ").toLowerCase();
            parts.push(e === "bev" ? "electric" : e);
        }
        if (filters.seats_needed) parts.push(filters.seats_needed + " seater");
        return parts.join(", ");
    }

    function buildCompareCard(rec, index, side, budget) {
        const rank = index + 1;
        const overBudget = budget && rec.price_usd > budget;
        return '' +
            '<div class="compare-card is-' + side + '">' +
                '<span class="cc-rank">' + rank + '</span>' +
                '<div class="cc-name">' +
                    '<div class="cc-brand">' + util.escapeHtml(rec.brand) + (rec.is_niche_brand ? " / NICHE" : "") + '</div>' +
                    '<div class="cc-model">' + util.escapeHtml(rec.model) + '</div>' +
                '</div>' +
                '<span class="cc-price' + (overBudget ? " is-over" : "") + '">' + util.formatPriceShort(rec.price_usd) + '</span>' +
            '</div>';
    }

    function renderCompare(result) {
        const naive = result.naive;
        const smart = result.smart;
        const budget = (smart.parsed_prefs && smart.parsed_prefs.budget) || state.budget || 50000;

        const naiveRecs = naive.recommendations || [];
        const smartRecs = smart.recommendations || [];

        dom.naiveCards.innerHTML = naiveRecs.length
            ? naiveRecs.map(function (r, i) { return buildCompareCard(r, i, "naive", budget); }).join("")
            : '<p style="color:var(--text-muted);font-size:0.8rem">No results.</p>';
        dom.smartCards.innerHTML = smartRecs.length
            ? smartRecs.map(function (r, i) { return buildCompareCard(r, i, "smart", budget); }).join("")
            : '<p style="color:var(--text-muted);font-size:0.8rem">No results.</p>';

        // comparison table
        const comp = result.comparison || {};
        const rows = [
            { name: "Budget Compliance", naive: comp.budget_compliance, smart: comp.budget_compliance, fmt: fmtPct },
            { name: "Brand Diversity", naive: comp.brand_diversity, smart: comp.brand_diversity, fmt: fmtNum },
            { name: "Type Diversity", naive: comp.type_diversity, smart: comp.type_diversity, fmt: fmtNum },
            { name: "Niche Exposure", naive: comp.niche_exposure, smart: comp.niche_exposure, fmt: fmtPct },
        ];
        dom.compareTableBody.innerHTML = rows.map(function (row) {
            const nVal = row.fmt(row.naive);
            const sVal = row.fmt(row.smart);
            const delta = computeDelta(row.naive, row.smart, row.name);
            return '' +
                '<tr>' +
                    '<td class="metric-name">' + util.escapeHtml(row.name) + '</td>' +
                    '<td class="col-naive">' + nVal + '</td>' +
                    '<td class="col-smart">' + sVal + '</td>' +
                    '<td class="' + delta.cls + '">' + delta.text + '</td>' +
                '</tr>';
        }).join("");
        dom.compareTableWrap.hidden = false;
        dom.comparePanel.hidden = false;
    }

    function fmtPct(v) { return Math.round((Number(v) || 0) * 100) + "%"; }
    function fmtNum(v) { return String(v); }
    function computeDelta(naive, smart, name) {
        const n = Number(naive) || 0;
        const s = Number(smart) || 0;
        if (name === "Niche Exposure" && n === 0 && s > 0) {
            return { cls: "delta-pos", text: "+" + fmtPct(s) + " (new)" };
        }
        const diff = s - n;
        if (diff > 0.0001) {
            const txt = (name === "Budget Compliance" || name === "Niche Exposure")
                ? "+" + Math.round(diff * 100) + "%"
                : "+" + diff;
            return { cls: "delta-pos", text: txt };
        }
        if (diff < -0.0001) {
            const txt = (name === "Budget Compliance" || name === "Niche Exposure")
                ? Math.round(diff * 100) + "%"
                : String(diff);
            return { cls: "delta-neu", text: txt };
        }
        return { cls: "delta-neu", text: "0" };
    }

    /* Evaluation dashboard */
    function initEval() {
        dom.evalToggle.addEventListener("click", function () {
            const expanded = dom.evalToggle.getAttribute("aria-expanded") === "true";
            togglePanel(dom.evalToggle, dom.evalBody, !expanded);
            if (!expanded && !state.evalLoaded) {
                loadEvaluation();
            }
        });
    }

    async function loadEvaluation() {
        showLoading("LOADING METRICS");
        try {
            const data = await api.evaluation();
            if (!data) {
                dom.evalSummary.innerHTML = '<p style="color:var(--text-muted)">Evaluation data not found. Run scripts/evaluator.py first.</p>';
            } else {
                renderEvaluation(data);
                state.evalLoaded = true;
            }
            // plots
            dom.plotMetric.src = api.plotUrl("metric_comparison.png");
            dom.plotPerQuery.src = api.plotUrl("per_query_breakdown.png");
            dom.plotFairness.src = api.plotUrl("fairness_distribution.png");
        } catch (err) {
            const msg = err.name === "AbortError"
                ? "Request timed out. The server may be waking up, please try again."
                : err.message;
            showToast(msg, true);
        } finally {
            hideLoading();
        }
    }

    function renderEvaluation(data) {
        const summary = data.summary || {};
        const improvements = data.improvements_pct || {};
        const catStats = data.catalog_stats || {};
        const smartSum = summary.smart || {};
        const naiveSum = summary.naive || {};

        const stats = [
            { label: "Queries Benchmarked", value: data.num_queries || 0, sub: "top_k = " + (data.top_k || 5) },
            { label: "Catalog Size", value: catStats.total_cars || 0, sub: catStats.total_brands + " brands" },
            { label: "Relevance (smart)", value: pct(smartSum.relevance && smartSum.relevance.mean), sub: deltaImp(improvements.relevance) },
            { label: "Budget Compliance (smart)", value: pct(smartSum.budget_compliance && smartSum.budget_compliance.mean), sub: deltaImp(improvements.budget_compliance) },
            { label: "Brand Diversity (smart)", value: num(smartSum.brand_diversity && smartSum.brand_diversity.mean), sub: deltaImp(improvements.brand_diversity) },
            { label: "Niche Exposure (smart)", value: pct(smartSum.niche_exposure && smartSum.niche_exposure.mean), sub: nicheImp(improvements.niche_exposure) },
        ];

        dom.evalSummary.innerHTML = stats.map(function (s) {
            return '' +
                '<div class="eval-stat">' +
                    '<span class="eval-stat-label">' + util.escapeHtml(s.label) + '</span>' +
                    '<span class="eval-stat-value">' + s.value + '</span>' +
                    (s.sub ? '<div class="eval-stat-sub">' + s.sub + '</div>' : '') +
                '</div>';
        }).join("");
    }

    function pct(v) { return Math.round((Number(v) || 0) * 100) + "%"; }
    function num(v) { return (Number(v) || 0).toFixed(1); }
    function deltaImp(v) {
        if (v == null || !isFinite(v)) return "";
        return '<span class="up">+' + Number(v).toFixed(1) + '% vs naive</span>';
    }
    function nicheImp(v) {
        if (v == null) return "";
        if (!isFinite(v)) return '<span class="new">new (naive = 0)</span>';
        return '<span class="up">+' + Number(v).toFixed(1) + '% vs naive</span>';
    }

    /* Catalog browser */
    function initCatalog() {
        dom.catalogToggle.addEventListener("click", function () {
            const expanded = dom.catalogToggle.getAttribute("aria-expanded") === "true";
            togglePanel(dom.catalogToggle, dom.catalogBody, !expanded);
            if (!expanded && !state.catalogLoaded) {
                loadCatalogOptions().then(loadCatalog);
            }
        });
        dom.filterPrice.addEventListener("input", function () {
            dom.priceLabel.textContent = util.formatPriceShort(Number(dom.filterPrice.value));
        });
        dom.applyFiltersBtn.addEventListener("click", loadCatalog);
        dom.resetFiltersBtn.addEventListener("click", function () {
            dom.filterBrand.value = "";
            dom.filterType.value = "";
            dom.filterEnergy.value = "";
            dom.filterPrice.value = "120000";
            dom.priceLabel.textContent = "$120k";
            loadCatalog();
        });
    }

    async function loadCatalogOptions() {
        if (!state.statsLoaded) {
            try { await bootstrap(); } catch (e) { /* ignore */ }
        }
        try {
            const data = await api.catalog({});
            state.catalogData = data.cars || [];
            populateFilterOptions(state.catalogData);
            state.catalogLoaded = true;
        } catch (err) {
            showToast(err.message, true);
        }
    }

    function populateFilterOptions(cars) {
        const brands = unique(cars.map(function (c) { return c.brand; })).sort();
        const types = unique(cars.map(function (c) { return c.type; })).sort();
        const energies = unique(cars.map(function (c) { return c.energy; })).sort();
        fillSelect(dom.filterBrand, brands);
        fillSelect(dom.filterType, types);
        fillSelect(dom.filterEnergy, energies);
    }

    function fillSelect(select, values) {
        const current = select.value;
        select.innerHTML = '<option value="">All</option>' + values.map(function (v) {
            return '<option value="' + util.escapeHtml(v) + '">' + util.escapeHtml(v) + '</option>';
        }).join("");
        select.value = current;
    }

    function unique(arr) {
        const seen = {};
        const out = [];
        arr.forEach(function (v) {
            if (!seen[v]) { seen[v] = true; out.push(v); }
        });
        return out;
    }

    async function loadCatalog() {
        const filters = {
            brand: dom.filterBrand.value,
            type: dom.filterType.value,
            energy: dom.filterEnergy.value,
            max_price: Number(dom.filterPrice.value),
        };
        showLoading("QUERYING INVENTORY");
        try {
            const data = await api.catalog(filters);
            renderCatalog(data.cars || [], data.count);
        } catch (err) {
            const msg = err.name === "AbortError"
                ? "Request timed out. The server may be waking up, please try again."
                : err.message;
            showToast(msg, true);
        } finally {
            hideLoading();
        }
    }

    function renderCatalog(cars, count) {
        dom.catalogCountDisplay.innerHTML = 'Showing <strong>' + count + '</strong> vehicle' + (count === 1 ? "" : "s");
        dom.catalogGrid.innerHTML = cars.length
            ? cars.map(buildCatalogItem).join("")
            : '<p style="color:var(--text-muted);grid-column:1/-1;padding:18px">No vehicles match these filters.</p>';
    }

    function buildCatalogItem(car) {
        const niche = car.is_niche_brand ? " is-niche" : "";
        // determine niche from brand against known set if flag missing
        const nicheBrands = ["BYD", "NIO", "Xpeng", "Li Auto", "Polestar", "Rivian", "Lucid", "Genesis", "Mini", "Subaru", "Mazda", "Volvo", "Porsche", "Lexus", "Buick"];
        const isNiche = car.is_niche_brand != null ? car.is_niche_brand : nicheBrands.indexOf(car.brand) !== -1;
        const cls = isNiche ? " is-niche" : "";
        const highlights = (car.highlights || []).slice(0, 2).map(function (h) {
            return util.escapeHtml(h.replace(/_/g, " "));
        }).join(" / ");
        return '' +
            '<div class="catalog-item' + cls + '">' +
                '<span class="cat-brand">' + util.escapeHtml(car.brand) + '</span>' +
                '<div class="cat-model">' + util.escapeHtml(car.model) + '</div>' +
                '<div class="cat-meta">' +
                    '<span class="cat-type">' + util.escapeHtml(car.type) + ' / ' + util.escapeHtml(car.energy) + '</span>' +
                    '<span class="cat-price">' + util.formatPriceShort(car.price_usd) + '</span>' +
                '</div>' +
                '<div class="cat-foot">' +
                    '<span>' + car.seats + ' seats / ' + Number(car.rating).toFixed(1) + '*</span>' +
                    '<span>' + highlights + '</span>' +
                '</div>' +
            '</div>';
    }

    /* Collapsible panel helper */
    function togglePanel(trigger, body, open) {
        trigger.setAttribute("aria-expanded", open ? "true" : "false");
        body.hidden = !open;
    }

    /* Init */
    function init() {
        initModeToggle();
        initFilters();
        initCompare();
        initEval();
        initCatalog();
        bootstrap();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
