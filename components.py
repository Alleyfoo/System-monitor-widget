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
