"""Support Desk Incident Radar — Streamlit mockup dashboard.

Synthetic-only early-warning support dashboard that translates technical/operational
signals into customer-service guidance. No real systems, no real data.
"""

from datetime import datetime, timezone

import streamlit as st

from components import (
    render_compact_detail,
    render_compact_header,
    render_compact_service_lights,
    render_detail_panel,
    render_known_issues,
    render_service_card,
    render_signal_table,
    render_timeline,
    render_top_metrics,
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

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, .stApp {
    font-family: 'Inter', system-ui, sans-serif;
    background: #F3F4F6;
    color: #111827;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111827;
}
[data-testid="stSidebar"] * {
    color: #F9FAFB !important;
}
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] input {
    background: #1F2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1F2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 6px !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #6B7280;
}
[data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}

/* Buttons */
.stButton > button {
    border-radius: 6px;
    font-weight: 500;
    font-size: 13px;
    transition: all 0.15s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
}
[data-testid="stDataFrame"] th {
    background: #F9FAFB;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6B7280;
}

/* Headings */
h1 { font-size: 28px; font-weight: 700; color: #111827; }
h2 { font-size: 20px; font-weight: 600; color: #111827; }
h3 { font-size: 16px; font-weight: 600; color: #111827; }

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    background: white;
}
</style>
"""
)


def main():
    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            '<div style="font-size:18px;font-weight:700;margin-bottom:4px;">'
            "Incident Radar</div>"
            '<div style="font-size:11px;color:#9CA3AF;margin-bottom:20px;'
            'padding-bottom:16px;border-bottom:1px solid #374151;">'
            "Support Desk · v1.0</div>",
            unsafe_allow_html=True,
        )

        st.markdown("### Configuration")
        display_mode = st.selectbox(
            "Display Mode",
            ["Compact widget", "Full dashboard"],
            index=0,
            key="display_mode_select",
            help="Compact widget: small service lights. Full dashboard: complete view with metrics and notices.",
        )

        scenario_name = st.selectbox(
            "Scenario",
            list(SCENARIOS.keys()),
            index=0,
            key="scenario_select",
            help="Select a pre-built incident scenario",
        )

        status_filter = st.selectbox(
            "Status Filter",
            ["All", "Red", "Orange", "Grey", "Blue", "Green"],
            index=0,
            key="status_filter_select",
            help="Filter service cards by status",
        )

        view_mode = st.selectbox(
            "View Mode",
            ["Support desk", "Manager", "Technical"],
            index=0,
            key="view_mode_select",
            help="Support desk: simplified view. Manager: confidence + timeline. Technical: full details.",
        )

        show_healthy = True
        if display_mode == "Compact widget":
            show_healthy = st.checkbox(
                "Show healthy services",
                value=True,
                key="show_healthy_checkbox",
                help="When unchecked, green services are collapsed into a summary line.",
            )

        st.markdown("---")
        if st.button("Refresh mock data", use_container_width=True, type="primary"):
            st.session_state.base_time = datetime.now(timezone.utc)
            st.session_state.selected_service = None
            st.rerun()

        st.markdown("---")
        st.markdown(
            '<div style="font-size:10px;color:#6B7280;line-height:1.5;">'
            "All data is synthetic. No real systems, no real customer data.<br>"
            "Built for demonstration purposes only.</div>",
            unsafe_allow_html=True,
        )

    # ── Initialize / retrieve session state ───────────────────────────────────
    if "base_time" not in st.session_state:
        st.session_state.base_time = datetime.now(timezone.utc)
    if "selected_service" not in st.session_state:
        st.session_state.selected_service = None

    base_time = st.session_state.base_time

    # ── Load scenario data ────────────────────────────────────────────────────
    scenario = load_scenario(scenario_name, base_time)
    services_data = scenario["services"]
    view_fields = get_view_mode_fields(view_mode)

    # ── Compute derived data ──────────────────────────────────────────────────
    metrics = generate_summary_metrics(services_data, base_time)
    known_issues = generate_known_issues(services_data, base_time)
    evidence_rows = generate_signal_evidence(services_data)

    filtered_services = filter_services_by_status(services_data, status_filter)
    filtered_services = sort_services_by_severity(filtered_services)

    # ── Page header ───────────────────────────────────────────────────────────
    if display_mode == "Compact widget":
        render_compact_header(metrics, services_data)
    else:
        st.markdown(
            '<div style="display:flex;align-items:center;justify-content:space-between;'
            'padding:0 0 16px;border-bottom:1px solid #E5E7EB;margin-bottom:20px;">'
            "<div>"
            '<h1 style="margin:0;">Support Desk Incident Radar</h1>'
            f'<p style="margin:4px 0 0;color:#6B7280;font-size:13px;">{scenario["description"]}</p>'
            "</div>"
            f'<span style="font-size:11px;color:#9CA3AF;font-family:monospace;">'
            f"Scenario: {scenario_name} | Mode: {view_mode}</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    if display_mode == "Compact widget":
        # ── Compact widget mode ────────────────────────────────────────────────
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
        # ── Full dashboard mode ────────────────────────────────────────────────
        # Top summary metrics
        st.markdown("### Summary")
        render_top_metrics(metrics)

        # Active service notices
        st.markdown("---")
        st.markdown("### Active Service Notices")
        render_known_issues(known_issues)

        # Service cards grid
        st.markdown("---")
        st.markdown("### Service / Module Status")

        cols = st.columns(3)

        for i, svc in enumerate(filtered_services):
            with cols[i % 3]:
                clicked = render_service_card(svc, view_fields, key=f"card_{i}")
                if clicked:
                    st.session_state.selected_service = svc["service"]

        # Detail panel for selected service
        selected_svc = None
        if st.session_state.selected_service:
            for svc in services_data:
                if svc["service"] == st.session_state.selected_service:
                    selected_svc = svc
                    break

            if selected_svc is None:
                st.info(
                    f"Previously selected service '{st.session_state.selected_service}' "
                    "is not visible with the current filter."
                )
            else:
                st.markdown("---")
                render_detail_panel(selected_svc, view_fields)

                if view_fields["show_timeline"]:
                    render_timeline(selected_svc)

        # Signal evidence table
        st.markdown("---")
        render_signal_table(evidence_rows)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div style="text-align:center;font-size:11px;color:#9CA3AF;padding:16px 0;">'
        "Support Desk Incident Radar · Synthetic mockup · No real data · "
        f'Generated {base_time.strftime("%Y-%m-%d %H:%M UTC")}'
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
