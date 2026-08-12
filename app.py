"""
================================================================================
 GLOBAL MACRO INVESTMENT ANALYZER  —  Professional Edition
================================================================================
 An institutional-grade research terminal bridging macroeconomics and capital
 markets. Compares 30 economies, screens 80 equities, and generates
 committee-ready research reports.

 Built by Vedant Patil  |  Single-file Streamlit application
 Run with:  python -m streamlit run app.py
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import requests
import datetime
import io
import math
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional dependency — degrade gracefully if missing
try:
    import yfinance as yf
    HAS_YFINANCE = True
except Exception:
    HAS_YFINANCE = False


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Global Macro Investment Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "2.0"


# ══════════════════════════════════════════════════════════════════════════════
#  THEME & CSS  —  Institutional research-terminal aesthetic
#  Palette: deep ink navy surfaces, champagne-gold brand accent, signal blue.
#  Type: Space Grotesk (display) / Inter (body) / IBM Plex Mono (data).
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    /* ── Root palette ── */
    :root {
        --bg-primary:    #0A101F;
        --bg-secondary:  #121A2E;
        --bg-tertiary:   #182238;
        --bg-elevated:   #1C2740;
        --border:        #22304E;
        --border-soft:   #1B2743;
        --text-primary:  #E9EEF7;
        --text-secondary:#96A2B8;
        --text-muted:    #5F6C85;
        --accent-blue:   #5B9CF6;
        --accent-navy:   #1E3A5F;
        --accent-gold:   #D4AF6E;
        --accent-gold-dim: rgba(212,175,110,0.35);
        --positive:      #34D399;
        --negative:      #F87171;
        --neutral:       #FBBF24;
        --font-display:  'Space Grotesk', 'Inter', sans-serif;
        --font-body:     'Inter', 'Segoe UI', sans-serif;
        --font-mono:     'IBM Plex Mono', ui-monospace, 'SF Mono', monospace;
    }

    /* ── App background ── */
    .stApp {
        background:
            radial-gradient(1100px 500px at 15% -10%, rgba(30,58,95,0.35), transparent 60%),
            radial-gradient(900px 420px at 95% 0%, rgba(212,175,110,0.05), transparent 55%),
            linear-gradient(180deg, #0A101F 0%, #0C1426 100%);
        color: var(--text-primary);
        font-family: var(--font-body);
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #0A101F; }
    ::-webkit-scrollbar-thumb { background: #22304E; border-radius: 6px; }
    ::-webkit-scrollbar-thumb:hover { background: #2C3D63; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #080D1A !important;
        border-right: 1px solid var(--border-soft);
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: var(--text-primary) !important;
        font-size: 0.95rem;
    }

    /* Sidebar radio navigation — menu-style items */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 0.3rem !important;
        display: flex;
        flex-direction: column;
    }
    section[data-testid="stSidebar"] .stRadio > div > label {
        background: transparent;
        border: 1px solid transparent;
        border-left: 3px solid transparent;
        border-radius: 5px;
        padding: 0.55rem 0.8rem !important;
        margin: 0 !important;
        transition: background 0.15s ease, border-color 0.15s ease;
        cursor: pointer;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(91,156,246,0.07);
        border-left-color: var(--accent-blue);
    }
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: rgba(212,175,110,0.09) !important;
        border-left-color: var(--accent-gold) !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label p {
        color: var(--text-primary) !important;
        font-size: 0.87rem !important;
        font-weight: 500 !important;
        font-family: var(--font-body);
    }
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Sidebar selectboxes */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #0E1526 !important;
        border-color: var(--border) !important;
    }

    /* ── Main content ── */
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1340px;
    }

    /* ── Headings ── */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4,
    div[data-testid="stMarkdownContainer"] h5,
    div[data-testid="stMarkdownContainer"] h6,
    [data-testid="stHeading"] {
        color: #FFFFFF !important;
        font-family: var(--font-display);
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    /* ── Body text ── */
    .stMarkdown p, .stMarkdown li,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: var(--text-primary) !important;
        line-height: 1.68;
        font-size: 0.94rem;
    }

    /* ── Inputs ── */
    .stSelectbox label, .stSlider label, .stTextInput label,
    .stSelectSlider label, [data-testid="stWidgetLabel"] p {
        color: var(--text-secondary) !important;
        font-weight: 600;
        font-size: 0.74rem !important;
        text-transform: uppercase;
        letter-spacing: 1.1px;
    }
    div[data-baseweb="select"] > div {
        background-color: var(--bg-secondary) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }
    .stTextInput input {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 5px;
    }

    /* ── Hero banner ── */
    .hero {
        background:
            linear-gradient(120deg, rgba(30,58,95,0.55) 0%, rgba(18,26,46,0.9) 55%),
            linear-gradient(135deg, #101B33 0%, #14203A 100%);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent-gold);
        padding: 2rem 2.3rem 1.7rem 2.3rem;
        border-radius: 8px;
        margin-bottom: 1.6rem;
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: "";
        position: absolute;
        top: 0; right: 0;
        width: 320px; height: 100%;
        background: radial-gradient(260px 160px at 85% 20%, rgba(212,175,110,0.10), transparent 70%);
        pointer-events: none;
    }
    .hero h1 {
        color: #FFFFFF !important;
        font-family: var(--font-display) !important;
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.35rem 0 !important;
        letter-spacing: -0.6px;
    }
    .hero .tagline {
        color: var(--accent-gold) !important;
        font-family: var(--font-mono);
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        margin-bottom: 0.55rem;
    }
    .hero .subtitle {
        color: #C6D2E6 !important;
        font-size: 0.98rem;
        margin: 0;
        max-width: 760px;
    }
    .hero .statusline {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 1.05rem;
    }
    .hero .status-chip {
        font-family: var(--font-mono);
        font-size: 0.66rem;
        letter-spacing: 1px;
        color: var(--text-secondary);
        background: rgba(10,16,31,0.55);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 0.28rem 0.6rem;
        text-transform: uppercase;
    }
    .hero .status-chip b { color: var(--accent-gold); font-weight: 600; }

    /* ── Metric / data cards ── */
    .data-card {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, #101828 100%);
        border: 1px solid var(--border);
        border-radius: 7px;
        padding: 1.05rem 1.25rem 0.95rem 1.25rem;
        margin-bottom: 0.8rem;
        position: relative;
        transition: border-color 0.18s ease, transform 0.18s ease;
    }
    .data-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-gold), transparent 65%);
        opacity: 0;
        transition: opacity 0.18s ease;
        border-radius: 7px 7px 0 0;
    }
    .data-card:hover { border-color: #2C3D63; }
    .data-card:hover::before { opacity: 1; }
    .data-card .label {
        color: var(--text-secondary);
        font-size: 0.66rem;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        font-weight: 600;
        margin-bottom: 0.4rem;
        font-family: var(--font-body);
    }
    .data-card .value {
        color: #FFFFFF;
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 1.12;
        font-family: var(--font-mono);
        font-variant-numeric: tabular-nums;
        letter-spacing: -0.3px;
    }
    .data-card .sub {
        color: var(--text-muted);
        font-size: 0.7rem;
        margin-top: 0.3rem;
        font-family: var(--font-mono);
        letter-spacing: 0.2px;
    }
    .data-card .delta-pos { color: var(--positive); font-family: var(--font-mono); font-size: 0.74rem; font-weight: 600; margin-top: 0.3rem; }
    .data-card .delta-neg { color: var(--negative); font-family: var(--font-mono); font-size: 0.74rem; font-weight: 600; margin-top: 0.3rem; }

    /* ── Pulse chips (market strip) ── */
    .pulse-row { display: flex; flex-wrap: wrap; gap: 0.7rem; margin: 0.2rem 0 0.6rem 0; }
    .pulse-chip {
        flex: 1 1 150px;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 7px;
        padding: 0.75rem 0.95rem;
        min-width: 148px;
    }
    .pulse-chip .p-name {
        color: var(--text-secondary);
        font-size: 0.64rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .pulse-chip .p-val {
        color: #FFFFFF;
        font-family: var(--font-mono);
        font-size: 1.02rem;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
    }
    .pulse-chip .p-chg { font-family: var(--font-mono); font-size: 0.74rem; font-weight: 600; margin-top: 0.15rem; }
    .p-up { color: var(--positive); }
    .p-dn { color: var(--negative); }

    /* ── Section heading ── */
    .section-head {
        color: #FFFFFF;
        font-family: var(--font-display);
        font-size: 1.18rem;
        font-weight: 600;
        margin: 1.9rem 0 0.7rem 0;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid var(--border);
        letter-spacing: -0.01em;
        display: flex;
        align-items: center;
    }
    .section-head::before {
        content: "";
        display: inline-block;
        width: 4px;
        height: 1.05rem;
        background: var(--accent-gold);
        border-radius: 2px;
        margin-right: 0.55rem;
    }

    /* ── Insight / commentary box ── */
    .insight {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent-blue);
        padding: 1.35rem 1.55rem;
        border-radius: 6px;
        margin: 0.8rem 0 1.2rem 0;
    }
    .insight h4 {
        color: var(--accent-blue) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.68rem !important;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        margin: 0 0 0.65rem 0 !important;
        font-weight: 600;
    }
    .insight p {
        color: var(--text-primary) !important;
        font-size: 0.91rem;
        line-height: 1.72;
        margin: 0.45rem 0 !important;
    }
    .insight strong { color: #FFFFFF !important; }

    /* ── Investor takeaway box ── */
    .takeaway {
        background: linear-gradient(135deg, rgba(212,175,110,0.09), rgba(212,175,110,0.02));
        border: 1px solid rgba(212,175,110,0.32);
        border-left: 3px solid var(--accent-gold);
        padding: 1.25rem 1.5rem;
        border-radius: 6px;
        margin: 1rem 0 1.2rem 0;
    }
    .takeaway h4 {
        color: var(--accent-gold) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.68rem !important;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        margin: 0 0 0.55rem 0 !important;
        font-weight: 600;
    }
    .takeaway p {
        color: #FFFFFF !important;
        font-size: 0.94rem !important;
        line-height: 1.66 !important;
        margin: 0 !important;
    }

    /* ── Memo box ── */
    .memo {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        padding: 2rem 2.4rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    .memo .memo-header {
        border-bottom: 2px solid var(--accent-gold);
        padding-bottom: 1rem;
        margin-bottom: 1.4rem;
    }
    .memo .memo-title {
        color: #FFFFFF;
        font-family: var(--font-display);
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.3px;
    }
    .memo .memo-meta {
        color: var(--text-secondary);
        font-family: var(--font-mono);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1.4px;
    }
    .memo h3 {
        color: var(--accent-gold) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.76rem !important;
        text-transform: uppercase;
        letter-spacing: 1.8px;
        margin: 1.4rem 0 0.5rem 0 !important;
        font-weight: 600;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.4rem;
    }
    .memo p {
        color: var(--text-primary) !important;
        font-size: 0.92rem;
        line-height: 1.78;
        margin: 0.5rem 0 !important;
    }

    /* ── Pills / badges ── */
    .badge {
        display: inline-block;
        padding: 0.22rem 0.68rem;
        border-radius: 4px;
        font-family: var(--font-mono);
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        margin-right: 0.4rem;
        text-transform: uppercase;
    }
    .badge-pos { background: rgba(52,211,153,0.12); color: var(--positive); border: 1px solid rgba(52,211,153,0.3); }
    .badge-neg { background: rgba(248,113,113,0.12); color: var(--negative); border: 1px solid rgba(248,113,113,0.3); }
    .badge-neu { background: rgba(251,191,36,0.12); color: var(--neutral); border: 1px solid rgba(251,191,36,0.3); }

    /* ── Buttons ── */
    .stButton > button, .stDownloadButton > button {
        background: var(--accent-navy) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--accent-blue) !important;
        border-radius: 5px;
        padding: 0.55rem 1.4rem;
        font-weight: 600;
        font-size: 0.86rem;
        font-family: var(--font-body);
        letter-spacing: 0.3px;
        transition: background 0.18s, border-color 0.18s, transform 0.12s;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: var(--accent-blue) !important;
        border-color: var(--accent-gold) !important;
        transform: translateY(-1px);
    }
    .stButton > button:focus-visible, .stDownloadButton > button:focus-visible {
        outline: 2px solid var(--accent-gold) !important;
        outline-offset: 2px;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid var(--border);
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 0;
        padding: 0.65rem 1.15rem;
        font-weight: 500;
        font-size: 0.88rem;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid var(--accent-gold) !important;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader, details summary {
        background: var(--bg-secondary) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--border);
        border-radius: 5px;
    }

    /* ── Markdown tables ── */
    .stMarkdown table {
        background: var(--bg-secondary);
        color: var(--text-primary) !important;
        border-collapse: collapse;
        width: 100%;
        border-radius: 6px;
        overflow: hidden;
    }
    .stMarkdown table th {
        background: var(--bg-tertiary);
        color: var(--accent-gold) !important;
        text-transform: uppercase;
        font-family: var(--font-mono);
        font-size: 0.68rem;
        letter-spacing: 1.2px;
        padding: 0.7rem 1rem;
        border-bottom: 2px solid var(--border);
        text-align: left;
    }
    .stMarkdown table td {
        color: var(--text-primary) !important;
        padding: 0.58rem 1rem;
        border-bottom: 1px solid var(--border-soft);
        font-size: 0.87rem;
        font-variant-numeric: tabular-nums;
    }
    .stMarkdown table tr:hover td { background: rgba(91,156,246,0.04); }

    /* ── Dataframe wrapper ── */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 7px;
        overflow: hidden;
    }

    /* ── Caption ── */
    .stCaption, [data-testid="stCaptionContainer"] p {
        color: var(--text-muted) !important;
        font-size: 0.73rem !important;
        font-family: var(--font-mono);
    }

    /* ── Alerts ── */
    div[data-testid="stAlert"] {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--text-primary);
    }

    /* ── Footer disclaimer ── */
    .disclaimer {
        text-align: center;
        color: var(--text-muted);
        font-family: var(--font-mono);
        font-size: 0.67rem;
        letter-spacing: 0.4px;
        padding: 2.4rem 0 1rem 0;
        border-top: 1px solid var(--border-soft);
        margin-top: 3rem;
        line-height: 1.7;
    }

    /* ── Reduced motion ── */
    @media (prefers-reduced-motion: reduce) {
        * { transition: none !important; animation: none !important; }
    }

    /* ── Hide default chrome (keep header so sidebar toggle works on Cloud) ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS  —  Countries, indicators, indices, fallbacks
# ══════════════════════════════════════════════════════════════════════════════

COUNTRIES = {
    "United States": "US",
    "China": "CN",
    "Japan": "JP",
    "Germany": "DE",
    "India": "IN",
    "United Kingdom": "GB",
    "France": "FR",
    "Italy": "IT",
    "Brazil": "BR",
    "Canada": "CA",
    "Russia": "RU",
    "South Korea": "KR",
    "Australia": "AU",
    "Spain": "ES",
    "Mexico": "MX",
    "Indonesia": "ID",
    "Saudi Arabia": "SA",
    "Turkey": "TR",
    "Switzerland": "CH",
    "Netherlands": "NL",
    "Singapore": "SG",
    "South Africa": "ZA",
    "Sweden": "SE",
    "Norway": "NO",
    "Poland": "PL",
    "Thailand": "TH",
    "Vietnam": "VN",
    "Philippines": "PH",
    "Malaysia": "MY",
    "United Arab Emirates": "AE",
}

ISO2_TO_ISO3 = {
    "US": "USA", "CN": "CHN", "JP": "JPN", "DE": "DEU", "IN": "IND",
    "GB": "GBR", "FR": "FRA", "IT": "ITA", "BR": "BRA", "CA": "CAN",
    "RU": "RUS", "KR": "KOR", "AU": "AUS", "ES": "ESP", "MX": "MEX",
    "ID": "IDN", "SA": "SAU", "TR": "TUR", "CH": "CHE", "NL": "NLD",
    "SG": "SGP", "ZA": "ZAF", "SE": "SWE", "NO": "NOR", "PL": "POL",
    "TH": "THA", "VN": "VNM", "PH": "PHL", "MY": "MYS", "AE": "ARE",
}


def flag_emoji(iso2):
    """Return the flag emoji for a 2-letter country code."""
    try:
        return "".join(chr(0x1F1E6 + ord(c) - 65) for c in iso2.upper())
    except Exception:
        return ""


# World Bank indicator codes
WB_INDICATORS = {
    "GDP": "NY.GDP.MKTP.CD",
    "GDP per Capita": "NY.GDP.PCAP.CD",
    "GDP Growth": "NY.GDP.MKTP.KD.ZG",
    "Inflation": "FP.CPI.TOTL.ZG",
    "Unemployment": "SL.UEM.TOTL.ZS",
    "Population": "SP.POP.TOTL",
    "Real Interest Rate": "FR.INR.RINR",
    "Lending Rate": "FR.INR.LEND",
    "Government Debt to GDP": "GC.DOD.TOTL.GD.ZS",
    "Current Account": "BN.CAB.XOKA.GD.ZS",
    "FDI Inflows": "BX.KLT.DINV.WD.GD.ZS",
    "Agriculture % GDP": "NV.AGR.TOTL.ZS",
    "Industry % GDP": "NV.IND.TOTL.ZS",
    "Services % GDP": "NV.SRV.TOTL.ZS",
    "Household Consumption % GDP": "NE.CON.PRVT.ZS",
    "Government Spending % GDP": "NE.CON.GOVT.ZS",
    "Investment % GDP": "NE.GDI.TOTL.ZS",
    "Exports % GDP": "NE.EXP.GNFS.ZS",
    "Imports % GDP": "NE.IMP.GNFS.ZS",
}

# Subset used for the Global Rankings panel (one batch call per indicator)
RANK_INDICATORS = {
    "GDP": "NY.GDP.MKTP.CD",
    "GDP per Capita": "NY.GDP.PCAP.CD",
    "GDP Growth": "NY.GDP.MKTP.KD.ZG",
    "Inflation": "FP.CPI.TOTL.ZG",
    "Unemployment": "SL.UEM.TOTL.ZS",
    "Government Debt to GDP": "GC.DOD.TOTL.GD.ZS",
    "Current Account": "BN.CAB.XOKA.GD.ZS",
}

# Country -> primary equity index ticker (Yahoo Finance)
EQUITY_INDICES = {
    "US": ("^GSPC",    "S&P 500"),
    "CN": ("000001.SS", "Shanghai Composite"),
    "JP": ("^N225",    "Nikkei 225"),
    "DE": ("^GDAXI",   "DAX"),
    "IN": ("^NSEI",    "Nifty 50"),
    "GB": ("^FTSE",    "FTSE 100"),
    "FR": ("^FCHI",    "CAC 40"),
    "IT": ("FTSEMIB.MI", "FTSE MIB"),
    "BR": ("^BVSP",    "Bovespa"),
    "CA": ("^GSPTSE",  "TSX Composite"),
    "KR": ("^KS11",    "KOSPI"),
    "AU": ("^AXJO",    "ASX 200"),
    "ES": ("^IBEX",    "IBEX 35"),
    "MX": ("^MXX",     "IPC Mexico"),
    "ID": ("^JKSE",    "Jakarta Composite"),
    "TR": ("XU100.IS", "BIST 100"),
    "CH": ("^SSMI",    "Swiss Market Index"),
    "NL": ("^AEX",     "AEX"),
    "SG": ("^STI",     "Straits Times"),
    "ZA": ("^J203.JO", "FTSE/JSE Top 40"),
    "SE": ("^OMX",     "OMX Stockholm 30"),
    "NO": ("^OSEAX",   "Oslo All-Share"),
    "PL": ("^WIG20",   "WIG20"),
    "TH": ("^SET.BK",  "SET Index"),
    "PH": ("PSEI.PS",  "PSEi"),
    "MY": ("^KLSE",    "FTSE Bursa Malaysia"),
}

# Global market pulse tickers (overview strip)
PULSE_TICKERS = {
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq",
    "^DJI": "Dow Jones",
    "^FTSE": "FTSE 100",
    "^N225": "Nikkei 225",
    "^NSEI": "NIFTY 50",
}

# Currency codes for FX (vs USD)
COUNTRY_CURRENCIES = {
    "US": "USD", "CN": "CNY", "JP": "JPY", "DE": "EUR", "IN": "INR",
    "GB": "GBP", "FR": "EUR", "IT": "EUR", "BR": "BRL", "CA": "CAD",
    "RU": "RUB", "KR": "KRW", "AU": "AUD", "ES": "EUR", "MX": "MXN",
    "ID": "IDR", "SA": "SAR", "TR": "TRY", "CH": "CHF", "NL": "EUR",
    "SG": "SGD", "ZA": "ZAR", "SE": "SEK", "NO": "NOK", "PL": "PLN",
    "TH": "THB", "VN": "VND", "PH": "PHP", "MY": "MYR", "AE": "AED",
}

# Fallback values for the 6 most-used countries (used if the WB API fails)
FALLBACK_DATA = {
    "US": {"GDP": 27.36e12, "GDP per Capita": 81630, "GDP Growth": 2.5,
           "Inflation": 4.1, "Unemployment": 3.6, "Population": 334.9e6,
           "Real Interest Rate": 3.2, "Lending Rate": 8.5,
           "Government Debt to GDP": 121.0, "Current Account": -3.0,
           "FDI Inflows": 1.5, "Agriculture % GDP": 1.0, "Industry % GDP": 18.4,
           "Services % GDP": 80.6, "Household Consumption % GDP": 68.2,
           "Government Spending % GDP": 14.4, "Investment % GDP": 21.3,
           "Exports % GDP": 11.6, "Imports % GDP": 15.5},
    "CN": {"GDP": 17.79e12, "GDP per Capita": 12614, "GDP Growth": 5.2,
           "Inflation": 0.2, "Unemployment": 5.2, "Population": 1410.0e6,
           "Real Interest Rate": 3.0, "Lending Rate": 4.4,
           "Government Debt to GDP": 83.0, "Current Account": 1.4,
           "FDI Inflows": 0.9, "Agriculture % GDP": 7.1, "Industry % GDP": 38.3,
           "Services % GDP": 54.6, "Household Consumption % GDP": 38.5,
           "Government Spending % GDP": 16.5, "Investment % GDP": 42.9,
           "Exports % GDP": 19.7, "Imports % GDP": 17.6},
    "JP": {"GDP": 4.21e12, "GDP per Capita": 33834, "GDP Growth": 1.9,
           "Inflation": 3.3, "Unemployment": 2.6, "Population": 124.5e6,
           "Real Interest Rate": -1.5, "Lending Rate": 1.4,
           "Government Debt to GDP": 251.0, "Current Account": 1.8,
           "FDI Inflows": 0.6, "Agriculture % GDP": 1.0, "Industry % GDP": 28.5,
           "Services % GDP": 70.5, "Household Consumption % GDP": 53.6,
           "Government Spending % GDP": 20.8, "Investment % GDP": 25.5,
           "Exports % GDP": 21.5, "Imports % GDP": 21.4},
    "DE": {"GDP": 4.46e12, "GDP per Capita": 52746, "GDP Growth": -0.3,
           "Inflation": 5.9, "Unemployment": 3.0, "Population": 84.5e6,
           "Real Interest Rate": -2.0, "Lending Rate": 4.5,
           "Government Debt to GDP": 64.0, "Current Account": 5.7,
           "FDI Inflows": 0.7, "Agriculture % GDP": 0.9, "Industry % GDP": 26.6,
           "Services % GDP": 72.5, "Household Consumption % GDP": 51.5,
           "Government Spending % GDP": 21.0, "Investment % GDP": 21.8,
           "Exports % GDP": 47.0, "Imports % GDP": 41.3},
    "IN": {"GDP": 3.55e12, "GDP per Capita": 2484, "GDP Growth": 7.6,
           "Inflation": 5.4, "Unemployment": 7.7, "Population": 1428.6e6,
           "Real Interest Rate": 3.5, "Lending Rate": 9.4,
           "Government Debt to GDP": 81.0, "Current Account": -1.2,
           "FDI Inflows": 1.5, "Agriculture % GDP": 16.8, "Industry % GDP": 25.9,
           "Services % GDP": 57.3, "Household Consumption % GDP": 60.5,
           "Government Spending % GDP": 10.3, "Investment % GDP": 31.7,
           "Exports % GDP": 21.5, "Imports % GDP": 24.0},
    "GB": {"GDP": 3.34e12, "GDP per Capita": 49464, "GDP Growth": 0.1,
           "Inflation": 7.3, "Unemployment": 4.0, "Population": 67.6e6,
           "Real Interest Rate": -1.0, "Lending Rate": 5.5,
           "Government Debt to GDP": 101.0, "Current Account": -3.3,
           "FDI Inflows": 0.5, "Agriculture % GDP": 0.7, "Industry % GDP": 17.4,
           "Services % GDP": 81.9, "Household Consumption % GDP": 63.0,
           "Government Spending % GDP": 20.5, "Investment % GDP": 17.8,
           "Exports % GDP": 31.1, "Imports % GDP": 32.4},
}

DEFAULT_FALLBACK = {
    "GDP": 500e9, "GDP per Capita": 12000, "GDP Growth": 3.0,
    "Inflation": 4.0, "Unemployment": 6.0, "Population": 50e6,
    "Real Interest Rate": 2.0, "Lending Rate": 6.5,
    "Government Debt to GDP": 60.0, "Current Account": -1.0,
    "FDI Inflows": 1.5, "Agriculture % GDP": 8.0, "Industry % GDP": 30.0,
    "Services % GDP": 62.0, "Household Consumption % GDP": 60.0,
    "Government Spending % GDP": 15.0, "Investment % GDP": 24.0,
    "Exports % GDP": 28.0, "Imports % GDP": 26.0,
}

# Equity universes
DOW30 = ["AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "GS",
         "HD", "HON", "IBM", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MSFT",
         "NKE", "NVDA", "PG", "SHW", "TRV", "UNH", "V", "VZ", "WMT", "AMZN"]

NIFTY50 = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
           "INFY.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS",
           "BAJFINANCE.NS", "HCLTECH.NS", "KOTAKBANK.NS", "MARUTI.NS", "SUNPHARMA.NS",
           "AXISBANK.NS", "M&M.NS", "ULTRACEMCO.NS", "TITAN.NS", "NTPC.NS", "ONGC.NS",
           "ADANIENT.NS", "ADANIPORTS.NS", "POWERGRID.NS", "BAJAJFINSV.NS",
           "TATAMOTORS.NS", "COALINDIA.NS", "ASIANPAINT.NS", "WIPRO.NS", "BAJAJ-AUTO.NS",
           "NESTLEIND.NS", "TRENT.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "GRASIM.NS",
           "HINDALCO.NS", "TECHM.NS", "CIPLA.NS", "DRREDDY.NS", "BRITANNIA.NS",
           "EICHERMOT.NS", "APOLLOHOSP.NS", "SHRIRAMFIN.NS", "HEROMOTOCO.NS",
           "INDUSINDBK.NS", "BPCL.NS", "TATACONSUM.NS", "DIVISLAB.NS", "SBILIFE.NS"]


def get_fallback(code, metric):
    """Return a fallback value, or the generic default if not in the lookup."""
    if code in FALLBACK_DATA and metric in FALLBACK_DATA[code]:
        return FALLBACK_DATA[code][metric]
    return DEFAULT_FALLBACK.get(metric)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA LAYER  —  World Bank + Yahoo Finance, parallelized and cached
# ══════════════════════════════════════════════════════════════════════════════

WB_TIMEOUT = 15


def _wb_fetch_series(country_code, indicator, start_year=1975, end_year=2025):
    """Raw World Bank series fetch (no Streamlit calls — safe for threads).
    Returns (years, values) sorted ascending, or ([], []) on failure."""
    url = (
        f"https://api.worldbank.org/v2/country/{country_code}"
        f"/indicator/{indicator}"
        f"?date={start_year}:{end_year}&format=json&per_page=500"
    )
    try:
        resp = requests.get(url, timeout=WB_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not data or len(data) < 2 or data[1] is None:
            return [], []
        pairs = []
        for entry in data[1]:
            if entry.get("value") is not None:
                pairs.append((int(entry["date"]), float(entry["value"])))
        if not pairs:
            return [], []
        pairs.sort(key=lambda p: p[0])
        return [p[0] for p in pairs], [p[1] for p in pairs]
    except Exception:
        return [], []


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def fetch_country_macro(country_code):
    """Full macro snapshot for one country, fetched in parallel.

    Returns (data, ts, latest_year):
      data        {indicator: latest value or fallback}
      ts          {indicator: (years, values)}
      latest_year {indicator: year of latest datapoint or None}
    """
    data, ts, latest_year = {}, {}, {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {
            ex.submit(_wb_fetch_series, country_code, code): name
            for name, code in WB_INDICATORS.items()
        }
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                yrs, vls = fut.result()
            except Exception:
                yrs, vls = [], []
            ts[name] = (yrs, vls)
            if yrs:
                data[name] = vls[-1]
                latest_year[name] = yrs[-1]
            else:
                data[name] = get_fallback(country_code, name)
                latest_year[name] = None
    return data, ts, latest_year


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def fetch_global_panel():
    """Latest key indicators for ALL tracked countries via batched WB calls
    (one request per indicator, all 30 countries at once).

    Returns a DataFrame indexed by ISO2 with columns for each RANK_INDICATOR
    plus 'Latest Year', or an empty DataFrame on total failure."""
    codes = ";".join(COUNTRIES.values())
    iso3_to_iso2 = {v: k for k, v in ISO2_TO_ISO3.items()}

    def _batch(indicator):
        url = (
            f"https://api.worldbank.org/v2/country/{codes}"
            f"/indicator/{indicator}"
            f"?date=2018:2025&format=json&per_page=2000"
        )
        out = {}
        try:
            resp = requests.get(url, timeout=WB_TIMEOUT + 10)
            resp.raise_for_status()
            data = resp.json()
            if not data or len(data) < 2 or data[1] is None:
                return out
            for entry in data[1]:
                if entry.get("value") is None:
                    continue
                iso3 = entry.get("countryiso3code") or ""
                iso2 = iso3_to_iso2.get(iso3)
                if not iso2:
                    continue
                yr = int(entry["date"])
                prev = out.get(iso2)
                if prev is None or yr > prev[0]:
                    out[iso2] = (yr, float(entry["value"]))
        except Exception:
            return {}
        return out

    results = {}
    with ThreadPoolExecutor(max_workers=7) as ex:
        futures = {ex.submit(_batch, code): name for name, code in RANK_INDICATORS.items()}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                results[name] = fut.result()
            except Exception:
                results[name] = {}

    if not any(results.get(n) for n in RANK_INDICATORS):
        return pd.DataFrame()

    rows = []
    for cname, iso2 in COUNTRIES.items():
        row = {"Country": cname, "ISO2": iso2, "ISO3": ISO2_TO_ISO3.get(iso2, "")}
        years_seen = []
        for name in RANK_INDICATORS:
            hit = results.get(name, {}).get(iso2)
            if hit:
                row[name] = hit[1]
                years_seen.append(hit[0])
            else:
                row[name] = None
        row["Latest Year"] = max(years_seen) if years_seen else None
        rows.append(row)
    return pd.DataFrame(rows)


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_equity_index(ticker, period="5y"):
    """Equity index history via yfinance. Returns (dates, closes) or ([], [])."""
    if not HAS_YFINANCE:
        return [], []
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if hist is None or hist.empty:
            return [], []
        dates = [d.strftime("%Y-%m-%d") for d in hist.index]
        closes = [float(c) for c in hist["Close"].tolist()]
        return dates, closes
    except Exception:
        return [], []


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_fx_rate(currency_code, period="2y"):
    """FX rate vs USD via yfinance (e.g. EURUSD=X). Returns (dates, closes)."""
    if not HAS_YFINANCE or currency_code == "USD":
        return [], []
    ticker = f"{currency_code}USD=X"
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if hist is None or hist.empty:
            return [], []
        dates = [d.strftime("%Y-%m-%d") for d in hist.index]
        closes = [float(c) for c in hist["Close"].tolist()]
        return dates, closes
    except Exception:
        return [], []


@st.cache_data(ttl=1200, show_spinner=False)
def fetch_market_pulse():
    """Latest level + 1-day change for the global index strip.
    Returns list of (name, last, pct_change) — empty list on failure."""
    if not HAS_YFINANCE:
        return []
    out = []
    try:
        px = yf.download(
            list(PULSE_TICKERS.keys()), period="7d", interval="1d",
            group_by="ticker", auto_adjust=True, threads=True, progress=False,
        )
        if px is None or px.empty:
            return []
        for tk, name in PULSE_TICKERS.items():
            try:
                if isinstance(px.columns, pd.MultiIndex):
                    closes = px[tk]["Close"].dropna()
                else:
                    closes = px["Close"].dropna()
                if len(closes) >= 2:
                    last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
                    out.append((name, last, (last / prev - 1) * 100 if prev else 0.0))
            except Exception:
                continue
    except Exception:
        return []
    return out


def _safe(v, default=None):
    if v is None:
        return default
    try:
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return default
    except Exception:
        pass
    return v


def _clean_name(ticker, info):
    n = info.get("shortName") or info.get("longName")
    if n:
        return str(n)
    return ticker.replace(".NS", "").replace("-", " ").title()


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_stock_data(tickers, market_name):
    """Refreshed stock data for a ticker universe.

    Price history arrives in ONE batched yf.download call; fundamentals are
    fetched in parallel threads. Beta falls back to a realized beta computed
    against the equal-weight universe when Yahoo does not supply one.

    Returns (rows, failed)."""
    if not HAS_YFINANCE:
        return [], []
    tickers = list(tickers)
    frames = {}

    # ── 1. Batched price download ──
    try:
        px = yf.download(
            tickers, period="1y", interval="1d",
            group_by="ticker", auto_adjust=True, threads=True, progress=False,
        )
    except Exception:
        px = None

    if px is not None and not px.empty:
        if isinstance(px.columns, pd.MultiIndex):
            for tk in tickers:
                try:
                    sub = px[tk].dropna(subset=["Close"])
                    if not sub.empty:
                        frames[tk] = sub
                except Exception:
                    continue
        elif len(tickers) == 1:
            sub = px.dropna(subset=["Close"])
            if not sub.empty:
                frames[tickers[0]] = sub

    # ── 2. Per-ticker fallback for anything the batch missed ──
    missing = [tk for tk in tickers if tk not in frames]
    if missing:
        def _hist(tk):
            try:
                h = yf.Ticker(tk).history(period="1y")
                if h is not None and not h.empty:
                    return tk, h.dropna(subset=["Close"])
            except Exception:
                pass
            return tk, None
        with ThreadPoolExecutor(max_workers=8) as ex:
            for tk, h in ex.map(_hist, missing):
                if h is not None and not h.empty:
                    frames[tk] = h

    failed = [tk for tk in tickers if tk not in frames]
    if not frames:
        return [], failed

    # ── 3. Fundamentals in parallel ──
    def _info(tk):
        try:
            return tk, (yf.Ticker(tk).info or {})
        except Exception:
            return tk, {}
    infos = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for tk, inf in ex.map(_info, list(frames.keys())):
            infos[tk] = inf

    # ── 4. Realized beta vs equal-weight universe (fallback) ──
    closes_df = pd.DataFrame({tk: f["Close"] for tk, f in frames.items()}).sort_index()
    rets_df = closes_df.pct_change().dropna(how="all")
    mkt = rets_df.mean(axis=1)
    var_m = float(mkt.var()) if len(mkt) > 20 else None

    rows = []
    for tk, hist in frames.items():
        try:
            info = infos.get(tk, {})
            closes = hist["Close"].tolist()
            volumes = hist["Volume"].tolist() if "Volume" in hist else []
            cur = float(closes[-1])
            prev = float(closes[-2]) if len(closes) > 1 else cur
            daily_pct = (cur / prev - 1) * 100 if prev else 0.0

            def ret_n(n):
                if len(closes) <= n:
                    return None
                base = closes[-(n + 1)]
                return (cur / base - 1) * 100 if base else None

            ytd_ret = None
            try:
                yr = datetime.date.today().year
                ytd_rows = hist[hist.index.year == yr]
                if not ytd_rows.empty:
                    base = float(ytd_rows["Close"].iloc[0])
                    if base:
                        ytd_ret = (cur / base - 1) * 100
            except Exception:
                pass

            hi52 = float(max(closes))
            lo52 = float(min(closes))
            dist_hi = (cur / hi52 - 1) * 100 if hi52 else None
            avg_vol = float(np.mean(volumes)) if volumes else None

            try:
                srets = rets_df[tk].dropna()
                vol_ann = float(srets.std() * np.sqrt(252) * 100) if len(srets) > 5 else None
            except Exception:
                srets, vol_ann = None, None

            beta = _safe(info.get("beta"))
            if beta is None and var_m and srets is not None and len(srets) > 20:
                try:
                    beta = float(srets.cov(mkt.reindex(srets.index)) / var_m)
                except Exception:
                    beta = None

            # yfinance >=0.2.50 reports dividendYield in percent; normalize legacy fractions
            dy = _safe(info.get("dividendYield"))
            if dy is not None and dy > 25:
                dy = dy / 100.0

            rows.append({
                "Ticker": tk,
                "Name": _clean_name(tk, info),
                "Sector": info.get("sector", "—"),
                "Price": cur,
                "Daily %": daily_pct,
                "5D %": ret_n(5),
                "1M %": ret_n(21),
                "3M %": ret_n(63),
                "YTD %": ytd_ret,
                "52W High": hi52,
                "52W Low": lo52,
                "From High %": dist_hi,
                "Volume": float(volumes[-1]) if volumes else None,
                "Avg Vol": avg_vol,
                "Volatility %": vol_ann,
                "Market Cap": _safe(info.get("marketCap")),
                "P/E": _safe(info.get("trailingPE")),
                "Fwd P/E": _safe(info.get("forwardPE")),
                "Div Yield %": dy,
                "Beta": beta,
                "Rec": info.get("recommendationKey", "—"),
            })
        except Exception:
            failed.append(tk)
            continue
    return rows, failed


# ══════════════════════════════════════════════════════════════════════════════
#  FORMATTING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def fmt_money(val):
    if val is None:
        return "N/A"
    if val >= 1e12:
        return f"${val/1e12:,.2f}T"
    if val >= 1e9:
        return f"${val/1e9:,.1f}B"
    if val >= 1e6:
        return f"${val/1e6:,.0f}M"
    return f"${val:,.0f}"


def fmt_dollar(val):
    if val is None:
        return "N/A"
    return f"${val:,.0f}"


def fmt_pct_signed(val):
    if val is None:
        return "N/A"
    return f"{val:+.1f}%"


def fmt_pct_simple(val):
    if val is None:
        return "N/A"
    return f"{val:.1f}%"


def fmt_pop(val):
    if val is None:
        return "N/A"
    if val >= 1e9:
        return f"{val/1e9:,.2f}B"
    if val >= 1e6:
        return f"{val/1e6:,.1f}M"
    return f"{val:,.0f}"


def fmt_num(v, suffix="", dec=2):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return "N/A"
    return f"{v:,.{dec}f}{suffix}"


def fmt_mcap(v, sym="$"):
    if v is None:
        return "N/A"
    if v >= 1e12:
        return f"{sym}{v/1e12:.2f}T"
    if v >= 1e9:
        return f"{sym}{v/1e9:.1f}B"
    return f"{sym}{v/1e6:.0f}M"


def fmt_volume(v):
    if v is None:
        return "N/A"
    if v >= 1e9:
        return f"{v/1e9:.2f}B"
    if v >= 1e6:
        return f"{v/1e6:.1f}M"
    return f"{v/1e3:.0f}K"


# ══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS  —  render primitives + version-safe Streamlit wrappers
# ══════════════════════════════════════════════════════════════════════════════

PLOT_CONFIG = {"displayModeBar": False}


def show_chart(fig):
    """Render a Plotly chart full-width across Streamlit versions."""
    try:
        st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)


def show_df(df, **kwargs):
    """Render a dataframe full-width across Streamlit versions."""
    try:
        st.dataframe(df, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kwargs)


def hero(tagline, title, subtitle, status=True):
    status_html = ""
    if status:
        today = datetime.date.today().strftime("%d %b %Y").upper()
        status_html = (
            '<div class="statusline">'
            f'<span class="status-chip">DATA · <b>WORLD BANK</b></span>'
            f'<span class="status-chip">MARKETS · <b>YAHOO FINANCE</b></span>'
            f'<span class="status-chip">SESSION · <b>{today}</b></span>'
            f'<span class="status-chip">BUILD · <b>V{APP_VERSION}</b></span>'
            '</div>'
        )
    st.markdown(
        f'<div class="hero">'
        f'<div class="tagline">{tagline}</div>'
        f'<h1>{title}</h1>'
        f'<p class="subtitle">{subtitle}</p>'
        f'{status_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def data_card(label, value, sub="", delta=None, delta_positive=True):
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    delta_html = ""
    if delta:
        cls = "delta-pos" if delta_positive else "delta-neg"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="{cls}">{arrow} {delta}</div>'
    st.markdown(
        f'<div class="data-card">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'{delta_html}{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_head(text):
    st.markdown(f'<div class="section-head">{text}</div>', unsafe_allow_html=True)


def insight_box(title, body_html):
    st.markdown(
        f'<div class="insight"><h4>{title}</h4>{body_html}</div>',
        unsafe_allow_html=True,
    )


def takeaway_box(text):
    st.markdown(
        f'<div class="takeaway"><h4>Investor Takeaway</h4><p>{text}</p></div>',
        unsafe_allow_html=True,
    )


def page_disclaimer():
    st.markdown(
        '<div class="disclaimer">'
        'GLOBAL MACRO INVESTMENT ANALYZER &nbsp;·&nbsp; Data: World Bank Open Data, Yahoo Finance '
        '&nbsp;·&nbsp; For educational and research use only — not investment advice.'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  CHART BUILDERS  —  Plotly on the institutional dark theme
# ══════════════════════════════════════════════════════════════════════════════

CHART_BG = "#121A2E"
CHART_GRID = "#22304E"
CHART_TEXT = "#C6D2E6"
COLOR_A = "#5B9CF6"
COLOR_B = "#D4AF6E"
COLOR_POS = "#34D399"
COLOR_NEG = "#F87171"
FONT_STACK = "Inter, 'Segoe UI', sans-serif"
MONO_STACK = "'IBM Plex Mono', ui-monospace, monospace"


def base_layout(title="", height=380):
    return dict(
        title=dict(text=title, font=dict(size=14, color="#FFFFFF", family=FONT_STACK),
                   x=0.01, xanchor="left"),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=CHART_TEXT, family=FONT_STACK, size=11.5),
        height=height,
        margin=dict(l=58, r=26, t=52, b=46),
        xaxis=dict(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID,
                   linecolor=CHART_GRID, tickfont=dict(family=MONO_STACK, size=10.5)),
        yaxis=dict(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID,
                   linecolor=CHART_GRID, tickfont=dict(family=MONO_STACK, size=10.5)),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FFFFFF", size=11),
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#182238", bordercolor="#2C3D63",
                        font=dict(family=MONO_STACK, size=11, color="#E9EEF7")),
    )


def line_chart(years_a, vals_a, years_b, vals_b, name_a, name_b, title, y_fmt=",.0f"):
    fig = go.Figure()
    if years_a:
        fig.add_trace(go.Scatter(
            x=years_a, y=vals_a, mode="lines", name=name_a,
            line=dict(color=COLOR_A, width=2.4),
        ))
    if years_b:
        fig.add_trace(go.Scatter(
            x=years_b, y=vals_b, mode="lines", name=name_b,
            line=dict(color=COLOR_B, width=2.4),
        ))
    layout = base_layout(title)
    layout["yaxis"]["tickformat"] = y_fmt
    fig.update_layout(**layout)
    return fig


def grouped_bar(labels, vals_a, vals_b, name_a, name_b, title, y_suffix="%"):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=vals_a, name=name_a, marker_color=COLOR_A,
        marker_line=dict(width=0),
        text=[f"{v:.1f}{y_suffix}" for v in vals_a],
        textposition="outside", textfont=dict(color="#FFFFFF", size=10.5, family=MONO_STACK),
    ))
    fig.add_trace(go.Bar(
        x=labels, y=vals_b, name=name_b, marker_color=COLOR_B,
        marker_line=dict(width=0),
        text=[f"{v:.1f}{y_suffix}" for v in vals_b],
        textposition="outside", textfont=dict(color="#FFFFFF", size=10.5, family=MONO_STACK),
    ))
    layout = base_layout(title, height=420)
    layout["barmode"] = "group"
    layout["bargap"] = 0.28
    fig.update_layout(**layout)
    return fig


def donut_chart(labels, values, title):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.58,
        marker=dict(colors=["#5B9CF6", "#D4AF6E", "#5F6C85", "#8A99B5"],
                    line=dict(color="#121A2E", width=2)),
        textinfo="label+percent",
        textfont=dict(color="#FFFFFF", size=11, family=FONT_STACK),
    ))
    layout = base_layout(title, height=340)
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def normalized_index_chart(dates_a, vals_a, dates_b, vals_b, name_a, name_b, title):
    """Rebase both series to 100 at start for a comparable performance view."""
    fig = go.Figure()
    if vals_a:
        base = vals_a[0]
        norm = [v / base * 100 for v in vals_a]
        fig.add_trace(go.Scatter(
            x=dates_a, y=norm, mode="lines", name=name_a,
            line=dict(color=COLOR_A, width=2),
        ))
    if vals_b:
        base = vals_b[0]
        norm = [v / base * 100 for v in vals_b]
        fig.add_trace(go.Scatter(
            x=dates_b, y=norm, mode="lines", name=name_b,
            line=dict(color=COLOR_B, width=2),
        ))
    layout = base_layout(title, height=400)
    layout["yaxis"]["title"] = dict(text="Indexed (Start = 100)",
                                    font=dict(size=11, color=CHART_TEXT))
    fig.add_hline(y=100, line_dash="dot", line_color="#3A4A70", line_width=1)
    fig.update_layout(**layout)
    return fig


def drawdown_chart(dates_a, vals_a, dates_b, vals_b, name_a, name_b):
    """Peak-to-trough drawdown series for both indices."""
    def dd(vals):
        peak, out = -float("inf"), []
        for v in vals:
            peak = max(peak, v)
            out.append((v / peak - 1) * 100 if peak else 0)
        return out

    fig = go.Figure()
    if vals_a:
        fig.add_trace(go.Scatter(
            x=dates_a, y=dd(vals_a), mode="lines", name=name_a,
            line=dict(color=COLOR_A, width=1.8), fill="tozeroy",
            fillcolor="rgba(91,156,246,0.14)",
        ))
    if vals_b:
        fig.add_trace(go.Scatter(
            x=dates_b, y=dd(vals_b), mode="lines", name=name_b,
            line=dict(color=COLOR_B, width=1.8), fill="tozeroy",
            fillcolor="rgba(212,175,110,0.12)",
        ))
    layout = base_layout("Drawdown from Peak (%)", height=340)
    fig.update_layout(**layout)
    return fig


def radar_compare(dims, vals_a, vals_b, name_a, name_b, title="Macro Profile Radar"):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_a + vals_a[:1], theta=dims + dims[:1], name=name_a,
        line=dict(color=COLOR_A, width=2), fill="toself",
        fillcolor="rgba(91,156,246,0.16)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=vals_b + vals_b[:1], theta=dims + dims[:1], name=name_b,
        line=dict(color=COLOR_B, width=2), fill="toself",
        fillcolor="rgba(212,175,110,0.14)",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#FFFFFF", family=FONT_STACK),
                   x=0.01, xanchor="left"),
        paper_bgcolor=CHART_BG,
        font=dict(color=CHART_TEXT, family=FONT_STACK, size=11),
        height=430,
        margin=dict(l=60, r=60, t=60, b=40),
        polar=dict(
            bgcolor="#0E1526",
            radialaxis=dict(range=[0, 100], gridcolor=CHART_GRID, linecolor=CHART_GRID,
                            tickfont=dict(family=MONO_STACK, size=9, color="#5F6C85")),
            angularaxis=dict(gridcolor=CHART_GRID, linecolor=CHART_GRID,
                             tickfont=dict(size=11, color="#C6D2E6")),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5,
                    bgcolor="rgba(0,0,0,0)", font=dict(color="#FFFFFF", size=11)),
        showlegend=True,
    )
    return fig


def gauge_chart(score, label, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number=dict(font=dict(family=MONO_STACK, size=40, color="#FFFFFF"), suffix=""),
        title=dict(text=label, font=dict(size=13, color="#96A2B8", family=FONT_STACK)),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#5F6C85",
                      tickfont=dict(family=MONO_STACK, size=9, color="#5F6C85")),
            bar=dict(color=color, thickness=0.28),
            bgcolor="#0E1526",
            borderwidth=1,
            bordercolor="#22304E",
            steps=[
                dict(range=[0, 40], color="rgba(248,113,113,0.13)"),
                dict(range=[40, 55], color="rgba(251,191,36,0.11)"),
                dict(range=[55, 72], color="rgba(212,175,110,0.10)"),
                dict(range=[72, 100], color="rgba(52,211,153,0.11)"),
            ],
            threshold=dict(line=dict(color="#FFFFFF", width=2), thickness=0.75, value=score),
        ),
    ))
    fig.update_layout(paper_bgcolor=CHART_BG, height=260,
                      margin=dict(l=30, r=30, t=48, b=12),
                      font=dict(family=FONT_STACK, color=CHART_TEXT))
    return fig


def choropleth_scores(df):
    """World map colored by composite macro score."""
    fig = go.Figure(go.Choropleth(
        locations=df["ISO3"],
        z=df["Score"],
        text=df["Country"],
        colorscale=[[0.0, "#7F1D1D"], [0.35, "#B45309"],
                    [0.6, "#1E3A5F"], [0.8, "#5B9CF6"], [1.0, "#34D399"]],
        zmin=20, zmax=90,
        marker_line_color="#0A101F",
        marker_line_width=0.6,
        colorbar=dict(
            title=dict(text="Score", font=dict(color=CHART_TEXT, size=11)),
            tickfont=dict(color=CHART_TEXT, family=MONO_STACK, size=10),
            thickness=12, len=0.7, outlinewidth=0,
        ),
        hovertemplate="<b>%{text}</b><br>Score: %{z}/100<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=CHART_BG,
        geo=dict(
            bgcolor="#0E1526",
            showframe=False,
            showcoastlines=False,
            landcolor="#182238",
            lakecolor="#0E1526",
            projection_type="natural earth",
        ),
        height=470,
        margin=dict(l=8, r=8, t=42, b=8),
        title=dict(text="Composite Macro Score — Global Map",
                   font=dict(size=14, color="#FFFFFF", family=FONT_STACK),
                   x=0.01, xanchor="left"),
        font=dict(family=FONT_STACK, color=CHART_TEXT),
    )
    return fig


def scatter_income_growth(df):
    """Classic development scatter: income (log) vs growth, sized by GDP."""
    d = df.dropna(subset=["GDP per Capita", "GDP Growth"]).copy()
    if d.empty:
        return None
    sizes = d["GDP"].fillna(d["GDP"].median() or 1.0)
    sizes = 12 + 34 * (sizes / sizes.max()) ** 0.5
    fig = go.Figure(go.Scatter(
        x=d["GDP per Capita"], y=d["GDP Growth"],
        mode="markers+text",
        text=d["ISO2"],
        textposition="top center",
        textfont=dict(family=MONO_STACK, size=9.5, color="#96A2B8"),
        marker=dict(
            size=sizes,
            color=d["Score"],
            colorscale=[[0.0, "#F87171"], [0.5, "#D4AF6E"], [1.0, "#34D399"]],
            cmin=25, cmax=85,
            line=dict(color="#0A101F", width=1),
            opacity=0.92,
        ),
        customdata=np.stack([d["Country"], d["Score"]], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>GDP/capita: $%{x:,.0f}"
                      "<br>Growth: %{y:.1f}%<br>Score: %{customdata[1]}<extra></extra>",
    ))
    layout = base_layout("Income vs Growth — bubble size = GDP, color = macro score", height=460)
    layout["xaxis"]["type"] = "log"
    layout["xaxis"]["title"] = dict(text="GDP per Capita (US$, log scale)",
                                    font=dict(size=11, color=CHART_TEXT))
    layout["yaxis"]["title"] = dict(text="Real GDP Growth (%)",
                                    font=dict(size=11, color=CHART_TEXT))
    layout["hovermode"] = "closest"
    fig.update_layout(**layout)
    return fig


def treemap_market(df, currency_symbol, title):
    """Sector -> stock treemap sized by market cap, colored by daily move."""
    d = df.dropna(subset=["Daily %"]).copy()
    if d.empty:
        return None
    d["Sector"] = d["Sector"].fillna("Other").replace({"—": "Other", "": "Other"})
    med_cap = d["Market Cap"].dropna().median()
    d["_size"] = d["Market Cap"].fillna(med_cap if med_cap and med_cap > 0 else 1.0)

    labels, parents, values, colors, texts = [], [], [], [], []
    for sec, grp in d.groupby("Sector"):
        labels.append(sec)
        parents.append("")
        values.append(float(grp["_size"].sum()))
        colors.append(0.0)
        texts.append("")
        for _, r in grp.iterrows():
            labels.append(r["Ticker"])
            parents.append(sec)
            values.append(float(r["_size"]))
            colors.append(float(r["Daily %"]))
            texts.append(f"{r['Daily %']:+.2f}%")

    fig = go.Figure(go.Treemap(
        labels=labels, parents=parents, values=values,
        branchvalues="total",
        text=texts,
        textinfo="label+text",
        textfont=dict(family=MONO_STACK, size=11, color="#FFFFFF"),
        marker=dict(
            colors=colors,
            colorscale=[[0.0, "#B91C1C"], [0.5, "#22304E"], [1.0, "#059669"]],
            cmid=0,
            line=dict(color="#0A101F", width=1.4),
        ),
        hovertemplate="<b>%{label}</b><br>Daily: %{color:+.2f}%<extra></extra>",
        pathbar=dict(visible=False),
    ))
    fig.update_layout(
        paper_bgcolor=CHART_BG,
        height=440,
        margin=dict(l=6, r=6, t=44, b=6),
        title=dict(text=title, font=dict(size=14, color="#FFFFFF", family=FONT_STACK),
                   x=0.01, xanchor="left"),
        font=dict(family=FONT_STACK, color=CHART_TEXT),
    )
    return fig


def pe_sensitivity_heatmap(payout, erp):
    """Justified P/E across a grid of risk-free rates and growth rates."""
    rf_axis = np.arange(1.0, 8.01, 0.5)
    g_axis = np.arange(0.5, 6.01, 0.25)
    z = []
    for rf in rf_axis:
        row = []
        ke = rf + erp
        for g in g_axis:
            if ke - g <= 0.4:
                row.append(None)
            else:
                row.append(round(payout * (1 + g / 100) / ((ke - g) / 100), 1))
        z.append(row)
    fig = go.Figure(go.Heatmap(
        z=z, x=[f"{g:.2f}" for g in g_axis], y=[f"{rf:.1f}" for rf in rf_axis],
        colorscale=[[0.0, "#0E1526"], [0.45, "#1E3A5F"], [0.75, "#5B9CF6"], [1.0, "#D4AF6E"]],
        colorbar=dict(title=dict(text="P/E ×", font=dict(color=CHART_TEXT, size=11)),
                      tickfont=dict(color=CHART_TEXT, family=MONO_STACK, size=10),
                      thickness=12, outlinewidth=0),
        hovertemplate="Risk-free %{y}% · Growth %{x}%<br>Justified P/E: %{z}×<extra></extra>",
        hoverongaps=False,
    ))
    layout = base_layout("Justified P/E Sensitivity — risk-free rate × long-term growth", height=430)
    layout["xaxis"]["title"] = dict(text="Long-term growth g (%)", font=dict(size=11, color=CHART_TEXT))
    layout["yaxis"]["title"] = dict(text="Risk-free rate (%)", font=dict(size=11, color=CHART_TEXT))
    layout["hovermode"] = "closest"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  SCORING FRAMEWORK
# ══════════════════════════════════════════════════════════════════════════════

def risk_adjusted_score(d):
    """Composite 0-100 macro health score."""
    score = 50
    g = d.get("GDP Growth")
    if g is not None:
        score += min(max(g, -5), 8) * 3
    i = d.get("Inflation")
    if i is not None:
        if i <= 2:
            score += 10
        elif i <= 4:
            score += 5
        elif i >= 8:
            score -= 12
    u = d.get("Unemployment")
    if u is not None:
        if u <= 4:
            score += 8
        elif u >= 10:
            score -= 10
    debt = d.get("Government Debt to GDP")
    if debt is not None:
        if debt <= 60:
            score += 6
        elif debt >= 100:
            score -= 8
    ca = d.get("Current Account")
    if ca is not None:
        if ca >= 0:
            score += 4
        elif ca <= -5:
            score -= 6
    return max(0, min(100, round(score)))


def score_label(s):
    if s >= 72:
        return "STRONG"
    if s >= 55:
        return "MODERATE"
    if s >= 40:
        return "CAUTIOUS"
    return "WEAK"


def score_color(s):
    if s >= 72:
        return "#34D399"
    if s >= 55:
        return "#D4AF6E"
    if s >= 40:
        return "#FBBF24"
    return "#F87171"


def _norm(v, lo, hi, invert=False):
    """Normalize a raw indicator to a 0-100 radar scale."""
    if v is None:
        return 50.0
    x = (v - lo) / (hi - lo) * 100.0
    x = max(0.0, min(100.0, x))
    return round(100.0 - x, 1) if invert else round(x, 1)


RADAR_DIMS = ["Growth", "Price Stability", "Labor", "Fiscal", "External", "Income"]


def radar_values(d):
    return [
        _norm(d.get("GDP Growth"), -2, 8),
        _norm(d.get("Inflation"), 0, 10, invert=True),
        _norm(d.get("Unemployment"), 2, 12, invert=True),
        _norm(d.get("Government Debt to GDP"), 20, 140, invert=True),
        _norm(d.get("Current Account"), -6, 6),
        _norm(d.get("GDP per Capita"), 1000, 70000),
    ]


# ══════════════════════════════════════════════════════════════════════════════
#  AI-STYLE COMMENTARY GENERATORS
# ══════════════════════════════════════════════════════════════════════════════

def commentary_country_compare(name_a, name_b, da, db):
    """Comparative macro commentary."""
    parts = []

    ga, gb = da.get("GDP Growth"), db.get("GDP Growth")
    if ga is not None and gb is not None:
        faster = name_a if ga > gb else name_b
        parts.append(
            f"<p><strong>Growth differential:</strong> {faster} is currently expanding "
            f"at the faster pace ({max(ga,gb):.1f}% vs {min(ga,gb):.1f}%). Sustained "
            f"differentials of this magnitude historically translate into stronger earnings "
            f"momentum and can support higher equity multiples in the faster-growing economy, "
            f"all else equal.</p>"
        )

    ia, ib = da.get("Inflation"), db.get("Inflation")
    if ia is not None and ib is not None:
        hi = name_a if ia > ib else name_b
        hi_v, lo_v = max(ia, ib), min(ia, ib)
        if hi_v > 6:
            tone = ("Elevated price pressures in this range typically force tighter monetary "
                    "policy, weighing on growth-sensitive equities and lengthening duration "
                    "risk for fixed income holders.")
        elif hi_v > 3:
            tone = ("Inflation in this band sits above most central bank targets but remains "
                    "manageable, leaving room for a gradual policy normalization path.")
        else:
            tone = ("Both economies show contained price dynamics, supportive of stable real "
                    "returns and lower discount rates.")
        parts.append(
            f"<p><strong>Inflation profile:</strong> {hi} runs hotter at {hi_v:.1f}%, "
            f"versus {lo_v:.1f}% in the comparator. {tone}</p>"
        )

    da_debt = da.get("Government Debt to GDP")
    db_debt = db.get("Government Debt to GDP")
    if da_debt is not None and db_debt is not None:
        hi_debt = name_a if da_debt > db_debt else name_b
        hi_dv = max(da_debt, db_debt)
        if hi_dv > 100:
            risk = ("raises sovereign credit and refinancing concerns, particularly in a "
                    "higher-rate environment")
        elif hi_dv > 60:
            risk = ("warrants monitoring but remains within manageable territory for "
                    "advanced economies")
        else:
            risk = "leaves meaningful fiscal headroom for counter-cyclical policy"
        parts.append(
            f"<p><strong>Fiscal position:</strong> {hi_debt} carries a heavier debt load "
            f"({hi_dv:.0f}% of GDP), which {risk}.</p>"
        )

    pca, pcb = da.get("GDP per Capita"), db.get("GDP per Capita")
    if pca and pcb:
        wealthier = name_a if pca > pcb else name_b
        ratio = max(pca, pcb) / max(min(pca, pcb), 1)
        parts.append(
            f"<p><strong>Income level:</strong> {wealthier} commands roughly {ratio:.1f}x "
            f"the per-capita income, signaling a more developed consumer base, deeper "
            f"capital markets, and typically lower equity risk premia.</p>"
        )

    return "".join(parts) if parts else "<p>Insufficient data for comparative commentary.</p>"


def commentary_markets(name_a, name_b, ret_a, ret_b, vol_a, vol_b, da, db):
    """Markets-vs-macro commentary."""
    parts = []
    if ret_a is not None and ret_b is not None:
        better = name_a if ret_a > ret_b else name_b
        parts.append(
            f"<p><strong>Equity performance:</strong> Over the trailing window, "
            f"{better}'s benchmark index has outperformed, returning "
            f"{max(ret_a,ret_b):+.1f}% versus {min(ret_a,ret_b):+.1f}%. "
            f"Equity returns reflect not only growth fundamentals but also liquidity "
            f"conditions, currency moves, and risk sentiment.</p>"
        )
    if vol_a is not None and vol_b is not None:
        less_vol = name_a if vol_a < vol_b else name_b
        parts.append(
            f"<p><strong>Volatility:</strong> {less_vol} has exhibited lower realized "
            f"volatility ({min(vol_a,vol_b):.1f}% annualized), suggesting a more "
            f"stable risk profile and potentially more attractive Sharpe characteristics "
            f"for risk-conscious allocators.</p>"
        )

    ga, gb = da.get("GDP Growth"), db.get("GDP Growth")
    if ga is not None and gb is not None and ret_a is not None and ret_b is not None:
        gdp_winner = name_a if ga > gb else name_b
        mkt_winner = name_a if ret_a > ret_b else name_b
        if gdp_winner == mkt_winner:
            parts.append(
                f"<p><strong>Macro-market alignment:</strong> The faster-growing economy "
                f"({gdp_winner}) is also the better-performing equity market, consistent "
                f"with the textbook growth-to-returns linkage.</p>"
            )
        else:
            parts.append(
                f"<p><strong>Macro-market divergence:</strong> Notably, the faster-growing "
                f"economy ({gdp_winner}) is not the better-performing equity market. This "
                f"divergence is common and reflects that equity returns are driven by "
                f"valuation re-rating, currency, sector mix, and global capital flows — "
                f"not pure GDP growth alone.</p>"
            )

    return "".join(parts) if parts else "<p>Market data unavailable for commentary.</p>"


def commentary_valuation(name_a, name_b, da, db):
    """Macro -> valuation educational commentary."""
    parts = []
    ga, gb = da.get("GDP Growth"), db.get("GDP Growth")
    ia, ib = da.get("Inflation"), db.get("Inflation")
    ra, rb = da.get("Lending Rate"), db.get("Lending Rate")

    if ga is not None and gb is not None:
        parts.append(
            f"<p><strong>Growth and earnings:</strong> Real GDP growth of {ga:.1f}% in "
            f"{name_a} vs {gb:.1f}% in {name_b} flows directly into corporate revenue "
            f"baselines. Faster nominal growth typically supports higher earnings expansion, "
            f"justifying richer forward P/E multiples in growth-oriented markets.</p>"
        )

    if ra is not None and rb is not None:
        parts.append(
            f"<p><strong>Discount rates:</strong> Lending rates of {ra:.1f}% ({name_a}) "
            f"and {rb:.1f}% ({name_b}) feed directly into the cost of equity through the "
            f"risk-free rate. Higher rates compress DCF valuations, particularly for "
            f"long-duration growth assets, while lower-rate regimes lift terminal value "
            f"contributions.</p>"
        )

    if ia is not None and ib is not None:
        parts.append(
            f"<p><strong>Inflation pass-through:</strong> Companies with pricing power "
            f"can pass through inflation ({max(ia,ib):.1f}% in the more inflated economy), "
            f"protecting margins. Sectors like consumer staples, energy, and materials "
            f"typically fare better in inflationary regimes, while long-duration tech and "
            f"REITs face multiple compression.</p>"
        )

    parts.append(
        "<p><strong>Risk premium framework:</strong> Equity Risk Premium = Earnings Yield "
        "- Risk-Free Rate. Markets with strong real growth, contained inflation, and "
        "stable institutions typically command lower required returns and trade at "
        "premium multiples.</p>"
    )

    return "".join(parts)


def commentary_risk(name_a, name_b, da, db):
    """Risk dashboard commentary."""
    parts = []

    risks_a, risks_b = [], []
    if da.get("Inflation", 0) > 6:
        risks_a.append("elevated inflation")
    if db.get("Inflation", 0) > 6:
        risks_b.append("elevated inflation")
    if da.get("Government Debt to GDP", 0) > 90:
        risks_a.append("high sovereign debt")
    if db.get("Government Debt to GDP", 0) > 90:
        risks_b.append("high sovereign debt")
    if da.get("Unemployment", 0) > 8:
        risks_a.append("weak labor market")
    if db.get("Unemployment", 0) > 8:
        risks_b.append("weak labor market")
    if (da.get("Current Account") or 0) < -4:
        risks_a.append("external imbalance")
    if (db.get("Current Account") or 0) < -4:
        risks_b.append("external imbalance")

    a_str = ", ".join(risks_a) if risks_a else "no major flagged risks"
    b_str = ", ".join(risks_b) if risks_b else "no major flagged risks"

    parts.append(
        f"<p><strong>{name_a} risk profile:</strong> {a_str.capitalize()}. "
        f"Inflation at {da.get('Inflation', 0):.1f}%, debt/GDP at "
        f"{da.get('Government Debt to GDP', 0):.0f}%, unemployment at "
        f"{da.get('Unemployment', 0):.1f}%.</p>"
    )
    parts.append(
        f"<p><strong>{name_b} risk profile:</strong> {b_str.capitalize()}. "
        f"Inflation at {db.get('Inflation', 0):.1f}%, debt/GDP at "
        f"{db.get('Government Debt to GDP', 0):.0f}%, unemployment at "
        f"{db.get('Unemployment', 0):.1f}%.</p>"
    )

    score_a = risk_adjusted_score(da)
    score_b = risk_adjusted_score(db)
    winner = name_a if score_a > score_b else name_b
    parts.append(
        f"<p><strong>Risk-adjusted view:</strong> On a composite framework weighing "
        f"growth, inflation control, fiscal stability, and external balance, "
        f"<strong>{winner}</strong> screens more attractively at this point in the cycle "
        f"({max(score_a,score_b)}/100 vs {min(score_a,score_b)}/100).</p>"
    )

    return "".join(parts)


def commentary_sectors(name_a, name_b, da, db):
    """Sector composition commentary."""
    parts = []
    sa = da.get("Services % GDP", 0) or 0
    sb = db.get("Services % GDP", 0) or 0
    ia = da.get("Industry % GDP", 0) or 0
    ib = db.get("Industry % GDP", 0) or 0
    aa = da.get("Agriculture % GDP", 0) or 0
    ab = db.get("Agriculture % GDP", 0) or 0

    if sa > sb + 5:
        parts.append(
            f"<p><strong>{name_a}</strong> is the more services-oriented economy "
            f"({sa:.0f}% vs {sb:.0f}%), typical of advanced economies with mature "
            f"financial, technology, and consumer service sectors. This composition "
            f"tends to be less cyclical and more resilient through downturns.</p>"
        )
    elif sb > sa + 5:
        parts.append(
            f"<p><strong>{name_b}</strong> is the more services-oriented economy "
            f"({sb:.0f}% vs {sa:.0f}%), typical of advanced economies with mature "
            f"financial, technology, and consumer service sectors.</p>"
        )

    if ia > ib + 5:
        parts.append(
            f"<p><strong>{name_a}</strong> has a heavier industrial base ({ia:.0f}% "
            f"vs {ib:.0f}%), exposing it to global trade cycles, commodity input costs, "
            f"and capital-goods demand.</p>"
        )
    elif ib > ia + 5:
        parts.append(
            f"<p><strong>{name_b}</strong> has a heavier industrial base ({ib:.0f}% "
            f"vs {ia:.0f}%), exposing it to global trade cycles and commodity prices.</p>"
        )

    if max(aa, ab) > 10:
        ag_country = name_a if aa > ab else name_b
        parts.append(
            f"<p><strong>{ag_country}</strong> retains a sizeable agricultural sector "
            f"({max(aa,ab):.0f}% of GDP), which historically signals an earlier stage of "
            f"economic development with significant runway for productivity-driven catch-up "
            f"growth and structural sector rotation.</p>"
        )

    return "".join(parts) if parts else "<p>Sector composition is broadly similar across the two economies.</p>"


# ══════════════════════════════════════════════════════════════════════════════
#  INVESTMENT MEMO (HTML)
# ══════════════════════════════════════════════════════════════════════════════

def generate_investment_memo(name_a, name_b, da, db):
    """Build a structured investment memo as HTML for in-app display."""
    score_a = risk_adjusted_score(da)
    score_b = risk_adjusted_score(db)
    winner = name_a if score_a > score_b else name_b
    today = datetime.date.today().strftime("%B %d, %Y")

    ga = da.get("GDP Growth", 0) or 0
    gb = db.get("GDP Growth", 0) or 0
    ia = da.get("Inflation", 0) or 0
    ib = db.get("Inflation", 0) or 0

    growth_phrase = f"{name_a} expanding at {ga:.1f}% versus {name_b} at {gb:.1f}%"
    inflation_phrase = f"inflation of {ia:.1f}% in {name_a} compared to {ib:.1f}% in {name_b}"

    memo_html = f"""
    <div class="memo">
      <div class="memo-header">
        <div class="memo-title">INVESTMENT MEMORANDUM</div>
        <div class="memo-meta">{name_a} vs {name_b}  |  {today}  |  Macro Strategy</div>
      </div>

      <h3>Executive Summary</h3>
      <p>This memo evaluates the relative macroeconomic and investment attractiveness of
      {name_a} and {name_b}. On a composite risk-adjusted framework, <strong>{winner}</strong>
      currently presents the more compelling profile, scoring {max(score_a,score_b)}/100
      versus {min(score_a,score_b)}/100 for the comparator.</p>

      <h3>Macro Overview</h3>
      <p>{name_a} posts nominal GDP of {fmt_money(da.get('GDP'))} with per-capita income of
      {fmt_dollar(da.get('GDP per Capita'))}, while {name_b} prints
      {fmt_money(db.get('GDP'))} and {fmt_dollar(db.get('GDP per Capita'))} respectively.
      The headline growth picture shows {growth_phrase}, with {inflation_phrase}.</p>

      <h3>Key Growth Drivers</h3>
      <p>{name_a}'s economic structure is dominated by services
      ({da.get('Services % GDP', 0):.0f}% of GDP), with industry contributing
      {da.get('Industry % GDP', 0):.0f}% and agriculture {da.get('Agriculture % GDP', 0):.0f}%.
      {name_b} shows a comparable mix at {db.get('Services % GDP', 0):.0f}% services,
      {db.get('Industry % GDP', 0):.0f}% industry, and {db.get('Agriculture % GDP', 0):.0f}%
      agriculture. Investment as a share of GDP runs at {da.get('Investment % GDP', 0):.0f}%
      and {db.get('Investment % GDP', 0):.0f}% respectively, a key indicator of forward
      productive capacity.</p>

      <h3>Market &amp; Investment Implications</h3>
      <p>From a portfolio perspective, the macro backdrop favors equity exposure to
      {winner if (da.get('GDP Growth', 0) if winner == name_a else db.get('GDP Growth', 0)) > 3 else 'defensive sectors and quality balance sheets'}.
      Fixed income investors should consider duration positioning given lending rates of
      {da.get('Lending Rate', 0):.1f}% in {name_a} and {db.get('Lending Rate', 0):.1f}%
      in {name_b}. Currency hedging decisions become material when allocating across these
      jurisdictions.</p>

      <h3>Key Risks</h3>
      <p>Principal risks include: (1) inflation persistence forcing tighter monetary
      conditions, (2) sovereign debt sustainability — {name_a} carries debt/GDP of
      {da.get('Government Debt to GDP', 0):.0f}% versus {db.get('Government Debt to GDP', 0):.0f}%
      for {name_b}, (3) external imbalance risk, and (4) policy or geopolitical shocks
      that disproportionately impact one jurisdiction.</p>

      <h3>Comparative View</h3>
      <p>On a side-by-side basis, {winner} screens better on the risk-adjusted composite,
      driven by {'stronger growth and contained inflation' if score_a > score_b and ga > 3
      else 'a more balanced fiscal and external position'}. The relative advantage is not
      absolute — investors with different objectives (income, growth, defensive) may reach
      different conclusions.</p>

      <h3>Investor Takeaway</h3>
      <p>For a long-only macro allocator, an overweight to <strong>{winner}</strong>
      is supported by the current data. Growth-oriented investors should weigh the GDP
      growth differential ({max(ga,gb):.1f}% vs {min(ga,gb):.1f}%), while stability-focused
      mandates should emphasize the inflation and debt picture. As always, this analysis
      is educational and should be combined with bottom-up security selection, valuation
      discipline, and active risk management.</p>
    </div>
    """
    return memo_html


# ══════════════════════════════════════════════════════════════════════════════
#  PDF BUILDERS (reportlab)
# ══════════════════════════════════════════════════════════════════════════════

def build_pdf_report(name_a, name_b, da, db, memo_text=""):
    """Country-pair research report PDF. Returns bytes or None."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib import colors as rl
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    except ImportError:
        return None

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=0.7 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )

    NAVY = rl.HexColor("#0A101F")
    GOLD = rl.HexColor("#C9A96E")
    DARK_GREY = rl.HexColor("#2F2F2F")
    LIGHT = rl.HexColor("#F0F4F8")
    BORDER = rl.HexColor("#DCE4EF")

    styles = getSampleStyleSheet()
    title_st = ParagraphStyle("T", parent=styles["Title"], fontSize=21,
                              textColor=NAVY, alignment=TA_CENTER, spaceAfter=4)
    sub_st = ParagraphStyle("S", parent=styles["Normal"], fontSize=10,
                            textColor=rl.HexColor("#5A7A9B"),
                            alignment=TA_CENTER, spaceAfter=16)
    head_st = ParagraphStyle("H", parent=styles["Heading2"], fontSize=12,
                             textColor=NAVY, spaceBefore=14, spaceAfter=6,
                             borderPadding=4)
    body_st = ParagraphStyle("B", parent=styles["Normal"], fontSize=9.5,
                             leading=14, textColor=DARK_GREY,
                             alignment=TA_JUSTIFY)
    small_st = ParagraphStyle("Sm", parent=styles["Normal"], fontSize=7.5,
                              textColor=rl.HexColor("#7A98B5"),
                              alignment=TA_CENTER)

    def styled_table(data, widths):
        t = Table(data, colWidths=widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), rl.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, rl.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, 0), 1.5, GOLD),
        ]))
        return t

    story = []

    story.append(Paragraph("GLOBAL MACRO INVESTMENT ANALYZER", title_st))
    story.append(Paragraph(
        f"Investment Research Report: {name_a} vs {name_b}", sub_st))
    story.append(Paragraph(
        f"Generated {datetime.date.today().strftime('%B %d, %Y')}  |  "
        f"Prepared by Vedant Patil  |  Professional Edition v{APP_VERSION}",
        sub_st))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Macro Snapshot", head_st))
    story.append(styled_table([
        ["Indicator", name_a, name_b],
        ["Nominal GDP", fmt_money(da.get("GDP")), fmt_money(db.get("GDP"))],
        ["GDP per Capita", fmt_dollar(da.get("GDP per Capita")),
         fmt_dollar(db.get("GDP per Capita"))],
        ["GDP Growth", fmt_pct_simple(da.get("GDP Growth")),
         fmt_pct_simple(db.get("GDP Growth"))],
        ["Inflation", fmt_pct_simple(da.get("Inflation")),
         fmt_pct_simple(db.get("Inflation"))],
        ["Unemployment", fmt_pct_simple(da.get("Unemployment")),
         fmt_pct_simple(db.get("Unemployment"))],
        ["Lending Rate", fmt_pct_simple(da.get("Lending Rate")),
         fmt_pct_simple(db.get("Lending Rate"))],
        ["Govt Debt / GDP", fmt_pct_simple(da.get("Government Debt to GDP")),
         fmt_pct_simple(db.get("Government Debt to GDP"))],
        ["Current Account", fmt_pct_simple(da.get("Current Account")),
         fmt_pct_simple(db.get("Current Account"))],
    ], [2.4 * inch, 2.1 * inch, 2.1 * inch]))
    story.append(Spacer(1, 10))

    sa = risk_adjusted_score(da)
    sb = risk_adjusted_score(db)
    story.append(Paragraph("Risk-Adjusted Macro Score", head_st))
    story.append(Paragraph(
        f"<b>{name_a}:</b> {sa}/100 ({score_label(sa)}) &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>{name_b}:</b> {sb}/100 ({score_label(sb)})", body_st))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Sector Composition (% of GDP)", head_st))
    story.append(styled_table([
        ["Sector", name_a, name_b],
        ["Agriculture", fmt_pct_simple(da.get("Agriculture % GDP")),
         fmt_pct_simple(db.get("Agriculture % GDP"))],
        ["Industry", fmt_pct_simple(da.get("Industry % GDP")),
         fmt_pct_simple(db.get("Industry % GDP"))],
        ["Services", fmt_pct_simple(da.get("Services % GDP")),
         fmt_pct_simple(db.get("Services % GDP"))],
    ], [2.4 * inch, 2.1 * inch, 2.1 * inch]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Investment Commentary", head_st))
    commentary = commentary_country_compare(name_a, name_b, da, db)
    plain = commentary.replace("<p>", "").replace("</p>", "\n\n")
    plain = plain.replace("<strong>", "<b>").replace("</strong>", "</b>")
    for para in plain.split("\n\n"):
        para = para.strip()
        if para:
            story.append(Paragraph(para, body_st))
            story.append(Spacer(1, 4))

    if memo_text:
        story.append(Spacer(1, 6))
        story.append(Paragraph("Investor Takeaway", head_st))
        story.append(Paragraph(memo_text, body_st))

    story.append(Spacer(1, 18))
    story.append(Paragraph(
        "Data Sources: World Bank Open Data, Yahoo Finance  |  "
        "Generated by Global Macro Investment Analyzer  |  "
        "For educational use only — not investment advice.",
        small_st))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


def build_ic_memo_pdf(name_a=None, name_b=None, da=None, db=None,
                      us_df=None, us_top5=None, us_def=None, us_grow=None, us_val=None,
                      in_df=None, in_top5=None, in_def=None, in_grow=None, in_val=None):
    """Investment Committee Memo PDF (macro + US + India equities)."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib import colors as rl
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, PageBreak)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    except ImportError:
        return None

    buf = io.BytesIO()
    NAVY = rl.HexColor("#0A2463")
    GOLD = rl.HexColor("#C9A96E")
    DARK = rl.HexColor("#2F2F2F")
    LIGHT = rl.HexColor("#F0F4F8")
    BORDER = rl.HexColor("#DCE4EF")

    def footer(canv, doc):
        canv.saveState()
        canv.setFont("Helvetica", 7.5)
        canv.setFillColor(rl.HexColor("#7A98B5"))
        canv.drawString(0.75 * inch, 0.4 * inch,
                        "Global Macro Investment Analyzer  |  Investment Committee Memo")
        canv.drawRightString(7.75 * inch, 0.4 * inch, f"Page {doc.page}")
        canv.setStrokeColor(BORDER)
        canv.line(0.75 * inch, 0.55 * inch, 7.75 * inch, 0.55 * inch)
        canv.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.75 * inch, bottomMargin=0.8 * inch,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch)

    styles = getSampleStyleSheet()
    title_st = ParagraphStyle("T", parent=styles["Title"], fontSize=23, textColor=NAVY,
                              alignment=TA_CENTER, spaceAfter=4)
    sub_st = ParagraphStyle("S", parent=styles["Normal"], fontSize=11,
                            textColor=rl.HexColor("#5A7A9B"), alignment=TA_CENTER, spaceAfter=18)
    head_st = ParagraphStyle("H", parent=styles["Heading2"], fontSize=13,
                             textColor=NAVY, spaceBefore=14, spaceAfter=6)
    body_st = ParagraphStyle("B", parent=styles["Normal"], fontSize=9.5, leading=14,
                             textColor=DARK, alignment=TA_JUSTIFY)
    small_st = ParagraphStyle("Sm", parent=styles["Normal"], fontSize=8,
                              textColor=rl.HexColor("#7A98B5"), alignment=TA_CENTER)

    def styled_table(data, widths):
        t = Table(data, colWidths=widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), rl.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, rl.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, 0), 1.5, GOLD),
        ]))
        return t

    def market_block(story, label, df, top5, def_p, grow_p, val_p):
        if df is None or (hasattr(df, "empty") and df.empty):
            story.append(Paragraph(
                f"<i>No {label} data available — visit the {label} equities page first.</i>",
                body_st))
            return
        story.append(Paragraph(f"<b>{label} — Top 5 Ranked</b>", body_st))
        if top5 is not None and not top5.empty:
            tbl = [["Ticker", "Name", "Score", "1M %", "YTD %", "From 52WH"]]
            for _, r in top5.iterrows():
                tbl.append([str(r["Ticker"]), str(r["Name"])[:24], f"{r['Score']:.1f}",
                            fmt_num(r.get("1M %"), "%", 1),
                            fmt_num(r.get("YTD %"), "%", 1),
                            fmt_num(r.get("From High %"), "%", 1)])
            story.append(styled_table(
                tbl, [0.9 * inch, 2.2 * inch, 0.7 * inch, 0.9 * inch, 0.9 * inch, 0.95 * inch]))
            story.append(Spacer(1, 4))
        for sublabel, picks in [("Defensive", def_p), ("Growth / Momentum", grow_p),
                                ("Value / Pullback", val_p)]:
            if picks is not None and not picks.empty:
                story.append(Paragraph(
                    f"<b>{label} {sublabel}:</b> " + ", ".join(picks["Ticker"].tolist()),
                    body_st))
                story.append(Spacer(1, 2))
        story.append(Spacer(1, 6))

    story = []
    story.append(Spacer(1, 60))
    story.append(Paragraph("GLOBAL MACRO INVESTMENT ANALYZER", title_st))
    story.append(Paragraph("Investment Committee Memo", sub_st))
    story.append(Spacer(1, 30))
    pair = f"{name_a} vs {name_b}" if name_a and name_b and name_a != name_b else "Cross-Market Equity View"
    story.append(Paragraph(f"<b>Subject:</b> {pair}", body_st))
    story.append(Paragraph(f"<b>Date:</b> {datetime.date.today().strftime('%B %d, %Y')}", body_st))
    story.append(Paragraph("<b>Prepared by:</b> Vedant Patil", body_st))
    story.append(Paragraph(f"<b>Platform:</b> Professional Edition v{APP_VERSION}", body_st))
    story.append(PageBreak())

    story.append(Paragraph("1. Executive Summary", head_st))
    es = "This memo presents an integrated macro and equity-market view"
    if name_a and name_b and name_a != name_b:
        es += f" across {pair}"
    es += ". "
    if da and db:
        gw = name_a if (da.get('GDP Growth') or 0) > (db.get('GDP Growth') or 0) else name_b
        es += f"On the macro front, {gw} screens favorably on growth momentum. "
    us_names = us_top5["Ticker"].head(3).tolist() if us_top5 is not None and not us_top5.empty else []
    in_names = in_top5["Ticker"].head(3).tolist() if in_top5 is not None and not in_top5.empty else []
    if us_names:
        es += f"Top-ranked U.S. names include {', '.join(us_names)}. "
    if in_names:
        es += f"Top-ranked India names include {', '.join(in_names)}. "
    es += "Full recommendations and risks follow."
    story.append(Paragraph(es, body_st))

    if da and db:
        story.append(Paragraph("2. Macro Dashboard Summary", head_st))
        story.append(styled_table([
            ["Indicator", name_a or "A", name_b or "B"],
            ["GDP Growth", fmt_pct_simple(da.get("GDP Growth")), fmt_pct_simple(db.get("GDP Growth"))],
            ["Inflation", fmt_pct_simple(da.get("Inflation")), fmt_pct_simple(db.get("Inflation"))],
            ["Lending Rate", fmt_pct_simple(da.get("Lending Rate")), fmt_pct_simple(db.get("Lending Rate"))],
            ["Unemployment", fmt_pct_simple(da.get("Unemployment")), fmt_pct_simple(db.get("Unemployment"))],
            ["Govt Debt/GDP", fmt_pct_simple(da.get("Government Debt to GDP")),
             fmt_pct_simple(db.get("Government Debt to GDP"))],
            ["Risk Score", f"{risk_adjusted_score(da)}/100", f"{risk_adjusted_score(db)}/100"],
        ], [2.4 * inch, 2.1 * inch, 2.1 * inch]))
        story.append(Spacer(1, 10))

    story.append(Paragraph("3. Market & Valuation Summary", head_st))
    story.append(Paragraph(
        "Equity returns are driven by earnings growth and multiple changes. Multiples reflect "
        "interest rates, inflation expectations, and risk appetite. The DCF framework links these "
        "explicitly: cash flows scale with nominal growth, while the discount rate moves with the "
        "risk-free rate and equity risk premium.", body_st))

    story.append(Paragraph("4. U.S. Top Stocks Summary (Dow 30)", head_st))
    market_block(story, "U.S.", us_df, us_top5, us_def, us_grow, us_val)

    story.append(Paragraph("5. India Top Stocks Summary (NIFTY 50)", head_st))
    market_block(story, "India", in_df, in_top5, in_def, in_grow, in_val)

    story.append(Paragraph("6. Investment Recommendation", head_st))
    rec_call = "NEUTRAL"
    if da and db:
        sa = risk_adjusted_score(da)
        sb = risk_adjusted_score(db)
        if max(sa, sb) > 70:
            rec_call = "OVERWEIGHT (higher-scoring economy)"
        elif max(sa, sb) < 45:
            rec_call = "UNDERWEIGHT"
    story.append(Paragraph(f"<b>Call:</b> {rec_call}", body_st))
    story.append(Paragraph(
        "Rationale: Composite scoring synthesizes growth, inflation, fiscal, and external balance "
        "signals, combined with bottom-up equity screens across U.S. and India markets. Catalysts "
        "to monitor include central bank communication, fiscal policy shifts, and corporate earnings.",
        body_st))

    story.append(Paragraph("7. Risk Factors", head_st))
    story.append(Paragraph(
        "<b>Inflation risk:</b> Persistence forces tighter policy and multiple compression. "
        "<b>Rate risk:</b> Long-duration assets vulnerable to upside surprises. "
        "<b>FX risk:</b> Currency moves can dominate equity returns for foreign investors. "
        "<b>Recession risk:</b> Earnings cuts and credit deterioration. "
        "<b>Geopolitical risk:</b> Trade, sanctions, conflict episodes. "
        "<b>Valuation risk:</b> Multiples compressing toward historical averages.", body_st))

    story.append(Paragraph("8. Appendix", head_st))
    story.append(Paragraph(
        "<b>Data sources:</b> World Bank Open Data API, Yahoo Finance (via yfinance). "
        "<b>Methodology:</b> Composite scoring weighting growth, inflation, fiscal, and external "
        "metrics; equity screening on momentum, valuation, yield, and beta.", body_st))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Disclaimer:</b> This platform is for educational and analytical purposes only and does "
        "not constitute financial advice, investment recommendation, or solicitation. All AI-generated "
        "views are illustrative.", small_st))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    buf.seek(0)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
#  STOCK ANALYTICS  —  scoring, screening, narrative generation
# ══════════════════════════════════════════════════════════════════════════════

def calculate_stock_score(rows):
    """Add a composite score 0-100 to each row in place."""
    for r in rows:
        s = 50.0
        m1 = _safe(r.get("1M %"))
        m3 = _safe(r.get("3M %"))
        ytd = _safe(r.get("YTD %"))
        dist = _safe(r.get("From High %"))
        pe = _safe(r.get("P/E"))
        dy = _safe(r.get("Div Yield %"))
        beta = _safe(r.get("Beta"))
        rec = r.get("Rec", "—")
        avg_vol = _safe(r.get("Avg Vol"))

        if m1 is not None:
            s += max(-15, min(m1, 15)) * 0.8
        if m3 is not None:
            s += max(-20, min(m3, 20)) * 0.4
        if ytd is not None:
            s += max(-30, min(ytd, 30)) * 0.2
        if dist is not None:
            s += max(-30, min(dist, 0)) * 0.15
        if pe is not None and pe > 0:
            if pe < 15:
                s += 6
            elif pe < 25:
                s += 2
            elif pe > 40:
                s -= 5
        if dy is not None and dy > 2:
            s += 3
        if beta is not None:
            if beta < 0.8:
                s += 2
            elif beta > 1.5:
                s -= 3
        if rec in ("strong_buy", "buy"):
            s += 6
        elif rec in ("sell", "strong_sell"):
            s -= 6
        if avg_vol is not None and avg_vol > 1e6:
            s += 1
        r["Score"] = round(max(0, min(100, s)), 1)
    return rows


def compute_peer_medians(df):
    """Median values used in dynamic reason/risk text."""
    med = {}
    for col in ["P/E", "1M %", "3M %", "YTD %", "Beta", "Div Yield %", "From High %",
                "Volatility %", "Score"]:
        try:
            med[col] = float(df[col].dropna().median())
        except Exception:
            med[col] = None
    return med


def generate_reason(row, category, peer_medians, market_name):
    """Data-specific reason string for a suggested stock."""
    tk = row["Ticker"]
    nm = row["Name"]
    m1 = _safe(row.get("1M %"))
    m3 = _safe(row.get("3M %"))
    ytd = _safe(row.get("YTD %"))
    dist = _safe(row.get("From High %"))
    pe = _safe(row.get("P/E"))
    dy = _safe(row.get("Div Yield %"))
    beta = _safe(row.get("Beta"))
    score = row.get("Score", 0)
    med_pe = peer_medians.get("P/E")
    med_score = peer_medians.get("Score") or 50

    if category == "top":
        bits = [f"composite score of {score:.1f}"]
        if score and med_score and score > med_score:
            bits.append(f"above the {market_name} median of {med_score:.1f}")
        if m1 is not None:
            bits.append(f"1M return {m1:+.1f}%")
        if ytd is not None:
            bits.append(f"YTD {ytd:+.1f}%")
        if dist is not None and dist > -5:
            bits.append(f"trading just {abs(dist):.1f}% off the 52-week high — signals institutional accumulation")
        elif dist is not None:
            bits.append(f"trading {abs(dist):.1f}% below the 52-week high")
        if pe is not None and med_pe and pe < med_pe:
            bits.append(f"P/E of {pe:.1f}x below the peer median of {med_pe:.1f}x")
        elif pe is not None:
            bits.append(f"P/E of {pe:.1f}x")
        return f"{tk} ({nm}) ranks favorably with " + ", ".join(bits) + "."

    if category == "def":
        bits = []
        if beta is not None:
            bits.append(f"beta of {beta:.2f}")
        if dy is not None and dy > 0:
            bits.append(f"dividend yield of {dy:.2f}%")
        if row.get("Volatility %") is not None:
            bits.append(f"realized volatility of {row['Volatility %']:.1f}%")
        if m1 is not None and abs(m1) < 5:
            bits.append(f"steady 1M move of {m1:+.1f}% reflecting limited price drawdown")
        sec = row.get("Sector", "")
        if sec and sec != "—":
            bits.append(f"sector exposure: {sec}")
        return (f"{tk} ({nm}) offers defensive characteristics — "
                + ", ".join(bits) + " — suited to risk-off positioning.")

    if category == "grow":
        bits = []
        if m1 is not None:
            bits.append(f"1M momentum of {m1:+.1f}%")
        if m3 is not None:
            bits.append(f"3M trend {m3:+.1f}%")
        if dist is not None:
            bits.append(f"price {abs(dist):.1f}% from 52W high")
        if beta is not None:
            bits.append(f"beta {beta:.2f} amplifies upside in risk-on")
        return (f"{tk} ({nm}) screens as a momentum / growth candidate with "
                + ", ".join(bits) + ".")

    # value / pullback
    bits = []
    if dist is not None:
        bits.append(f"trading {abs(dist):.1f}% below 52W high — mean-reversion setup")
    if pe is not None and med_pe and pe < med_pe:
        bits.append(f"P/E {pe:.1f}x vs peer median {med_pe:.1f}x")
    elif pe is not None:
        bits.append(f"P/E {pe:.1f}x")
    if dy is not None and dy > 1.5:
        bits.append(f"dividend yield {dy:.2f}% offers carry while waiting for recovery")
    if m1 is not None and m1 > 0:
        bits.append(f"1M return {m1:+.1f}% suggests early stabilization")
    return f"{tk} ({nm}) flags as a value / pullback opportunity: " + ", ".join(bits) + "."


def generate_risk(row, category, peer_medians, market_name):
    """Data-specific risk string for a suggested stock."""
    pe = _safe(row.get("P/E"))
    med_pe = peer_medians.get("P/E")
    beta = _safe(row.get("Beta"))
    dist = _safe(row.get("From High %"))
    dy = _safe(row.get("Div Yield %"))
    m1 = _safe(row.get("1M %"))
    sec = row.get("Sector", "—")

    if category == "top":
        if pe is not None and med_pe and pe > med_pe * 1.2:
            return (f"Valuation risk elevated — P/E of {pe:.1f}x sits {((pe/med_pe)-1)*100:.0f}% above the "
                    f"peer median, leaving the stock sensitive to earnings misses or rate-driven multiple compression.")
        if dist is not None and dist > -3:
            return (f"Trading within {abs(dist):.1f}% of 52W high — limited margin of safety; "
                    f"sharp reversal possible on macro disappointment or guidance cuts.")
        if beta is not None and beta > 1.3:
            return f"Higher beta ({beta:.2f}) means drawdowns will exceed index moves in any risk-off episode."
        return "Concentrated single-name exposure; consensus crowding can amplify downside on negative surprises."

    if category == "def":
        if dy is not None and dy < 1:
            return f"Limited dividend cushion ({dy:.2f}%) — defensive character relies primarily on price stability rather than income."
        if m1 is not None and m1 < -3:
            return f"Recent 1M weakness ({m1:+.1f}%) signals defensive label may be tested; monitor for trend deterioration."
        return ("Opportunity cost — defensive names typically lag in strong rally environments, "
                "and dividend payouts can be cut under earnings stress.")

    if category == "grow":
        if beta is not None and beta > 1.4:
            return (f"Elevated beta of {beta:.2f} implies drawdowns roughly {((beta-1)*100):.0f}% greater than the index "
                    f"in corrections. Position sizing discipline essential.")
        if dist is not None and dist > -3:
            return ("Stock already near 52W high — chase risk is real; entry on a 5-10% pullback offers better risk/reward.")
        if pe is not None and med_pe and pe > med_pe * 1.3:
            return f"P/E of {pe:.1f}x leaves zero margin for execution missteps — earnings guidance becomes the swing factor."
        return "Momentum trades fail abruptly when narrative shifts; use trailing stops and respect technical breaks."

    # value
    if dist is not None and dist < -25:
        return (f"Stock trades {abs(dist):.1f}% below 52W high — potential value trap if the drawdown reflects "
                f"structural deterioration (earnings cuts, sector decline) rather than temporary sentiment.")
    if m1 is not None and m1 < -5:
        return f"Continued 1M weakness ({m1:+.1f}%) means catching a falling knife is a real risk — wait for trend confirmation."
    if pe is not None and pe < 0:
        return "Negative earnings make P/E meaningless — fundamentals may not support a recovery thesis."
    return f"Sector headwinds in {sec} can persist longer than expected, delaying mean reversion."


def generate_equity_research_summary(df, market_name):
    """Market-aware research commentary HTML block."""
    pos = int((df["Daily %"] > 0).sum())
    neg = int((df["Daily %"] < 0).sum())
    total = len(df)
    avg_daily = float(df["Daily %"].mean()) if not df["Daily %"].dropna().empty else 0
    avg_1m_series = df["1M %"].dropna()
    avg_1m = float(avg_1m_series.mean()) if not avg_1m_series.empty else None

    best = df.dropna(subset=["Daily %"]).nlargest(3, "Daily %")
    worst = df.dropna(subset=["Daily %"]).nsmallest(3, "Daily %")
    mom = df.dropna(subset=["1M %"]).nlargest(3, "1M %")
    defensive = df.dropna(subset=["Beta"]).nsmallest(3, "Beta")
    value = df[df["P/E"].notna() & (df["P/E"] > 0)].nsmallest(3, "P/E")
    income = df.dropna(subset=["Div Yield %"]).nlargest(3, "Div Yield %")
    near_hi = df.dropna(subset=["From High %"]).nlargest(3, "From High %")
    pullback = df.dropna(subset=["From High %"]).nsmallest(3, "From High %")
    high_beta = df.dropna(subset=["Beta"]).nlargest(3, "Beta")

    body = []
    body.append(f"<p><strong>Market breadth:</strong> {pos}/{total} advancers vs {neg}/{total} decliners. "
                f"Average daily move {avg_daily:+.2f}%"
                + (f"; trailing-month average {avg_1m:+.1f}%." if avg_1m is not None else ".")
                + f" {'Breadth is broadly constructive.' if pos > neg else 'Breadth skews defensive — risk appetite muted.'}</p>")
    if not best.empty:
        body.append(f"<p><strong>Today's leaders:</strong> {', '.join(best['Ticker'].tolist())} "
                    f"led the tape with gains of {best['Daily %'].iloc[0]:+.1f}% to {best['Daily %'].iloc[-1]:+.1f}%.</p>")
    if not worst.empty:
        body.append(f"<p><strong>Today's laggards:</strong> {', '.join(worst['Ticker'].tolist())} "
                    f"underperformed, declining {worst['Daily %'].iloc[0]:.1f}% to {worst['Daily %'].iloc[-1]:.1f}%.</p>")
    if not mom.empty:
        body.append(f"<p><strong>Momentum leaders (1M):</strong> {', '.join(mom['Ticker'].tolist())} — "
                    f"strongest trailing-month performance, signaling buying pressure and earnings momentum.</p>")
    if not defensive.empty:
        body.append(f"<p><strong>Defensive names (low beta):</strong> {', '.join(defensive['Ticker'].tolist())} — "
                    f"attractive for portfolios prioritizing stability through volatility regimes.</p>")
    if not value.empty:
        body.append(f"<p><strong>Value screen (low P/E):</strong> {', '.join(value['Ticker'].tolist())} — "
                    f"trading at the cheapest earnings multiples within the index.</p>")
    if not income.empty:
        body.append(f"<p><strong>Income / dividend leaders:</strong> {', '.join(income['Ticker'].tolist())} — "
                    f"highest dividend yields, suitable for income-oriented allocators.</p>")
    if not high_beta.empty:
        body.append(f"<p><strong>Riskier high-beta names:</strong> {', '.join(high_beta['Ticker'].tolist())} — "
                    f"highest amplification of market moves; suited to risk-on regimes.</p>")
    if not near_hi.empty:
        body.append(f"<p><strong>Trading near 52-week highs:</strong> {', '.join(near_hi['Ticker'].tolist())} — "
                    f"strongest relative price action; breakout setups for momentum traders.</p>")
    if not pullback.empty:
        body.append(f"<p><strong>Pullback opportunities:</strong> {', '.join(pullback['Ticker'].tolist())} — "
                    f"trading furthest from 52-week highs; potential mean-reversion candidates.</p>")

    if "Sector" in df.columns:
        sector_counts = df["Sector"].value_counts().head(3)
        sector_txt = "; ".join([f"{s} ({c})" for s, c in sector_counts.items() if s and s != "—"])
        if sector_txt:
            body.append(f"<p><strong>Sector mix:</strong> Largest sector representations in {market_name}: {sector_txt}.</p>")

    body.append(f"<p><strong>{market_name} investment view:</strong> "
                f"{'Constructive breadth and momentum suggest continued risk appetite.' if pos > neg else 'Defensive positioning warranted while breadth recovers.'}"
                f" Cross-check single-name selections against sector flows and macro regime.</p>")
    return "".join(body)


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED LOADER
# ══════════════════════════════════════════════════════════════════════════════

def load_pair(code_a, code_b):
    """Load macro data (parallel) for a country pair."""
    with st.spinner("Loading macroeconomic data from World Bank..."):
        da, ts_a, ya = fetch_country_macro(code_a)
        db, ts_b, yb = fetch_country_macro(code_b)
    return da, db, ts_a, ts_b, ya, yb


def year_tag(latest_years, key):
    y = latest_years.get(key)
    return f"{y} · World Bank" if y else "World Bank"


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

def page_overview():
    hero(
        "Institutional Macro & Markets Research",
        "Global Macro Investment Analyzer",
        "A research terminal bridging macroeconomics and capital markets — "
        "compare 30 economies, screen 80 equities, and generate committee-ready "
        "research in one place.",
    )

    # ── Platform stats ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        data_card("Coverage", f"{len(COUNTRIES)}", "Economies tracked")
    with c2:
        data_card("Indicators", f"{len(WB_INDICATORS)}", "Macro variables")
    with c3:
        data_card("Markets", f"{len(EQUITY_INDICES)}", "Equity indices")
    with c4:
        data_card("Equities", f"{len(DOW30) + len(NIFTY50)}", "Dow 30 + NIFTY 50")

    # ── Global market pulse ──
    pulse = fetch_market_pulse()
    if pulse:
        section_head("Global Market Pulse")
        chips = []
        for name, last, chg in pulse:
            cls = "p-up" if chg >= 0 else "p-dn"
            sign = "▲" if chg >= 0 else "▼"
            chips.append(
                f'<div class="pulse-chip">'
                f'<div class="p-name">{name}</div>'
                f'<div class="p-val">{last:,.0f}</div>'
                f'<div class="p-chg {cls}">{sign} {chg:+.2f}%</div>'
                f'</div>'
            )
        st.markdown(f'<div class="pulse-row">{"".join(chips)}</div>', unsafe_allow_html=True)
        st.caption("Last close vs prior session · Yahoo Finance · refreshed intraday")

    # ── What the platform does ──
    section_head("Platform Overview")
    st.markdown(
        "<p>The platform applies a <strong>quantitative macro framework</strong> to "
        "compare economies, assess investment attractiveness, and translate "
        "macroeconomic signals into market positioning. World Bank macro data and "
        "live equity market intelligence feed a transparent scoring engine and "
        "analytical commentary that together produce research-grade output.</p>",
        unsafe_allow_html=True,
    )

    insight_box(
        "Investment Thesis",
        "<p>Macro is the largest single driver of cross-border return dispersion. "
        "Studies of global equity returns consistently show that <strong>country "
        "selection</strong> often contributes more to portfolio returns than security "
        "selection within a country. This platform frames those country-level decisions "
        "through a quantitative lens.</p>"
        "<p>Pairing macroeconomic data with market-implied signals lets an investor "
        "answer: <strong>which economy offers the better risk-adjusted growth profile? "
        "Which is pricing in too much optimism? Where do macro tailwinds support "
        "multiple expansion?</strong></p>",
    )

    # ── Module directory ──
    section_head("Research Modules")
    modules = [
        ("Global Rankings", "All 30 economies scored, mapped, and ranked on the composite macro framework."),
        ("Country Comparison", "Side-by-side macro snapshot, radar profile, and historical trends for any pair."),
        ("Markets & Performance", "Index performance, drawdowns, volatility, and macro-market alignment."),
        ("Valuation Lab", "Interactive justified-P/E model linking rates, growth, and equity multiples."),
        ("Risk Dashboard", "Composite risk gauges with inflation, debt, FX, and external balance analysis."),
        ("Economic Structure", "GDP decomposition by sector and expenditure with investment implications."),
        ("Scenario Studio", "Stress-test rate, inflation, and growth shocks and read asset-class impact."),
        ("U.S. Equities — Dow 30", "Daily screening, sector heat map, and ranked stock ideas with reasons and risks."),
        ("India Equities — NIFTY 50", "The same institutional screening engine applied to India's benchmark."),
        ("Research Reports", "One-click investment memoranda and committee-ready PDF reports."),
    ]
    cols = st.columns(2)
    for i, (title, desc) in enumerate(modules):
        with cols[i % 2]:
            st.markdown(
                f'<div class="data-card">'
                f'<div class="label">Module {i+1:02d}</div>'
                f'<div class="value" style="font-size:1.02rem;font-family:var(--font-display)">{title}</div>'
                f'<div class="sub" style="margin-top:0.45rem;font-size:0.8rem;font-family:var(--font-body);letter-spacing:0">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Methodology ──
    section_head("Methodology at a Glance")
    st.markdown(
        "<p><strong>Composite macro score (0–100):</strong> starts at 50 and rewards "
        "real growth, contained inflation, healthy labor markets, fiscal headroom, and "
        "external balance — the same transparent rules on every page. "
        "<strong>Equity score (0–100):</strong> blends momentum (1M/3M/YTD), distance "
        "from 52-week high, valuation, yield, beta, and analyst consensus. All scoring "
        "rules are published in-app; nothing is a black box.</p>",
        unsafe_allow_html=True,
    )

    page_disclaimer()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: GLOBAL RANKINGS
# ══════════════════════════════════════════════════════════════════════════════

def page_rankings():
    hero(
        "Module 01",
        "Global Macro Rankings",
        "All 30 tracked economies scored on the composite framework — mapped, "
        "ranked, and screened in one view.",
    )

    with st.spinner("Building the global panel from World Bank data..."):
        panel = fetch_global_panel()

    if panel is None or panel.empty:
        st.info(
            "The World Bank API did not return the global panel just now. "
            "Refresh in a moment — the rest of the platform remains fully available."
        )
        page_disclaimer()
        return

    # Score every economy
    scores, labels = [], []
    for _, r in panel.iterrows():
        d = {k: r.get(k) for k in RANK_INDICATORS}
        s = risk_adjusted_score(d)
        scores.append(s)
        labels.append(score_label(s))
    panel = panel.copy()
    panel["Score"] = scores
    panel["Rating"] = labels
    panel["Flag"] = panel["ISO2"].apply(flag_emoji)
    panel = panel.sort_values("Score", ascending=False).reset_index(drop=True)
    panel.insert(0, "Rank", panel.index + 1)

    # ── Leaders ──
    section_head("Leaders")
    top = panel.iloc[0]
    grow = panel.dropna(subset=["GDP Growth"]).nlargest(1, "GDP Growth")
    lo_inf = panel.dropna(subset=["Inflation"]).nsmallest(1, "Inflation")
    hi_inc = panel.dropna(subset=["GDP per Capita"]).nlargest(1, "GDP per Capita")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        data_card("Top Composite Score", f"{top['Flag']} {top['Country']}",
                  f"{top['Score']}/100 · {top['Rating']}")
    with c2:
        if not grow.empty:
            g = grow.iloc[0]
            data_card("Fastest Growth", f"{g['Flag']} {g['Country']}",
                      f"{g['GDP Growth']:.1f}% real GDP growth")
    with c3:
        if not lo_inf.empty:
            i = lo_inf.iloc[0]
            data_card("Lowest Inflation", f"{i['Flag']} {i['Country']}",
                      f"{i['Inflation']:.1f}% CPI")
    with c4:
        if not hi_inc.empty:
            h = hi_inc.iloc[0]
            data_card("Highest Income", f"{h['Flag']} {h['Country']}",
                      f"${h['GDP per Capita']:,.0f} per capita")

    # ── World map ──
    section_head("World Map")
    show_chart(choropleth_scores(panel))

    # ── Ranking table ──
    section_head("Full Ranking Table")
    tbl = panel[["Rank", "Country", "Score", "Rating", "GDP Growth", "Inflation",
                 "Unemployment", "Government Debt to GDP", "Current Account",
                 "GDP per Capita", "Latest Year"]].copy()
    tbl.columns = ["Rank", "Country", "Score", "Rating", "Growth %", "Inflation %",
                   "Unemp %", "Debt/GDP %", "Cur Acct %", "GDP/Capita $", "Data Year"]

    def _score_style(v):
        try:
            return f"color:{score_color(int(v))};font-weight:700"
        except Exception:
            return ""

    try:
        styled = (tbl.style
                  .format({"Growth %": "{:.1f}", "Inflation %": "{:.1f}",
                           "Unemp %": "{:.1f}", "Debt/GDP %": "{:.0f}",
                           "Cur Acct %": "{:+.1f}", "GDP/Capita $": "{:,.0f}",
                           "Data Year": "{:.0f}"}, na_rep="N/A")
                  .map(_score_style, subset=["Score"])
                  .set_properties(**{"background-color": "#121A2E", "color": "#C6D2E6"}))
        show_df(styled, hide_index=True, height=560)
    except Exception:
        show_df(tbl, hide_index=True, height=560)

    csv = tbl.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Rankings (CSV)", data=csv,
        file_name=f"GMI_Global_Rankings_{datetime.date.today().isoformat()}.csv",
        mime="text/csv",
    )

    # ── Income vs growth scatter ──
    section_head("Development Map — Income vs Growth")
    fig = scatter_income_growth(panel)
    if fig:
        show_chart(fig)
        st.caption("Bubble size = nominal GDP · color = composite macro score · hover for detail")

    takeaway_box(
        "Rankings compress a complex reality into one number — use them as a screening "
        "device, not a verdict. High scorers combine growth with stability; low scorers "
        "usually carry one dominant imbalance (inflation, debt, or external deficits) "
        "that a deeper country-pair comparison will surface."
    )

    page_disclaimer()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: COUNTRY COMPARISON
# ══════════════════════════════════════════════════════════════════════════════

def page_compare(name_a, name_b, code_a, code_b):
    hero(
        "Module 02",
        "Country Comparison",
        "Macro snapshot, radar profile, historical trends, and comparative "
        "analysis for the selected pair.",
    )

    da, db, ts_a, ts_b, ya, yb = load_pair(code_a, code_b)

    # ── Snapshot cards ──
    section_head("Macro Snapshot")
    metrics_to_show = [
        ("GDP", fmt_money, "Nominal, current US$", False),
        ("GDP per Capita", fmt_dollar, "Per capita, current US$", False),
        ("GDP Growth", fmt_pct_simple, "Annual real growth", True),
        ("Inflation", fmt_pct_simple, "Consumer price index", True),
        ("Unemployment", fmt_pct_simple, "Total labor force", True),
        ("Population", fmt_pop, "Total population", False),
    ]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {flag_emoji(code_a)} {name_a}")
        for label, fn, sub, _ in metrics_to_show:
            data_card(label, fn(da.get(label)), f"{sub} · {year_tag(ya, label)}")
    with col2:
        st.markdown(f"#### {flag_emoji(code_b)} {name_b}")
        for label, fn, sub, _ in metrics_to_show:
            data_card(label, fn(db.get(label)), f"{sub} · {year_tag(yb, label)}")

    # ── Radar profile ──
    section_head("Macro Profile Radar")
    show_chart(radar_compare(RADAR_DIMS, radar_values(da), radar_values(db),
                             name_a, name_b))
    st.caption("Each axis normalized 0–100 across typical global ranges · higher is stronger")

    # ── Historical trends ──
    section_head("Historical Trends")
    chart_specs = [
        ("GDP", ",.0s"),
        ("GDP per Capita", "$,.0f"),
        ("GDP Growth", ".1f"),
        ("Inflation", ".1f"),
        ("Unemployment", ".1f"),
        ("Government Debt to GDP", ".0f"),
    ]
    for i in range(0, len(chart_specs), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(chart_specs):
                break
            label, yfmt = chart_specs[idx]
            with col:
                yrs_a, va = ts_a.get(label, ([], []))
                yrs_b, vb = ts_b.get(label, ([], []))
                show_chart(line_chart(yrs_a, va, yrs_b, vb, name_a, name_b, label, yfmt))

    # ── Download snapshot ──
    snap = pd.DataFrame({
        "Indicator": list(WB_INDICATORS.keys()),
        name_a: [da.get(k) for k in WB_INDICATORS],
        name_b: [db.get(k) for k in WB_INDICATORS],
    })
    st.download_button(
        "Download Snapshot (CSV)",
        data=snap.to_csv(index=False).encode("utf-8"),
        file_name=f"GMI_Snapshot_{code_a}_vs_{code_b}.csv",
        mime="text/csv",
    )

    # ── Commentary ──
    section_head("Comparative Analysis")
    insight_box("Macro Commentary", commentary_country_compare(name_a, name_b, da, db))

    sa = risk_adjusted_score(da)
    sb = risk_adjusted_score(db)
    winner = name_a if sa > sb else name_b
    takeaway_box(
        f"On a composite risk-adjusted basis, <strong>{winner}</strong> screens more "
        f"favorably ({max(sa,sb)}/100 vs {min(sa,sb)}/100). Growth-oriented allocators "
        f"should weigh the GDP growth differential, while stability-focused mandates "
        f"should emphasize inflation control and fiscal headroom."
    )

    page_disclaimer()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: MARKETS & PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════

def page_markets(name_a, name_b, code_a, code_b):
    hero(
        "Module 03",
        "Markets & Performance",
        "Benchmark index performance, drawdowns, volatility, and macro-market "
        "alignment for the selected pair.",
    )

    if not HAS_YFINANCE:
        st.warning("Live market data requires the 'yfinance' library. "
                   "Install it with: pip install yfinance")
        page_disclaimer()
        return

    if code_a not in EQUITY_INDICES or code_b not in EQUITY_INDICES:
        st.info(
            "Equity index coverage is not available for one or both selections. "
            "Try countries with major benchmark indices (US, IN, JP, DE, GB, FR, etc.)."
        )
        page_disclaimer()
        return

    ticker_a, idx_name_a = EQUITY_INDICES[code_a]
    ticker_b, idx_name_b = EQUITY_INDICES[code_b]

    period = st.select_slider("Lookback Period", options=["1y", "2y", "5y", "10y"], value="5y")

    with st.spinner("Fetching equity index data..."):
        dates_a, vals_a = fetch_equity_index(ticker_a, period=period)
        dates_b, vals_b = fetch_equity_index(ticker_b, period=period)

    if not vals_a and not vals_b:
        st.error("Could not retrieve market data. Please try again in a moment.")
        page_disclaimer()
        return

    # ── Snapshot ──
    section_head("Benchmark Index Snapshot")
    col1, col2 = st.columns(2)
    with col1:
        if vals_a:
            ret_a_hdr = (vals_a[-1] / vals_a[0] - 1) * 100
            data_card(idx_name_a, f"{vals_a[-1]:,.0f}",
                      f"{name_a} benchmark",
                      delta=f"{ret_a_hdr:+.1f}% over {period}",
                      delta_positive=ret_a_hdr >= 0)
        else:
            data_card(idx_name_a, "N/A", "data unavailable")
    with col2:
        if vals_b:
            ret_b_hdr = (vals_b[-1] / vals_b[0] - 1) * 100
            data_card(idx_name_b, f"{vals_b[-1]:,.0f}",
                      f"{name_b} benchmark",
                      delta=f"{ret_b_hdr:+.1f}% over {period}",
                      delta_positive=ret_b_hdr >= 0)
        else:
            data_card(idx_name_b, "N/A", "data unavailable")

    # ── Indexed performance + drawdown ──
    section_head("Indexed Performance (Start = 100)")
    show_chart(normalized_index_chart(dates_a, vals_a, dates_b, vals_b,
                                      idx_name_a, idx_name_b,
                                      f"{idx_name_a} vs {idx_name_b}"))

    section_head("Drawdown Analysis")
    show_chart(drawdown_chart(dates_a, vals_a, dates_b, vals_b, idx_name_a, idx_name_b))

    # ── Risk & return metrics ──
    def daily_returns(vals):
        if len(vals) < 2:
            return []
        return [(vals[i] / vals[i - 1] - 1) for i in range(1, len(vals))]

    def annualized_vol(rets):
        if len(rets) < 2:
            return None
        mean = sum(rets) / len(rets)
        var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
        return math.sqrt(var) * math.sqrt(252) * 100

    def max_drawdown(vals):
        if not vals:
            return None
        peak, mdd = vals[0], 0.0
        for v in vals:
            peak = max(peak, v)
            mdd = min(mdd, (v / peak - 1) * 100)
        return mdd

    rets_a = daily_returns(vals_a)
    rets_b = daily_returns(vals_b)
    vol_a = annualized_vol(rets_a)
    vol_b = annualized_vol(rets_b)
    total_ret_a = (vals_a[-1] / vals_a[0] - 1) * 100 if vals_a else None
    total_ret_b = (vals_b[-1] / vals_b[0] - 1) * 100 if vals_b else None
    mdd_a = max_drawdown(vals_a)
    mdd_b = max_drawdown(vals_b)
    yrs = {"1y": 1, "2y": 2, "5y": 5, "10y": 10}[period]

    section_head("Risk & Return Metrics")
    rcol1, rcol2 = st.columns(2)
    for col, idx_name, tot, vol, mdd in [
        (rcol1, idx_name_a, total_ret_a, vol_a, mdd_a),
        (rcol2, idx_name_b, total_ret_b, vol_b, mdd_b),
    ]:
        with col:
            st.markdown(f"#### {idx_name}")
            data_card("Total Return", f"{tot:+.1f}%" if tot is not None else "N/A", f"Over {period}")
            if tot is not None:
                ann_ret = ((1 + tot / 100) ** (1 / yrs) - 1) * 100
                data_card("Annualized Return", f"{ann_ret:+.1f}%", "Geometric mean")
            data_card("Annualized Volatility", f"{vol:.1f}%" if vol else "N/A", "Daily returns × √252")
            data_card("Max Drawdown", f"{mdd:.1f}%" if mdd is not None else "N/A", "Peak-to-trough")
            if tot is not None and vol and vol > 0:
                ann_ret = ((1 + tot / 100) ** (1 / yrs) - 1) * 100
                data_card("Return / Volatility", f"{ann_ret / vol:.2f}",
                          "Ann. return ÷ ann. volatility")

    # ── Correlation ──
    try:
        sa_ser = pd.Series(vals_a, index=pd.to_datetime(dates_a)).pct_change()
        sb_ser = pd.Series(vals_b, index=pd.to_datetime(dates_b)).pct_change()
        joined = pd.concat([sa_ser, sb_ser], axis=1, join="inner").dropna()
        corr = float(joined.corr().iloc[0, 1]) if len(joined) > 30 else None
    except Exception:
        corr = None
    if corr is not None:
        c1, _ = st.columns([1, 1])
        with c1:
            data_card("Cross-Market Correlation", f"{corr:.2f}",
                      "Daily returns · diversification signal")

    # ── Commentary ──
    da, db, _, _, _, _ = load_pair(code_a, code_b)
    section_head("Macro–Market Linkage")
    insight_box(
        "Markets Commentary",
        commentary_markets(name_a, name_b, total_ret_a, total_ret_b, vol_a, vol_b, da, db),
    )

    if total_ret_a is not None and total_ret_b is not None:
        better_mkt = name_a if total_ret_a > total_ret_b else name_b
        takeaway_box(
            f"<strong>{better_mkt}</strong> has delivered the stronger equity return "
            f"over the trailing {period}. Investors should evaluate whether this "
            f"outperformance reflects sustainable earnings power, multiple expansion, "
            f"or temporary risk sentiment — a key distinction for forward positioning."
        )

    page_disclaimer()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: VALUATION LAB
# ══════════════════════════════════════════════════════════════════════════════

def page_valuation(name_a, name_b, code_a, code_b):
    hero(
        "Module 04",
        "Valuation Lab",
        "An interactive framework linking macro variables to equity multiples — "
        "seeded with live data for the selected pair.",
    )

    da, db, ts_a, ts_b, ya, yb = load_pair(code_a, code_b)

    section_head("Valuation-Relevant Indicators")
    val_metrics = [
        ("GDP Growth", fmt_pct_simple, "Real growth rate"),
        ("Inflation", fmt_pct_simple, "CPI inflation"),
        ("Lending Rate", fmt_pct_simple, "Commercial lending rate"),
        ("Real Interest Rate", fmt_pct_simple, "Inflation-adjusted"),
    ]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {flag_emoji(code_a)} {name_a}")
        for lbl, fn, sub in val_metrics:
            data_card(lbl, fn(da.get(lbl)), f"{sub} · {year_tag(ya, lbl)}")
    with col2:
        st.markdown(f"#### {flag_emoji(code_b)} {name_b}")
        for lbl, fn, sub in val_metrics:
            data_card(lbl, fn(db.get(lbl)), f"{sub} · {year_tag(yb, lbl)}")

    # ── Interactive justified P/E model ──
    section_head("Interactive Model — Justified P/E")
    st.markdown(
        "<p>The justified P/E from the Gordon Growth model is "
        "<strong>P/E = payout × (1 + g) ÷ (kₑ − g)</strong>, where the cost of equity "
        "kₑ = risk-free rate + equity risk premium. Adjust the assumptions below to see "
        "how rates and growth drive multiples for each economy.</p>",
        unsafe_allow_html=True,
    )

    def seed_rf(d):
        v = d.get("Lending Rate")
        if v is None:
            v = 4.0
        return float(max(0.5, min(12.0, round(v, 1))))

    def seed_g(d):
        v = d.get("GDP Growth")
        if v is None:
            v = 2.5
        return float(max(0.5, min(6.0, round(v, 1))))

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        rf_a = st.slider(f"Risk-free — {name_a} (%)", 0.5, 12.0, seed_rf(da), 0.1)
    with s2:
        rf_b = st.slider(f"Risk-free — {name_b} (%)", 0.5, 12.0, seed_rf(db), 0.1)
    with s3:
        erp = st.slider("Equity risk premium (%)", 2.0, 9.0, 5.0, 0.25)
    with s4:
        payout = st.slider("Payout ratio (%)", 20, 80, 45, 5)

    def justified_pe(rf, g):
        ke = rf + erp
        if ke - g <= 0.4:
            return None
        return (payout / 100.0) * (1 + g / 100.0) / ((ke - g) / 100.0)

    g_a, g_b = seed_g(da), seed_g(db)
    pe_a = justified_pe(rf_a, g_a)
    pe_b = justified_pe(rf_b, g_b)

    m1, m2 = st.columns(2)
    with m1:
        data_card(f"Implied P/E — {name_a}",
                  f"{pe_a:.1f}×" if pe_a else "N/M",
                  f"kₑ {rf_a + erp:.1f}% · g {g_a:.1f}% · payout {payout}%")
    with m2:
        data_card(f"Implied P/E — {name_b}",
                  f"{pe_b:.1f}×" if pe_b else "N/M",
                  f"kₑ {rf_b + erp:.1f}% · g {g_b:.1f}% · payout {payout}%")

    show_chart(pe_sensitivity_heatmap(payout, erp))
    st.caption("Growth seeded from each economy's latest real GDP growth · N/M where growth approaches the cost of equity")

    # ── Commentary ──
    section_head("Macro to Valuation Framework")
    insight_box("Valuation Commentary", commentary_valuation(name_a, name_b, da, db))

    # ── Educational frameworks ──
    section_head("Educational Frameworks")
    t1, t2, t3 = st.tabs(["DCF Linkage", "P/E and Rates", "Equity Risk Premium"])
    with t1:
        st.markdown(
            "<p><strong>Discounted Cash Flow logic:</strong> Firm value equals the present "
            "value of future free cash flows discounted at the weighted average cost of "
            "capital (WACC). Both terms are macro-sensitive: future cash flows scale "
            "with nominal GDP growth, while WACC moves with the risk-free rate "
            "(set largely by central bank policy and inflation expectations).</p>"
            "<p>A 100 bps rise in the risk-free rate, holding all else constant, can "
            "compress fair value by 10-20% for long-duration growth equities, and far less "
            "for stable, near-term cash generators. This is why <strong>duration matching "
            "matters at the portfolio level.</strong></p>",
            unsafe_allow_html=True,
        )
    with t2:
        st.markdown(
            "<p><strong>P/E and rates inverse relationship:</strong> Empirically, market "
            "P/E multiples and real interest rates tend to be inversely correlated. "
            "Periods of low real rates (post-2008, 2020-2021) supported elevated "
            "multiples; rate normalization (2022-2023) drove broad multiple compression "
            "across global equities.</p>"
            "<p>The mechanism: lower discount rates increase the present value of future "
            "cash flows, particularly the terminal value, which often represents 60-80% "
            "of intrinsic value in DCF models.</p>",
            unsafe_allow_html=True,
        )
    with t3:
        st.markdown(
            "<p><strong>Equity Risk Premium (ERP) = Earnings Yield − Risk-Free Rate.</strong> "
            "A widening ERP suggests equities are pricing in more risk relative to bonds; "
            "a compressed ERP signals investor optimism (or complacency).</p>"
            "<p>Cross-country, ERPs vary with sovereign risk, currency stability, "
            "institutional quality, and capital market depth. Emerging markets typically "
            "command higher ERPs to compensate for these risks.</p>",
            unsafe_allow_html=True,
        )

    takeaway_box(
        "Macro variables don't just describe the economy — they directly determine the "
        "discount rate and cash flow growth assumptions in every valuation model. A "
        "rigorous investment process always cross-checks bottom-up valuation work "
        "against the prevailing macro regime."
    )

    page_disclaimer()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: RISK DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def page_risk(name_a, name_b, code_a, code_b):
    hero(
        "Module 05",
        "Risk Dashboard",
        "Composite macro risk gauges with inflation, debt, currency, and "
        "external balance analysis.",
    )

    da, db, ts_a, ts_b, ya, yb = load_pair(code_a, code_b)

    # ── Composite gauges ──
    section_head("Risk-Adjusted Macro Score")
    sa = risk_adjusted_score(da)
    sb = risk_adjusted_score(db)
    col1, col2 = st.columns(2)
    with col1:
        show_chart(gauge_chart(sa, f"{name_a} · {score_label(sa)}", score_color(sa)))
    with col2:
        show_chart(gauge_chart(sb, f"{name_b} · {score_label(sb)}", score_color(sb)))

    # ── Radar ──
    section_head("Risk Factor Radar")
    show_chart(radar_compare(RADAR_DIMS, radar_values(da), radar_values(db),
                             name_a, name_b, title="Normalized Risk Dimensions"))

    # ── Risk factor table ──
    section_head("Risk Factor Breakdown")
    risk_metrics = [
        ("Inflation", "Inflation", "%"),
        ("Unemployment", "Unemployment", "%"),
        ("Government Debt to GDP", "Govt Debt/GDP", "%"),
        ("Current Account", "Current Account/GDP", "%"),
        ("Real Interest Rate", "Real Interest Rate", "%"),
    ]
    table_md = "| Indicator | " + name_a + " | " + name_b + " |\n"
    table_md += "|---|---|---|\n"
    for key, lbl, suf in risk_metrics:
        va = da.get(key)
        vb = db.get(key)
        va_s = f"{va:.1f}{suf}" if va is not None else "N/A"
        vb_s = f"{vb:.1f}{suf}" if vb is not None else "N/A"
        table_md += f"| {lbl} | {va_s} | {vb_s} |\n"
    st.markdown(table_md)

    # ── Inflation trend ──
    section_head("Inflation Trend (Historical)")
    yrs_a, va = ts_a.get("Inflation", ([], []))
    yrs_b, vb = ts_b.get("Inflation", ([], []))
    show_chart(line_chart(yrs_a, va, yrs_b, vb, name_a, name_b, "Inflation (%)", ".1f"))

    # ── FX risk ──
    if HAS_YFINANCE:
        section_head("Currency Risk (FX vs USD)")
        cur_a = COUNTRY_CURRENCIES.get(code_a, "USD")
        cur_b = COUNTRY_CURRENCIES.get(code_b, "USD")
        with st.spinner("Fetching FX data..."):
            fx_a_dates, fx_a_vals = fetch_fx_rate(cur_a)
            fx_b_dates, fx_b_vals = fetch_fx_rate(cur_b)
        if fx_a_vals or fx_b_vals:
            show_chart(normalized_index_chart(
                fx_a_dates, fx_a_vals, fx_b_dates, fx_b_vals,
                f"{cur_a}/USD", f"{cur_b}/USD",
                "Currency Performance vs USD (Indexed)",
            ))
            st.caption("A falling line = depreciation vs the U.S. dollar over the window")
        else:
            st.caption("FX data unavailable for the selected currencies.")

    # ── Commentary ──
    section_head("Risk Assessment")
    insight_box("Risk Commentary", commentary_risk(name_a, name_b, da, db))

    winner = name_a if sa > sb else name_b
    takeaway_box(
        f"On a risk-adjusted composite, <strong>{winner}</strong> presents the more "
        f"attractive macro risk profile. This does not mean it is risk-free — only "
        f"that the balance of inflation, fiscal, labor, and external indicators is "
        f"more favorable at present. Risk profiles can shift quickly with monetary "
        f"policy or geopolitical developments."
    )

    page_disclaimer()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: ECONOMIC STRUCTURE
# ══════════════════════════════════════════════════════════════════════════════

def page_structure(name_a, name_b, code_a, code_b):
    hero(
        "Module 06",
        "Economic Structure",
        "Decomposition of GDP by sector and expenditure components with "
        "investment implications.",
    )

    da, db, _, _, ya, yb = load_pair(code_a, code_b)

    # ── Sector donuts ──
    section_head("Sector Composition (% of GDP)")
    labels = ["Agriculture", "Industry", "Services"]
    col1, col2 = st.columns(2)
    with col1:
        vals = [
            da.get("Agriculture % GDP", 0) or 0,
            da.get("Industry % GDP", 0) or 0,
            da.get("Services % GDP", 0) or 0,
        ]
        show_chart(donut_chart(labels, vals, f"{flag_emoji(code_a)} {name_a}"))
    with col2:
        vals_b = [
            db.get("Agriculture % GDP", 0) or 0,
            db.get("Industry % GDP", 0) or 0,
            db.get("Services % GDP", 0) or 0,
        ]
        show_chart(donut_chart(labels, vals_b, f"{flag_emoji(code_b)} {name_b}"))

    # ── Expenditure side ──
    section_head("GDP Expenditure Components")
    exp_labels = ["Household<br>Consumption", "Govt<br>Spending", "Investment", "Exports", "Imports"]
    exp_keys = [
        "Household Consumption % GDP",
        "Government Spending % GDP",
        "Investment % GDP",
        "Exports % GDP",
        "Imports % GDP",
    ]
    va_exp = [da.get(k) or 0 for k in exp_keys]
    vb_exp = [db.get(k) or 0 for k in exp_keys]
    show_chart(grouped_bar(exp_labels, va_exp, vb_exp, name_a, name_b,
                           "Expenditure Side of GDP (% of GDP)"))

    # ── Trade openness ──
    section_head("Trade Openness")
    open_a = (da.get("Exports % GDP") or 0) + (da.get("Imports % GDP") or 0)
    open_b = (db.get("Exports % GDP") or 0) + (db.get("Imports % GDP") or 0)
    c1, c2 = st.columns(2)
    with c1:
        data_card(f"{name_a} — Trade / GDP", f"{open_a:.0f}%",
                  "Exports + imports as % of GDP")
    with c2:
        data_card(f"{name_b} — Trade / GDP", f"{open_b:.0f}%",
                  "Exports + imports as % of GDP")

    # ── Commentary ──
    section_head("Structural Analysis")
    insight_box("Sector Commentary", commentary_sectors(name_a, name_b, da, db))

    takeaway_box(
        "Economic structure shapes which sectors dominate equity benchmarks and where "
        "long-term productivity gains will emerge. Service-heavy economies tend to host "
        "deeper financial and consumer-discretionary sectors, while industry-heavy "
        "economies offer more cyclical exposure to global trade and capital spending cycles."
    )

    page_disclaimer()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: SCENARIO STUDIO
# ══════════════════════════════════════════════════════════════════════════════

SCENARIOS = {
    "Interest rates rise 100 bps": {
        "body": (
            "<p><strong>Mechanism:</strong> A 100 bps hike in policy rates raises the "
            "discount rate across all fixed income and equity valuation models.</p>"
            "<p><strong>Equity impact:</strong> Long-duration growth stocks (tech, "
            "biotech, REITs) face the steepest multiple compression — historically "
            "5-15% derating per 100 bps. Value sectors (financials, energy, materials) "
            "tend to outperform.</p>"
            "<p><strong>Fixed income impact:</strong> Bond prices fall; longer-duration "
            "Treasuries/sovereigns lose more. Credit spreads typically widen modestly.</p>"
            "<p><strong>Cross-country:</strong> The economy with the higher pre-existing "
            "debt service burden faces sharper growth headwinds.</p>"
        ),
        "impact": [
            ("Growth equities", "neg", "Multiple compression on higher discount rates"),
            ("Value equities", "pos", "Financials benefit from wider margins"),
            ("Government bonds", "neg", "Prices fall as yields reset higher"),
            ("Credit", "neg", "Spreads widen modestly"),
            ("EM currencies", "neg", "Dollar strength pressures EM FX"),
            ("Cash / short duration", "pos", "Higher carry with minimal duration risk"),
        ],
    },
    "Inflation declines 200 bps": {
        "body": (
            "<p><strong>Mechanism:</strong> Declining inflation gives central banks "
            "scope to ease policy, lowering the risk-free rate and lifting valuations.</p>"
            "<p><strong>Equity impact:</strong> Multiple expansion — particularly for "
            "long-duration growth stocks. Real assets (TIPS, commodities) underperform.</p>"
            "<p><strong>Fixed income impact:</strong> Bond rally, credit spreads tighten, "
            "duration outperforms.</p>"
            "<p><strong>Cross-country:</strong> The economy with higher current "
            "inflation has more room to benefit from disinflation.</p>"
        ),
        "impact": [
            ("Growth equities", "pos", "Multiple expansion as discount rates fall"),
            ("Value equities", "neu", "Participates but lags growth"),
            ("Government bonds", "pos", "Duration rallies on easing expectations"),
            ("Credit", "pos", "Spreads tighten with risk appetite"),
            ("Commodities / TIPS", "neg", "Inflation hedges lose their bid"),
            ("EM currencies", "pos", "Carry trades revive as volatility falls"),
        ],
    },
    "GDP growth slows 150 bps": {
        "body": (
            "<p><strong>Mechanism:</strong> Slowing growth weighs on corporate earnings "
            "and consumer spending. Cyclicals derate first.</p>"
            "<p><strong>Equity impact:</strong> Cyclical sectors (consumer discretionary, "
            "industrials, materials) underperform. Defensive sectors (staples, utilities, "
            "healthcare) outperform on a relative basis.</p>"
            "<p><strong>Fixed income impact:</strong> Bond yields fall as growth "
            "expectations decline. Quality credit outperforms.</p>"
        ),
        "impact": [
            ("Cyclical equities", "neg", "Earnings downgrades lead the derating"),
            ("Defensive equities", "pos", "Relative outperformance in slowdowns"),
            ("Government bonds", "pos", "Yields fall with growth expectations"),
            ("High-yield credit", "neg", "Default risk premia widen"),
            ("Commodities", "neg", "Demand outlook softens"),
            ("Quality factor", "pos", "Balance-sheet strength gets rewarded"),
        ],
    },
    "Recession scenario (-2% growth)": {
        "body": (
            "<p><strong>Mechanism:</strong> Outright contraction drives broad earnings "
            "downgrades, credit deterioration, and risk-off positioning.</p>"
            "<p><strong>Equity impact:</strong> Historically, equities draw down "
            "20-35% in recessions. Defensive sectors lose less; cyclicals lose more.</p>"
            "<p><strong>Fixed income impact:</strong> Government bonds rally hard "
            "(flight to quality); high-yield credit spreads widen sharply.</p>"
            "<p><strong>Policy response:</strong> Central banks typically cut rates "
            "aggressively, providing eventual support for risk assets.</p>"
        ),
        "impact": [
            ("Equities (broad)", "neg", "Historical recession drawdowns of 20-35%"),
            ("Government bonds", "pos", "Flight-to-quality rally"),
            ("High-yield credit", "neg", "Spreads widen sharply on default risk"),
            ("Gold / safe havens", "pos", "Defensive bid strengthens"),
            ("EM assets", "neg", "Capital flight amplifies losses"),
            ("Cash", "pos", "Optionality for trough deployment"),
        ],
    },
    "Risk-off / flight to quality": {
        "body": (
            "<p><strong>Mechanism:</strong> Investor risk appetite collapses; capital "
            "flows from risky assets to safe havens.</p>"
            "<p><strong>Equity impact:</strong> Emerging markets and small caps "
            "underperform; large-cap quality outperforms. EM currencies weaken.</p>"
            "<p><strong>Fixed income:</strong> US Treasuries, German Bunds, Japanese "
            "JGBs, gold, and CHF/JPY typically rally.</p>"
        ),
        "impact": [
            ("Large-cap quality", "neu", "Relative safety within equities"),
            ("Small caps / EM equity", "neg", "First assets sold in de-risking"),
            ("US Treasuries / Bunds", "pos", "Core safe-haven rally"),
            ("Gold", "pos", "Classic risk-off hedge"),
            ("EM currencies", "neg", "Capital flight pressure"),
            ("CHF / JPY", "pos", "Funding currencies strengthen"),
        ],
    },
    "Soft landing (gradual easing)": {
        "body": (
            "<p><strong>Mechanism:</strong> Inflation normalizes without recession; "
            "central banks ease gradually. Goldilocks regime for risk assets.</p>"
            "<p><strong>Equity impact:</strong> Broad rally across sectors, with growth "
            "and cyclicals leading. Multiple expansion likely.</p>"
            "<p><strong>Fixed income:</strong> Modest bond rally, credit spreads tighten "
            "to cycle lows.</p>"
        ),
        "impact": [
            ("Equities (broad)", "pos", "Goldilocks backdrop lifts multiples"),
            ("Growth & cyclicals", "pos", "Lead the rally"),
            ("Government bonds", "pos", "Modest duration tailwind"),
            ("Credit", "pos", "Spreads grind to cycle tights"),
            ("Volatility", "neg", "Vol sellers dominate"),
            ("Cash", "neg", "Underperforms risk assets"),
        ],
    },
}


def page_scenario(name_a, name_b, code_a, code_b):
    hero(
        "Module 07",
        "Scenario Studio",
        "Stress-test macro assumptions and read the implied asset-class and "
        "cross-country impact.",
    )

    da, db, _, _, _, _ = load_pair(code_a, code_b)

    section_head("Scenario Configuration")
    scenario = st.selectbox("Select Scenario", list(SCENARIOS.keys()))
    spec = SCENARIOS[scenario]

    section_head("Transmission Mechanism")
    insight_box(f"Scenario: {scenario}", spec["body"])

    # ── Asset-class impact grid ──
    section_head("Illustrative Asset-Class Impact")
    rows_html = []
    for asset, direction, note in spec["impact"]:
        badge_cls = {"pos": "badge-pos", "neg": "badge-neg", "neu": "badge-neu"}[direction]
        badge_txt = {"pos": "Positive", "neg": "Negative", "neu": "Neutral"}[direction]
        rows_html.append(
            f'<div class="data-card" style="margin-bottom:0.55rem">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:0.8rem;flex-wrap:wrap">'
            f'<div>'
            f'<div class="label" style="margin-bottom:0.2rem">{asset}</div>'
            f'<div class="sub" style="font-family:var(--font-body);letter-spacing:0;font-size:0.8rem">{note}</div>'
            f'</div>'
            f'<span class="badge {badge_cls}">{badge_txt}</span>'
            f'</div></div>'
        )
    st.markdown("".join(rows_html), unsafe_allow_html=True)
    st.caption("Directional and illustrative — grounded in typical historical regime behavior, not a forecast")

    # ── Cross-country exposure ──
    section_head("Cross-Country Exposure")
    if scenario == "Interest rates rise 100 bps":
        worse = name_a if (da.get("Government Debt to GDP") or 0) > (db.get("Government Debt to GDP") or 0) else name_b
        take = (
            f"In a rate-hike scenario, <strong>{worse}</strong> faces relatively "
            f"greater fiscal stress given its heavier debt burden. Defensive equity "
            f"positioning and shorter-duration bonds are typically warranted."
        )
    elif scenario == "Inflation declines 200 bps":
        better = name_a if (da.get("Inflation") or 0) > (db.get("Inflation") or 0) else name_b
        take = (
            f"<strong>{better}</strong> stands to benefit more from disinflation given "
            f"its higher starting inflation. Long-duration growth equity exposure is "
            f"the highest-conviction trade in this scenario."
        )
    elif scenario == "GDP growth slows 150 bps":
        worse = name_a if (da.get("GDP Growth") or 0) < (db.get("GDP Growth") or 0) else name_b
        take = (
            f"<strong>{worse}</strong>'s already slower growth path makes it more "
            f"vulnerable to a further deceleration. Defensive equity tilt and quality "
            f"credit positioning are warranted across both economies."
        )
    elif scenario == "Recession scenario (-2% growth)":
        take = (
            "In a recession, capital preservation dominates. Underweight cyclicals, "
            "overweight quality and government bonds, and maintain dry powder for "
            "deployment at trough valuations."
        )
    elif scenario == "Risk-off / flight to quality":
        em_country = name_a if (da.get("GDP per Capita") or 0) < (db.get("GDP per Capita") or 0) else name_b
        take = (
            f"<strong>{em_country}</strong> (the lower per-capita income economy) is "
            f"more vulnerable in a risk-off episode given typical EM capital flight "
            f"dynamics. Hedge currency exposure or rotate into developed-market quality."
        )
    else:
        take = (
            "A soft-landing environment is the most constructive backdrop for risk "
            "assets. Overweight equities, underweight cash, maintain balanced duration "
            "in fixed income."
        )
    takeaway_box(take)

    page_disclaimer()


# ══════════════════════════════════════════════════════════════════════════════
#  EQUITIES PAGES  —  shared engine for Dow 30 and NIFTY 50
# ══════════════════════════════════════════════════════════════════════════════

def render_equities_page(market_name, tickers, currency_symbol, module_num, session_key):
    hero(
        f"Module {module_num}",
        f"{market_name} Equities",
        "Refreshed screening dashboard with sector heat map, transparent scoring, "
        "and ranked stock ideas with stated reasons and risks.",
    )

    if not HAS_YFINANCE:
        st.error("This module requires the 'yfinance' library. Install with: pip install yfinance")
        page_disclaimer()
        return

    with st.spinner(f"Fetching {market_name} market data (batched)..."):
        rows, failed = fetch_stock_data(tuple(tickers), market_name)

    if not rows:
        st.warning("Unable to fetch live stock data right now. Please try again shortly — "
                   "market data providers occasionally rate-limit shared cloud hosts.")
        page_disclaimer()
        return
    if failed:
        st.caption(f"Data unavailable for {len(failed)} ticker(s): "
                   f"{', '.join(failed[:8])}{'...' if len(failed) > 8 else ''}")

    calculate_stock_score(rows)
    df = pd.DataFrame(rows)
    peer_medians = compute_peer_medians(df)

    # ── Breadth ──
    section_head("Market Breadth Snapshot")
    pos = int((df["Daily %"] > 0).sum())
    neg = int((df["Daily %"] < 0).sum())
    avg_daily = float(df["Daily %"].mean())
    avg_1m_s = df["1M %"].dropna()
    avg_1m = float(avg_1m_s.mean()) if not avg_1m_s.empty else None
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        data_card("Advancers", f"{pos}/{len(df)}", "Up today")
    with c2:
        data_card("Decliners", f"{neg}/{len(df)}", "Down today")
    with c3:
        data_card("Avg Daily Move", f"{avg_daily:+.2f}%", "Universe mean")
    with c4:
        data_card("Avg 1M Return", f"{avg_1m:+.1f}%" if avg_1m is not None else "N/A", "Trailing month")

    # ── Sector heat map ──
    fig_tree = treemap_market(df, currency_symbol,
                              f"{market_name} Sector Heat Map — size = market cap, color = daily move")
    if fig_tree:
        section_head("Sector Heat Map")
        show_chart(fig_tree)

    # ── Filters + search ──
    section_head("Screening Table")
    fc1, fc2 = st.columns([2, 1])
    with fc1:
        flt = st.selectbox(
            "Screen",
            ["All stocks", "Top daily gainers", "Top 5-day performers",
             "Top 1-month performers", "Undervalued (low P/E)",
             "High dividend yield", "Low-beta defensive", "Near 52-week high",
             "Pullback opportunities"],
            key=f"flt_{session_key}",
        )
    with fc2:
        query = st.text_input("Search ticker or name", "", key=f"q_{session_key}",
                              placeholder="e.g. AAPL")

    view = df.copy()
    try:
        if flt == "Top daily gainers":
            view = view.sort_values("Daily %", ascending=False).head(10)
        elif flt == "Top 5-day performers":
            view = view.sort_values("5D %", ascending=False).head(10)
        elif flt == "Top 1-month performers":
            view = view.sort_values("1M %", ascending=False).head(10)
        elif flt == "Undervalued (low P/E)":
            view = view[view["P/E"].notna() & (view["P/E"] > 0)].sort_values("P/E").head(10)
        elif flt == "High dividend yield":
            view = view[view["Div Yield %"].notna()].sort_values("Div Yield %", ascending=False).head(10)
        elif flt == "Low-beta defensive":
            view = view[view["Beta"].notna()].sort_values("Beta").head(10)
        elif flt == "Near 52-week high":
            view = view[view["From High %"].notna()].sort_values("From High %", ascending=False).head(10)
        elif flt == "Pullback opportunities":
            view = view[view["From High %"].notna()].sort_values("From High %").head(10)
    except Exception:
        view = df
    if query:
        q = query.strip().lower()
        try:
            view = view[view["Ticker"].str.lower().str.contains(q) |
                        view["Name"].str.lower().str.contains(q)]
        except Exception:
            pass

    cols = ["Ticker", "Name", "Price", "Daily %", "5D %", "1M %", "3M %", "YTD %",
            "From High %", "Market Cap", "P/E", "Div Yield %", "Beta", "Score"]
    display_df = view[cols].copy()

    def color_returns(v):
        if pd.isna(v):
            return "color:#96A2B8"
        try:
            v = float(v)
        except Exception:
            return ""
        if v > 0:
            return "color:#34D399;font-weight:600"
        if v < 0:
            return "color:#F87171;font-weight:600"
        return "color:#C6D2E6"

    try:
        styled = (display_df.style
                  .format({
                      "Price": (currency_symbol + "{:,.2f}"),
                      "Daily %": "{:+.2f}%", "5D %": "{:+.1f}%", "1M %": "{:+.1f}%",
                      "3M %": "{:+.1f}%", "YTD %": "{:+.1f}%", "From High %": "{:+.1f}%",
                      "Market Cap": lambda x: fmt_mcap(x, currency_symbol),
                      "P/E": "{:.1f}", "Div Yield %": "{:.2f}%", "Beta": "{:.2f}",
                      "Score": "{:.1f}",
                  }, na_rep="N/A")
                  .map(color_returns, subset=["Daily %", "5D %", "1M %", "3M %", "YTD %", "From High %"])
                  .set_properties(**{"background-color": "#121A2E", "color": "#C6D2E6"}))
        show_df(styled, hide_index=True)
    except Exception:
        show_df(display_df, hide_index=True)

    st.download_button(
        f"Download {market_name} Data (CSV)",
        data=df[cols].to_csv(index=False).encode("utf-8"),
        file_name=f"GMI_{session_key}_{datetime.date.today().isoformat()}.csv",
        mime="text/csv",
    )

    # ── Charts ──
    section_head("Performance Charts")
    tabs = st.tabs(["Daily Returns", "1-Month Returns", "Market Cap", "Risk-Return"])

    with tabs[0]:
        d = df.dropna(subset=["Daily %"]).sort_values("Daily %", ascending=True)
        colors = [COLOR_POS if v > 0 else COLOR_NEG for v in d["Daily %"]]
        fig = go.Figure(go.Bar(x=d["Daily %"], y=d["Ticker"], orientation="h",
                               marker_color=colors,
                               text=[f"{v:+.2f}%" for v in d["Daily %"]],
                               textposition="outside",
                               textfont=dict(color="#FFFFFF", size=10, family=MONO_STACK)))
        fig.update_layout(**base_layout("Daily % Change", height=max(620, 15 * len(d))))
        show_chart(fig)

    with tabs[1]:
        d = df.dropna(subset=["1M %"]).sort_values("1M %", ascending=True)
        colors = [COLOR_POS if v > 0 else COLOR_NEG for v in d["1M %"]]
        fig = go.Figure(go.Bar(x=d["1M %"], y=d["Ticker"], orientation="h",
                               marker_color=colors,
                               text=[f"{v:+.1f}%" for v in d["1M %"]],
                               textposition="outside",
                               textfont=dict(color="#FFFFFF", size=10, family=MONO_STACK)))
        fig.update_layout(**base_layout("1-Month % Return", height=max(620, 15 * len(d))))
        show_chart(fig)

    with tabs[2]:
        d = df.dropna(subset=["Market Cap"]).sort_values("Market Cap", ascending=False).head(20)
        fig = go.Figure(go.Bar(x=d["Ticker"], y=d["Market Cap"], marker_color=COLOR_A,
                               text=[fmt_mcap(v, currency_symbol) for v in d["Market Cap"]],
                               textposition="outside",
                               textfont=dict(color="#FFFFFF", size=10, family=MONO_STACK)))
        fig.update_layout(**base_layout("Market Capitalization (Top 20)", height=500))
        show_chart(fig)

    with tabs[3]:
        d = df.dropna(subset=["Beta", "1M %"])
        if not d.empty:
            fig = go.Figure(go.Scatter(
                x=d["Beta"], y=d["1M %"], mode="markers+text",
                text=d["Ticker"], textposition="top center",
                marker=dict(size=11, color=COLOR_B, line=dict(color="#0A101F", width=1)),
                textfont=dict(color="#96A2B8", size=9.5, family=MONO_STACK),
            ))
            layout = base_layout("Risk vs Return (Beta vs 1M %)", height=520)
            layout["xaxis"]["title"] = dict(text="Beta", font=dict(size=11, color=CHART_TEXT))
            layout["yaxis"]["title"] = dict(text="1-Month Return (%)", font=dict(size=11, color=CHART_TEXT))
            layout["hovermode"] = "closest"
            fig.update_layout(**layout)
            show_chart(fig)
        else:
            st.caption("Insufficient beta data for the risk-return scatter.")

    # ── Research summary ──
    section_head("Equity Research Summary")
    insight_box("Research Commentary", generate_equity_research_summary(df, market_name))

    # ── Ranked ideas ──
    section_head(f"Ranked {market_name} Stock Ideas")
    st.markdown(
        '<p style="color:#D4AF6E;font-weight:600;font-size:0.8rem;letter-spacing:0.8px;'
        'font-family:var(--font-mono);text-transform:uppercase">'
        'Model-generated screens — educational, not investment advice.</p>',
        unsafe_allow_html=True,
    )

    top5 = df.nlargest(5, "Score")
    def_picks = df[df["Beta"].notna()].nsmallest(3, "Beta")
    growth_picks = df[df["Beta"].notna() & df["1M %"].notna()].sort_values(
        ["1M %", "Beta"], ascending=[False, False]).head(3)
    val_picks = df[df["From High %"].notna() & df["P/E"].notna() & (df["P/E"] > 0)].sort_values(
        "From High %").head(3)

    def render_picks(title, picks, kind):
        st.markdown(f"#### {title}")
        if picks.empty:
            st.caption("Not enough data for this category.")
            return
        for _, r in picks.iterrows():
            reason = generate_reason(r, kind, peer_medians, market_name)
            risk = generate_risk(r, kind, peer_medians, market_name)
            dp_bits = []
            if _safe(r.get("Price")) is not None:
                dp_bits.append(f"Px {currency_symbol}{r['Price']:,.2f}")
            if _safe(r.get("1M %")) is not None:
                dp_bits.append(f"1M {r['1M %']:+.1f}%")
            if _safe(r.get("YTD %")) is not None:
                dp_bits.append(f"YTD {r['YTD %']:+.1f}%")
            if _safe(r.get("From High %")) is not None:
                dp_bits.append(f"vs 52WH {r['From High %']:+.1f}%")
            if _safe(r.get("P/E")) is not None:
                dp_bits.append(f"P/E {r['P/E']:.1f}x")
            if _safe(r.get("Beta")) is not None:
                dp_bits.append(f"β {r['Beta']:.2f}")
            if _safe(r.get("Div Yield %")) is not None:
                dp_bits.append(f"Yld {r['Div Yield %']:.2f}%")
            dp_line = "  ·  ".join(dp_bits)

            st.markdown(
                f'<div class="data-card">'
                f'<div class="label">{r["Ticker"]} &nbsp;·&nbsp; {r["Name"]}</div>'
                f'<div style="color:#FFFFFF;margin-top:0.45rem;font-size:0.89rem;line-height:1.6;font-family:var(--font-body)">'
                f'<strong style="color:#D4AF6E">Reason:</strong> {reason}<br/>'
                f'<strong style="color:#F87171">Key risk:</strong> {risk}<br/>'
                f'<strong style="color:#5B9CF6">Data:</strong> '
                f'<span style="color:#C6D2E6;font-family:var(--font-mono);font-size:0.8rem">{dp_line}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    render_picks(f"Top 5 {market_name} Stocks to Consider", top5, "top")
    render_picks("3 Defensive Picks", def_picks, "def")
    render_picks("3 Higher-Risk Growth / Momentum Picks", growth_picks, "grow")
    render_picks("3 Value / Pullback Opportunities", val_picks, "val")

    # ── Transparent scoring table ──
    section_head("Transparent Scoring Table")
    score_df = df[["Ticker", "Name", "Score", "1M %", "3M %", "YTD %", "From High %",
                   "P/E", "Div Yield %", "Beta", "Rec"]].sort_values("Score", ascending=False)
    show_df(score_df, hide_index=True)

    # Persist for the IC memo
    st.session_state[f"{session_key}_df"] = df
    st.session_state[f"{session_key}_top5"] = top5
    st.session_state[f"{session_key}_def"] = def_picks
    st.session_state[f"{session_key}_grow"] = growth_picks
    st.session_state[f"{session_key}_val"] = val_picks
    st.session_state[f"{session_key}_medians"] = peer_medians

    page_disclaimer()


def page_us_stocks():
    render_equities_page("U.S.", DOW30, "$", "08", "dow30")


def page_india_stocks():
    render_equities_page("India", NIFTY50, "₹", "09", "nifty50")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: RESEARCH REPORTS  (memo + committee memo, consolidated)
# ══════════════════════════════════════════════════════════════════════════════

def page_reports(name_a, name_b, code_a, code_b):
    hero(
        "Module 10",
        "Research Reports",
        "Generate structured investment memoranda and committee-ready PDF "
        "reports for the selected pair.",
    )

    tab1, tab2 = st.tabs(["Investment Memo", "Investment Committee Memo"])

    with tab1:
        st.markdown(
            "<p>A structured research memo combining the macro snapshot, risk-adjusted "
            "scoring, and comparative commentary — rendered on screen and exportable "
            "as a formatted PDF.</p>",
            unsafe_allow_html=True,
        )
        pair_key = f"{name_a} vs {name_b}"
        if st.button("Generate Investment Memo", type="primary"):
            da, db, _, _, _, _ = load_pair(code_a, code_b)
            st.session_state["memo_html"] = generate_investment_memo(name_a, name_b, da, db)
            st.session_state["memo_pair"] = pair_key
            try:
                st.session_state["memo_pdf"] = build_pdf_report(name_a, name_b, da, db)
            except Exception:
                st.session_state["memo_pdf"] = None

        if (st.session_state.get("memo_html")
                and st.session_state.get("memo_pair") == pair_key):
            st.markdown(st.session_state["memo_html"], unsafe_allow_html=True)
            pdf_bytes = st.session_state.get("memo_pdf")
            if pdf_bytes:
                st.download_button(
                    "Download Memo as PDF",
                    data=pdf_bytes,
                    file_name=f"GMI_Memo_{name_a}_vs_{name_b}.pdf".replace(" ", "_"),
                    mime="application/pdf",
                )
            else:
                st.info("PDF export requires the reportlab library on the host — "
                        "the on-screen memo above is complete.")

    with tab2:
        st.markdown(
            "<p>The Investment Committee Memo combines the macro view with the latest "
            "<strong>U.S. Equities</strong> and <strong>India Equities</strong> analyses. "
            "Visit those pages first to populate the equity sections — otherwise they "
            "are omitted gracefully.</p>",
            unsafe_allow_html=True,
        )
        eq_loaded = []
        if st.session_state.get("dow30_df") is not None:
            eq_loaded.append("U.S. Dow 30")
        if st.session_state.get("nifty50_df") is not None:
            eq_loaded.append("India NIFTY 50")
        st.caption("Equity sections loaded this session: "
                   + (", ".join(eq_loaded) if eq_loaded else "none yet"))

        if st.button("Generate Investment Committee Memo PDF", type="primary"):
            with st.spinner("Building the Investment Committee Memo..."):
                try:
                    if name_a != name_b:
                        da, db, _, _, _, _ = load_pair(code_a, code_b)
                    else:
                        da = db = None
                except Exception:
                    da = db = None
                try:
                    st.session_state["ic_pdf"] = build_ic_memo_pdf(
                        name_a=name_a, name_b=name_b, da=da, db=db,
                        us_df=st.session_state.get("dow30_df"),
                        us_top5=st.session_state.get("dow30_top5"),
                        us_def=st.session_state.get("dow30_def"),
                        us_grow=st.session_state.get("dow30_grow"),
                        us_val=st.session_state.get("dow30_val"),
                        in_df=st.session_state.get("nifty50_df"),
                        in_top5=st.session_state.get("nifty50_top5"),
                        in_def=st.session_state.get("nifty50_def"),
                        in_grow=st.session_state.get("nifty50_grow"),
                        in_val=st.session_state.get("nifty50_val"),
                    )
                    st.session_state["ic_error"] = (
                        None if st.session_state["ic_pdf"]
                        else "PDF library not available. Install with: pip install reportlab"
                    )
                except Exception as e:
                    st.session_state["ic_pdf"] = None
                    st.session_state["ic_error"] = f"Memo generation failed: {type(e).__name__}"

        if st.session_state.get("ic_pdf"):
            st.success("Memo generated successfully.")
            st.download_button(
                "Download Investment Committee Memo",
                data=st.session_state["ic_pdf"],
                file_name=f"GMI_IC_Memo_{datetime.date.today().isoformat()}.pdf",
                mime="application/pdf",
            )
        elif st.session_state.get("ic_error"):
            st.error(st.session_state["ic_error"])

    page_disclaimer()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR + MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════

PAGES = [
    "Overview",
    "Global Rankings",
    "Country Comparison",
    "Markets & Performance",
    "Valuation Lab",
    "Risk Dashboard",
    "Economic Structure",
    "Scenario Studio",
    "U.S. Equities — Dow 30",
    "India Equities — NIFTY 50",
    "Research Reports",
]

PAIR_PAGES = {
    "Country Comparison", "Markets & Performance", "Valuation Lab",
    "Risk Dashboard", "Economic Structure", "Scenario Studio", "Research Reports",
}


def sidebar_brand():
    st.markdown(
        '<div style="padding:0.9rem 0 1.3rem 0;border-bottom:1px solid #1B2743;'
        'margin-bottom:1.1rem">'
        '<div style="color:#D4AF6E;font-family:var(--font-mono);font-size:0.64rem;font-weight:600;'
        'letter-spacing:2.6px;text-transform:uppercase">GMI · Research Terminal</div>'
        '<div style="color:#FFFFFF;font-family:var(--font-display);font-size:1.12rem;font-weight:700;'
        'margin-top:0.35rem;line-height:1.25;letter-spacing:-0.3px">Global Macro<br/>Investment Analyzer</div>'
        '<div style="color:#96A2B8;font-size:0.72rem;margin-top:0.5rem">'
        f'by Vedant Patil &nbsp;·&nbsp; v{APP_VERSION}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def sidebar_pair():
    """Global analysis-pair selector shared by all comparison modules."""
    st.markdown(
        '<div style="color:#D4AF6E;font-family:var(--font-mono);font-size:0.64rem;font-weight:600;'
        'letter-spacing:2.4px;text-transform:uppercase;margin:1.2rem 0 0.5rem 0">'
        'Analysis Pair</div>',
        unsafe_allow_html=True,
    )
    names = list(COUNTRIES.keys())
    name_a = st.selectbox("Economy A", names, index=names.index("United States"), key="pair_a")
    name_b = st.selectbox("Economy B", names, index=names.index("India"), key="pair_b")
    return name_a, name_b, COUNTRIES[name_a], COUNTRIES[name_b]


def main():
    with st.sidebar:
        sidebar_brand()

        st.markdown(
            '<div style="color:#D4AF6E;font-family:var(--font-mono);font-size:0.64rem;font-weight:600;'
            'letter-spacing:2.4px;text-transform:uppercase;margin-bottom:0.55rem">'
            'Navigation</div>',
            unsafe_allow_html=True,
        )
        selected_page = st.radio(
            "Navigation Menu",
            PAGES,
            index=0,
            label_visibility="collapsed",
            key="navigation",
        )

        name_a = name_b = code_a = code_b = None
        if selected_page in PAIR_PAGES:
            name_a, name_b, code_a, code_b = sidebar_pair()

        st.markdown(
            '<div style="padding:1.1rem 0 0 0;margin-top:1.6rem;border-top:1px solid #1B2743">'
            '<div style="color:#5F6C85;font-family:var(--font-mono);font-size:0.66rem;line-height:1.7">'
            'DATA · WORLD BANK<br/>MARKETS · YAHOO FINANCE<br/>'
            'EDUCATIONAL USE ONLY<br/>NOT INVESTMENT ADVICE'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # ── Pair validation for comparison modules ──
    if selected_page in PAIR_PAGES and name_a == name_b:
        hero("Selection Required", selected_page,
             "Two different economies are needed for a comparison.")
        st.warning("Please select two different economies in the sidebar to continue.")
        page_disclaimer()
        return

    # ── Routing ──
    if selected_page == "Overview":
        page_overview()
    elif selected_page == "Global Rankings":
        page_rankings()
    elif selected_page == "Country Comparison":
        page_compare(name_a, name_b, code_a, code_b)
    elif selected_page == "Markets & Performance":
        page_markets(name_a, name_b, code_a, code_b)
    elif selected_page == "Valuation Lab":
        page_valuation(name_a, name_b, code_a, code_b)
    elif selected_page == "Risk Dashboard":
        page_risk(name_a, name_b, code_a, code_b)
    elif selected_page == "Economic Structure":
        page_structure(name_a, name_b, code_a, code_b)
    elif selected_page == "Scenario Studio":
        page_scenario(name_a, name_b, code_a, code_b)
    elif selected_page == "U.S. Equities — Dow 30":
        page_us_stocks()
    elif selected_page == "India Equities — NIFTY 50":
        page_india_stocks()
    elif selected_page == "Research Reports":
        page_reports(name_a, name_b, code_a, code_b)
    else:
        page_overview()


if __name__ == "__main__":
    main()
