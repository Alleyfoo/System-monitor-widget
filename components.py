"""Reusable UI components for Support Desk Incident Radar."""

import streamlit as st


def render_top_metrics(metrics: dict):
    cols = st.columns(7)
    with cols[0]:
        color = metrics["overall_color"]
        st.markdown(
            f'<div style="background:{color}15;border:2px solid {color};border-radius:8px;'
            f'padding:16px 12px;text-align:center;">'
            f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;'
            f'color:#6B7280;margin-bottom:4px;">Overall Status</div>'
            f'<div style="font-size:24px;font-weight:700;color:{color};">{metrics["overall_label"]}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.metric("Known Incidents", metrics["known_incidents"])
    with cols[2]:
        st.metric("Visibility Issues", metrics["visibility_issues"])
    with cols[3]:
        st.metric("Planned Maint.", metrics["planned_maintenance"])
    with cols[4]:
        st.metric("Tickets (1h)", metrics["tickets_last_hour"])
    with cols[5]:
        st.metric("Call Spike", f'{metrics["call_spike_pct"]}%')
    with cols[6]:
        st.metric("Last Updated", metrics["last_updated"])


def render_service_card(svc: dict, view_fields: dict, key: str) -> bool:
    color = svc["status_color"]
    label = svc["status_label"]
    emoji = {"green": "●", "orange": "◐", "red": "◉", "grey": "○", "blue": "◈"}[
        svc["status"]
    ]

    card_html = (
        f'<div style="background:white;border:2px solid {color};border-radius:10px;'
        f"padding:18px 16px;transition:box-shadow 0.15s;"
        f'box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'
        f'<span style="font-weight:600;font-size:15px;color:#111827;">{svc["service"]}</span>'
        f'<span style="font-size:18px;color:{color};">{emoji}</span>'
        f"</div>"
        f'<div style="display:inline-block;background:{color}18;color:{color};'
        f'font-size:11px;font-weight:600;padding:3px 10px;border-radius:12px;margin-bottom:8px;">'
        f"{label}</div>"
        f'<p style="font-size:12px;color:#6B7280;margin:0 0 8px;line-height:1.4;">{svc["impact_text"]}</p>'
        f'<div style="display:flex;gap:16px;font-size:11px;color:#9CA3AF;">'
    )

    if view_fields["show_confidence"]:
        card_html += f'<span>Confidence: {svc["confidence"]:.0%}</span>'
    card_html += f'<span>Checked: {svc["last_checked"]}</span>'
    card_html += (
        f'<span>C:{svc["calls"]} E:{svc["emails"]} T:{svc["tickets"]}</span>'
        f"</div></div>"
    )

    st.markdown(card_html, unsafe_allow_html=True)
    return st.button("View details", key=key, use_container_width=True)


def _build_ticket_note(svc: dict) -> str:
    lines = [
        f"=== Caller Handling Note ===",
        f"Service: {svc['service']}",
        f"Status: {svc['status_label']}",
    ]
    if svc.get("incident_id"):
        lines.append(f"Reference: {svc['incident_id']}")
    lines.append("")
    lines.append(f"Told caller: {svc['what_to_say']}")
    lines.append("")
    lines.append("To collect:")
    if svc["what_to_collect"]:
        for item in svc["what_to_collect"]:
            lines.append(f"  - {item}")
    else:
        lines.append("  - Nothing specific")
    lines.append("")
    lines.append("Do NOT promise:")
    for item in svc["what_not_to_do"]:
        lines.append(f"  - {item}")
    lines.append("")
    lines.append(f"Escalation: {svc['support_instruction']}")
    return "\n".join(lines)


def render_detail_panel(svc: dict, view_fields: dict):
    color = svc["status_color"]

    st.markdown("---")
    st.markdown(f"### {svc['service']} — Detail Panel")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Status:** :{color}[{svc['status_label']}]")
        st.markdown(f"**User Impact:** {svc['impact_text']}")
        if svc.get("incident_id"):
            st.markdown(f"**Incident ID:** `{svc['incident_id']}`")
        if view_fields["show_host_status"]:
            st.markdown(f"**Host Status:** `{svc['host_status']}`")
            st.markdown(f"**Module Status:** `{svc['module_status']}`")
        else:
            st.markdown(
                f"**System Status:** {svc.get('host_module_plain', 'No data available.')}"
            )
        if view_fields["show_technical_evidence"]:
            st.markdown(
                f"**Technical Evidence:** {svc.get('technical_evidence', 'No data')}"
            )
        else:
            st.markdown(f"**Caller Reports:** {svc.get('support_evidence', 'No data')}")

        if svc.get("affected_workflows"):
            st.markdown("**Affected Workflows:**")
            for wf in svc["affected_workflows"]:
                st.markdown(f"- {wf}")

    with col2:
        st.markdown("**What to say to caller:**")
        st.info(svc["what_to_say"])
        st.markdown("**What to collect:**")
        if svc["what_to_collect"]:
            for item in svc["what_to_collect"]:
                st.markdown(f"- {item}")
        else:
            st.markdown("- Nothing specific")

    st.markdown("**What NOT to do:**")
    for item in svc["what_not_to_do"]:
        st.warning(item)

    st.markdown(f"**Escalation:** {svc['support_instruction']}")

    st.markdown("---")
    st.markdown("#### Copy/Paste Ticket Note")
    note = _build_ticket_note(svc)
    st.text_area(
        "Copy this note into your ticket system",
        value=note,
        height=280,
        key=f"note_{svc['service']}",
        label_visibility="collapsed",
    )


def render_timeline(svc: dict):
    if "timeline" not in svc or not svc["timeline"]:
        return

    st.markdown("#### Incident Timeline")
    color_map = {
        "green": "#16A34A",
        "orange": "#EA580C",
        "red": "#DC2626",
        "grey": "#9CA3AF",
        "blue": "#2563EB",
    }

    html = '<div style="position:relative;padding-left:24px;margin:12px 0;">'
    html += '<div style="position:absolute;left:7px;top:4px;bottom:4px;width:2px;background:#E5E7EB;"></div>'

    for event in svc["timeline"]:
        c = color_map.get(event["status"], "#9CA3AF")
        html += (
            f'<div style="position:relative;margin-bottom:14px;">'
            f'<div style="position:absolute;left:-20px;top:4px;width:10px;height:10px;'
            f'border-radius:50%;background:{c};border:2px solid white;"></div>'
            f'<span style="font-size:11px;color:#9CA3AF;font-family:monospace;">{event["time"]}</span> '
            f'<span style="font-size:13px;color:#374151;">{event["description"]}</span>'
            f"</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_signal_table(evidence_rows: list[dict]):
    st.markdown("#### Signal Evidence Table")
    import pandas as pd

    df = pd.DataFrame(evidence_rows)
    st.dataframe(df, width="stretch", hide_index=True)


SHORT_NAMES = {
    "Login / Authentication": "Login",
    "Document generation": "Docs",
    "Ticketing system": "Tickets",
    "Data updates": "Data",
    "File shares": "Files",
    "Integrations": "Int",
    "Messaging": "Msg",
    "Reporting": "Reports",
    "Search": "Search",
    "Printing": "Print",
}

STATUS_DOT = {"green": "●", "orange": "◐", "red": "◉", "grey": "○", "blue": "◈"}


def _compact_header_html(metrics: dict, services_data: list[dict]) -> str:
    color = metrics["overall_color"]
    red_count = sum(1 for s in services_data if s["status"] == "red")
    orange_count = sum(1 for s in services_data if s["status"] == "orange")
    return (
        f'<div style="display:flex;align-items:center;gap:12px;'
        f"padding:8px 0 12px;border-bottom:1px solid #E5E7EB;margin-bottom:12px;"
        f'flex-wrap:wrap;">'
        f'<span style="font-weight:700;font-size:15px;color:#111827;">Support Radar</span>'
        f'<span style="font-size:18px;color:{color};">{STATUS_DOT.get(metrics["overall_status"], "●")}</span>'
        f'<span style="font-size:12px;color:#DC2626;">{red_count} red</span>'
        f'<span style="font-size:12px;color:#EA580C;">{orange_count} orange</span>'
        f'<span style="font-size:12px;color:#9CA3AF;">{metrics["visibility_issues"]} grey</span>'
        f'<span style="font-size:11px;color:#9CA3AF;margin-left:auto;">'
        f'Last checked {metrics["last_updated"]}</span>'
        f"</div>"
    )


def render_compact_header(metrics: dict, services_data: list[dict]):
    st.markdown(_compact_header_html(metrics, services_data), unsafe_allow_html=True)


def render_compact_service_lights(
    services_data: list[dict],
    view_fields: dict,
    show_healthy: bool = True,
) -> bool:
    severity_order = {"red": 0, "orange": 1, "grey": 2, "blue": 3, "green": 4}
    sorted_svcs = sorted(
        services_data, key=lambda s: severity_order.get(s["status"], 5)
    )

    green_svcs = [s for s in sorted_svcs if s["status"] == "green"]
    non_green = [s for s in sorted_svcs if s["status"] != "green"]

    clicked_service = None

    html_parts = [
        '<div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;">'
    ]
    for svc in non_green:
        short = SHORT_NAMES.get(svc["service"], svc["service"])
        color = svc["status_color"]
        dot = STATUS_DOT[svc["status"]]
        badge = ""
        if svc["status"] in ("red", "orange") and (svc["calls"] + svc["tickets"]) > 0:
            badge = f' <span style="font-size:10px;color:#6B7280;">{svc["calls"] + svc["tickets"]}</span>'
        html_parts.append(
            f'<div style="background:white;border:1.5px solid {color};border-radius:6px;'
            f"padding:5px 10px;display:flex;align-items:center;gap:5px;"
            f'font-size:12px;font-weight:500;color:#111827;white-space:nowrap;">'
            f'<span style="font-size:14px;color:{color};">{dot}</span>'
            f"{short}{badge}"
            f"</div>"
        )

    if show_healthy and green_svcs:
        html_parts.append(
            f'<span style="font-size:11px;color:#9CA3AF;margin-left:4px;">'
            f"{len(green_svcs)} healthy</span>"
        )
    elif not show_healthy and green_svcs:
        html_parts.append(
            f'<span style="font-size:11px;color:#9CA3AF;margin-left:4px;">'
            f"{len(green_svcs)} healthy services hidden</span>"
        )

    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)

    st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
    cols = st.columns(min(len(sorted_svcs), 10))
    for i, svc in enumerate(sorted_svcs):
        short = SHORT_NAMES.get(svc["service"], svc["service"])
        color = svc["status_color"]
        dot = STATUS_DOT[svc["status"]]
        with cols[i % 10]:
            if st.button(
                f"{dot} {short}",
                key=f"clight_{i}",
                use_container_width=True,
                help=f'{svc["service"]}: {svc["status_label"]}',
            ):
                clicked_service = svc["service"]

    return clicked_service


def render_compact_detail(svc: dict, view_fields: dict):
    color = svc["status_color"]

    st.markdown("---")
    st.markdown(f"#### {svc['service']} — {svc['status_label']}")

    st.markdown(f"**User Impact:** {svc['impact_text']}")
    if svc.get("incident_id"):
        st.markdown(f"**Incident ID:** `{svc['incident_id']}`")
    st.markdown(
        f"**System Status:** {svc.get('host_module_plain', 'No data available.')}"
    )

    st.markdown("**What to say to caller:**")
    st.info(svc["what_to_say"])

    st.markdown("**What to collect:**")
    if svc["what_to_collect"]:
        for item in svc["what_to_collect"]:
            st.markdown(f"- {item}")
    else:
        st.markdown("- Nothing specific")

    with st.expander("Affected workflows"):
        if svc.get("affected_workflows"):
            for wf in svc["affected_workflows"]:
                st.markdown(f"- {wf}")
        else:
            st.markdown("No workflow data available.")

    with st.expander("Caller reports"):
        st.markdown(svc.get("support_evidence", "No data"))

    if view_fields["show_technical_evidence"]:
        with st.expander("Technical evidence"):
            st.markdown(svc.get("technical_evidence", "No data"))

    st.markdown("---")
    st.markdown("#### Copy/Paste Ticket Note")
    note = _build_ticket_note(svc)
    st.text_area(
        "Copy this note into your ticket system",
        value=note,
        height=280,
        key=f"cnote_{svc['service']}",
        label_visibility="collapsed",
    )


def render_known_issues(issues: list[dict]):
    if not issues:
        st.info("No active service notices.")
        return

    for issue in issues:
        color = issue["status_color"]
        st.markdown(
            f'<div style="background:white;border-left:4px solid {color};border-radius:6px;'
            f'padding:14px 16px;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,0.05);">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
            f'<span style="font-weight:600;font-size:14px;">{issue["title"]}</span>'
            f'<span style="background:{color}18;color:{color};font-size:11px;font-weight:600;'
            f'padding:2px 10px;border-radius:10px;">{issue["status"]}</span>'
            f"</div>"
            f'<div style="font-size:12px;color:#6B7280;margin-top:6px;display:flex;flex-wrap:wrap;gap:16px;">'
            f'<span>Started: {issue["started"]}</span>'
            f'<span>{issue["incident_id"]}</span>'
            f'<span>{issue["owner"]}</span>'
            f"</div>"
            f'<div style="font-size:12px;color:#374151;margin-top:8px;background:#F9FAFB;'
            f'padding:8px 10px;border-radius:4px;">'
            f'<strong>Support instruction:</strong> {issue["support_instruction"]}'
            f"</div></div>",
            unsafe_allow_html=True,
        )
