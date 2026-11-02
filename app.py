import html
import re
import threading
import time
import concurrent.futures

import streamlit as st
import plotly.graph_objects as go

# Import backend agents
from agents.screening_agent import ScreeningAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.aggregator_agent import AggregatorAgent

st.set_page_config(
    page_title="StockSage",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Design tokens + styles
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&display=swap');

:root {
    --paper: #ffffff;
    --wash: #f6f6f2;
    --ink: #14181b;
    --ink-2: #3d434a;
    --ink-3: #565c64;
    --rule: #e3e3dc;
    --rule-strong: #c9c9c0;
    --petrol: #0a5c73;
    --petrol-wash: #e6f0f3;
    --buy: #14683f;
    --buy-wash: #e3f4ea;
    --hold: #7d5200;
    --hold-wash: #fff1cf;
    --sell: #a3261d;
    --sell-wash: #fbe6e4;
    --radius: 8px;
    --font: 'Public Sans', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}

/* ---- Base ---------------------------------------------------------------- */
html { font-size: 17px; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
    line-height: 1.55;
    background: var(--paper) !important;
    color: var(--ink) !important;
    font-family: var(--font) !important;
    font-feature-settings: "tnum" 1;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stDecoration"], .stAppDeployButton, [data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stMainBlockContainer"], .block-container {
    max-width: 1320px !important;
    padding: 0 clamp(16px, 3vw, 40px) 64px !important;
}
h1, h2, h3, h4, p, label, span, div, li, td, th { font-family: var(--font); }
::selection { background: var(--petrol); color: #fff; }
a { text-underline-offset: 3px; }
:focus-visible { outline: 2px solid var(--petrol) !important; outline-offset: 2px !important; }
* { scrollbar-width: thin; scrollbar-color: var(--rule-strong) transparent; }

/* ---- Top bar ------------------------------------------------------------- */
.topbar {
    display: flex; align-items: center; justify-content: space-between; gap: 16px;
    padding: 20px 0 18px; margin-bottom: 28px; border-bottom: 1px solid var(--rule);
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-mark { width: 32px; height: 32px; border-radius: 7px; background: var(--ink); display: grid; place-items: center; flex: none; }
.brand-name { font-size: 20px; font-weight: 700; letter-spacing: -0.02em; color: var(--ink); }
.topbar-note { font-size: 14px; color: var(--ink-3); text-align: right; }

/* ---- Control panel (the form) ------------------------------------------- */
[data-testid="stForm"] {
    border: 1px solid var(--rule) !important;
    border-radius: var(--radius) !important;
    background: var(--paper) !important;
    padding: 20px !important;
    box-shadow: none !important;
}
.panel-title { font-size: 15px; font-weight: 650; margin: 0 0 4px; letter-spacing: -0.01em; }
.panel-sub { font-size: 14px; color: var(--ink-3); margin: 0 0 16px; line-height: 1.45; }
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
    font-size: 13.5px !important; font-weight: 600 !important; color: var(--ink) !important;
    letter-spacing: 0.01em;
}
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"], input, textarea {
    background: var(--paper) !important;
    border-color: var(--rule-strong) !important;
    border-radius: 6px !important;
    color: var(--ink) !important;
    font-family: var(--font) !important;
}
[data-baseweb="select"] > div, [data-baseweb="select"] > div > div { min-height: 42px; background: var(--paper) !important; }
[data-baseweb="select"] > div:focus-within, [data-baseweb="input"]:focus-within {
    border-color: var(--petrol) !important; box-shadow: 0 0 0 1px var(--petrol) !important;
}
[data-baseweb="popover"] li, [data-baseweb="menu"] li { font-family: var(--font) !important; }

/* Segmented radios (analysis mode + stock inspector) */
[data-testid="stRadio"] [role="radiogroup"] { gap: 6px !important; flex-wrap: wrap; }
label[data-testid="stRadioOption"] {
    border: 1px solid var(--rule-strong); border-radius: 6px; padding: 7px 14px !important;
    background: var(--paper); cursor: pointer; margin: 0 !important;
    transition: background 140ms ease-out, border-color 140ms ease-out;
}
label[data-testid="stRadioOption"] > div > div:first-child { display: none !important; }
label[data-testid="stRadioOption"] p { font-size: 13px !important; font-weight: 600 !important; color: var(--ink-2) !important; margin: 0; }
label[data-testid="stRadioOption"]:hover { background: var(--wash); }
label[data-testid="stRadioOption"][data-selected="true"] { background: var(--ink); border-color: var(--ink); }
label[data-testid="stRadioOption"][data-selected="true"] p { color: #fff !important; }
label[data-testid="stRadioOption"]:has(input:focus-visible) { outline: 2px solid var(--petrol); outline-offset: 2px; }

/* Slider */
[data-testid="stSlider"] [role="slider"] { background: var(--petrol) !important; box-shadow: none !important; }
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {
    color: var(--ink-2) !important; font-size: 12px !important; font-weight: 600;
}

/* Primary button */
[data-testid="stFormSubmitButton"] button, .stButton button {
    background: var(--ink) !important; color: #fff !important; border: 1px solid var(--ink) !important;
    border-radius: 6px !important; min-height: 44px; font-weight: 600 !important; font-size: 14px !important;
    transition: background 140ms ease-out, transform 140ms ease-out;
}
[data-testid="stFormSubmitButton"] button:hover, .stButton button:hover { background: #2b3238 !important; border-color: #2b3238 !important; }
[data-testid="stFormSubmitButton"] button:active { transform: translateY(1px); }
[data-testid="stFormSubmitButton"] button p { color: #fff !important; font-weight: 600 !important; }

/* Weight read-out inside panel */
.weights { display: flex; flex-direction: column; gap: 8px; margin: 2px 0 16px; }
.weights-bar { display: flex; height: 8px; border-radius: 2px; overflow: hidden; background: var(--wash); }
.weights-bar i { display: block; height: 100%; }
.weights-bar .wf { background: var(--petrol); }
.weights-bar .ws { background: var(--ink); }
.weights-legend { display: flex; justify-content: space-between; font-size: 13px; color: var(--ink-2); font-weight: 500; }

/* Progress + alerts */
[data-testid="stProgress"] > div > div { background: var(--wash) !important; }
[data-testid="stProgress"] > div > div > div { background: var(--petrol) !important; }
[data-testid="stAlert"] { border-radius: var(--radius) !important; border: 1px solid var(--rule-strong) !important; background: var(--wash) !important; color: var(--ink) !important; }

/* ---- Empty state --------------------------------------------------------- */
.intro h1 { font-size: clamp(30px, 4.4vw, 52px); line-height: 1.05; letter-spacing: -0.035em; font-weight: 700; margin: 4px 0 14px; max-width: 18ch; text-wrap: balance; }
.intro .lede { font-size: 17px; line-height: 1.55; color: var(--ink-2); max-width: 58ch; margin: 0 0 32px; }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid var(--ink); margin-bottom: 36px; }
.step { padding: 16px 20px 4px 0; }
.step + .step { padding-left: 20px; border-left: 1px solid var(--rule); }
.step h3 { font-size: 15px; font-weight: 650; margin: 0 0 6px; letter-spacing: -0.01em; }
.step p { font-size: 15px; line-height: 1.5; color: var(--ink-2); margin: 0; max-width: 34ch; }
.example-label { font-size: 14.5px; font-weight: 600; color: var(--ink); margin: 0 0 12px; }
.example { border: 1px solid var(--rule); border-radius: var(--radius); padding: 20px; max-width: 640px; }
.example-row { display: flex; align-items: center; gap: 14px; }
.example-row .tk { font-weight: 650; min-width: 76px; }
.intro p.fineprint { font-size: 14px; color: var(--ink-3); margin: 28px 0 0; max-width: 62ch; line-height: 1.5; }

/* ---- The score bar (signature) ------------------------------------------ */
.sb { position: relative; display: flex; height: 12px; background: var(--wash); border-radius: 2px; flex: 1; min-width: 72px; }
.sb i { display: block; height: 100%; }
.sb i.f { background: var(--petrol); border-radius: 2px 0 0 2px; }
.sb i.s { background: var(--ink); }
.sb b { position: absolute; top: -4px; bottom: -4px; width: 1px; background: var(--ink-3); }
.sb b.t40 { left: 40%; }
.sb b.t70 { left: 70%; }
.sb-lg { height: 18px; }
.sb-axis { position: relative; height: 16px; margin-top: 6px; font-size: 11px; color: var(--ink-3); font-weight: 500; }
.sb-axis span { position: absolute; transform: translateX(-50%); white-space: nowrap; }

.legend { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 13.5px; color: var(--ink-2); font-weight: 500; align-items: center; }
.legend .sw { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; vertical-align: -1px; }
.legend .sw.f { background: var(--petrol); }
.legend .sw.s { background: var(--ink); }
.legend .tick { display: inline-block; width: 1px; height: 12px; background: var(--ink-3); margin-right: 6px; vertical-align: -2px; }

/* ---- Results ------------------------------------------------------------- */
.summary { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px 24px; padding: 2px 0 14px; }
.summary h2 { font-size: 22px; font-weight: 700; letter-spacing: -0.025em; margin: 0; }
.summary .meta { font-size: 14px; color: var(--ink-3); }
.tally { display: flex; gap: 16px; font-size: 14px; font-weight: 600; }
.tally span { display: inline-flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot.buy { background: var(--buy); } .dot.hold { background: #c98a00; } .dot.sell { background: var(--sell); }

.table-wrap { overflow-x: auto; border-top: 1px solid var(--ink); margin-top: 14px; }
table.rank { width: 100%; border-collapse: collapse; font-size: 15.5px; border: 0 !important; }
table.rank th, table.rank td { border-left: 0 !important; border-right: 0 !important; border-top: 0 !important; background-clip: padding-box; }
table.rank th { text-align: left; font-size: 13.5px; font-weight: 600; color: var(--ink-3); padding: 10px 12px 10px 0; border-bottom: 1px solid var(--rule); white-space: nowrap; }
table.rank td { padding: 14px 12px 14px 0; border-bottom: 1px solid var(--rule); vertical-align: middle; }
table.rank tr:last-child td { border-bottom-color: var(--rule-strong); }
table.rank .num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; padding-right: 20px; }
table.rank th.num { text-align: right; padding-right: 20px; }
table.rank .rk { width: 36px; color: var(--ink-3); font-variant-numeric: tabular-nums; }
table.rank .nm b { display: block; font-weight: 650; letter-spacing: -0.005em; }
table.rank .nm span { display: block; font-size: 13px; color: var(--ink-3); margin-top: 2px; max-width: 26ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
table.rank .scorecell { min-width: 220px; }
.scoreline { display: flex; align-items: center; gap: 14px; }
.scoreline .val { font-weight: 700; font-size: 16px; min-width: 40px; text-align: right; font-variant-numeric: tabular-nums; }
table.rank tr.top td { background: var(--wash); }
table.rank tr.top td:first-child { padding-left: 10px; color: var(--ink); font-weight: 700; }
.badge { display: inline-block; font-size: 13px; font-weight: 700; letter-spacing: 0.04em; padding: 4px 10px; border-radius: 4px; }
.badge.buy { color: var(--buy); background: var(--buy-wash); }
.badge.hold { color: var(--hold); background: var(--hold-wash); }
.badge.sell { color: var(--sell); background: var(--sell-wash); }

/* ---- Detail -------------------------------------------------------------- */
.detail-head { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 16px; padding: 8px 0 20px; }
.detail-head h2 { font-size: clamp(26px, 3vw, 36px); font-weight: 700; letter-spacing: -0.03em; margin: 0; line-height: 1.1; }
.detail-head .co { font-size: 14px; color: var(--ink-3); margin-top: 6px; }
.detail-score { display: flex; align-items: center; gap: 14px; }
.detail-score .big { font-size: clamp(32px, 4vw, 44px); font-weight: 700; letter-spacing: -0.04em; line-height: 1; font-variant-numeric: tabular-nums; }
.detail-score .big small { font-size: 14px; color: var(--ink-3); font-weight: 500; letter-spacing: 0; }
.blend { border: 1px solid var(--rule); border-radius: var(--radius); padding: 18px 20px 14px; margin-bottom: 24px; }
.blend-parts { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--rule); }
.blend-part .k { font-size: 13.5px; font-weight: 600; color: var(--ink-3); display: flex; align-items: center; gap: 6px; }
.blend-part .v { font-size: 22px; font-weight: 700; letter-spacing: -0.02em; margin-top: 2px; font-variant-numeric: tabular-nums; }
.blend-part .v small { font-size: 13px; font-weight: 500; color: var(--ink-3); letter-spacing: 0; }
.sec-title { font-size: 14.5px; font-weight: 650; color: var(--ink); margin: 0 0 4px; padding-bottom: 10px; border-bottom: 1px solid var(--ink); letter-spacing: 0.005em; }
dl.facts { margin: 0; display: grid; grid-template-columns: 1fr auto; }
dl.facts dt, dl.facts dd { padding: 11px 0; border-bottom: 1px solid var(--rule); margin: 0; font-size: 15.5px; }
dl.facts dt { color: var(--ink-2); }
dl.facts dd { text-align: right; font-weight: 600; font-variant-numeric: tabular-nums; padding-left: 16px; }
dl.facts dd.na { color: var(--ink-3); font-weight: 400; }
.why { margin: 24px 0 8px; }
.why p.body { font-size: 16.5px; line-height: 1.7; color: var(--ink); max-width: 72ch; margin: 14px 0 0; }
.news { margin-top: 28px; }
.news ul { list-style: none; margin: 0; padding: 0; }
.news li { display: grid; grid-template-columns: 1fr auto; gap: 4px 20px; padding: 14px 0; border-bottom: 1px solid var(--rule); align-items: start; }
.news a { color: var(--ink); font-weight: 600; font-size: 16px; line-height: 1.4; text-decoration: underline; text-decoration-color: var(--rule-strong); transition: text-decoration-color 140ms ease-out; }
.news a:hover { text-decoration-color: var(--petrol); color: var(--petrol); }
.news .src { grid-column: 1; font-size: 13.5px; color: var(--ink-3); }
.news .tone { grid-row: 1 / span 2; grid-column: 2; font-size: 13.5px; font-weight: 600; white-space: nowrap; display: inline-flex; align-items: center; gap: 6px; font-variant-numeric: tabular-nums; }
.tone.positive { color: var(--buy); } .tone.negative { color: var(--sell); } .tone.neutral { color: var(--ink-3); }
.empty-note { font-size: 15px; color: var(--ink-3); padding: 14px 0; }
.stack-gap { height: 36px; }
.lead { font-size: 17px; line-height: 1.6; color: var(--ink); max-width: 70ch; margin: 0 0 20px; }

/* ---- Plain-language tooltips (hover, keyboard focus, or tap) ------------- */
.tip { position: relative; display: inline-grid; place-items: center; width: 17px; height: 17px; margin-left: 6px;
    border-radius: 50%; border: 1.5px solid var(--ink-3); color: var(--ink-2); font-size: 11px; font-weight: 700;
    line-height: 1; cursor: help; vertical-align: 1px; background: var(--paper); text-transform: none; letter-spacing: 0; }
.tip:hover, .tip:focus { background: var(--ink); color: #fff; border-color: var(--ink); outline: none; }
.tip::after { content: attr(data-tip); position: absolute; z-index: 60; left: 50%; top: calc(100% + 8px);
    transform: translateX(-30%); width: 250px; padding: 10px 12px; border-radius: 6px; background: var(--ink); color: #fff;
    font-size: 14px; font-weight: 450; line-height: 1.45; text-align: left; white-space: normal;
    box-shadow: 0 6px 18px rgba(20, 24, 27, 0.22); opacity: 0; visibility: hidden; pointer-events: none;
    transition: opacity 120ms ease-out; }
.tip:hover::after, .tip:focus::after { opacity: 1; visibility: visible; }
.tip.r::after { left: auto; right: -8px; transform: none; }
@media (max-width: 640px) { .tip::after { width: 220px; } }


/* ---- Live agent panel ---------------------------------------------------- */
.run { border: 1px solid var(--rule); border-radius: var(--radius); padding: 20px; }
.run-head { display: flex; justify-content: space-between; align-items: baseline; font-size: 15px; }
.run-head span { font-weight: 700; font-variant-numeric: tabular-nums; }
.run-bar { height: 6px; background: var(--wash); border-radius: 2px; margin: 10px 0 8px; overflow: hidden; }
.run-bar i { display: block; height: 100%; background: var(--petrol); transition: width 250ms ease-out; }
.agent { display: grid; grid-template-columns: 14px minmax(180px, 1.1fr) 2fr auto; gap: 6px 14px; align-items: center; padding: 14px 0; border-top: 1px solid var(--rule); }
.run-bar + .agent { border-top: 1px solid var(--ink); }
.astate { width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--rule-strong); }
.agent.run .astate { border-color: var(--petrol); background: var(--petrol-wash); animation: pulse 1s ease-in-out infinite; }
.agent.done .astate { background: var(--ink); border-color: var(--ink); }
.ainfo b { display: block; font-size: 15px; font-weight: 650; }
.ainfo span { display: block; font-size: 13.5px; color: var(--ink-3); margin-top: 2px; line-height: 1.4; }
.achips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font-size: 13px; font-weight: 600; padding: 3px 9px; border-radius: 4px; border: 1px solid var(--rule-strong); color: var(--ink-3); background: var(--paper); }
.chip.run { color: var(--petrol); border-color: var(--petrol); background: var(--petrol-wash); }
.chip.done { color: #fff; background: var(--ink); border-color: var(--ink); }
.chip.fail { color: var(--sell); background: var(--sell-wash); border-color: var(--sell); text-decoration: line-through; }
.chip.skip { color: var(--ink-3); background: var(--wash); border-style: dashed; }
.acount { font-size: 13px; font-weight: 600; color: var(--ink-3); min-width: 44px; text-align: right; font-variant-numeric: tabular-nums; }
@keyframes pulse { 50% { opacity: 0.35; } }
@media (max-width: 760px) {
    .agent { grid-template-columns: 14px 1fr auto; }
    .achips { grid-column: 2 / span 2; }
}


/* ---- Layout + responsive ------------------------------------------------- */
.st-key-shell > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] { align-items: flex-start; gap: clamp(24px, 3vw, 48px) !important; }
.st-key-shell > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child { position: sticky; top: 16px; }

@media (max-width: 1100px) {
    .steps { grid-template-columns: 1fr; border-top: 1px solid var(--ink); }
    .step, .step + .step { padding: 14px 0; border-left: 0; border-bottom: 1px solid var(--rule); }
    .step p { max-width: none; }
}
@media (max-width: 960px) {
    .st-key-shell > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    .st-key-shell > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-width: 100% !important; flex: 1 1 100% !important; position: static !important; }
    .topbar-note { display: none; }
    table.rank .c-pe, table.rank .c-roe { display: none; }
}
@media (max-width: 640px) {
    table.rank .c-price { display: none; }
    table.rank .scorecell { min-width: 0; }
    table.rank td, table.rank th { padding-right: 8px; }
    table.rank .rk { width: 22px; }
    table.rank .nm span { display: none; }
    .sb { min-width: 44px; }
    .scoreline { gap: 8px; }
    .scoreline .val { min-width: 34px; font-size: 15px; }
    .badge { padding: 3px 7px; font-size: 11px; }
    .tally { gap: 12px; }
    .blend-parts { grid-template-columns: 1fr; }
    .detail-head { align-items: flex-start; }
    .news li { grid-template-columns: 1fr; }
    .news .tone { grid-row: auto; grid-column: 1; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Backend wiring (unchanged behaviour)
# ---------------------------------------------------------------------------
@st.cache_resource
def get_agents():
    return ScreeningAgent(), FundamentalAgent(), SentimentAgent(), AggregatorAgent()

screening_agent, fundamental_agent, sentiment_agent, aggregator_agent = get_agents()

@st.cache_data(ttl=600)
def cached_fundamental_analysis(ticker):
    return fundamental_agent.analyze_stock(ticker)

@st.cache_data(ttl=1800)
def cached_sentiment_analysis(ticker, company_name):
    return sentiment_agent.analyze_sentiment(ticker, company_name)

def process_single_ticker(t, fund_weight, sent_weight, prog, lock):
    """Worker: fundamentals, then sentiment, then aggregation for one ticker.
    Reports each agent's state into `prog` so the UI can show live progress."""
    def mark(stage, state):
        with lock:
            prog[t][stage] = state

    mark('fund', 'run')
    fund_data = cached_fundamental_analysis(t)
    if fund_data.get('error') or not is_num(fund_data.get('current_price')):
        mark('fund', 'fail'); mark('sent', 'skip'); mark('agg', 'skip')
        return {'ticker': t, 'error': f"No market data found for {t}. Check the name or symbol."}
    mark('fund', 'done')

    company = fund_data.get('company_name', t)
    mark('sent', 'run')
    sent_data = cached_sentiment_analysis(t, company)
    mark('sent', 'done')

    mark('agg', 'run')
    agg = aggregator_agent.aggregate_scores(
        ticker=t, company_name=company,
        screening_data={'ticker': t},
        fundamental_data=fund_data,
        sentiment_data=sent_data,
        fundamental_weight=fund_weight / 100,
        sentiment_weight=sent_weight / 100,
    )
    agg['_fund'] = fund_data
    agg['_sent'] = sent_data
    mark('agg', 'done')
    return agg

SECTORS = {
    "IT & Technology":      ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
    "Banking & Finance":    ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
    "Automotive":           ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT"],
    "Pharmaceuticals":      ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "BIOCON"],
    "Green Energy":         ["ADANIGREEN", "SUZLON", "TATAPOWER", "NTPC", "POWERGRID"],
    "Diversified":          ["RELIANCE", "ITC", "HINDUNILVR", "LT", "ASIANPAINT"],
}

COMPANY_NAMES = {
    "tata consultancy services": "TCS", "tata consultancy": "TCS", "infosys": "INFY", "hcl technologies": "HCLTECH",
    "hcl tech": "HCLTECH", "hcl": "HCLTECH", "wipro": "WIPRO", "tech mahindra": "TECHM",
    "hdfc bank": "HDFCBANK", "hdfc": "HDFCBANK", "icici bank": "ICICIBANK", "icici": "ICICIBANK",
    "state bank of india": "SBIN", "sbi": "SBIN", "kotak mahindra bank": "KOTAKBANK", "kotak": "KOTAKBANK",
    "axis bank": "AXISBANK", "axis": "AXISBANK", "maruti suzuki": "MARUTI", "maruti": "MARUTI",
    "tata motors": "TATAMOTORS", "mahindra": "M&M", "mahindra and mahindra": "M&M", "bajaj auto": "BAJAJ-AUTO",
    "eicher motors": "EICHERMOT", "eicher": "EICHERMOT", "sun pharma": "SUNPHARMA", "sun pharmaceutical": "SUNPHARMA",
    "dr reddys": "DRREDDY", "dr reddy": "DRREDDY", "cipla": "CIPLA", "divis labs": "DIVISLAB", "divis": "DIVISLAB",
    "biocon": "BIOCON", "adani green": "ADANIGREEN", "suzlon": "SUZLON", "tata power": "TATAPOWER",
    "ntpc": "NTPC", "power grid": "POWERGRID", "reliance": "RELIANCE", "reliance industries": "RELIANCE",
    "itc": "ITC", "hindustan unilever": "HINDUNILVR", "hul": "HINDUNILVR", "larsen and toubro": "LT",
    "larsen & toubro": "LT", "l&t": "LT", "asian paints": "ASIANPAINT",
}

def resolve_stocks(text, limit=8):
    """Turn 'Infosys, reliance, TCS' into ['INFY', 'RELIANCE', 'TCS']. Names or tickers both work."""
    out = []
    for raw in re.split(r'[,\n;]+', text or ''):
        raw = raw.strip()
        if not raw:
            continue
        key = re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9&\- ]', '', raw.lower())).strip()
        tk = COMPANY_NAMES.get(key) or re.sub(r'\.(NS|BO)$', '', raw.upper().replace(' ', ''))
        if tk and tk not in out:
            out.append(tk)
    return out[:limit]

AGENTS = [
    ("screen", "Screening agent", "Chooses which stocks to analyze"),
    ("fund", "Fundamental agent", "Reads price, P/E, profitability and debt from Yahoo Finance"),
    ("sent", "Sentiment agent", "Reads recent news headlines and scores their tone"),
    ("agg", "Aggregator agent", "Blends both scores using your weighting into Buy, Hold or Sell"),
]

def render_run(prog, tickers):
    """Live panel: one row per agent, one chip per stock. Everything the pipeline does, visible."""
    n = len(tickers)
    done_steps = 1 + sum(1 for t in tickers for k in ('fund', 'sent', 'agg') if prog[t][k] in ('done', 'fail', 'skip'))
    pct = int(done_steps / (1 + 3 * n) * 100)
    rows = []
    for key, name, desc in AGENTS:
        if key == "screen":
            chips = f'<span class="chip done">{n} stock{"s" if n != 1 else ""} selected</span>'
            state, count = "done", "Done"
        else:
            states = [prog[t][key] for t in tickers]
            finished = sum(1 for x in states if x in ('done', 'fail', 'skip'))
            running = any(x == 'run' for x in states)
            state = "done" if finished == n else "run" if running else "wait"
            count = "Done" if finished == n else f"{finished} of {n}"
            chips = "".join(f'<span class="chip {x}">{esc(t)}</span>' for t, x in zip(tickers, states))
        rows.append(
            f'<div class="agent {state}"><span class="astate" aria-hidden="true"></span>'
            f'<div class="ainfo"><b>{name}</b><span>{desc}</span></div>'
            f'<div class="achips">{chips}</div><span class="acount">{count}</span></div>')
    return (f'<div class="run" role="status" aria-live="polite"><div class="run-head"><b>Analysis running</b>'
            f'<span>{pct}%</span></div><div class="run-bar"><i style="width:{pct}%"></i></div>'
            + "".join(rows) + '</div>')

# ---------------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------------
def esc(v):
    return html.escape(str(v), quote=True)

def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)

def fmt_num(v, digits=2):
    return f"{v:,.{digits}f}" if is_num(v) else None

def fmt_pct(v, digits=1):
    return f"{v * 100:.{digits}f}%" if is_num(v) else None

def fmt_price(fund):
    p = fund.get('current_price')
    if not is_num(p):
        return None
    cur = fund.get('currency', 'INR')
    sym = {"INR": "₹", "USD": "$"}.get(cur, f"{cur} ")
    return f"{sym}{p:,.2f}"

def na(v):
    return v if v else "—"


GLOSSARY = {
    "Price": "The latest price of one share.",
    "Market cap": "The total value of the whole company on the stock market.",
    "P/E ratio": "How many rupees you pay for each rupee of the company's yearly profit. Lower can mean cheaper. Very high can mean expensive.",
    "P/B ratio": "Share price compared with what the company owns minus what it owes. Lower can mean cheaper.",
    "Return on equity": "How much profit the company makes from its shareholders' money. Higher is better.",
    "Profit margin": "How much of every 100 rupees of sales is left as profit. Higher is better.",
    "Debt to equity": "How much the company has borrowed compared with its own money. Lower is safer.",
    "Revenue growth": "How much the company's sales grew compared with last year.",
    "Dividend yield": "Yearly cash the company pays shareholders, as a percent of the share price.",
}

def tip(text, right=False):
    """Small (?) that explains a term in plain words. Works on hover, keyboard focus and tap."""
    return (f'<span class="tip{" r" if right else ""}" tabindex="0" role="note" '
            f'aria-label="{esc(text)}" data-tip="{esc(text)}">?</span>')

def badge(rec):
    cls = {"BUY": "buy", "HOLD": "hold", "SELL": "sell"}.get(rec, "hold")
    return f'<span class="badge {cls}">{esc(rec)}</span>'

def score_bar(result, large=False):
    """Signature element: one bar, split into fundamental and sentiment
    contribution, with ticks at the 40 (hold) and 70 (buy) thresholds."""
    overall = max(0.0, min(100.0, float(result.get('overall_score', 0) or 0)))
    w = result.get('weights_used') or {}
    fw = (w.get('fundamental', 60) or 0) / 100
    sw = (w.get('sentiment', 40) or 0) / 100
    f = (result.get('fundamental_score', 0) or 0) * fw
    s = (result.get('sentiment_score', 0) or 0) * sw
    total = f + s
    if total > 0:
        fpart, spart = overall * f / total, overall * s / total
    else:
        fpart = spart = 0
    cls = "sb sb-lg" if large else "sb"
    return (f'<div class="{cls}" role="img" aria-label="Score {overall:.1f} of 100: '
            f'{fpart:.1f} from fundamentals, {spart:.1f} from sentiment">'
            f'<i class="f" style="width:{fpart:.2f}%"></i><i class="s" style="width:{spart:.2f}%"></i>'
            f'<b class="t40"></b><b class="t70"></b></div>')

def legend_html():
    return ('<div class="legend">'
            '<span><i class="sw f"></i>From fundamentals</span>'
            '<span><i class="sw s"></i>From news sentiment</span>'
            '<span><i class="tick"></i>40 = Hold starts</span>'
            '<span><i class="tick"></i>70 = Buy starts</span></div>')

def safe_url(u):
    u = str(u or '').strip()
    return u if u.lower().startswith(('http://', 'https://')) else ''

# ---------------------------------------------------------------------------
# Top bar
# ---------------------------------------------------------------------------
st.markdown("""
<div class="topbar">
  <div class="brand">
    <div class="brand-mark" aria-hidden="true">
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="2" y="9" width="3.4" height="7" fill="#fff"/><rect x="7.3" y="5" width="3.4" height="11" fill="#fff"/><rect x="12.6" y="1.5" width="3.4" height="14.5" fill="#fff"/></svg>
    </div>
    <div class="brand-name">StockSage</div>
  </div>
  <div class="topbar-note">NSE stocks scored from fundamentals and news sentiment</div>
</div>
""", unsafe_allow_html=True)

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
    st.session_state.analysis_meta = None

# ---------------------------------------------------------------------------
# Layout: controls (left) | work area (right)
# ---------------------------------------------------------------------------
with st.container(key="shell"):
    left_panel, right_panel = st.columns([1, 2.6], gap="large")

    with left_panel:
        with st.form("parameters_form", clear_on_submit=False):
            st.markdown('<p class="panel-title">Analysis setup</p>'
                        '<p class="panel-sub">Choose a sector and press Run. Everything else is optional.</p>',
                        unsafe_allow_html=True)

            sector = st.selectbox("Sector", list(SECTORS.keys()),
                                  help="A sector is a group of similar companies, like banks or car makers. We compare the biggest ones in the sector you choose.")
            custom_input = st.text_input(
                "Or type your own stocks (optional)",
                placeholder="Infosys, Reliance, HDFC Bank",
                help="Leave this empty to analyze the sector above. Company names and ticker symbols both work, separated by commas.")
            num_stocks = st.slider("How many sector stocks", min_value=1, max_value=5, value=5,
                                   help="How many companies from the sector to compare. More stocks takes a few seconds longer.")
            fund_weight = st.slider("Weight on fundamentals (%)", min_value=0, max_value=100, value=60, step=10,
                                    help="Fundamentals are the company's own numbers: profit, debt and price. The rest of the score comes from recent news. At 60, the numbers count 60% and the news counts 40%. Not sure? Leave it at 60. Slide right to trust the numbers more, left to trust the news more.")
            sent_weight = 100 - fund_weight

            st.markdown(
                f'<div class="weights"><div class="weights-bar" aria-hidden="true">'
                f'<i class="wf" style="width:{fund_weight}%"></i><i class="ws" style="width:{sent_weight}%"></i></div>'
                f'<div class="weights-legend"><span>Fundamentals {fund_weight}%</span><span>News sentiment {sent_weight}%</span></div></div>',
                unsafe_allow_html=True)

            run_btn = st.form_submit_button("Run analysis", width="stretch")

    with right_panel:
        if run_btn:
            if custom_input.strip():
                tickers = resolve_stocks(custom_input)
                basket_label = "Your stocks"
            else:
                tickers = SECTORS.get(sector, [])[:num_stocks]
                basket_label = sector

            if not tickers:
                st.error("Couldn't read any stocks from that. Try names like Infosys or symbols like TCS, or clear the box to use the sector.")
            else:
                prog = {t: {'fund': 'wait', 'sent': 'wait', 'agg': 'wait'} for t in tickers}
                lock = threading.Lock()
                panel = st.empty()
                results, errors = [], []

                with concurrent.futures.ThreadPoolExecutor(max_workers=len(tickers)) as executor:
                    futures = {executor.submit(process_single_ticker, t, fund_weight, sent_weight, prog, lock): t
                               for t in tickers}
                    while True:
                        with lock:
                            panel.markdown(render_run(prog, tickers), unsafe_allow_html=True)
                        if all(f.done() for f in futures):
                            break
                        time.sleep(0.2)

                for future, t in futures.items():
                    try:
                        data = future.result()
                        if 'error' in data and not data.get('overall_score'):
                            errors.append((t, data['error']))
                        else:
                            results.append(data)
                    except Exception as e:
                        errors.append((t, f"Something went wrong analyzing {t} ({e})."))

                time.sleep(0.5)
                panel.empty()

                for t, err in errors:
                    st.warning(err)

                results.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
                st.session_state.analysis_results = results
                st.session_state.analysis_meta = {
                    'basket': basket_label, 'fw': fund_weight, 'sw': sent_weight,
                    'asked': len(tickers),
                }
                st.session_state.pop('inspect', None)

        results = st.session_state.analysis_results
        meta = st.session_state.analysis_meta or {}

        # ------------------------- Empty state ---------------------------
        if results is None:
            st.markdown(
                '<div class="intro">'
                '<h1>Rank NSE stocks by the numbers and the news.</h1>'
                '<p class="lede">Each stock gets a 0–100 score. Part comes from company fundamentals (valuation, profitability, debt), '
                'part from the tone of recent headlines. You decide how much each part counts.</p>'
                '<div class="steps">'
                '<div class="step"><h3>Screen</h3><p>Pick a sector, or type company names like Infosys or Reliance. No ticker symbols needed.</p></div>'
                '<div class="step"><h3>Score</h3><p>Separate agents read Yahoo Finance data and recent news for every stock, live on screen.</p></div>'
                '<div class="step"><h3>Blend</h3><p>Your weight slider mixes the two scores into one rating: Buy, Hold or Sell.</p></div>'
                '</div>'
                '<p class="example-label">How to read a result</p>'
                '<div class="example">'
                '<div class="example-row"><span class="tk">Example</span>'
                '<div class="sb sb-lg" role="img" aria-label="Example score of 78, 47 from fundamentals and 31 from sentiment">'
                '<i class="f" style="width:46.8%"></i><i class="s" style="width:31.2%"></i><b class="t40"></b><b class="t70"></b></div>'
                '<span class="badge buy">BUY</span></div>'
                '<div style="margin:14px 0 0">' + legend_html() + '</div></div>'
                '<p class="fineprint">Scores come from a simple formula over public data. This is a project demo, not investment advice.</p>'
                '</div>', unsafe_allow_html=True)

        # --------------------------- Results ------------------------------
        elif not results:
            st.markdown('<div class="intro"><h1>No results.</h1>'
                        '<p class="lede">None of the stocks could be analyzed. Check the ticker symbols and try again.</p></div>',
                        unsafe_allow_html=True)
        else:
            buys = sum(1 for r in results if r['recommendation'] == 'BUY')
            holds = sum(1 for r in results if r['recommendation'] == 'HOLD')
            sells = sum(1 for r in results if r['recommendation'] == 'SELL')
            top = results[0]
            avg = sum(r['overall_score'] for r in results) / len(results)

            st.markdown(
                '<div class="summary"><div>'
                f'<h2>{esc(meta.get("basket", "Results"))}: {esc(top["ticker"])} ranks first</h2>'
                f'<div class="meta">{len(results)} stocks · average score {avg:.1f} · '
                f'{meta.get("fw", 60)}% fundamentals / {meta.get("sw", 40)}% news</div></div>'
                '<div class="tally">'
                f'<span><i class="dot buy"></i>{buys} Buy</span>'
                f'<span><i class="dot hold"></i>{holds} Hold</span>'
                f'<span><i class="dot sell"></i>{sells} Sell</span></div></div>',
                unsafe_allow_html=True)
            st.markdown(legend_html(), unsafe_allow_html=True)

            rows = []
            for i, r in enumerate(results, start=1):
                f = r.get('_fund', {})
                rows.append(
                    f'<tr class="{"top" if i == 1 else ""}">'
                    f'<td class="rk">{i}</td>'
                    f'<td class="nm"><b>{esc(r["ticker"])}</b><span>{esc(r["company_name"])}</span></td>'
                    f'<td class="num c-price">{esc(na(fmt_price(f)))}</td>'
                    f'<td class="num c-pe">{esc(na(fmt_num(f.get("pe_ratio"))))}</td>'
                    f'<td class="num c-roe">{esc(na(fmt_pct(f.get("roe"))))}</td>'
                    f'<td class="scorecell"><div class="scoreline">{score_bar(r)}'
                    f'<span class="val">{r["overall_score"]:.1f}</span></div></td>'
                    f'<td>{badge(r["recommendation"])}</td></tr>')

            st.markdown(
                '<div class="table-wrap"><table class="rank"><thead><tr>'
                '<th>#</th><th>Stock</th><th class="num c-price">Price</th>'
                f'<th class="num c-pe">P/E{tip(GLOSSARY["P/E ratio"])}</th>'
                f'<th class="num c-roe">ROE{tip(GLOSSARY["Return on equity"])}</th>'
                f'<th>Score{tip("Out of 100. The bar shows how much came from company numbers (teal) and how much from news (black). The thin lines mark 40 and 70.")}</th>'
                f'<th>Signal{tip("Buy means a score of 70 or more. Hold is 40 to 69. Sell is below 40. It is a simple formula, not advice.", right=True)}</th></tr></thead><tbody>'
                + "".join(rows) + '</tbody></table></div>', unsafe_allow_html=True)

            # ------------------------- Detail ----------------------------
            st.markdown('<div class="stack-gap"></div>', unsafe_allow_html=True)
            tickers_ranked = [r['ticker'] for r in results]
            if st.session_state.get('inspect') not in tickers_ranked:
                st.session_state['inspect'] = tickers_ranked[0]
            chosen = st.radio("Inspect a stock", tickers_ranked, horizontal=True, key="inspect")
            result = next(r for r in results if r['ticker'] == chosen)

            f = result.get('_fund', {})
            s = result.get('_sent', {})
            w = result.get('weights_used') or {}
            fw_pct = w.get('fundamental', meta.get('fw', 60))
            sw_pct = w.get('sentiment', meta.get('sw', 40))

            st.markdown(
                '<div class="detail-head"><div>'
                f'<h2>{esc(result["ticker"])}</h2><div class="co">{esc(result["company_name"])}</div></div>'
                f'<div class="detail-score"><div class="big">{result["overall_score"]:.1f}<small> / 100</small></div>'
                f'{badge(result["recommendation"])}</div></div>',
                unsafe_allow_html=True)

            verdict = {"BUY": "a Buy: it looks attractive on this formula",
                       "HOLD": "a Hold: neither clearly good nor clearly bad",
                       "SELL": "a Sell: it looks weak on this formula"}.get(result["recommendation"], "a Hold")
            st.markdown(
                f'<p class="lead"><b>In plain words:</b> {esc(result["ticker"])} scored {result["overall_score"]:.1f} out of 100, which is {verdict}. '
                f'Its company numbers scored {result.get("fundamental_score", 0):.0f} and its news scored {result.get("sentiment_score", 0):.0f}. '
                f'Your {fw_pct:.0f}/{sw_pct:.0f} weighting mixed them into that one score.</p>',
                unsafe_allow_html=True)
            st.markdown(
                '<div class="blend">' + score_bar(result, large=True) +
                '<div class="sb-axis" aria-hidden="true"><span style="left:0;transform:none">0</span>'
                '<span style="left:40%">40</span><span style="left:70%">70</span>'
                '<span style="left:100%;transform:translateX(-100%)">100</span></div>'
                '<div class="blend-parts">'
                f'<div class="blend-part"><div class="k"><i class="sw f legend-sw" style="display:inline-block;width:10px;height:10px;border-radius:2px;background:var(--petrol)"></i>Fundamentals{tip("The score from company numbers: valuation, profit and debt, taken from Yahoo Finance.")}</div>'
                f'<div class="v">{result.get("fundamental_score", 0):.1f} <small>at {fw_pct:.0f}% weight</small></div></div>'
                f'<div class="blend-part"><div class="k"><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:var(--ink)"></i>News sentiment{tip("The score from how positive or negative the latest news headlines about this company are.", right=True)}</div>'
                f'<div class="v">{result.get("sentiment_score", 0):.1f} <small>at {sw_pct:.0f}% weight</small></div></div>'
                '</div></div>', unsafe_allow_html=True)

            col_facts, col_radar = st.columns([1, 1], gap="large")

            with col_facts:
                pe_val, roe_val, de_val = f.get('pe_ratio'), f.get('roe'), f.get('debt_to_equity')
                facts = [
                    ("Price", fmt_price(f)),
                    ("Market cap", f.get('market_cap') if f.get('market_cap') not in (None, 'N/A') else None),
                    ("P/E ratio", fmt_num(pe_val)),
                    ("P/B ratio", fmt_num(f.get('pb_ratio'))),
                    ("Return on equity", fmt_pct(roe_val)),
                    ("Profit margin", fmt_pct(f.get('profit_margin'))),
                    ("Debt to equity", fmt_num(de_val)),
                    ("Revenue growth", fmt_pct(f.get('revenue_growth'))),
                    ("Dividend yield", (fmt_num(f.get('dividend_yield')) + "%") if is_num(f.get('dividend_yield')) else None),
                ]
                dl = "".join(
                    f'<dt>{esc(k)}{tip(GLOSSARY[k]) if k in GLOSSARY else ""}</dt><dd class="{"" if v else "na"}">{esc(v) if v else "—"}</dd>'
                    for k, v in facts)
                st.markdown(f'<p class="sec-title">Financials</p><dl class="facts">{dl}</dl>', unsafe_allow_html=True)

            with col_radar:
                st.markdown('<p class="sec-title">Score profile</p>', unsafe_allow_html=True)
                pe_score = min(100, max(0, 100 - ((pe_val or 15) - 10) * 2))
                roe_score = min(100, (roe_val or 0) * 400)
                debt_score = min(100, 100 - (de_val or 0) * 20)
                categories = ['Valuation', 'Profitability', 'Health', 'Sentiment', 'Fundamentals']
                values = [pe_score, roe_score, debt_score,
                          result.get('sentiment_score', 50), result.get('fundamental_score', 50)]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]], theta=categories + [categories[0]],
                    fill='toself', fillcolor='rgba(10,92,115,0.14)',
                    line=dict(color='#0a5c73', width=2), name='Scores',
                    hovertemplate='%{theta}: %{r:.0f}<extra></extra>'))
                fig.update_layout(
                    polar=dict(
                        bgcolor='rgba(0,0,0,0)',
                        radialaxis=dict(visible=True, range=[0, 100], showticklabels=False,
                                        gridcolor='#e3e3dc', linecolor='#e3e3dc'),
                        angularaxis=dict(gridcolor='#e3e3dc', linecolor='#c9c9c0',
                                         tickfont=dict(family='Public Sans, sans-serif', size=12, color='#4a5057'))),
                    showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=72, r=72, t=24, b=24), height=320)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

            reasoning = result.get('reasoning') or 'No written analysis is available for this stock.'
            st.markdown(f'<div class="why"><p class="sec-title">Why this rating</p><p class="body">{esc(reasoning)}</p></div>',
                        unsafe_allow_html=True)

            articles = (s or {}).get('detailed_analysis', []) or []
            if articles:
                items = []
                for a in articles[:6]:
                    label = a.get('sentiment_label', 'neutral')
                    label = label if label in ('positive', 'negative', 'neutral') else 'neutral'
                    score = a.get('sentiment_score', 0.0)
                    score = score if is_num(score) else 0.0
                    url = safe_url(a.get('url'))
                    title = esc(a.get('title', 'Untitled article'))
                    head = (f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{title}</a>'
                            if url else f'<span style="font-weight:600">{title}</span>')
                    src = esc(a.get('source', 'Unknown'))
                    pub = esc(a.get('published_at', ''))
                    items.append(
                        f'<li><div>{head}</div>'
                        f'<span class="tone {label}"><i class="dot" style="background:currentColor"></i>{label.capitalize()} {score:+.2f}</span>'
                        f'<div class="src">{src}{" · " + pub if pub else ""}</div></li>')
                st.markdown(
                    f'<div class="news"><p class="sec-title">Headlines behind the sentiment score ({len(articles)} found, top {min(6, len(articles))} shown)</p>'
                    f'<ul>{"".join(items)}</ul></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="news"><p class="sec-title">Headlines behind the sentiment score</p>'
                            '<div class="empty-note">No news articles were found for this stock, so sentiment is neutral by default.</div></div>',
                            unsafe_allow_html=True)
