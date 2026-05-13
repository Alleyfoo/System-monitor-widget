"""Support Desk Incident Radar — Streamlit mockup dashboard.

Synthetic-only early-warning support dashboard that translates technical/operational
signals into customer-service guidance. No real systems, no real data.
"""

from datetime import datetime, timezone

import streamlit as st

from components import (
    _caption,
    render_compact_detail,
    render_compact_header,
    render_compact_service_lights,
    render_detail_panel,
    render_known_issues,
    render_service_card,
    render_signal_table,
    render_top_metrics,
    render_topbar,
)
from mock_data import (
    generate_known_issues,
    generate_signal_evidence,
    generate_summary_metrics,
)
from scenarios import SCENARIOS, load_scenario
from scoring import (
    filter_services_by_status,
    get_view_mode_fields,
    sort_services_by_severity,
)

st.set_page_config(
    page_title="Support Desk Incident Radar",
    layout="wide",
    initial_sidebar_state="expanded",
)


_GLOBAL_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap');

:root, html[data-theme="light"] {
  --bg:        #F4F3EF;
  --surface:   #FFFFFF;
  --surface-2: #FAF9F6;
  --sidebar:   #111214;
  --sidebar-fg:#E6E4DE;
  --sidebar-mut:#7C7C75;
  --line:      #E4E2DB;
  --line-2:    #EFEDE6;
  --ink:       #16181B;
  --ink-2:     #3C3D3F;
  --mut:       #767670;
  --mut-2:     #9B9A92;
  --accent:    #B8782F;
  --accent-bg: #F4ECDE;
  --red:       #BE3F38;
  --red-bg:    #F7E5E3;
  --orange:    #C8702A;
  --orange-bg: #F6E8D5;
  --green:     #4F8254;
  --green-bg:  #E1ECDE;
  --grey:      #7C7B74;
  --grey-bg:   #ECEAE3;
  --blue:      #466196;
  --blue-bg:   #E1E6F1;
}
html[data-theme="dark"] {
  --bg:        #0C0D0F;
  --surface:   #15171A;
  --surface-2: #181A1E;
  --sidebar:   #0A0B0C;
  --sidebar-fg:#D6D3CB;
  --sidebar-mut:#6E6D67;
  --line:      #25282C;
  --line-2:    #1D2024;
  --ink:       #E9E6DE;
  --ink-2:     #BFBDB5;
  --mut:       #82817A;
  --mut-2:     #595852;
  --accent:    #D49855;
  --accent-bg: #2C2317;
  --red:       #D55B53;
  --red-bg:    #2E1B1A;
  --orange:    #DC8A45;
  --orange-bg: #2A1F12;
  --green:     #6FA374;
  --green-bg:  #19261B;
  --grey:      #8E8D85;
  --grey-bg:   #1F2124;
  --blue:      #7891C3;
  --blue-bg:   #181E2A;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--ink);
  font-family: 'Geist', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  font-feature-settings: 'ss01','cv11','cv05';
  font-size: 13px;
  line-height: 1.45;
}
.mono { font-family: 'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace; font-feature-settings: 'zero','ss01'; }
.tnum { font-variant-numeric: tabular-nums; }

.block-container { padding: 22px 28px 60px !important; max-width: none !important; }

/* Sidebar overrides */
[data-testid="stSidebar"] { background: var(--sidebar) !important; }
[data-testid="stSidebar"] * { color: var(--sidebar-fg); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 { color: var(--sidebar-fg); }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stRadio label {
  font-size: 10px !important;
  color: var(--sidebar-mut) !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 500;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background: #18191D !important;
  border: 1px solid #25272C !important;
  border-radius: 4px !important;
  padding: 7px 9px !important;
  font-size: 12px !important;
  color: var(--sidebar-fg) !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] hr { border-color: #1F2025 !important; margin: 14px 0 !important; }

/* Sidebar brand */
.sb-brand {
  display: flex; align-items: baseline; gap: 6px;
  padding-bottom: 14px; border-bottom: 1px solid #1F2025; margin-bottom: 6px;
}
.sb-brand .mark { width: 10px; height: 10px; background: var(--accent); border-radius: 2px; transform: translateY(2px); }
.sb-brand .name { font-weight: 600; font-size: 14px; letter-spacing: -0.01em; color: var(--sidebar-fg); }
.sb-brand .ver { color: var(--sidebar-mut); font-size: 10px; margin-left: auto; font-family: 'Geist Mono', monospace; }

.sb-section {
  font-size: 9px; text-transform: uppercase; letter-spacing: 0.14em;
  color: var(--sidebar-mut); font-weight: 600; margin: 14px 0 4px;
}
.sb-fineprint {
  font-size: 10px; color: var(--sidebar-mut); line-height: 1.55;
  margin-top: 22px; padding-top: 14px; border-top: 1px solid #1F2025;
}

/* Buttons */
.stButton > button {
  border-radius: 4px !important;
  font-family: 'Geist', sans-serif !important;
  font-weight: 500 !important;
  font-size: 12px !important;
  border: 1px solid var(--line) !important;
  background: var(--surface) !important;
  color: var(--ink-2) !important;
  transition: border-color 0.12s, background 0.12s !important;
  box-shadow: none !important;
}
.stButton > button:hover {
  border-color: var(--mut-2) !important;
  transform: none !important;
  box-shadow: none !important;
}
.stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: var(--accent) !important;
  color: #1A1208 !important;
  border-color: var(--accent) !important;
  font-weight: 600 !important;
}

/* Top bar */
.topbar {
  display:flex; align-items: flex-end; justify-content: space-between;
  padding-bottom: 16px; margin-bottom: 18px;
  border-bottom: 1px solid var(--line);
}
.topbar h1 {
  margin: 0; font-size: 20px; font-weight: 600; letter-spacing: -0.015em;
  color: var(--ink);
}
.topbar .sub { font-size: 12px; color: var(--mut); margin-top: 4px; max-width: 56ch; }
.topbar .meta { text-align: right; }
.topbar .meta .row {
  font-size: 10.5px; color: var(--mut); letter-spacing: 0.04em;
  text-transform: uppercase; margin-bottom: 4px;
}
.topbar .meta .row .v {
  color: var(--ink-2); text-transform: none; letter-spacing: 0;
  margin-left: 8px; font-family: 'Geist Mono', monospace;
}
.topbar .pulse {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: 'Geist Mono', monospace; font-size: 11px; color: var(--ink-2);
}
.topbar .pulse .dot {
  width:6px; height:6px; border-radius: 50%;
  background: var(--red);
  animation: pulse 1.8s infinite;
}
@keyframes pulse {
  0%   { box-shadow: 0 0 0 0 rgba(190,63,56,0.55); }
  70%  { box-shadow: 0 0 0 8px rgba(190,63,56,0); }
  100% { box-shadow: 0 0 0 0 rgba(190,63,56,0); }
}
@media (prefers-reduced-motion: reduce) {
  .topbar .pulse .dot { animation: none; }
}

/* Section caption */
.caption { display: flex; align-items: baseline; gap: 10px; margin: 24px 0 10px; }
.caption h2 {
  margin: 0; font-size: 10.5px; font-weight: 600;
  color: var(--mut); text-transform: uppercase; letter-spacing: 0.16em;
}
.caption .rule { flex: 1; height: 1px; background: var(--line); }
.caption .count { font-family: 'Geist Mono', monospace; font-size: 10.5px; color: var(--mut-2); }

/* KPIs */
.kpis {
  display: grid; grid-template-columns: 1.6fr repeat(6, 1fr); gap: 1px;
  background: var(--line); border: 1px solid var(--line);
  border-radius: 6px; overflow: hidden;
}
.kpi {
  background: var(--surface); padding: 14px 16px; min-height: 84px;
  display:flex; flex-direction: column; justify-content: space-between;
  position: relative;
}
.kpi .lbl { font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--mut); font-weight: 500; }
.kpi .val {
  font-family: 'Geist Mono', monospace; font-variant-numeric: tabular-nums;
  font-size: 26px; font-weight: 500; color: var(--ink);
  letter-spacing: -0.02em; line-height: 1;
}
.kpi .delta { font-family: 'Geist Mono', monospace; font-size: 10.5px; color: var(--mut); }
.kpi.kpi-hero .strip { position: absolute; left:0; top:0; bottom:0; width: 3px; background: var(--red); }
.kpi.kpi-hero .lbl-row { display:flex; justify-content: space-between; align-items: center;}
.kpi.kpi-hero .since { font-family: 'Geist Mono', monospace; font-size: 10.5px; color: var(--mut); }
.kpi.kpi-hero .breakdown { display: flex; gap: 12px; margin-top: 6px;}
.kpi.kpi-hero .breakdown span { font-family: 'Geist Mono', monospace; font-size: 11px; color: var(--ink-2);}
.kpi.kpi-hero .breakdown .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 5px; vertical-align: 1px; }
.kpi .spark { width: 100%; height: 20px; display: block; }

/* Badge */
.badge {
  font-family: 'Geist Mono', monospace; font-size: 10px; font-weight: 600;
  letter-spacing: 0.04em; text-transform: uppercase;
  padding: 3px 7px; border-radius: 3px;
  display: inline-flex; align-items: center; gap: 5px;
}
.badge .d { width:5px; height:5px; border-radius: 50%; background: currentColor; }
.badge.red    { color: var(--red);    background: var(--red-bg); }
.badge.orange { color: var(--orange); background: var(--orange-bg); }
.badge.green  { color: var(--green);  background: var(--green-bg); }
.badge.grey   { color: var(--grey);   background: var(--grey-bg); }
.badge.blue   { color: var(--blue);   background: var(--blue-bg); }

/* Notices */
.notices { border: 1px solid var(--line); border-radius: 6px; background: var(--surface); overflow: hidden; }
.notice {
  display: grid; grid-template-columns: 6px 1.7fr 1fr 0.6fr 1.4fr;
  gap: 14px; padding: 11px 14px 11px 0;
  border-top: 1px solid var(--line-2); align-items: center;
}
.notice:first-child { border-top: 0; }
.notice .bar { align-self: stretch; background: var(--mut); }
.notice .ttl { display:flex; flex-direction: column; gap: 2px; }
.notice .ttl .name { font-weight: 500; color: var(--ink); font-size: 13px; }
.notice .ttl .sub  { font-size: 11px; color: var(--mut); }
.notice .meta-col  { font-family: 'Geist Mono', monospace; font-size: 11px; color: var(--ink-2); }
.notice .meta-col .k { color: var(--mut); margin-right: 4px; }
.notice .badge { justify-self: start; }
.notice .instr { font-size: 11.5px; color: var(--ink-2); line-height: 1.45; margin: 0; }

/* Service grid cards */
.card {
  background: var(--surface); border: 1px solid var(--line); border-radius: 6px;
  padding: 13px 14px 12px; position: relative; overflow: hidden;
  transition: border-color 0.12s;
}
.card:hover { border-color: var(--mut-2); }
.card.selected { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent) inset; }
.card .stripe { position: absolute; left: 0; top: 0; bottom: 0; width: 2px; background: var(--green); }
.card .head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.card .name { font-weight: 500; font-size: 13px; color: var(--ink); letter-spacing: -0.005em; }
.card .impact { font-size: 11.5px; color: var(--mut); line-height: 1.4; min-height: 32px; margin: 0; }
.card .ribbon { display: flex; gap: 1px; margin: 8px 0; height: 6px; border-radius: 1px; overflow: hidden; }
.card .ribbon span { flex: 1; background: var(--green); opacity: 0.95; }
.card .ribbon span.green  { background: var(--green); }
.card .ribbon span.orange { background: var(--orange); }
.card .ribbon span.red    { background: var(--red); }
.card .ribbon span.grey   { background: var(--grey); }
.card .ribbon span.blue   { background: var(--blue); }
.card .foot { display: flex; justify-content: space-between; align-items: center; gap: 10px; padding-top: 8px; border-top: 1px dashed var(--line); }
.card .foot .stats { font-family: 'Geist Mono', monospace; font-size: 10.5px; color: var(--mut); display: flex; gap: 9px; }
.card .foot .stats b { font-weight: 500; color: var(--ink-2); }
.card .foot .chk { font-family: 'Geist Mono', monospace; font-size: 10.5px; color: var(--mut-2); }
.card .spark { height: 18px; width: 100%; display: block; }
.card[data-status="orange"] .stripe { background: var(--orange); }
.card[data-status="red"]    .stripe { background: var(--red); }
.card[data-status="grey"]   .stripe { background: var(--grey); }
.card[data-status="blue"]   .stripe { background: var(--blue); }

/* Detail */
.detail {
  margin-top: 20px; border: 1px solid var(--line); border-radius: 6px;
  background: var(--surface); overflow: hidden;
}
.detail-head {
  display:flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; border-bottom: 1px solid var(--line); background: var(--surface-2);
}
.detail-head .l { display:flex; align-items: center; gap: 12px; flex-wrap: wrap;}
.detail-head .l .stripe { width: 3px; height: 26px; background: var(--red); border-radius: 1px;}
.detail-head h3 { margin: 0; font-size: 15px; font-weight: 600; letter-spacing: -0.01em; color: var(--ink); }
.detail-head .id { font-family: 'Geist Mono', monospace; font-size: 11px; color: var(--mut); }
.detail-head .actions { display:flex; gap: 6px; }
.detail-head .actions button {
  background: transparent; border: 1px solid var(--line); color: var(--ink-2);
  border-radius: 4px; padding: 5px 9px; font: 500 11px/1 'Geist', sans-serif;
  cursor: pointer;
}
.detail-head .actions button.primary { background: var(--ink); color: var(--surface); border-color: var(--ink); }

.detail-body { display: grid; grid-template-columns: 1.15fr 1fr 1fr; gap: 0; }
.dcol { padding: 16px 18px; border-right: 1px solid var(--line); }
.dcol:last-child { border-right: 0; }
.dlabel {
  font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.14em;
  color: var(--mut); font-weight: 600; margin: 0 0 6px;
}
.dlabel + p, .dlabel + .v { margin: 0; }
.dcol p { font-size: 12.5px; color: var(--ink-2); line-height: 1.5; margin: 0 0 14px; }
.dcol .v { font-size: 12.5px; color: var(--ink); margin-bottom: 14px;}
.dcol .v.mono { font-family: 'Geist Mono', monospace; font-size: 11.5px; color: var(--ink-2); }

.workflows { list-style: none; padding: 0; margin: 0 0 14px; }
.workflows li {
  font-size: 11.5px; color: var(--ink-2);
  padding: 5px 0 5px 14px; border-top: 1px solid var(--line-2);
  position: relative;
}
.workflows li:first-child { border-top: 0;}
.workflows li::before {
  content: ""; position: absolute; left: 0; top: 11px;
  width: 6px; height: 1px; background: var(--mut-2);
}

.say {
  background: var(--accent-bg); color: var(--ink);
  border-left: 2px solid var(--accent);
  padding: 10px 12px; border-radius: 3px;
  font-size: 12.5px; line-height: 1.5; margin-bottom: 14px;
}
.checklist { list-style: none; padding:0; margin: 0 0 14px; }
.checklist li {
  font-size: 11.5px; color: var(--ink-2);
  padding: 3px 0 3px 18px; position: relative;
}
.checklist li::before {
  content: ""; position: absolute; left: 0; top: 8px;
  width: 6px; height: 6px; border: 1px solid var(--mut); border-radius: 1px;
}
.donts { list-style: none; padding:0; margin: 0; }
.donts li {
  font-size: 11.5px; color: var(--ink-2);
  padding: 5px 9px 5px 22px;
  border-left: 2px solid var(--red); background: var(--red-bg);
  margin-bottom: 3px; border-radius: 2px; position: relative;
}
.donts li::before {
  content: "×"; position: absolute; left: 7px; top: 4px;
  color: var(--red); font-weight: 600; font-size: 13px;
}

/* Timeline */
.timeline-wrap { padding: 14px 18px; border-top: 1px solid var(--line); }
.timeline {
  display: grid; grid-template-columns: repeat(24, 1fr); gap: 1px;
  height: 18px; border-radius: 2px; overflow: hidden; margin: 6px 0 4px;
}
.timeline span { background: var(--green); }
.timeline span.green  { background: var(--green); }
.timeline span.orange { background: var(--orange); }
.timeline span.red    { background: var(--red); }
.timeline span.grey   { background: var(--grey); }
.timeline span.blue   { background: var(--blue); }
.timeline-scale {
  display: flex; justify-content: space-between;
  font-family: 'Geist Mono', monospace; font-size: 10px; color: var(--mut-2);
}
.timeline-events {
  display: grid; grid-template-columns: 70px 1fr;
  gap: 8px; margin-top: 14px;
}
.timeline-events .t { font-family: 'Geist Mono', monospace; font-size: 11px; color: var(--mut);}
.timeline-events .d {
  font-size: 11.5px; color: var(--ink-2);
  border-left: 1px solid var(--line); padding-left: 10px; position: relative;
}
.timeline-events .d::before {
  content: ""; position: absolute; left: -3px; top: 7px;
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--mut); border: 1px solid var(--surface);
}
.timeline-events .d.green::before  { background: var(--green); }
.timeline-events .d.orange::before { background: var(--orange); }
.timeline-events .d.red::before    { background: var(--red); }

/* Ticket note */
.ticket-note {
  background: var(--surface-2); border: 1px solid var(--line);
  border-radius: 4px; padding: 12px 14px;
  font-family: 'Geist Mono', monospace; font-size: 11.5px;
  color: var(--ink-2); white-space: pre-wrap; line-height: 1.6;
  overflow-x: auto; margin-top: 6px;
}
.ticket-note .hdr { color: var(--accent); }
.ticket-note .k   { color: var(--mut); }

/* Signal table */
.signal { border: 1px solid var(--line); border-radius: 6px; overflow: hidden; background: var(--surface); }
table.signal-table { width: 100%; border-collapse: collapse; font-size: 12px; }
table.signal-table thead th {
  text-align: left; font-size: 9.5px; text-transform: uppercase;
  letter-spacing: 0.12em; color: var(--mut); font-weight: 600;
  padding: 10px 12px; background: var(--surface-2);
  border-bottom: 1px solid var(--line); white-space: nowrap;
}
table.signal-table tbody td {
  padding: 9px 12px; border-bottom: 1px solid var(--line-2);
  color: var(--ink-2); vertical-align: middle;
}
table.signal-table tbody tr:last-child td { border-bottom: 0; }
table.signal-table tbody td.svc { color: var(--ink); font-weight: 500; }
table.signal-table tbody td.num {
  font-family: 'Geist Mono', monospace; font-variant-numeric: tabular-nums;
  text-align: right; width: 1%; white-space: nowrap;
}
table.signal-table tbody td.evidence { font-size: 11px; color: var(--ink-2); max-width: 380px;}
table.signal-table tbody td.evidence.muted { color: var(--mut-2); font-style: italic; }
table.signal-table tbody tr:hover td { background: var(--surface-2); }

/* Footer */
.radar-footer {
  margin-top: 28px; padding-top: 14px; border-top: 1px solid var(--line);
  font-size: 10.5px; color: var(--mut); font-family: 'Geist Mono', monospace;
  display: flex; gap: 20px; flex-wrap: wrap;
}
.radar-footer .l { letter-spacing: 0.02em; }
.radar-footer .r { margin-left: auto; color: var(--mut-2); }

::selection { background: var(--accent-bg); color: var(--ink); }
</style>
"""


def _inject_theme(theme: str):
    safe = "dark" if theme == "Dark" else "light"
    st.html(
        f"<script>document.documentElement.setAttribute('data-theme','{safe}');</script>"
    )


def main():
    st.html(_GLOBAL_STYLE)

    if "theme" not in st.session_state:
        st.session_state.theme = "Light"

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<div class="sb-brand">'
            '<span class="mark"></span>'
            '<span class="name">Incident Radar</span>'
            '<span class="ver">v1.0</span>'
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sb-section">Configuration</div>', unsafe_allow_html=True)
        display_mode = st.selectbox(
            "Display mode",
            ["Compact widget", "Full dashboard"],
            index=1,
            key="display_mode_select",
        )
        scenario_name = st.selectbox(
            "Scenario",
            list(SCENARIOS.keys()),
            index=1,
            key="scenario_select",
        )
        status_filter = st.selectbox(
            "Status filter",
            ["All", "Red", "Orange", "Grey", "Blue", "Green"],
            index=0,
            key="status_filter_select",
        )
        view_mode = st.selectbox(
            "View mode",
            ["Support desk", "Manager", "Technical"],
            index=2,
            key="view_mode_select",
        )

        st.markdown('<div class="sb-section">Display</div>', unsafe_allow_html=True)
        theme = st.radio(
            "Theme",
            ["Light", "Dark"],
            index=0 if st.session_state.theme == "Light" else 1,
            horizontal=True,
            key="theme_radio",
        )
        st.session_state.theme = theme

        show_healthy = True
        if display_mode == "Compact widget":
            show_healthy = st.checkbox(
                "Show healthy services",
                value=True,
                key="show_healthy_checkbox",
            )

        if st.button("Refresh mock data ↻", use_container_width=True, type="primary"):
            st.session_state.base_time = datetime.now(timezone.utc)
            st.session_state.selected_service = None
            st.rerun()

        st.markdown(
            '<div class="sb-fineprint">All data is synthetic. No real systems, '
            "no real customer data. Built for demonstration purposes only.</div>",
            unsafe_allow_html=True,
        )

    _inject_theme(theme)

    # ── State ─────────────────────────────────────────────────────────────────
    if "base_time" not in st.session_state:
        st.session_state.base_time = datetime.now(timezone.utc)
    if "selected_service" not in st.session_state:
        st.session_state.selected_service = None
    base_time = st.session_state.base_time

    scenario = load_scenario(scenario_name, base_time)
    services_data = scenario["services"]
    view_fields = get_view_mode_fields(view_mode)

    metrics = generate_summary_metrics(services_data, base_time)
    known_issues = generate_known_issues(services_data, base_time)
    evidence_rows = generate_signal_evidence(services_data)

    filtered_services = filter_services_by_status(services_data, status_filter)
    filtered_services = sort_services_by_severity(filtered_services)

    if display_mode == "Compact widget":
        render_compact_header(metrics, services_data)

        clicked = render_compact_service_lights(
            services_data, view_fields, show_healthy=show_healthy
        )
        if clicked:
            st.session_state.selected_service = clicked

        selected_svc = None
        if st.session_state.selected_service:
            visible_names = {
                svc["service"]
                for svc in (
                    services_data
                    if show_healthy
                    else [s for s in services_data if s["status"] != "green"]
                )
            }
            if st.session_state.selected_service not in visible_names:
                st.info(
                    f"Selected service '{st.session_state.selected_service}' "
                    "is hidden by the current compact filter."
                )
                st.session_state.selected_service = None
            else:
                for svc in services_data:
                    if svc["service"] == st.session_state.selected_service:
                        selected_svc = svc
                        break

        if selected_svc:
            render_compact_detail(selected_svc, view_fields)
    else:
        # Full dashboard
        st.html(
            render_topbar(
                metrics,
                scenario_name,
                scenario["description"],
                view_mode,
                base_time,
            )
        )

        n_metrics = 7
        st.html(_caption("Summary", f"{n_metrics:02d} metrics"))
        render_top_metrics(metrics, known_issues, base_time)

        st.html(
            _caption(
                "Active service notices",
                f"{len(known_issues):02d} active",
            )
        )
        render_known_issues(known_issues)

        st.html(
            _caption(
                "Service / module status",
                f"{len(filtered_services)} services · sorted by severity",
            )
        )

        cols = st.columns(4)
        for i, svc in enumerate(filtered_services):
            with cols[i % 4]:
                clicked = render_service_card(svc, view_fields, key=f"card_{i}")
                if clicked:
                    st.session_state.selected_service = svc["service"]
                    st.rerun()

        selected_svc = None
        if st.session_state.selected_service:
            for svc in services_data:
                if svc["service"] == st.session_state.selected_service:
                    selected_svc = svc
                    break

            if selected_svc is not None:
                render_detail_panel(selected_svc, view_fields, base_time=base_time)

        st.html(
            _caption("Signal evidence", f"{len(evidence_rows)} rows · last hour")
        )
        render_signal_table(evidence_rows, services_data)

    st.html(
        f'<footer class="radar-footer">'
        f'<span class="l">Support Desk Incident Radar · synthetic mockup · no real data</span>'
        f'<span class="r tnum">Generated {base_time.strftime("%Y-%m-%d %H:%M UTC")}</span>'
        f"</footer>"
    )


if __name__ == "__main__":
    main()
