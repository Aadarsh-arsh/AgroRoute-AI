"""Shared visual design system for all AgroRoute AI Streamlit pages.

This module intentionally contains presentation code only; search, ML, inference,
mission and rover state live in their existing modules.
"""
from __future__ import annotations

from html import escape
import streamlit as st

THEME_CSS = r"""
<style>
/* AgroRoute design tokens */
:root { --ag-green:#187447; --ag-green-dark:#10472e; --ag-mint:#e9f5ed;
 --ag-ink:#183d29; --ag-muted:#697f71; --ag-line:#dbe9df; --ag-radius:18px;
 --ag-shadow:0 9px 26px rgba(29,68,42,.055); }
.stApp {background:linear-gradient(180deg,#f5f9f5 0%,#eff6f0 100%);color:#1b3d2b;}
.block-container {max-width:1480px;padding-top:1.3rem;padding-bottom:3rem;}
header[data-testid="stHeader"] {background:transparent;}
[data-testid="stSidebar"] {background:#ffffff !important;border-right:1px solid var(--ag-line) !important;}
[data-testid="stSidebar"] * {color:var(--ag-ink) !important;}
[data-testid="stSidebarNav"] {padding-top:.5rem;}
[data-testid="stSidebarNav"]::before {content:"🌱  AgroRoute AI";display:block;
 font-size:1.17rem;font-weight:850;letter-spacing:-.02em;color:#16462e;
 padding:8px 17px 18px;margin:6px 9px 8px;border-bottom:1px solid #e2ece5;}
[data-testid="stSidebarNav"] a {border-radius:12px;margin:2px 8px;padding:7px 10px;}
[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"][aria-current="page"] {background:#e3f2e8 !important;color:#0b673b !important;font-weight:750;}
[data-testid="stSidebarNav"] a:hover {background:#f1f7f2 !important;}
[data-testid="stSidebar"] hr{border-color:#dce9df !important;}
[data-testid="stSidebar"] div.stButton>button[kind="primary"] *,
[data-testid="stSidebar"] div.stDownloadButton>button[kind="primary"] *{color:white !important;}
[data-testid="stSidebar"] div[data-baseweb="select"] > div,
[data-testid="stSidebar"] div[data-baseweb="input"] > div {background:#f8fbf8 !important;border-color:#d9e8dd !important;}
[data-testid="stMetric"] {background:#fff;border:1px solid var(--ag-line);border-radius:18px;
padding:17px 19px;box-shadow:var(--ag-shadow);min-height:112px;}
[data-testid="stMetricLabel"] {font-weight:650;color:var(--ag-muted);}
[data-testid="stMetricValue"] {font-weight:800;color:#163e27;letter-spacing:-1.3px;font-size:clamp(1.45rem,2.35vw,2.3rem);}
[data-testid="stVerticalBlock"] {row-gap:.55rem;}
h1,h2,h3,h4 {color:#173f29;letter-spacing:-.024em;}
h2,h3 {font-weight:750;}
[data-testid="stHeadingWithActionElements"] {margin-top:.4rem;}
div.stButton>button[kind="primary"],div.stDownloadButton>button[kind="primary"] {
  background:linear-gradient(105deg,#176f45,#219a5b) !important;
  border:1px solid #18814c !important;border-radius:12px !important;
  color:white !important;box-shadow:0 5px 16px rgba(20,113,67,.18);
  font-weight:700 !important;min-height:42px;
}
div.stButton>button[kind="primary"]:hover {background:#125a37 !important;transform:translateY(-1px);}
div.stButton>button[kind="secondary"],div.stDownloadButton>button,
[data-testid="stPageLink"] a {border-radius:12px !important;border-color:#d7e8dd !important;}
div.stButton>button[kind="secondary"]:hover,
[data-testid="stPageLink"] a:hover {border-color:#1b8953 !important;color:#176c43 !important;background:#f1faf4 !important;}
[data-testid="stPlotlyChart"] {background:#fff;border:1px solid var(--ag-line);border-radius:20px;padding:8px 7px;
box-shadow:var(--ag-shadow);overflow:hidden;}
[data-testid="stDataFrame"] {border-radius:15px;overflow:hidden;box-shadow:0 4px 18px rgba(13,59,34,.04);}
[data-testid="stAlert"] {border-radius:14px !important;}
[data-testid="stExpander"] {background:white;border-radius:14px;border:1px solid var(--ag-line);}
[data-testid="stFileUploader"], [data-testid="stForm"] {border-radius:16px;}
[data-testid="stSlider"] div[role="slider"] {background-color:#218855;}
.ag-page-hero {display:flex;justify-content:space-between;align-items:center;gap:18px;
background:linear-gradient(110deg,#12472f 0%,#19734a 60%,#28a36a 100%);
border-radius:24px;color:#fff;padding:24px 28px;margin:0 0 22px;
box-shadow:0 16px 36px rgba(12,93,53,.13);}
.ag-page-hero .ag-eyebrow {display:inline-block;color:#bceccc;letter-spacing:.12em;text-transform:uppercase;
font-size:.69rem;font-weight:800;margin-bottom:7px;}
.ag-page-hero h1 {color:#fff !important;font-weight:850 !important;font-size:clamp(1.6rem,2.6vw,2.45rem);
line-height:1.12;margin:0 0 9px;letter-spacing:-.032em;}
.ag-page-hero p {color:#e2f5e8;margin:0;line-height:1.55;max-width:900px;font-size:.91rem;}
.ag-hero-icon {display:flex;align-items:center;justify-content:center;width:74px;height:74px;
flex-shrink:0;border-radius:20px;font-size:2.05rem;background:rgba(255,255,255,.14);
border:1px solid rgba(255,255,255,.22);}
.ag-section-title {margin:14px 0 9px;font-size:1.15rem;font-weight:780;color:#1b482f;}
.ag-help-strip {padding:12px 15px;background:#eaf5ec;border:1px solid #d4ead9;border-radius:13px;
color:#235139;font-size:.9rem;margin:8px 0 12px;}
.ag-footer {margin-top:32px;padding:16px 19px;border-top:1px solid #d9e9de;
font-size:.79rem;color:#738b7b;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;}
.ag-footer span {font-weight:750;color:#166840;}
/* Protect layout at tablet/mobile widths */
@media(max-width:750px){.ag-page-hero{padding:20px 17px;border-radius:18px;}
 .ag-hero-icon{width:52px;height:52px;font-size:1.4rem;}
 .block-container{padding-left:1rem;padding-right:1rem;}
 [data-testid="stMetric"]{padding:11px 12px;min-height:95px;}}
</style>
"""


def apply_theme() -> None:
    """Load the same responsive design tokens on every standalone Streamlit page."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def page_hero(title: str, subtitle: str, *, icon: str = '🌱', eyebrow: str = 'AGROUTE AI • INTELLIGENCE SUITE') -> None:
    st.markdown(
        '<section class="ag-page-hero" aria-label="Page introduction">'
        f'<div><span class="ag-eyebrow">{escape(eyebrow)}</span>'
        f'<h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>'
        f'<div class="ag-hero-icon" aria-hidden="true">{escape(icon)}</div>'
        '</section>', unsafe_allow_html=True,
    )


def footer(note: str = 'Academic software simulation • Predictions are experimental, not field-verified diagnoses.') -> None:
    st.markdown(
        '<div class="ag-footer"><div><span>AgroRoute AI</span> · Precision agriculture intelligence</div>'
        f'<div>{escape(note)}</div></div>', unsafe_allow_html=True,
    )
    st.page_link('pages/1_Smart_Dashboard.py', label='← Back to Smart Dashboard', icon='🏠')


def section_title(title: str, detail: str = '') -> None:
    st.markdown(f'<div class="ag-section-title">{escape(title)}</div>', unsafe_allow_html=True)
    if detail:
        st.caption(detail)


def info_strip(message: str) -> None:
    st.markdown(f'<div class="ag-help-strip">{escape(message)}</div>', unsafe_allow_html=True)
