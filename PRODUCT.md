# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

A college student presenting StockSage at hackathons and college evaluations; the people who see it are judges, classmates and evaluators watching a live demo, usually on a projector or laptop, sometimes on a phone. Not a commercial product (confirmed: "for my college purposes, nothing serious").

## Product Purpose

StockSage scores Indian (NSE) stocks by combining company fundamentals (from Yahoo Finance via yfinance) with the sentiment of recent news headlines (VADER over Google/Yahoo RSS). It returns a 0–100 score and a BUY / HOLD / SELL label per stock. Success in a demo: within one run, a viewer understands which stock ranked best, why, and how the two signals combined.

## Positioning

A small multi-agent pipeline (screening → fundamentals + sentiment in parallel → aggregator) whose weighting between hard numbers and news mood is a live, user-controlled slider. The blend is the idea.

## Operating Context

Streamlit app run locally (`streamlit run app.py`). One run analyses up to 5 tickers concurrently and takes a few seconds. Data depends on live Yahoo Finance and RSS availability; any metric can be missing.

## Capabilities and Constraints

- Modes: sector basket (IT, Banking, Auto, Pharma, Green Energy, Diversified; 5 tickers each) or custom comma-separated tickers.
- Controls: max stocks (1–5), fundamental weight 0–100% (sentiment = remainder).
- Per stock: overall / fundamental / sentiment scores, recommendation, generated reasoning text, price, P/E, P/B, ROE, debt-to-equity, market cap, margins, news articles with per-article sentiment.
- Thresholds: score ≥ 70 BUY, 40–69 HOLD, < 40 SELL.
- Stack: Python + Streamlit (inferred; user delegated all decisions).

## Brand Commitments

Name "StockSage". User asked for a light/white UI and explicitly rejected the indigo-500 / purple-gradient "AI vibe-coded" look.

## Evidence on Hand

Only live data from the APIs. No users, testimonials, track record or backtests exist; never imply predictive accuracy.

## Product Principles

1. Show the ranking first; detail on demand.
2. Make the fundamental/sentiment blend visible, since it is the product's idea.
3. Missing data reads as "—", never as a broken layout.
4. It is a scoring demo, not financial advice; say so plainly once.
