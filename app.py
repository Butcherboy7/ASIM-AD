import streamlit as st
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Import backend agents
from agents.screening_agent import ScreeningAgent
from agents.fundamental_agent import FundamentalAgent
from agents.sentiment_agent import SentimentAgent
from agents.aggregator_agent import AggregatorAgent

# Set page config
st.set_page_config(
    page_title="StockSage AI",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for high-end glassmorphic theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* Global styles */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background-color: #050505 !important;
        font-family: 'Outfit', sans-serif !important;
        color: #ffffff !important;
        overflow-y: auto !important;
    }
    
    /* Radial glows for 3D depth */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: -20%;
        left: -10%;
        width: 60vw;
        height: 60vw;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(30,27,75,0.4) 0%, rgba(5,5,5,0) 70%);
        pointer-events: none;
        z-index: 0;
    }
    
    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: fixed;
        bottom: -20%;
        right: -10%;
        width: 70vw;
        height: 70vw;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(76,29,149,0.3) 0%, rgba(5,5,5,0) 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* Main Container padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        z-index: 10;
    }

    /* Header styling */
    .header-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 30px;
    }
    .header-logo {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(59,130,246,0.3);
        font-weight: bold;
        font-size: 20px;
    }
    .header-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(to right, #ffffff, #9ca3af);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    /* Glassmorphic Panel */
    .glass-panel {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(24px) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    
    .glass-panel::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.02) 100%);
    }

    /* Sidebar controls styling */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(24px) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
        margin-bottom: 24px;
    }

    /* Hero section styling */
    .hero-title {
        font-size: 64px;
        font-weight: 900;
        line-height: 1.1;
        letter-spacing: -2px;
        margin-bottom: 16px;
    }
    .hero-gradient {
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 20px;
        color: #9ca3af;
        line-height: 1.6;
        max-width: 500px;
        margin-bottom: 30px;
    }

    /* Custom Streamlit Element overrides */
    div[data-baseweb="select"] > div, input, select, textarea {
        background-color: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* Stat Cards */
    .stat-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .stat-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .stat-value {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .stat-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #9ca3af;
        font-weight: 600;
    }

    /* Custom Progress styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
    }

    /* Recommendation badges */
    .badge-buy {
        color: #4ade80 !important;
        background: rgba(74, 222, 128, 0.1) !important;
        border: 1px solid rgba(74, 222, 128, 0.3) !important;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        letter-spacing: 1px;
        font-size: 12px;
    }
    .badge-hold {
        color: #facc15 !important;
        background: rgba(250, 204, 21, 0.1) !important;
        border: 1px solid rgba(250, 204, 21, 0.3) !important;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        letter-spacing: 1px;
        font-size: 12px;
    }
    .badge-sell {
        color: #f87171 !important;
        background: rgba(248, 113, 113, 0.1) !important;
        border: 1px solid rgba(248, 113, 113, 0.3) !important;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        letter-spacing: 1px;
        font-size: 12px;
    }

    /* Metrics table layout */
    .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .metric-name {
        color: #9ca3af;
        font-size: 14px;
    }
    .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-weight: bold;
        color: #ffffff;
    }

    /* Streamlit Expander custom styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 8px;
    }
    .streamlit-expanderContent {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-top: none !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        padding: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Logo & Title header
st.markdown("""
<div class="header-container">
    <div class="header-logo">⚡</div>
    <div class="header-title">StockSage</div>
</div>
""", unsafe_allow_html=True)

# Initialize agents
@st.cache_resource
def get_agents():
    return ScreeningAgent(), FundamentalAgent(), SentimentAgent(), AggregatorAgent()

screening_agent, fundamental_agent, sentiment_agent, aggregator_agent = get_agents()

# Cached data fetches at Streamlit level to avoid redundant network requests
@st.cache_data(ttl=600)
def cached_fundamental_analysis(ticker):
    return fundamental_agent.analyze_stock(ticker)

@st.cache_data(ttl=1800)
def cached_sentiment_analysis(ticker, company_name):
    return sentiment_agent.analyze_sentiment(ticker, company_name)

def process_single_ticker(t, fund_weight, sent_weight):
    """Worker function to process a single ticker, utilizing cached agent calls."""
    fund_data = cached_fundamental_analysis(t)
    company = fund_data.get('company_name', t)
    sent_data = cached_sentiment_analysis(t, company)
    
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
    return agg

SECTORS = {
    "IT & Technology":      ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"],
    "Banking & Finance":    ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
    "Automotive":           ["MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "EICHERMOT"],
    "Pharmaceuticals":      ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "BIOCON"],
    "Green Energy":         ["ADANIGREEN", "SUZLON", "TATAPOWER", "NTPC", "POWERGRID"],
    "Diversified":          ["RELIANCE", "ITC", "HINDUNILVR", "LT", "ASIANPAINT"],
}

# Layout with two columns: Sidebar panel (Left) and Results area (Right)
left_panel, right_panel = st.columns([1, 2.5], gap="large")

with left_panel:
    with st.form("parameters_form", clear_on_submit=False):
        st.subheader("Analysis Parameters")
        
        mode = st.radio(
            "Analysis Mode",
            options=["Sector Basket", "Custom"],
            horizontal=True
        )
        
        if mode == "Sector Basket":
            sector = st.selectbox("Sector", list(SECTORS.keys()))
            tickers_input = ""
        else:
            sector = ""
            tickers_input = st.text_input("Tickers (Comma separated)", placeholder="AAPL, TSLA, MSFT")
            
        num_stocks = st.slider("Max Stocks to Analyze", min_value=1, max_value=5, value=5)
        
        fund_weight = st.slider("Fundamental Weight (%)", min_value=0, max_value=100, value=60, step=10)
        sent_weight = 100 - fund_weight
        st.caption(f"Weighting: **{fund_weight}%** Fundamental / **{sent_weight}%** Sentiment")
        
        run_btn = st.form_submit_button("⚡ Run Analysis", use_container_width=True)

with right_panel:
    # State tracking for analysis results
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

    if run_btn:
        # Resolve tickers
        if mode == "Sector Basket":
            tickers = SECTORS.get(sector, [])[:num_stocks]
        else:
            tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()][:num_stocks]
            
        if not tickers:
            st.error("Please enter or select at least one valid ticker symbol.")
        else:
            # Set up loading block
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.markdown("**Status**: Fetching stock data & scraping news concurrently...")
            progress_bar.progress(15)
            
            results = []
            errors = []
            
            import concurrent.futures
            
            # Fetch tickers concurrently
            total_tickers = len(tickers)
            completed_tickers = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=total_tickers) as executor:
                # Submit workers
                future_to_ticker = {
                    executor.submit(process_single_ticker, t, fund_weight, sent_weight): t 
                    for t in tickers
                }
                
                for future in concurrent.futures.as_completed(future_to_ticker):
                    t = future_to_ticker[future]
                    completed_tickers += 1
                    pct = 10 + int((completed_tickers / total_tickers) * 90)
                    progress_bar.progress(min(pct, 100))
                    status_text.markdown(f"**Status**: Completed analysis for **{t}** ({completed_tickers}/{total_tickers})...")
                    
                    try:
                        data = future.result()
                        if 'error' in data and not data.get('overall_score'):
                            errors.append((t, data['error']))
                        else:
                            results.append(data)
                    except Exception as e:
                        errors.append((t, str(e)))
            
            for t, err in errors:
                st.warning(f"Failed to analyze {t}: {err}")
                
            results.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
            st.session_state.analysis_results = results
            
            progress_bar.progress(100)
            status_text.markdown("**Status**: Analysis complete.")
            time.sleep(0.3)
            progress_bar.empty()
            status_text.empty()

    # Render results or Hero
    results = st.session_state.analysis_results
    
    if results is None:
        # Hero view
        st.markdown("""
        <div style="margin-top: 50px;">
            <h1 class="hero-title">Invest with <br/><span class="hero-gradient">AI Precision.</span></h1>
            <p class="hero-subtitle">Experience the next generation of financial analysis. We merge deep fundamental data with real-time global news sentiment into a single, intuitive dashboard.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Results overview container
        avg_score = sum(r['overall_score'] for r in results) / len(results) if results else 0
        buys = sum(1 for r in results if r['recommendation'] == 'BUY')
        holds = sum(1 for r in results if r['recommendation'] == 'HOLD')
        sells = sum(1 for r in results if r['recommendation'] == 'SELL')
        
        st.markdown(f"""
        <div class="stat-container">
            <div class="stat-card">
                <div class="stat-value">{avg_score:.1f}</div>
                <div class="stat-label">Avg Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #4ade80;">{buys}</div>
                <div class="stat-label">Buy Signals</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #facc15;">{holds}</div>
                <div class="stat-label">Hold Signals</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #f87171;">{sells}</div>
                <div class="stat-label">Sell Signals</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Render Stock Cards
        for idx, result in enumerate(results):
            ticker = result['ticker']
            company_name = result['company_name']
            overall_score = result['overall_score']
            rec = result['recommendation']
            
            # Badge selection
            badge_class = "badge-buy" if rec == 'BUY' else "badge-hold" if rec == 'HOLD' else "badge-sell"
            
            card_title = f"{ticker} — {company_name}"
            
            with st.expander(f"💼 {card_title}", expanded=(idx == 0)):
                # Header info row inside expander
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div>
                        <span class="{badge_class}">{rec}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: #9ca3af; font-size: 13px;">OVERALL SCORE</span>
                        <h3 style="margin: 0; font-size: 24px; font-weight: bold;">{overall_score:.1f}</h3>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                exp_col1, exp_col2 = st.columns([1.1, 0.9], gap="medium")
                
                # Fetch details
                f = result.get('_fund', {})
                s = result.get('_sent', {})
                
                with exp_col1:
                    st.markdown("#### Financials & Indicators")
                    
                    price_val = f.get('current_price', 'N/A')
                    curr = f.get('currency', '')
                    price_str = f"{curr} {price_val}" if price_val != 'N/A' else 'N/A'
                    
                    pe_val = f.get('pe_ratio')
                    pe_str = f"{pe_val:.2f}" if pe_val is not None else 'N/A'
                    
                    roe_val = f.get('roe')
                    roe_str = f"{roe_val * 100:.1f}%" if roe_val is not None else 'N/A'
                    
                    de_val = f.get('debt_to_equity')
                    de_str = f"{de_val:.2f}" if de_val is not None else 'N/A'
                    
                    st.markdown(f"""
                    <div class="metric-row"><span class="metric-name">Current Price</span><span class="metric-val">{price_str}</span></div>
                    <div class="metric-row"><span class="metric-name">P/E Ratio</span><span class="metric-val">{pe_str}</span></div>
                    <div class="metric-row"><span class="metric-name">Return on Equity (ROE)</span><span class="metric-val">{roe_str}</span></div>
                    <div class="metric-row"><span class="metric-name">Debt to Equity</span><span class="metric-val">{de_str}</span></div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br/>", unsafe_allow_html=True)
                    
                    reasoning_text = result.get('reasoning', 'No reasoning analysis available.')
                    st.markdown(f"""
                    <div style="padding: 16px; border-radius: 12px; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.2); color: #bfdbfe; font-size: 14px; line-height: 1.5;">
                        ℹ️ <b>Analysis Summary:</b> {reasoning_text}
                    </div>
                    """, unsafe_allow_html=True)
                
                with exp_col2:
                    st.markdown("#### Analysis Radar")
                    
                    # Calculate values to match Radar Chart
                    pe_score = min(100, max(0, 100 - ((pe_val or 15) - 10) * 2))
                    roe_score = min(100, (roe_val or 0) * 400)
                    debt_score = min(100, 100 - (de_val or 0) * 20)
                    sentiment_score = result.get('sentiment_score', 50)
                    fundamental_score = result.get('fundamental_score', 50)
                    
                    categories = ['Valuation', 'Profitability', 'Health', 'Sentiment', 'Fundamentals']
                    values = [pe_score, roe_score, debt_score, sentiment_score, fundamental_score]
                    
                    # Create Plotly Radar Chart matching Recharts style
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values + [values[0]],
                        theta=categories + [categories[0]],
                        fill='toself',
                        fillcolor='rgba(59, 130, 246, 0.2)',
                        line=dict(color='#3b82f6', width=2),
                        name='Scores'
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            bgcolor='rgba(0,0,0,0)',
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100],
                                color='#4b5563',
                                showticklabels=False,
                                gridcolor='rgba(255,255,255,0.06)'
                            ),
                            angularaxis=dict(
                                color='#9ca3af',
                                gridcolor='rgba(255,255,255,0.06)',
                                tickfont=dict(family='Outfit', size=10)
                            )
                        ),
                        showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=35, r=35, t=35, b=35),
                        height=310
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    
                st.markdown("<hr style='margin: 15px 0; border-color: rgba(255,255,255,0.05);'/>", unsafe_allow_html=True)
                
                # Render news articles
                detailed_news = s.get('detailed_analysis', [])
                if detailed_news:
                    with st.expander("📰 Referenced News Articles"):
                        for a in detailed_news[:6]:  # show top 6 news
                            title = a.get('title', 'No title available')
                            score = a.get('sentiment_score', 0.0)
                            label = a.get('sentiment_label', 'neutral')
                            source = a.get('source', 'Unknown')
                            url = a.get('url', '#')
                            published = a.get('published_at', '')
                            
                            # Badge formatting
                            color = "#4ade80" if label == "positive" else "#f87171" if label == "negative" else "#9ca3af"
                            bg_color = "rgba(74, 222, 128, 0.1)" if label == "positive" else "rgba(248, 113, 113, 0.1)" if label == "negative" else "rgba(156, 163, 175, 0.1)"
                            border = "1px solid rgba(74, 222, 128, 0.3)" if label == "positive" else "1px solid rgba(248, 113, 113, 0.3)" if label == "negative" else "1px solid rgba(156, 163, 175, 0.3)"
                            
                            st.markdown(f"""
                            <div style="padding: 12px; margin-bottom: 10px; background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; display: flex; justify-content: space-between; align-items: center; gap: 15px;">
                                <div style="flex-grow: 1;">
                                    <a href="{url}" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600; font-size: 14px; hover: text-decoration: underline;">{title}</a>
                                    <div style="color: #9ca3af; font-size: 11px; margin-top: 4px;">Source: {source} | Date: {published}</div>
                                </div>
                                <div style="text-align: right; min-width: 120px;">
                                    <span style="color: {color}; background: {bg_color}; border: {border}; padding: 4px 8px; border-radius: 6px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;">
                                        {label} ({score:.2f})
                                    </span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No referenced news articles found for this ticker.")
