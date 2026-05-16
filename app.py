"""
================================================================================
 GLOBAL MACRO INVESTMENT ANALYZER
================================================================================
 An AI-powered platform that bridges macroeconomics and financial markets to
 deliver investment-oriented analysis on any pair of countries.

 Built by Vedant Patil  |  Single-file Streamlit application
 Run with:  python -m streamlit run app.py
================================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import requests
import datetime
import io
import math
import pandas as pd
import numpy as np

# Optional dependency — gracefully degrade if missing
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


# ══════════════════════════════════════════════════════════════════════════════
#  THEME & CSS  —  Institutional dark "Bloomberg-inspired" aesthetic
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── Root palette ── */
    :root {
        --bg-primary:   #0b1220;
        --bg-secondary: #131c2e;
        --bg-tertiary:  #1a2438;
        --border:       #1f2a44;
        --text-primary: #e8edf5;
        --text-secondary:#8b96a7;
        --text-muted:   #5a6578;
        --accent-blue:  #4a90e2;
        --accent-navy:  #1e3a5f;
        --accent-gold:  #c9a96e;
        --positive:     #4ade80;
        --negative:     #f87171;
        --neutral:      #fbbf24;
    }

    /* ── App background ── */
    .stApp {
        background: linear-gradient(180deg, #0b1220 0%, #0e1628 100%);
        color: var(--text-primary);
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #0a1020 !important;
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: var(--text-primary) !important;
        font-size: 0.95rem;
    }

    /* ── Sidebar radio navigation — menu-style items ── */
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 0.35rem !important;
        display: flex;
        flex-direction: column;
    }
    section[data-testid="stSidebar"] .stRadio > div > label {
        background: transparent;
        border: 1px solid transparent;
        border-left: 3px solid transparent;
        border-radius: 4px;
        padding: 0.6rem 0.8rem !important;
        margin: 0 !important;
        transition: all 0.15s ease;
        cursor: pointer;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(74,144,226,0.08);
        border-left-color: #4a90e2;
    }
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: rgba(201,169,110,0.1) !important;
        border-left-color: #c9a96e !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label p {
        color: var(--text-primary) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* ── Main content padding ── */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* ── Force ALL headings white ── */
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
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    /* ── Body text ── */
    .stMarkdown p, .stMarkdown li,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: var(--text-primary) !important;
        line-height: 1.65;
    }

    /* ── Selectbox / inputs ── */
    .stSelectbox label, .stSlider label, .stTextInput label {
        color: var(--text-primary) !important;
        font-weight: 500;
    }
    div[data-baseweb="select"] > div {
        background-color: var(--bg-secondary) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }

    /* ── Hero banner ── */
    .hero {
        background: linear-gradient(135deg, #0f1e3a 0%, #1a3158 60%, #243f6b 100%);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent-gold);
        padding: 2.2rem 2.4rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        color: #FFFFFF !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.4rem 0 !important;
        letter-spacing: -0.5px;
    }
    .hero .tagline {
        color: var(--accent-gold) !important;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    .hero .subtitle {
        color: #c5d1e3 !important;
        font-size: 1.0rem;
        margin: 0;
    }

    /* ── Metric / data cards ── */
    .data-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.8rem;
    }
    .data-card .label {
        color: var(--text-secondary);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .data-card .value {
        color: #FFFFFF;
        font-size: 1.55rem;
        font-weight: 700;
        line-height: 1.15;
        font-variant-numeric: tabular-nums;
    }
    .data-card .sub {
        color: var(--text-muted);
        font-size: 0.72rem;
        margin-top: 0.25rem;
    }

    /* ── Section heading rule ── */
    .section-head {
        color: #FFFFFF;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 1.8rem 0 0.6rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--border);
        letter-spacing: -0.01em;
    }
    .section-head::before {
        content: "▎";
        color: var(--accent-gold);
        margin-right: 0.4rem;
    }

    /* ── Insight / commentary box ── */
    .insight {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent-blue);
        padding: 1.4rem 1.6rem;
        border-radius: 4px;
        margin: 0.8rem 0 1.2rem 0;
    }
    .insight h4 {
        color: var(--accent-blue) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0 0 0.6rem 0 !important;
        font-weight: 700;
    }
    .insight p {
        color: var(--text-primary) !important;
        font-size: 0.92rem;
        line-height: 1.7;
        margin: 0.4rem 0 !important;
    }
    .insight strong {
        color: #FFFFFF !important;
    }

    /* ── Investor takeaway box (gold accent) ── */
    .takeaway {
        background: linear-gradient(135deg, rgba(201,169,110,0.08), rgba(201,169,110,0.02));
        border: 1px solid rgba(201,169,110,0.3);
        border-left: 3px solid var(--accent-gold);
        padding: 1.3rem 1.5rem;
        border-radius: 4px;
        margin: 1rem 0 1.2rem 0;
    }
    .takeaway h4 {
        color: var(--accent-gold) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0 0 0.5rem 0 !important;
        font-weight: 700;
    }
    .takeaway p {
        color: #FFFFFF !important;
        font-size: 0.95rem !important;
        line-height: 1.65 !important;
        margin: 0 !important;
    }

    /* ── Memo box (formal report style) ── */
    .memo {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        padding: 2rem 2.4rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .memo .memo-header {
        border-bottom: 2px solid var(--accent-gold);
        padding-bottom: 1rem;
        margin-bottom: 1.4rem;
    }
    .memo .memo-title {
        color: #FFFFFF;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 0 0.3rem 0;
    }
    .memo .memo-meta {
        color: var(--text-secondary);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .memo h3 {
        color: var(--accent-gold) !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 1.4rem 0 0.5rem 0 !important;
        font-weight: 700;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.4rem;
    }
    .memo p {
        color: var(--text-primary) !important;
        font-size: 0.93rem;
        line-height: 1.75;
        margin: 0.5rem 0 !important;
    }

    /* ── Pill / badge ── */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-right: 0.4rem;
    }
    .badge-pos {
        background: rgba(74,222,128,0.12);
        color: var(--positive);
        border: 1px solid rgba(74,222,128,0.3);
    }
    .badge-neg {
        background: rgba(248,113,113,0.12);
        color: var(--negative);
        border: 1px solid rgba(248,113,113,0.3);
    }
    .badge-neu {
        background: rgba(251,191,36,0.12);
        color: var(--neutral);
        border: 1px solid rgba(251,191,36,0.3);
    }

    /* ── Buttons ── */
    .stButton > button, .stDownloadButton > button {
        background: var(--accent-navy) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--accent-blue) !important;
        border-radius: 4px;
        padding: 0.55rem 1.4rem;
        font-weight: 600;
        font-size: 0.88rem;
        letter-spacing: 0.3px;
        transition: all 0.2s;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: var(--accent-blue) !important;
        border-color: var(--accent-gold) !important;
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
        padding: 0.7rem 1.2rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid var(--accent-gold) !important;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: var(--bg-secondary) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--border);
        border-radius: 4px;
    }

    /* ── Tables / dataframes (for markdown tables) ── */
    .stMarkdown table {
        background: var(--bg-secondary);
        color: var(--text-primary) !important;
        border-collapse: collapse;
        width: 100%;
    }
    .stMarkdown table th {
        background: var(--bg-tertiary);
        color: var(--accent-gold) !important;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 1px;
        padding: 0.7rem 1rem;
        border-bottom: 2px solid var(--border);
    }
    .stMarkdown table td {
        color: var(--text-primary) !important;
        padding: 0.6rem 1rem;
        border-bottom: 1px solid var(--border);
        font-size: 0.88rem;
    }

    /* ── Caption ── */
    .stCaption, [data-testid="stCaptionContainer"] p {
        color: var(--text-muted) !important;
        font-size: 0.75rem !important;
    }

    /* ── Footer disclaimer ── */
    .disclaimer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.7rem;
        padding: 2.5rem 0 1rem 0;
        border-top: 1px solid var(--border);
        margin-top: 3rem;
        line-height: 1.6;
    }

    /* ── Hide only the menu and footer (keep header so sidebar toggle works on Cloud) ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

# Country -> primary equity index ticker (Yahoo Finance)
EQUITY_INDICES = {
    "US": ("^GSPC",   "S&P 500"),
    "CN": ("000001.SS","Shanghai Composite"),
    "JP": ("^N225",   "Nikkei 225"),
    "DE": ("^GDAXI",  "DAX"),
    "IN": ("^NSEI",   "Nifty 50"),
    "GB": ("^FTSE",   "FTSE 100"),
    "FR": ("^FCHI",   "CAC 40"),
    "IT": ("FTSEMIB.MI","FTSE MIB"),
    "BR": ("^BVSP",   "Bovespa"),
    "CA": ("^GSPTSE", "TSX Composite"),
    "KR": ("^KS11",   "KOSPI"),
    "AU": ("^AXJO",   "ASX 200"),
    "ES": ("^IBEX",   "IBEX 35"),
    "MX": ("^MXX",    "IPC Mexico"),
    "ID": ("^JKSE",   "Jakarta Composite"),
    "TR": ("XU100.IS","BIST 100"),
    "CH": ("^SSMI",   "Swiss Market Index"),
    "NL": ("^AEX",    "AEX"),
    "SG": ("^STI",    "Straits Times"),
    "ZA": ("^J203.JO","FTSE/JSE Top 40"),
    "SE": ("^OMX",    "OMX Stockholm 30"),
    "NO": ("^OSEAX",  "Oslo All-Share"),
    "PL": ("^WIG20",  "WIG20"),
    "TH": ("^SET.BK", "SET Index"),
    "PH": ("PSEI.PS", "PSEi"),
    "MY": ("^KLSE",   "FTSE Bursa Malaysia"),
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

# Fallback values for the 6 most-used countries (used if WB API fails)
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


def get_fallback(code, metric):
    """Return fallback value or default if not in lookup."""
    if code in FALLBACK_DATA and metric in FALLBACK_DATA[code]:
        return FALLBACK_DATA[code][metric]
    return DEFAULT_FALLBACK.get(metric)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_wb_indicator(country_code, indicator, start_year=1980, end_year=2024):
    """
    Fetch a World Bank indicator. Returns (years, values) lists.
    Returns ([], []) on failure.
    """
    url = (
        f"https://api.worldbank.org/v2/country/{country_code}"
        f"/indicator/{indicator}"
        f"?date={start_year}:{end_year}&format=json&per_page=500"
    )
    try:
        resp = requests.get(url, timeout=15)
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


def latest_value(years, values):
    if not years:
        return None
    return values[-1]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_country_macro(country_code):
    """
    Fetch full macro snapshot for a country: returns (data dict, ts dict).
    data dict = {indicator_name: latest_value}
    ts dict   = {indicator_name: (years, values)}
    Falls back to FALLBACK_DATA if API returns nothing.
    """
    data = {}
    ts = {}
    for name, code in WB_INDICATORS.items():
        yrs, vls = fetch_wb_indicator(country_code, code)
        ts[name] = (yrs, vls)
        v = latest_value(yrs, vls)
        data[name] = v if v is not None else get_fallback(country_code, name)
    return data, ts


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_equity_index(ticker, period="5y"):
    """Fetch equity index history via yfinance. Returns (dates, closes) or ([],[])."""
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
    """Fetch FX rate vs USD via yfinance (e.g., EURUSD=X). Returns (dates, closes)."""
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


def fmt_pct(val):
    if val is None:
        return "N/A"
    return f"{val:+.1f}%" if abs(val) < 100 else f"{val:.1f}%"


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


def data_card(label, value, sub=""):
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="data-card">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'{sub_html}'
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


# ══════════════════════════════════════════════════════════════════════════════
#  CHART BUILDERS  —  Plotly with dark institutional theme
# ══════════════════════════════════════════════════════════════════════════════

CHART_BG = "#131c2e"
CHART_PAPER = "#131c2e"
CHART_GRID = "#1f2a44"
CHART_TEXT = "#c5d1e3"
COLOR_A = "#4a90e2"
COLOR_B = "#c9a96e"


def base_layout(title="", height=380):
    return dict(
        title=dict(text=title, font=dict(size=14, color="#FFFFFF", family="Inter, sans-serif")),
        paper_bgcolor=CHART_PAPER,
        plot_bgcolor=CHART_BG,
        font=dict(color=CHART_TEXT, family="Inter, sans-serif", size=11),
        height=height,
        margin=dict(l=55, r=25, t=50, b=45),
        xaxis=dict(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID, linecolor=CHART_GRID),
        yaxis=dict(gridcolor=CHART_GRID, zerolinecolor=CHART_GRID, linecolor=CHART_GRID),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FFFFFF", size=11),
        ),
        hovermode="x unified",
    )


def line_chart(years_a, vals_a, years_b, vals_b, name_a, name_b, title, y_fmt=",.0f"):
    fig = go.Figure()
    if years_a:
        fig.add_trace(go.Scatter(
            x=years_a, y=vals_a, mode="lines", name=name_a,
            line=dict(color=COLOR_A, width=2.5),
        ))
    if years_b:
        fig.add_trace(go.Scatter(
            x=years_b, y=vals_b, mode="lines", name=name_b,
            line=dict(color=COLOR_B, width=2.5),
        ))
    layout = base_layout(title)
    layout["yaxis"]["tickformat"] = y_fmt
    fig.update_layout(**layout)
    return fig


def grouped_bar(labels, vals_a, vals_b, name_a, name_b, title, y_suffix="%"):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=vals_a, name=name_a,
        marker_color=COLOR_A,
        text=[f"{v:.1f}{y_suffix}" for v in vals_a],
        textposition="outside", textfont=dict(color="#FFFFFF", size=11),
    ))
    fig.add_trace(go.Bar(
        x=labels, y=vals_b, name=name_b,
        marker_color=COLOR_B,
        text=[f"{v:.1f}{y_suffix}" for v in vals_b],
        textposition="outside", textfont=dict(color="#FFFFFF", size=11),
    ))
    layout = base_layout(title, height=420)
    layout["barmode"] = "group"
    fig.update_layout(**layout)
    return fig


def donut_chart(labels, values, title):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=["#4a90e2", "#c9a96e", "#5a6578", "#7a8a9e"]),
        textinfo="label+percent",
        textfont=dict(color="#FFFFFF", size=11),
    ))
    layout = base_layout(title, height=340)
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def normalized_index_chart(dates_a, vals_a, dates_b, vals_b, name_a, name_b, title):
    """Rebase both series to 100 at start for comparable performance view."""
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
    layout["yaxis"]["title"] = "Indexed (Start = 100)"
    fig.update_layout(**layout)
    return fig


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
            tone = "Elevated price pressures in this range typically force tighter monetary policy, weighing on growth-sensitive equities and lengthening duration risk for fixed income holders."
        elif hi_v > 3:
            tone = "Inflation in this band sits above most central bank targets but remains manageable, leaving room for a gradual policy normalization path."
        else:
            tone = "Both economies show contained price dynamics, supportive of stable real returns and lower discount rates."
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
            risk = "raises sovereign credit and refinancing concerns, particularly in a higher-rate environment"
        elif hi_dv > 60:
            risk = "warrants monitoring but remains within manageable territory for advanced economies"
        else:
            risk = "leaves meaningful fiscal headroom for counter-cyclical policy"
        parts.append(
            f"<p><strong>Fiscal position:</strong> {hi_debt} carries a heavier debt load "
            f"({hi_dv:.0f}% of GDP), which {risk}.</p>"
        )

    pop_a, pop_b = da.get("Population"), db.get("Population")
    if pop_a and pop_b and pop_a > 0 and pop_b > 0:
        gdp_a, gdp_b = da.get("GDP"), da.get("GDP")  # used per-capita logic next
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
        return "#4ade80"
    if s >= 55:
        return "#c9a96e"
    if s >= 40:
        return "#fbbf24"
    return "#f87171"


# ══════════════════════════════════════════════════════════════════════════════
#  INVESTMENT MEMO GENERATOR
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

    growth_phrase = (
        f"{name_a} expanding at {ga:.1f}% versus {name_b} at {gb:.1f}%"
    )
    inflation_phrase = (
        f"inflation of {ia:.1f}% in {name_a} compared to {ib:.1f}% in {name_b}"
    )

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
#  PDF REPORT BUILDER (reportlab)
# ══════════════════════════════════════════════════════════════════════════════

def build_pdf_report(name_a, name_b, da, db, memo_text=""):
    """Generate a professional PDF research report. Returns bytes or None."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib import colors as rl
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    except ImportError:
        return None

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=0.7 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )

    NAVY = rl.HexColor("#0b1220")
    GOLD = rl.HexColor("#c9a96e")
    DARK_GREY = rl.HexColor("#2F2F2F")
    LIGHT = rl.HexColor("#f0f4f8")
    BORDER = rl.HexColor("#dce4ef")

    styles = getSampleStyleSheet()
    title_st = ParagraphStyle("T", parent=styles["Title"], fontSize=22,
                              textColor=NAVY, alignment=TA_CENTER, spaceAfter=4)
    sub_st = ParagraphStyle("S", parent=styles["Normal"], fontSize=10,
                            textColor=rl.HexColor("#5a7a9b"),
                            alignment=TA_CENTER, spaceAfter=18)
    head_st = ParagraphStyle("H", parent=styles["Heading2"], fontSize=12,
                             textColor=NAVY, spaceBefore=14, spaceAfter=6,
                             borderPadding=4)
    body_st = ParagraphStyle("B", parent=styles["Normal"], fontSize=9.5,
                             leading=14, textColor=DARK_GREY,
                             alignment=TA_JUSTIFY)
    small_st = ParagraphStyle("Sm", parent=styles["Normal"], fontSize=7.5,
                              textColor=rl.HexColor("#7a98b5"),
                              alignment=TA_CENTER)

    story = []

    # Header
    story.append(Paragraph("GLOBAL MACRO INVESTMENT ANALYZER", title_st))
    story.append(Paragraph(
        f"Investment Memorandum: {name_a} vs {name_b}", sub_st))
    story.append(Paragraph(
        f"Generated {datetime.date.today().strftime('%B %d, %Y')}  |  "
        f"Prepared by Vedant Patil",
        sub_st))
    story.append(Spacer(1, 8))

    # Macro snapshot table
    story.append(Paragraph("Macro Snapshot", head_st))
    table_data = [
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
    ]
    t = Table(table_data, colWidths=[2.4 * inch, 2.1 * inch, 2.1 * inch])
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
    story.append(t)
    story.append(Spacer(1, 10))

    # Risk scores
    sa = risk_adjusted_score(da)
    sb = risk_adjusted_score(db)
    story.append(Paragraph("Risk-Adjusted Macro Score", head_st))
    story.append(Paragraph(
        f"<b>{name_a}:</b> {sa}/100 ({score_label(sa)}) &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>{name_b}:</b> {sb}/100 ({score_label(sb)})", body_st))
    story.append(Spacer(1, 8))

    # Sector breakdown
    story.append(Paragraph("Sector Composition (% of GDP)", head_st))
    sec_data = [
        ["Sector", name_a, name_b],
        ["Agriculture", fmt_pct_simple(da.get("Agriculture % GDP")),
         fmt_pct_simple(db.get("Agriculture % GDP"))],
        ["Industry", fmt_pct_simple(da.get("Industry % GDP")),
         fmt_pct_simple(db.get("Industry % GDP"))],
        ["Services", fmt_pct_simple(da.get("Services % GDP")),
         fmt_pct_simple(db.get("Services % GDP"))],
    ]
    t2 = Table(sec_data, colWidths=[2.4 * inch, 2.1 * inch, 2.1 * inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, rl.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, GOLD),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    # Investment commentary
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


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED HELPERS  —  Country selector + data load
# ══════════════════════════════════════════════════════════════════════════════

def country_selector(default_a="United States", default_b="China", key_suffix=""):
    """Render two country selectboxes and return (name_a, name_b, code_a, code_b)."""
    names = list(COUNTRIES.keys())
    c1, c2 = st.columns(2)
    with c1:
        name_a = st.selectbox(
            "Country A", names,
            index=names.index(default_a) if default_a in names else 0,
            key=f"sel_a_{key_suffix}",
        )
    with c2:
        name_b = st.selectbox(
            "Country B", names,
            index=names.index(default_b) if default_b in names else 1,
            key=f"sel_b_{key_suffix}",
        )
    return name_a, name_b, COUNTRIES[name_a], COUNTRIES[name_b]


def load_pair(code_a, code_b):
    """Load macro data for a country pair."""
    with st.spinner("Loading macroeconomic data from World Bank..."):
        da, ts_a = fetch_country_macro(code_a)
        db, ts_b = fetch_country_macro(code_b)
    return da, db, ts_a, ts_b


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: HOME / OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

def page_home():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">AI-Powered Macro & Markets Research</div>'
        '<h1>Global Macro Investment Analyzer</h1>'
        '<p class="subtitle">Bridging macroeconomics and capital markets to deliver '
        'investment-oriented analysis on any pair of economies.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    section_head("Platform Overview")
    st.markdown(
        "<p>This platform applies a <strong>quantitative macro framework</strong> to "
        "compare economies, assess investment attractiveness, and translate "
        "macroeconomic signals into actionable market insights. It combines World Bank "
        "macroeconomic data with live equity market intelligence and AI-driven "
        "analytical commentary to generate research-grade output.</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        data_card("Coverage", f"{len(COUNTRIES)}", "Countries tracked")
    with c2:
        data_card("Indicators", f"{len(WB_INDICATORS)}", "Macro variables")
    with c3:
        data_card("Markets", f"{len(EQUITY_INDICES)}", "Equity indices")

    section_head("How It Works")
    st.markdown(
        "<p>The platform organizes macro intelligence into nine integrated modules: "
        "country comparison, markets analysis, valuation logic, automated investment "
        "memos, risk dashboards, sector decomposition, scenario modeling, and "
        "downloadable PDF research reports. Each module uses the same underlying data "
        "pipeline but answers a different analytical question.</p>",
        unsafe_allow_html=True,
    )

    section_head("Why It Matters for Investors")
    insight_box(
        "Investment Thesis",
        "<p>Macro is the largest single driver of cross-border return dispersion. "
        "Studies of global equity returns have consistently shown that <strong>country "
        "selection</strong> often contributes more to portfolio returns than security "
        "selection within a country. This platform helps investors systematically frame "
        "those country-level decisions through a quantitative lens.</p>"
        "<p>By pairing macroeconomic data with market-implied signals, an investor can "
        "answer questions such as: <strong>which economy offers the better risk-adjusted "
        "growth profile? Which is pricing in too much optimism? Where do macro tailwinds "
        "support equity multiple expansion?</strong></p>",
    )

    section_head("Featured Analysis Modules")
    cols = st.columns(2)
    modules = [
        ("Country Comparison", "Side-by-side macro snapshot with growth, inflation, fiscal, and external metrics."),
        ("Markets & Investment", "Equity index performance, volatility analysis, and macro-market alignment."),
        ("Valuation & Macro", "Educational framework on how growth, rates, and inflation drive equity multiples."),
        ("Investment Memo Generator", "One-click structured research memo with executive summary and takeaways."),
        ("Risk Dashboard", "Composite risk-adjusted scoring across inflation, debt, labor, and external balance."),
        ("Scenario Analysis", "Stress-test macro assumptions and model implied portfolio impact."),
    ]
    for i, (title, desc) in enumerate(modules):
        with cols[i % 2]:
            st.markdown(
                f'<div class="data-card">'
                f'<div class="label">Module</div>'
                f'<div class="value" style="font-size:1.05rem">{title}</div>'
                f'<div class="sub" style="margin-top:0.5rem;font-size:0.82rem">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="disclaimer">'
        'Data sources: World Bank Open Data, Yahoo Finance &nbsp;|&nbsp; '
        'Built with Python &amp; Streamlit &nbsp;|&nbsp; '
        'For educational and research use only — not investment advice.'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: COUNTRY COMPARISON
# ══════════════════════════════════════════════════════════════════════════════

def page_country_compare():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">Module 01</div>'
        '<h1>Country Comparison</h1>'
        '<p class="subtitle">Macro snapshot, historical trends, and AI-generated '
        'comparative analysis.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    name_a, name_b, code_a, code_b = country_selector(key_suffix="cc")
    if name_a == name_b:
        st.warning("Please select two different countries.")
        return

    da, db, ts_a, ts_b = load_pair(code_a, code_b)

    # ── Snapshot cards ──
    section_head("Macro Snapshot")
    col1, col2 = st.columns(2)
    metrics_to_show = [
        ("GDP", fmt_money, "Nominal, current US$"),
        ("GDP per Capita", fmt_dollar, "Per capita, current US$"),
        ("GDP Growth", fmt_pct_simple, "Annual real growth"),
        ("Inflation", fmt_pct_simple, "Consumer price index"),
        ("Unemployment", fmt_pct_simple, "Total labor force"),
        ("Population", fmt_pop, "Total population"),
    ]
    with col1:
        st.markdown(f"#### {name_a}")
        for label, fn, sub in metrics_to_show:
            data_card(label, fn(da.get(label)), sub)
    with col2:
        st.markdown(f"#### {name_b}")
        for label, fn, sub in metrics_to_show:
            data_card(label, fn(db.get(label)), sub)

    # ── Historical trends ──
    section_head("Historical Trends")
    chart_specs = [
        ("GDP", ",.0s"),
        ("GDP per Capita", "$,.0f"),
        ("GDP Growth", ".1f"),
        ("Inflation", ".1f"),
    ]
    for i in range(0, len(chart_specs), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(chart_specs):
                break
            label, yfmt = chart_specs[idx]
            with col:
                ya, va = ts_a.get(label, ([], []))
                yb, vb = ts_b.get(label, ([], []))
                fig = line_chart(ya, va, yb, vb, name_a, name_b, label, yfmt)
                st.plotly_chart(fig, use_container_width=True)

    # ── AI commentary ──
    section_head("AI Comparative Analysis")
    insight_box("Macro Commentary", commentary_country_compare(name_a, name_b, da, db))

    # ── Investor takeaway ──
    sa = risk_adjusted_score(da)
    sb = risk_adjusted_score(db)
    winner = name_a if sa > sb else name_b
    takeaway_box(
        f"On a composite risk-adjusted basis, <strong>{winner}</strong> screens more "
        f"favorably ({max(sa,sb)}/100 vs {min(sa,sb)}/100). Growth-oriented allocators "
        f"should weigh the GDP growth differential, while stability-focused mandates "
        f"should emphasize inflation control and fiscal headroom."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: MARKETS & INVESTMENT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def page_markets():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">Module 02</div>'
        '<h1>Markets &amp; Investment Analysis</h1>'
        '<p class="subtitle">Equity index performance, volatility, and macro-market '
        'alignment.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    name_a, name_b, code_a, code_b = country_selector(
        default_a="United States", default_b="India", key_suffix="mk")
    if name_a == name_b:
        st.warning("Please select two different countries.")
        return

    if not HAS_YFINANCE:
        st.warning(
            "Live market data requires the 'yfinance' library. "
            "Install it with: pip install yfinance"
        )
        return

    if code_a not in EQUITY_INDICES or code_b not in EQUITY_INDICES:
        st.info(
            f"Equity index coverage not available for one or both selections. "
            f"Try countries with major benchmark indices (US, IN, JP, DE, GB, FR, etc.)."
        )
        return

    ticker_a, idx_name_a = EQUITY_INDICES[code_a]
    ticker_b, idx_name_b = EQUITY_INDICES[code_b]

    period = st.select_slider(
        "Lookback Period",
        options=["1y", "2y", "5y", "10y"],
        value="5y",
    )

    with st.spinner("Fetching equity index data..."):
        dates_a, vals_a = fetch_equity_index(ticker_a, period=period)
        dates_b, vals_b = fetch_equity_index(ticker_b, period=period)

    if not vals_a and not vals_b:
        st.error("Could not retrieve market data. Please try again later.")
        return

    section_head("Benchmark Index Snapshot")
    col1, col2 = st.columns(2)
    with col1:
        if vals_a:
            ret_a = (vals_a[-1] / vals_a[0] - 1) * 100
            data_card(idx_name_a, f"{vals_a[-1]:,.0f}",
                      f"{ret_a:+.1f}% over {period}")
        else:
            data_card(idx_name_a, "N/A", "data unavailable")
    with col2:
        if vals_b:
            ret_b = (vals_b[-1] / vals_b[0] - 1) * 100
            data_card(idx_name_b, f"{vals_b[-1]:,.0f}",
                      f"{ret_b:+.1f}% over {period}")
        else:
            data_card(idx_name_b, "N/A", "data unavailable")

    # ── Normalized comparison chart ──
    section_head("Indexed Performance (Start = 100)")
    fig = normalized_index_chart(
        dates_a, vals_a, dates_b, vals_b,
        idx_name_a, idx_name_b,
        f"{idx_name_a} vs {idx_name_b}",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Compute returns and volatility ──
    def daily_returns(vals):
        if len(vals) < 2:
            return []
        return [(vals[i] / vals[i-1] - 1) for i in range(1, len(vals))]

    def annualized_vol(rets):
        if len(rets) < 2:
            return None
        mean = sum(rets) / len(rets)
        var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
        return math.sqrt(var) * math.sqrt(252) * 100

    rets_a = daily_returns(vals_a)
    rets_b = daily_returns(vals_b)
    vol_a = annualized_vol(rets_a)
    vol_b = annualized_vol(rets_b)
    total_ret_a = (vals_a[-1] / vals_a[0] - 1) * 100 if vals_a else None
    total_ret_b = (vals_b[-1] / vals_b[0] - 1) * 100 if vals_b else None

    section_head("Risk & Return Metrics")
    rcol1, rcol2 = st.columns(2)
    with rcol1:
        st.markdown(f"#### {idx_name_a}")
        data_card("Total Return", f"{total_ret_a:+.1f}%" if total_ret_a is not None else "N/A", f"Over {period}")
        data_card("Annualized Volatility", f"{vol_a:.1f}%" if vol_a else "N/A", "Daily returns × √252")
        if total_ret_a is not None and vol_a and vol_a > 0:
            yrs = {"1y": 1, "2y": 2, "5y": 5, "10y": 10}[period]
            ann_ret = ((1 + total_ret_a / 100) ** (1 / yrs) - 1) * 100
            data_card("Annualized Return", f"{ann_ret:+.1f}%", "Geometric mean")
    with rcol2:
        st.markdown(f"#### {idx_name_b}")
        data_card("Total Return", f"{total_ret_b:+.1f}%" if total_ret_b is not None else "N/A", f"Over {period}")
        data_card("Annualized Volatility", f"{vol_b:.1f}%" if vol_b else "N/A", "Daily returns × √252")
        if total_ret_b is not None and vol_b and vol_b > 0:
            yrs = {"1y": 1, "2y": 2, "5y": 5, "10y": 10}[period]
            ann_ret = ((1 + total_ret_b / 100) ** (1 / yrs) - 1) * 100
            data_card("Annualized Return", f"{ann_ret:+.1f}%", "Geometric mean")

    # ── Macro-market commentary ──
    da, db, _, _ = load_pair(code_a, code_b)
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


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: VALUATION & MACRO INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════

def page_valuation():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">Module 03</div>'
        '<h1>Valuation &amp; Macro Insights</h1>'
        '<p class="subtitle">Educational framework on how macro variables drive '
        'equity and fixed income valuations.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    name_a, name_b, code_a, code_b = country_selector(key_suffix="val")
    if name_a == name_b:
        st.warning("Please select two different countries.")
        return

    da, db, _, _ = load_pair(code_a, code_b)

    section_head("Valuation-Relevant Indicators")
    col1, col2 = st.columns(2)
    val_metrics = [
        ("GDP Growth", fmt_pct_simple, "Real growth rate"),
        ("Inflation", fmt_pct_simple, "CPI inflation"),
        ("Lending Rate", fmt_pct_simple, "Commercial lending rate"),
        ("Real Interest Rate", fmt_pct_simple, "Inflation-adjusted"),
    ]
    with col1:
        st.markdown(f"#### {name_a}")
        for lbl, fn, sub in val_metrics:
            data_card(lbl, fn(da.get(lbl)), sub)
    with col2:
        st.markdown(f"#### {name_b}")
        for lbl, fn, sub in val_metrics:
            data_card(lbl, fn(db.get(lbl)), sub)

    section_head("Macro to Valuation Framework")
    insight_box(
        "Valuation Commentary",
        commentary_valuation(name_a, name_b, da, db),
    )

    # Educational tabs
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


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: INVESTMENT MEMO GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def page_memo():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">Module 04</div>'
        '<h1>Investment Memo Generator</h1>'
        '<p class="subtitle">One-click structured research memo combining macro, '
        'risk, and investment commentary.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    name_a, name_b, code_a, code_b = country_selector(key_suffix="memo")
    if name_a == name_b:
        st.warning("Please select two different countries.")
        return

    if st.button("Generate Investment Memo", type="primary"):
        da, db, _, _ = load_pair(code_a, code_b)
        memo_html = generate_investment_memo(name_a, name_b, da, db)
        st.markdown(memo_html, unsafe_allow_html=True)

        # Offer PDF download
        try:
            pdf_bytes = build_pdf_report(name_a, name_b, da, db)
            if pdf_bytes:
                st.download_button(
                    "Download Memo as PDF",
                    data=pdf_bytes,
                    file_name=f"Investment_Memo_{name_a}_vs_{name_b}.pdf",
                    mime="application/pdf",
                )
        except Exception:
            st.info("PDF generation unavailable. Install reportlab: pip install reportlab")
    else:
        st.info("Select two countries above and click **Generate Investment Memo** to produce a structured research note.")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: RISK DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def page_risk():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">Module 05</div>'
        '<h1>Risk Dashboard</h1>'
        '<p class="subtitle">Composite macro risk scoring with inflation, debt, '
        'currency, and external balance analysis.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    name_a, name_b, code_a, code_b = country_selector(key_suffix="risk")
    if name_a == name_b:
        st.warning("Please select two different countries.")
        return

    da, db, ts_a, ts_b = load_pair(code_a, code_b)

    # ── Composite scores ──
    section_head("Risk-Adjusted Macro Score")
    sa = risk_adjusted_score(da)
    sb = risk_adjusted_score(db)
    col1, col2 = st.columns(2)
    for col, name, score in [(col1, name_a, sa), (col2, name_b, sb)]:
        with col:
            color = score_color(score)
            label = score_label(score)
            st.markdown(
                f'<div class="data-card" style="text-align:center;padding:1.6rem">'
                f'<div class="label">{name}</div>'
                f'<div style="font-size:3rem;font-weight:800;color:{color};line-height:1">{score}</div>'
                f'<div style="font-size:0.85rem;font-weight:600;color:{color};letter-spacing:1.5px;margin-top:0.4rem">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

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

    # ── Inflation trend chart ──
    section_head("Inflation Trend (Historical)")
    ya, va = ts_a.get("Inflation", ([], []))
    yb, vb = ts_b.get("Inflation", ([], []))
    fig = line_chart(ya, va, yb, vb, name_a, name_b, "Inflation (%)", ".1f")
    st.plotly_chart(fig, use_container_width=True)

    # ── Currency / FX ──
    if HAS_YFINANCE:
        section_head("Currency Risk (FX vs USD)")
        cur_a = COUNTRY_CURRENCIES.get(code_a, "USD")
        cur_b = COUNTRY_CURRENCIES.get(code_b, "USD")
        with st.spinner("Fetching FX data..."):
            fx_a_dates, fx_a_vals = fetch_fx_rate(cur_a)
            fx_b_dates, fx_b_vals = fetch_fx_rate(cur_b)
        if fx_a_vals or fx_b_vals:
            fig_fx = normalized_index_chart(
                fx_a_dates, fx_a_vals, fx_b_dates, fx_b_vals,
                f"{cur_a}/USD", f"{cur_b}/USD",
                "Currency Performance vs USD (Indexed)",
            )
            st.plotly_chart(fig_fx, use_container_width=True)
        else:
            st.caption("FX data unavailable for the selected currencies.")

    # ── Risk commentary ──
    section_head("AI Risk Assessment")
    insight_box("Risk Commentary", commentary_risk(name_a, name_b, da, db))

    winner = name_a if sa > sb else name_b
    takeaway_box(
        f"On a risk-adjusted composite, <strong>{winner}</strong> presents the more "
        f"attractive macro risk profile. This does not mean it is risk-free — only "
        f"that the balance of inflation, fiscal, labor, and external indicators is "
        f"more favorable at present. Risk profiles can shift quickly with monetary "
        f"policy or geopolitical developments."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: SECTOR / ECONOMIC STRUCTURE
# ══════════════════════════════════════════════════════════════════════════════

def page_sectors():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">Module 06</div>'
        '<h1>Sector &amp; Economic Structure</h1>'
        '<p class="subtitle">Decomposition of GDP by sector and expenditure '
        'components with investment implications.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    name_a, name_b, code_a, code_b = country_selector(key_suffix="sec")
    if name_a == name_b:
        st.warning("Please select two different countries.")
        return

    da, db, _, _ = load_pair(code_a, code_b)

    # ── Sector pies ──
    section_head("Sector Composition (% of GDP)")
    col1, col2 = st.columns(2)
    with col1:
        labels = ["Agriculture", "Industry", "Services"]
        vals = [
            da.get("Agriculture % GDP", 0) or 0,
            da.get("Industry % GDP", 0) or 0,
            da.get("Services % GDP", 0) or 0,
        ]
        st.plotly_chart(donut_chart(labels, vals, name_a), use_container_width=True)
    with col2:
        vals_b = [
            db.get("Agriculture % GDP", 0) or 0,
            db.get("Industry % GDP", 0) or 0,
            db.get("Services % GDP", 0) or 0,
        ]
        st.plotly_chart(donut_chart(labels, vals_b, name_b), use_container_width=True)

    # ── Side-by-side bar ──
    section_head("GDP Expenditure Components")
    exp_labels = ["Household\nConsumption", "Govt\nSpending", "Investment", "Exports", "Imports"]
    exp_keys = [
        "Household Consumption % GDP",
        "Government Spending % GDP",
        "Investment % GDP",
        "Exports % GDP",
        "Imports % GDP",
    ]
    va_exp = [da.get(k) or 0 for k in exp_keys]
    vb_exp = [db.get(k) or 0 for k in exp_keys]
    fig_exp = grouped_bar(exp_labels, va_exp, vb_exp, name_a, name_b,
                          "Expenditure Side of GDP (% of GDP)")
    st.plotly_chart(fig_exp, use_container_width=True)

    # ── Commentary ──
    section_head("Structural Analysis")
    insight_box("Sector Commentary", commentary_sectors(name_a, name_b, da, db))

    takeaway_box(
        "Economic structure shapes which sectors dominate equity benchmarks and where "
        "long-term productivity gains will emerge. Service-heavy economies tend to host "
        "deeper financial and consumer-discretionary sectors, while industry-heavy "
        "economies offer more cyclical exposure to global trade and capital spending cycles."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: SCENARIO ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def page_scenario():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">Module 07</div>'
        '<h1>Scenario Analysis</h1>'
        '<p class="subtitle">Stress-test macro assumptions and assess implications '
        'for portfolio positioning.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    name_a, name_b, code_a, code_b = country_selector(key_suffix="scn")
    if name_a == name_b:
        st.warning("Please select two different countries.")
        return

    da, db, _, _ = load_pair(code_a, code_b)

    section_head("Scenario Configuration")
    scenario = st.selectbox(
        "Select Scenario",
        [
            "Interest rates rise 100 bps",
            "Inflation declines 200 bps",
            "GDP growth slows 150 bps",
            "Recession scenario (-2% growth)",
            "Risk-off / flight to quality",
            "Soft landing (gradual easing)",
        ],
    )

    section_head("Scenario Impact Analysis")

    if scenario == "Interest rates rise 100 bps":
        body = (
            "<p><strong>Mechanism:</strong> A 100 bps hike in policy rates raises the "
            "discount rate across all fixed income and equity valuation models.</p>"
            "<p><strong>Equity impact:</strong> Long-duration growth stocks (tech, "
            "biotech, REITs) face the steepest multiple compression — historically "
            "5-15% derating per 100 bps. Value sectors (financials, energy, materials) "
            "tend to outperform.</p>"
            "<p><strong>Fixed income impact:</strong> Bond prices fall; longer-duration "
            "Treasuries/sovereigns lose more. Credit spreads typically widen modestly.</p>"
            "<p><strong>Cross-country:</strong> The economy with higher pre-existing "
            "debt service burden faces sharper growth headwinds.</p>"
        )
        worse = (
            name_a if (da.get("Government Debt to GDP") or 0) >
                       (db.get("Government Debt to GDP") or 0)
            else name_b
        )
        take = (
            f"In a rate-hike scenario, <strong>{worse}</strong> faces relatively "
            f"greater fiscal stress given its heavier debt burden. Defensive equity "
            f"positioning and shorter-duration bonds are typically warranted."
        )

    elif scenario == "Inflation declines 200 bps":
        body = (
            "<p><strong>Mechanism:</strong> Declining inflation gives central banks "
            "scope to ease policy, lowering the risk-free rate and lifting valuations.</p>"
            "<p><strong>Equity impact:</strong> Multiple expansion — particularly for "
            "long-duration growth stocks. Real assets (TIPS, commodities) underperform.</p>"
            "<p><strong>Fixed income impact:</strong> Bond rally, credit spreads tighten, "
            "duration outperforms.</p>"
            "<p><strong>Cross-country:</strong> The economy with higher current "
            "inflation has more room to benefit from disinflation.</p>"
        )
        better = name_a if (da.get("Inflation") or 0) > (db.get("Inflation") or 0) else name_b
        take = (
            f"<strong>{better}</strong> stands to benefit more from disinflation given "
            f"its higher starting inflation. Long-duration growth equity exposure is "
            f"the highest-conviction trade in this scenario."
        )

    elif scenario == "GDP growth slows 150 bps":
        body = (
            "<p><strong>Mechanism:</strong> Slowing growth weighs on corporate earnings "
            "and consumer spending. Cyclicals derate first.</p>"
            "<p><strong>Equity impact:</strong> Cyclical sectors (consumer discretionary, "
            "industrials, materials) underperform. Defensive sectors (staples, utilities, "
            "healthcare) outperform on relative basis.</p>"
            "<p><strong>Fixed income impact:</strong> Bond yields fall as growth "
            "expectations decline. Quality credit outperforms.</p>"
        )
        worse = name_a if (da.get("GDP Growth") or 0) < (db.get("GDP Growth") or 0) else name_b
        take = (
            f"<strong>{worse}</strong>'s already slower growth path makes it more "
            f"vulnerable to a further deceleration. Defensive equity tilt and quality "
            f"credit positioning are warranted across both economies."
        )

    elif scenario == "Recession scenario (-2% growth)":
        body = (
            "<p><strong>Mechanism:</strong> Outright contraction drives broad earnings "
            "downgrades, credit deterioration, and risk-off positioning.</p>"
            "<p><strong>Equity impact:</strong> Historically, equities draw down "
            "20-35% in recessions. Defensive sectors lose less; cyclicals lose more.</p>"
            "<p><strong>Fixed income impact:</strong> Government bonds rally hard "
            "(flight to quality); high-yield credit spreads widen sharply.</p>"
            "<p><strong>Policy response:</strong> Central banks typically cut rates "
            "aggressively, providing eventual support for risk assets.</p>"
        )
        take = (
            "In a recession, capital preservation dominates. Underweight cyclicals, "
            "overweight quality and government bonds, and maintain dry powder for "
            "deployment at trough valuations."
        )

    elif scenario == "Risk-off / flight to quality":
        body = (
            "<p><strong>Mechanism:</strong> Investor risk appetite collapses; capital "
            "flows from risky assets to safe havens.</p>"
            "<p><strong>Equity impact:</strong> Emerging markets and small caps "
            "underperform; large-cap quality outperforms. EM currencies weaken.</p>"
            "<p><strong>Fixed income:</strong> US Treasuries, German Bunds, Japanese "
            "JGBs, gold, and CHF/JPY typically rally.</p>"
        )
        em_country = name_a if (da.get("GDP per Capita") or 0) < (db.get("GDP per Capita") or 0) else name_b
        take = (
            f"<strong>{em_country}</strong> (the lower per-capita income economy) is "
            f"more vulnerable in a risk-off episode given typical EM capital flight "
            f"dynamics. Hedge currency exposure or rotate into developed-market quality."
        )

    else:  # Soft landing
        body = (
            "<p><strong>Mechanism:</strong> Inflation normalizes without recession; "
            "central banks ease gradually. Goldilocks regime for risk assets.</p>"
            "<p><strong>Equity impact:</strong> Broad rally across sectors, with growth "
            "and cyclicals leading. Multiple expansion likely.</p>"
            "<p><strong>Fixed income:</strong> Modest bond rally, credit spreads tighten "
            "to cycle lows.</p>"
        )
        take = (
            "A soft-landing environment is the most constructive backdrop for risk "
            "assets. Overweight equities, underweight cash, maintain balanced duration "
            "in fixed income."
        )

    insight_box(f"Scenario: {scenario}", body)
    takeaway_box(take)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: EXPORT / REPORT CENTER
# ══════════════════════════════════════════════════════════════════════════════

def page_export():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">Module 08</div>'
        '<h1>Export &amp; Report Center</h1>'
        '<p class="subtitle">Generate downloadable PDF research reports for any '
        'country pair.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    name_a, name_b, code_a, code_b = country_selector(key_suffix="exp")
    if name_a == name_b:
        st.warning("Please select two different countries.")
        return

    st.markdown(
        "<p>Generate a polished PDF research report containing the macro snapshot, "
        "sector composition, risk-adjusted scores, and AI-generated investment "
        "commentary. Suitable for sharing with peers or attaching to applications.</p>",
        unsafe_allow_html=True,
    )

    if st.button("Generate Full PDF Report", type="primary"):
        with st.spinner("Building research report..."):
            da, db, _, _ = load_pair(code_a, code_b)
            try:
                pdf_bytes = build_pdf_report(name_a, name_b, da, db)
                if pdf_bytes:
                    st.success("Report ready for download.")
                    st.download_button(
                        "Download PDF",
                        data=pdf_bytes,
                        file_name=f"GMI_Report_{name_a}_vs_{name_b}.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.error("PDF library not available. Install with: pip install reportlab")
            except Exception as e:
                st.error(f"Report generation failed. Please try a different country pair.")


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED STOCK ANALYSIS ENGINE  (used by both U.S. and India pages)
# ══════════════════════════════════════════════════════════════════════════════

DOW30 = ["AAPL","AMGN","AXP","BA","CAT","CRM","CSCO","CVX","DIS","GS","HD",
         "HON","IBM","JNJ","JPM","KO","MCD","MMM","MRK","MSFT","NKE","NVDA",
         "PG","SHW","TRV","UNH","V","VZ","WMT","AMZN"]

NIFTY50 = ["RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS",
           "INFY.NS","SBIN.NS","LICI.NS","ITC.NS","HINDUNILVR.NS","LT.NS",
           "BAJFINANCE.NS","HCLTECH.NS","KOTAKBANK.NS","MARUTI.NS","SUNPHARMA.NS",
           "AXISBANK.NS","M&M.NS","ULTRACEMCO.NS","TITAN.NS","NTPC.NS","ONGC.NS",
           "ADANIENT.NS","ADANIPORTS.NS","POWERGRID.NS","BAJAJFINSV.NS",
           "TATAMOTORS.NS","COALINDIA.NS","ASIANPAINT.NS","WIPRO.NS","BAJAJ-AUTO.NS",
           "NESTLEIND.NS","TRENT.NS","JSWSTEEL.NS","TATASTEEL.NS","GRASIM.NS",
           "HINDALCO.NS","TECHM.NS","CIPLA.NS","DRREDDY.NS","BRITANNIA.NS",
           "EICHERMOT.NS","APOLLOHOSP.NS","SHRIRAMFIN.NS","HEROMOTOCO.NS",
           "INDUSINDBK.NS","BPCL.NS","TATACONSUM.NS","DIVISLAB.NS","SBILIFE.NS"]


def _safe(v, default=None):
    if v is None: return default
    try:
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return default
    except Exception:
        pass
    return v


def _clean_name(ticker, info):
    n = info.get("shortName") or info.get("longName")
    if n: return str(n)
    return ticker.replace(".NS", "").replace("-", " ").title()


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_stock_data(tickers, market_name):
    """Fetch daily-refreshed stock data for any ticker list. Returns list of dicts.
    Used for both Dow 30 and NIFTY 50."""
    if not HAS_YFINANCE:
        return [], []
    rows, failed = [], []
    for tk in tickers:
        try:
            t = yf.Ticker(tk)
            try:
                info = t.info or {}
            except Exception:
                info = {}
            hist = t.history(period="1y")
            if hist is None or hist.empty:
                failed.append(tk); continue

            closes = hist["Close"].tolist()
            volumes = hist["Volume"].tolist()
            cur = float(closes[-1])
            prev = float(closes[-2]) if len(closes) > 1 else cur
            daily_pct = (cur / prev - 1) * 100 if prev else 0.0

            def ret_n(n):
                if len(closes) <= n: return None
                base = closes[-(n+1)]
                return (cur / base - 1) * 100 if base else None

            ytd_ret = None
            try:
                yr = datetime.date.today().year
                ytd_rows = hist[hist.index.year == yr]
                if not ytd_rows.empty:
                    base = float(ytd_rows["Close"].iloc[0])
                    if base: ytd_ret = (cur / base - 1) * 100
            except Exception:
                pass

            hi52 = float(max(closes))
            lo52 = float(min(closes))
            dist_hi = (cur / hi52 - 1) * 100 if hi52 else None
            avg_vol = float(np.mean(volumes)) if volumes else None

            # daily-return volatility (annualized) for context
            try:
                rets = np.diff(closes) / closes[:-1]
                vol_ann = float(np.std(rets) * np.sqrt(252) * 100) if len(rets) > 5 else None
            except Exception:
                vol_ann = None

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
                "Market Cap": info.get("marketCap"),
                "P/E": info.get("trailingPE"),
                "Fwd P/E": info.get("forwardPE"),
                "Div Yield %": (info.get("dividendYield") or 0) * 100 if info.get("dividendYield") else None,
                "Beta": info.get("beta"),
                "Rec": info.get("recommendationKey", "—"),
            })
        except Exception:
            failed.append(tk)
            continue
    return rows, failed


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

        if m1 is not None:  s += max(-15, min(m1, 15)) * 0.8
        if m3 is not None:  s += max(-20, min(m3, 20)) * 0.4
        if ytd is not None: s += max(-30, min(ytd, 30)) * 0.2
        if dist is not None: s += max(-30, min(dist, 0)) * 0.15
        if pe is not None and pe > 0:
            if pe < 15: s += 6
            elif pe < 25: s += 2
            elif pe > 40: s -= 5
        if dy is not None and dy > 2: s += 3
        if beta is not None:
            if beta < 0.8: s += 2
            elif beta > 1.5: s -= 3
        if rec in ("strong_buy", "buy"): s += 6
        elif rec in ("sell", "strong_sell"): s -= 6
        if avg_vol is not None and avg_vol > 1e6: s += 1
        r["Score"] = round(max(0, min(100, s)), 1)
    return rows


def compute_peer_medians(df):
    """Return median values for use in dynamic reason/risk text."""
    med = {}
    for col in ["P/E", "1M %", "3M %", "YTD %", "Beta", "Div Yield %", "From High %",
                "Volatility %", "Score"]:
        try:
            med[col] = float(df[col].dropna().median())
        except Exception:
            med[col] = None
    return med


def generate_reason(row, category, peer_medians, market_name):
    """Return a data-specific reason string for a suggested stock."""
    tk = row["Ticker"]; nm = row["Name"]
    m1 = _safe(row.get("1M %")); m3 = _safe(row.get("3M %"))
    ytd = _safe(row.get("YTD %")); dist = _safe(row.get("From High %"))
    pe = _safe(row.get("P/E")); dy = _safe(row.get("Div Yield %"))
    beta = _safe(row.get("Beta")); score = row.get("Score", 0)
    med_pe = peer_medians.get("P/E"); med_score = peer_medians.get("Score") or 50

    if category == "top":
        bits = [f"composite score of {score:.1f}"]
        if score and med_score and score > med_score:
            bits.append(f"above the {market_name} median of {med_score:.1f}")
        if m1 is not None: bits.append(f"1M return {m1:+.1f}%")
        if ytd is not None: bits.append(f"YTD {ytd:+.1f}%")
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
        if beta is not None: bits.append(f"beta of {beta:.2f}")
        if dy is not None and dy > 0: bits.append(f"dividend yield of {dy:.2f}%")
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
        if m1 is not None: bits.append(f"1M momentum of {m1:+.1f}%")
        if m3 is not None: bits.append(f"3M trend {m3:+.1f}%")
        if dist is not None: bits.append(f"price {abs(dist):.1f}% from 52W high")
        if beta is not None: bits.append(f"beta {beta:.2f} amplifies upside in risk-on")
        return (f"{tk} ({nm}) screens as a momentum / growth candidate with "
                + ", ".join(bits) + ".")

    # value / pullback
    bits = []
    if dist is not None: bits.append(f"trading {abs(dist):.1f}% below 52W high — mean-reversion setup")
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
    """Return a data-specific risk string for a suggested stock."""
    pe = _safe(row.get("P/E")); med_pe = peer_medians.get("P/E")
    beta = _safe(row.get("Beta")); dist = _safe(row.get("From High %"))
    dy = _safe(row.get("Div Yield %")); m1 = _safe(row.get("1M %"))
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
    """Produce a market-aware research commentary HTML block."""
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

    # Sector-style interpretation
    if "Sector" in df.columns:
        sector_counts = df["Sector"].value_counts().head(3)
        sector_txt = "; ".join([f"{s} ({c})" for s, c in sector_counts.items() if s and s != "—"])
        if sector_txt:
            body.append(f"<p><strong>Sector mix:</strong> Largest sector representations in {market_name}: {sector_txt}.</p>")

    body.append(f"<p><strong>{market_name} investment view:</strong> "
                f"{'Constructive breadth and momentum suggest continued risk appetite.' if pos > neg else 'Defensive positioning warranted while breadth recovers.'}"
                f" Cross-check single-name selections against sector flows and macro regime.</p>")
    return "".join(body)


def fmt_num(v, suffix="", dec=2):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return "N/A"
    return f"{v:,.{dec}f}{suffix}"


def fmt_mcap(v, sym="$"):
    if v is None: return "N/A"
    if v >= 1e12: return f"{sym}{v/1e12:.2f}T"
    if v >= 1e9:  return f"{sym}{v/1e9:.1f}B"
    return f"{sym}{v/1e6:.0f}M"


def fmt_volume(v):
    if v is None: return "N/A"
    if v >= 1e9: return f"{v/1e9:.2f}B"
    if v >= 1e6: return f"{v/1e6:.1f}M"
    return f"{v/1e3:.0f}K"


def render_top_stocks_page(market_name, tickers, currency_symbol, module_num, session_key):
    """Render a full top-stocks page for either US or India market."""
    st.markdown(
        f'<div class="hero">'
        f'<div class="tagline">Module {module_num}</div>'
        f'<h1>{market_name} Top Stocks</h1>'
        f'<p class="subtitle">Daily-refreshed dashboard with equity research commentary '
        f'and data-driven AI ranking.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not HAS_YFINANCE:
        st.error("This module requires the 'yfinance' library. Install with: pip install yfinance")
        return

    with st.spinner(f"Fetching daily {market_name} data..."):
        rows, failed = fetch_stock_data(tuple(tickers), market_name)

    if not rows:
        st.warning("Unable to fetch live stock data. Please try again shortly.")
        return
    if failed:
        st.warning(f"Could not fetch data for {len(failed)} ticker(s): {', '.join(failed[:8])}{'...' if len(failed) > 8 else ''}")

    calculate_stock_score(rows)
    df = pd.DataFrame(rows)
    peer_medians = compute_peer_medians(df)

    # ── Filters ──
    section_head("Filters")
    flt = st.selectbox(
        "Show",
        ["All stocks", "Top daily gainers", "Top 5-day performers",
         "Top 1-month performers", "Undervalued (low P/E)",
         "High dividend yield", "Low-beta defensive", "Near 52-week high",
         "Pullback opportunities"],
        key=f"flt_{session_key}",
    )
    view = df.copy()
    try:
        if flt == "Top daily gainers": view = view.sort_values("Daily %", ascending=False).head(10)
        elif flt == "Top 5-day performers": view = view.sort_values("5D %", ascending=False).head(10)
        elif flt == "Top 1-month performers": view = view.sort_values("1M %", ascending=False).head(10)
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

    # ── Breadth ──
    section_head("Market Breadth Snapshot")
    pos = int((df["Daily %"] > 0).sum())
    neg = int((df["Daily %"] < 0).sum())
    avg_daily = float(df["Daily %"].mean())
    avg_1m_s = df["1M %"].dropna()
    avg_1m = float(avg_1m_s.mean()) if not avg_1m_s.empty else None
    c1, c2, c3, c4 = st.columns(4)
    with c1: data_card("Advancers", f"{pos}/{len(df)}", "Up today")
    with c2: data_card("Decliners", f"{neg}/{len(df)}", "Down today")
    with c3: data_card("Avg Daily", f"{avg_daily:+.2f}%", "Mean")
    with c4: data_card("Avg 1M", f"{avg_1m:+.1f}%" if avg_1m is not None else "N/A", "Trailing 1M")

    # ── Table ──
    section_head(f"{market_name} Snapshot")
    cols = ["Ticker","Name","Price","Daily %","5D %","1M %","3M %","YTD %",
            "From High %","Market Cap","P/E","Div Yield %","Beta","Score"]
    display_df = view[cols].copy()

    def color_returns(v):
        if pd.isna(v): return "color:#8b96a7"
        try: v = float(v)
        except: return ""
        if v > 0: return "color:#4ade80;font-weight:600"
        if v < 0: return "color:#f87171;font-weight:600"
        return "color:#c5d1e3"

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
                  .map(color_returns, subset=["Daily %","5D %","1M %","3M %","YTD %","From High %"])
                  .set_properties(**{"background-color": "#131c2e", "color": "#c5d1e3"}))
        st.dataframe(styled, use_container_width=True, hide_index=True)
    except Exception:
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── Charts ──
    section_head("Performance Charts")
    tabs = st.tabs(["Daily Returns", "1-Month Returns", "Market Cap", "Risk-Return"])

    with tabs[0]:
        d = df.dropna(subset=["Daily %"]).sort_values("Daily %", ascending=True)
        colors = ["#4ade80" if v > 0 else "#f87171" for v in d["Daily %"]]
        fig = go.Figure(go.Bar(x=d["Daily %"], y=d["Ticker"], orientation="h",
                               marker_color=colors, text=[f"{v:+.2f}%" for v in d["Daily %"]],
                               textposition="outside", textfont=dict(color="#FFFFFF", size=10)))
        fig.update_layout(**base_layout("Daily % Change", height=max(620, 14*len(d))))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        d = df.dropna(subset=["1M %"]).sort_values("1M %", ascending=True)
        colors = ["#4ade80" if v > 0 else "#f87171" for v in d["1M %"]]
        fig = go.Figure(go.Bar(x=d["1M %"], y=d["Ticker"], orientation="h",
                               marker_color=colors, text=[f"{v:+.1f}%" for v in d["1M %"]],
                               textposition="outside", textfont=dict(color="#FFFFFF", size=10)))
        fig.update_layout(**base_layout("1-Month % Return", height=max(620, 14*len(d))))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        d = df.dropna(subset=["Market Cap"]).sort_values("Market Cap", ascending=False).head(20)
        fig = go.Figure(go.Bar(x=d["Ticker"], y=d["Market Cap"], marker_color="#4a90e2",
                               text=[fmt_mcap(v, currency_symbol) for v in d["Market Cap"]],
                               textposition="outside", textfont=dict(color="#FFFFFF", size=10)))
        fig.update_layout(**base_layout("Market Capitalization (Top 20)", height=500))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:
        d = df.dropna(subset=["Beta","1M %"])
        if not d.empty:
            fig = go.Figure(go.Scatter(
                x=d["Beta"], y=d["1M %"], mode="markers+text",
                text=d["Ticker"], textposition="top center",
                marker=dict(size=12, color="#c9a96e", line=dict(color="#FFFFFF", width=1)),
                textfont=dict(color="#FFFFFF", size=10),
            ))
            layout = base_layout("Risk vs Return (Beta vs 1M %)", height=520)
            layout["xaxis"]["title"] = "Beta"
            layout["yaxis"]["title"] = "1-Month Return (%)"
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Insufficient beta data for risk-return scatter.")

    # ── Research commentary ──
    section_head("Equity Research Summary")
    insight_box("Research Commentary", generate_equity_research_summary(df, market_name))

    # ── AI suggestions ──
    section_head(f"AI-Based {market_name} Investment Suggestions")
    st.markdown(
        '<p style="color:#c9a96e;font-weight:600;font-size:0.85rem;letter-spacing:0.5px">'
        'These suggestions are AI based only.</p>',
        unsafe_allow_html=True,
    )

    top5 = df.nlargest(5, "Score")
    def_picks = df[df["Beta"].notna()].nsmallest(3, "Beta")
    growth_picks = df[df["Beta"].notna() & df["1M %"].notna()].sort_values(
        ["1M %","Beta"], ascending=[False, False]).head(3)
    val_picks = df[df["From High %"].notna() & df["P/E"].notna() & (df["P/E"] > 0)].sort_values(
        "From High %").head(3)

    def render_picks(title, picks, kind):
        st.markdown(f"#### {title}")
        if picks.empty:
            st.caption("Not enough data for this category."); return
        for _, r in picks.iterrows():
            reason = generate_reason(r, kind, peer_medians, market_name)
            risk = generate_risk(r, kind, peer_medians, market_name)
            # supporting datapoints line
            dp_bits = []
            if _safe(r.get("Price")) is not None:
                dp_bits.append(f"Px {currency_symbol}{r['Price']:,.2f}")
            if _safe(r.get("1M %")) is not None: dp_bits.append(f"1M {r['1M %']:+.1f}%")
            if _safe(r.get("YTD %")) is not None: dp_bits.append(f"YTD {r['YTD %']:+.1f}%")
            if _safe(r.get("From High %")) is not None: dp_bits.append(f"vs 52WH {r['From High %']:+.1f}%")
            if _safe(r.get("P/E")) is not None: dp_bits.append(f"P/E {r['P/E']:.1f}x")
            if _safe(r.get("Beta")) is not None: dp_bits.append(f"β {r['Beta']:.2f}")
            if _safe(r.get("Div Yield %")) is not None: dp_bits.append(f"Yld {r['Div Yield %']:.2f}%")
            dp_line = "  ·  ".join(dp_bits)

            st.markdown(
                f'<div class="data-card">'
                f'<div class="label">{r["Ticker"]} &nbsp;·&nbsp; {r["Name"]} &nbsp;·&nbsp; '
                f'<span style="color:#c9a96e">{title.split()[1] if len(title.split())>1 else "Pick"}</span></div>'
                f'<div style="color:#FFFFFF;margin-top:0.4rem;font-size:0.9rem;line-height:1.55">'
                f'<strong style="color:#c9a96e">Reason:</strong> {reason}<br/>'
                f'<strong style="color:#f87171">Key risk:</strong> {risk}<br/>'
                f'<strong style="color:#4a90e2">Data:</strong> <span style="color:#c5d1e3">{dp_line}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    render_picks(f"Top 5 {market_name} Stocks to Consider", top5, "top")
    render_picks("3 Defensive Picks", def_picks, "def")
    render_picks("3 Higher-Risk Growth / Momentum Picks", growth_picks, "grow")
    render_picks("3 Value / Pullback Opportunities", val_picks, "val")

    # ── Score table ──
    section_head("Transparent Scoring Table")
    score_df = df[["Ticker","Name","Score","1M %","3M %","YTD %","From High %",
                   "P/E","Div Yield %","Beta","Rec"]].sort_values("Score", ascending=False)
    st.dataframe(score_df, use_container_width=True, hide_index=True)

    # Persist for memo PDF
    st.session_state[f"{session_key}_df"] = df
    st.session_state[f"{session_key}_top5"] = top5
    st.session_state[f"{session_key}_def"] = def_picks
    st.session_state[f"{session_key}_grow"] = growth_picks
    st.session_state[f"{session_key}_val"] = val_picks
    st.session_state[f"{session_key}_medians"] = peer_medians

    st.markdown(
        '<div class="disclaimer">'
        'This platform is for educational and analytical purposes only and does not '
        'constitute financial advice.'
        '</div>',
        unsafe_allow_html=True,
    )


def page_us_stocks():
    render_top_stocks_page(
        market_name="U.S.",
        tickers=DOW30,
        currency_symbol="$",
        module_num="09",
        session_key="dow30",
    )


def page_india_stocks():
    render_top_stocks_page(
        market_name="India",
        tickers=NIFTY50,
        currency_symbol="₹",
        module_num="10",
        session_key="nifty50",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  INVESTMENT COMMITTEE MEMO PDF  (now covers US + India)
# ══════════════════════════════════════════════════════════════════════════════

def build_ic_memo_pdf(name_a=None, name_b=None, da=None, db=None,
                      us_df=None, us_top5=None, us_def=None, us_grow=None, us_val=None,
                      in_df=None, in_top5=None, in_def=None, in_grow=None, in_val=None):
    """Generate the polished Investment Committee Memo PDF (US + India aware)."""
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
    NAVY = rl.HexColor("#0a2463"); GOLD = rl.HexColor("#c9a96e")
    DARK = rl.HexColor("#2F2F2F"); LIGHT = rl.HexColor("#f0f4f8")
    BORDER = rl.HexColor("#dce4ef")

    def footer(canv, doc):
        canv.saveState()
        canv.setFont("Helvetica", 7.5)
        canv.setFillColor(rl.HexColor("#7a98b5"))
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
    title_st = ParagraphStyle("T", parent=styles["Title"], fontSize=24, textColor=NAVY,
                              alignment=TA_CENTER, spaceAfter=4)
    sub_st = ParagraphStyle("S", parent=styles["Normal"], fontSize=11,
                            textColor=rl.HexColor("#5a7a9b"), alignment=TA_CENTER, spaceAfter=18)
    head_st = ParagraphStyle("H", parent=styles["Heading2"], fontSize=13,
                             textColor=NAVY, spaceBefore=14, spaceAfter=6)
    body_st = ParagraphStyle("B", parent=styles["Normal"], fontSize=9.5, leading=14,
                             textColor=DARK, alignment=TA_JUSTIFY)
    small_st = ParagraphStyle("Sm", parent=styles["Normal"], fontSize=8,
                              textColor=rl.HexColor("#7a98b5"), alignment=TA_CENTER)

    def styled_table(data, widths):
        t = Table(data, colWidths=widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), NAVY),
            ("TEXTCOLOR", (0,0), (-1,0), rl.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 10),
            ("FONTSIZE", (0,1), (-1,-1), 9),
            ("ALIGN", (1,0), (-1,-1), "CENTER"),
            ("ALIGN", (0,0), (0,-1), "LEFT"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT, rl.white]),
            ("GRID", (0,0), (-1,-1), 0.5, BORDER),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LINEBELOW", (0,0), (-1,0), 1.5, GOLD),
        ]))
        return t

    def market_block(story, label, df, top5, def_p, grow_p, val_p, ccy="$"):
        if df is None or df.empty:
            story.append(Paragraph(f"<i>No {label} data available — visit the {label} Top Stocks page first.</i>", body_st))
            return
        story.append(Paragraph(f"<b>{label} — Top 5 Ranked</b>", body_st))
        if top5 is not None and not top5.empty:
            tbl = [["Ticker", "Name", "Score", "1M %", "YTD %", "From 52WH"]]
            for _, r in top5.iterrows():
                tbl.append([str(r["Ticker"]), str(r["Name"])[:24], f"{r['Score']:.1f}",
                            fmt_num(r.get("1M %"), "%", 1),
                            fmt_num(r.get("YTD %"), "%", 1),
                            fmt_num(r.get("From High %"), "%", 1)])
            story.append(styled_table(tbl, [0.9*inch, 2.2*inch, 0.7*inch, 0.9*inch, 0.9*inch, 0.95*inch]))
            story.append(Spacer(1, 4))
        for sublabel, picks in [("Defensive", def_p), ("Growth / Momentum", grow_p), ("Value / Pullback", val_p)]:
            if picks is not None and not picks.empty:
                story.append(Paragraph(f"<b>{label} {sublabel}:</b> " +
                                       ", ".join(picks["Ticker"].tolist()), body_st))
                story.append(Spacer(1, 2))
        story.append(Spacer(1, 6))

    story = []
    # ── Title page ──
    story.append(Spacer(1, 60))
    story.append(Paragraph("GLOBAL MACRO INVESTMENT ANALYZER", title_st))
    story.append(Paragraph("Investment Committee Memo", sub_st))
    story.append(Spacer(1, 30))
    pair = f"{name_a} vs {name_b}" if name_a and name_b and name_a != name_b else "Cross-Market Equity View"
    story.append(Paragraph(f"<b>Subject:</b> {pair}", body_st))
    story.append(Paragraph(f"<b>Date:</b> {datetime.date.today().strftime('%B %d, %Y')}", body_st))
    story.append(Paragraph("<b>Prepared by:</b> Vedant Patil", body_st))
    story.append(PageBreak())

    # ── Executive Summary ──
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
    if us_names: es += f"Top-ranked U.S. names include {', '.join(us_names)}. "
    if in_names: es += f"Top-ranked India names include {', '.join(in_names)}. "
    es += "Full recommendations and risks follow."
    story.append(Paragraph(es, body_st))

    # ── Macro Dashboard ──
    if da and db:
        story.append(Paragraph("2. Macro Dashboard Summary", head_st))
        story.append(styled_table([
            ["Indicator", name_a or "A", name_b or "B"],
            ["GDP Growth", fmt_pct_simple(da.get("GDP Growth")), fmt_pct_simple(db.get("GDP Growth"))],
            ["Inflation", fmt_pct_simple(da.get("Inflation")), fmt_pct_simple(db.get("Inflation"))],
            ["Lending Rate", fmt_pct_simple(da.get("Lending Rate")), fmt_pct_simple(db.get("Lending Rate"))],
            ["Unemployment", fmt_pct_simple(da.get("Unemployment")), fmt_pct_simple(db.get("Unemployment"))],
            ["Govt Debt/GDP", fmt_pct_simple(da.get("Government Debt to GDP")), fmt_pct_simple(db.get("Government Debt to GDP"))],
            ["Risk Score", f"{risk_adjusted_score(da)}/100", f"{risk_adjusted_score(db)}/100"],
        ], [2.4*inch, 2.1*inch, 2.1*inch]))
        story.append(Spacer(1, 10))

    # ── Market & Valuation ──
    story.append(Paragraph("3. Market & Valuation Summary", head_st))
    story.append(Paragraph(
        "Equity returns are driven by earnings growth and multiple changes. Multiples reflect "
        "interest rates, inflation expectations, and risk appetite. The DCF framework links these "
        "explicitly: cash flows scale with nominal growth, while the discount rate moves with the "
        "risk-free rate and equity risk premium.", body_st))

    # ── U.S. Top Stocks ──
    story.append(Paragraph("4. U.S. Top Stocks Summary (Dow 30)", head_st))
    market_block(story, "U.S.", us_df, us_top5, us_def, us_grow, us_val, "$")

    # ── India Top Stocks ──
    story.append(Paragraph("5. India Top Stocks Summary (NIFTY 50)", head_st))
    market_block(story, "India", in_df, in_top5, in_def, in_grow, in_val, "₹")

    # ── Recommendation ──
    story.append(Paragraph("6. Investment Recommendation", head_st))
    rec_call = "NEUTRAL"
    if da and db:
        sa = risk_adjusted_score(da); sb = risk_adjusted_score(db)
        if max(sa, sb) > 70: rec_call = "OVERWEIGHT (higher-scoring economy)"
        elif max(sa, sb) < 45: rec_call = "UNDERWEIGHT"
    story.append(Paragraph(f"<b>Call:</b> {rec_call}", body_st))
    story.append(Paragraph(
        "Rationale: Composite scoring synthesizes growth, inflation, fiscal, and external balance "
        "signals, combined with bottom-up equity screens across U.S. and India markets. Catalysts "
        "to monitor include central bank communication, fiscal policy shifts, and corporate earnings.",
        body_st))

    # ── Risk Factors ──
    story.append(Paragraph("7. Risk Factors", head_st))
    story.append(Paragraph(
        "<b>Inflation risk:</b> Persistence forces tighter policy and multiple compression. "
        "<b>Rate risk:</b> Long-duration assets vulnerable to upside surprises. "
        "<b>FX risk:</b> Currency moves can dominate equity returns for foreign investors. "
        "<b>Recession risk:</b> Earnings cuts and credit deterioration. "
        "<b>Geopolitical risk:</b> Trade, sanctions, conflict episodes. "
        "<b>Valuation risk:</b> Multiples compressing toward historical averages.", body_st))

    # ── Appendix ──
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


def page_ic_memo():
    st.markdown(
        '<div class="hero">'
        '<div class="tagline">Module 11</div>'
        '<h1>Investment Committee Memo Generator</h1>'
        '<p class="subtitle">Generate a polished PDF investment memo combining macro, '
        'U.S. equities, and India equities.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    section_head("Country Pair (optional)")
    name_a, name_b, code_a, code_b = country_selector(key_suffix="icmemo")

    st.markdown(
        "<p>The memo combines the macro view with the latest <strong>U.S. Top Stocks</strong> and "
        "<strong>India Top Stocks</strong> analyses. Visit those pages first to populate the equity "
        "sections — otherwise they will be omitted gracefully.</p>",
        unsafe_allow_html=True,
    )

    if st.button("Generate Investment Committee Memo PDF", type="primary"):
        with st.spinner("Building Investment Committee Memo..."):
            try:
                da, db, _, _ = load_pair(code_a, code_b) if name_a != name_b else (None, None, None, None)
            except Exception:
                da = db = None
            try:
                pdf_bytes = build_ic_memo_pdf(
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
                if pdf_bytes:
                    st.success("Memo generated successfully.")
                    st.download_button(
                        "Download Investment Committee Memo",
                        data=pdf_bytes,
                        file_name=f"IC_Memo_{datetime.date.today().isoformat()}.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.error("PDF library not available. Install with: pip install reportlab")
            except Exception as e:
                st.error(f"Memo generation failed: {type(e).__name__}")

    st.markdown(
        '<div class="disclaimer">'
        'For educational and analytical purposes only — not financial advice.'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ── Master list of pages ──
    PAGES = [
        "Home / Overview",
        "Country Comparison",
        "Markets & Investment Analysis",
        "Valuation & Macro Insights",
        "Investment Memo Generator",
        "Risk Dashboard",
        "Sector / Economic Structure",
        "Scenario Analysis",
        "Export / Report Center",
        "U.S. Top Stocks",
        "India Top Stocks",
        "Investment Committee Memo",
    ]

    # ── Sidebar branding ──
    with st.sidebar:
        st.markdown(
            '<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid #1f2a44;'
            'margin-bottom:1.2rem">'
            '<div style="color:#c9a96e;font-size:0.7rem;font-weight:700;'
            'letter-spacing:2px;text-transform:uppercase">GMI Analyzer</div>'
            '<div style="color:#FFFFFF;font-size:1.15rem;font-weight:700;'
            'margin-top:0.3rem;line-height:1.2">Global Macro<br/>Investment Analyzer</div>'
            '<div style="color:#8b96a7;font-size:0.72rem;margin-top:0.5rem">'
            'by Vedant Patil</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="color:#c9a96e;font-size:0.7rem;font-weight:700;'
            'letter-spacing:2px;text-transform:uppercase;margin-bottom:0.6rem">'
            'Navigation</div>',
            unsafe_allow_html=True,
        )

        # ── Single navigation widget — drives the entire app ──
        selected_page = st.sidebar.radio(
            "Navigation Menu",
            PAGES,
            index=0,
            label_visibility="collapsed",
            key="navigation",
        )

        st.markdown(
            '<div style="padding:1.2rem 0 0 0;margin-top:2rem;border-top:1px solid #1f2a44">'
            '<div style="color:#5a6578;font-size:0.7rem;line-height:1.5">'
            'Data: World Bank<br/>Markets: Yahoo Finance<br/>'
            'Educational use only<br/>Not investment advice'
            '</div></div>',
            unsafe_allow_html=True,
        )

    # ══════════════════════════════════════════════════════
    #  PAGE ROUTING — explicit if/elif so each page renders
    # ══════════════════════════════════════════════════════
    if selected_page == "Home / Overview":
        page_home()
    elif selected_page == "Country Comparison":
        page_country_compare()
    elif selected_page == "Markets & Investment Analysis":
        page_markets()
    elif selected_page == "Valuation & Macro Insights":
        page_valuation()
    elif selected_page == "Investment Memo Generator":
        page_memo()
    elif selected_page == "Risk Dashboard":
        page_risk()
    elif selected_page == "Sector / Economic Structure":
        page_sectors()
    elif selected_page == "Scenario Analysis":
        page_scenario()
    elif selected_page == "Export / Report Center":
        page_export()
    elif selected_page == "U.S. Top Stocks":
        page_us_stocks()
    elif selected_page == "India Top Stocks":
        page_india_stocks()
    elif selected_page == "Investment Committee Memo":
        page_ic_memo()
    else:
        page_home()


if __name__ == "__main__":
    main()
