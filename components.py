"""Reusable UI components for Support Desk Incident Radar."""

import html
import re

import streamlit as st


_BADGE_LABELS = {
    "red": "Major",
    "orange": "Degraded",
    "green": "Healthy",
    "grey": "Unknown",
    "blue": "Maint.",
}


def _badge(status: str, label: str | None = None) -> str:
    text = label if label is not None else _BADGE_LABELS.get(status, status)
    return (
        f'<span class="badge {status}"><span class="d"></span>'
        f"{html.escape(text)}</span>"
    )


def _caption(title: str, count: str) -> str:
    return (
        f'<div class="caption"><h2>{html.escape(title)}</h2>'
        f'<div class="rule"></div>'
        f'<div class="count mono">{html.escape(count)}</div></div>'
    )


def _spark(values: list[float], color_var: str, height: int = 18) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1.0
    top_pad = 2
    span = height - top_pad - 2
    pts = " ".join(
        f"{i * (100 / (len(values) - 1)):.1f},"
        f"{(height - 2) - ((v - lo) / rng) * span:.1f}"
        for i, v in enumerate(values)
    )
    return (
        f'<svg class="spark" viewBox="0 0 100 {height}" preserveAspectRatio="none">'
        f'<polyline fill="none" stroke="{color_var}" stroke-width="1.2" '
        f'points="{pts}"/></svg>'
    )


def _ribbon(statuses: list[str], cls: str = "ribbon") -> str:
    cells = "".join(f'<span class="{s}"></span>' for s in statuses)
    return f'<div class="{cls}">{cells}</div>'


def render_topbar(
    metrics: dict,
    scenario_name: str,
    scenario_description: str,
    view_mode: str,
    base_time,
) -> str:
    pulse_color = metrics["overall_color"]
    return (
        f'<div class="topbar">'
        f"<div>"
        f'<h1>Support Desk Incident Radar</h1>'
        f'<div class="sub">{html.escape(scenario_description)}</div>'
        f"</div>"
        f'<div class="meta">'
        f'<div class="row">Scenario <span class="v mono">{html.escape(scenario_name)}</span></div>'
        f'<div class="row">View <span class="v mono">{html.escape(view_mode)}</span></div>'
        f'<div class="pulse"><span class="dot" style="background:{pulse_color};'
        f'box-shadow:0 0 0 0 {pulse_color}"></span>'
        f'<span>LIVE · {base_time.strftime("%Y-%m-%d %H:%M UTC")}</span></div>'
        f"</div></div>"
    )


def render_top_metrics(metrics: dict, known_issues: list[dict], base_time):
    overall = metrics["overall_status"]
    overall_color = metrics["overall_color"]
    overall_label = metrics["overall_label"]

    counts = {
        "red": metrics.get("red_count", 0),
        "orange": metrics.get("orange_count", 0),
        "green": metrics.get("green_count", 0),
        "grey": metrics.get("grey_count", 0),
        "blue": metrics.get("blue_count", 0),
    }

    since_html = ""
    if known_issues:
        starts = sorted(i["started"] for i in known_issues)
        since_html = f'<span class="since">since {html.escape(starts[0])}</span>'

    spark_color_var = (
        "var(--red)" if overall == "red"
        else "var(--orange)" if overall == "orange"
        else "var(--mut-2)"
    )
    call_spike = metrics["call_spike_pct"]
    call_spike_color = (
        "var(--red)" if call_spike >= 100
        else "var(--orange)" if call_spike >= 30
        else "var(--ink)"
    )
    delta_known = (
        f"+{metrics['known_incidents']} vs 1h ago"
        if metrics["known_incidents"] > 0
        else "— stable"
    )
    tickets_spark = _spark(
        [3, 4, 5, 6, 7, 9, 12, 14, 17, 18, 19] if overall == "red"
        else [5, 5, 6, 6, 5, 6, 7, 6, 6, 5, 6],
        spark_color_var,
        height=24,
    )
    call_spark = _spark(
        [2, 3, 5, 8, 12, 16, 20, 24, 28, 32, 34] if call_spike >= 100
        else [6, 6, 7, 6, 7, 6, 6, 7, 6, 7, 6],
        spark_color_var,
        height=24,
    )

    hero_value_style = (
        f"font-family: 'Geist', sans-serif; font-size:22px; font-weight:600; "
        f"letter-spacing:-0.01em; color:{overall_color};"
    )

    breakdown = (
        f'<div class="breakdown">'
        f'<span><span class="dot" style="background:var(--red)"></span>'
        f'{counts["red"]} red</span>'
        f'<span><span class="dot" style="background:var(--orange)"></span>'
        f'{counts["orange"]} orange</span>'
        f'<span><span class="dot" style="background:var(--green)"></span>'
        f'{counts["green"]} healthy</span>'
        f"</div>"
    )

    html_str = (
        f'<section class="kpis">'
        f'<div class="kpi kpi-hero">'
        f'<span class="strip" style="background:{overall_color}"></span>'
        f'<div class="lbl-row"><span class="lbl">Overall status</span>{since_html}</div>'
        f"<div>"
        f'<div class="val" style="{hero_value_style}">{html.escape(overall_label)}</div>'
        f"{breakdown}"
        f"</div></div>"
        f'<div class="kpi"><span class="lbl">Known incidents</span>'
        f'<span class="val tnum">{metrics["known_incidents"]}</span>'
        f'<span class="delta">{delta_known}</span></div>'
        f'<div class="kpi"><span class="lbl">Visibility issues</span>'
        f'<span class="val tnum">{metrics["visibility_issues"]}</span>'
        f'<span class="delta">— stable</span></div>'
        f'<div class="kpi"><span class="lbl">Planned maint.</span>'
        f'<span class="val tnum">{metrics["planned_maintenance"]}</span>'
        f'<span class="delta">— none</span></div>'
        f'<div class="kpi"><span class="lbl">Tickets · 1h</span>'
        f'<span class="val tnum">{metrics["tickets_last_hour"]}</span>'
        f"{tickets_spark}</div>"
        f'<div class="kpi"><span class="lbl">Call spike</span>'
        f'<span class="val tnum" style="color:{call_spike_color}">{call_spike:+d}%</span>'
        f"{call_spark}</div>"
        f'<div class="kpi"><span class="lbl">Last checked</span>'
        f'<span class="val tnum" style="font-size:18px;">'
        f'{base_time.strftime("%H:%M")}</span>'
        f'<span class="delta">just now</span></div>'
        f"</section>"
    )
    st.html(html_str)


def render_known_issues(issues: list[dict]):
    if not issues:
        st.html(
            '<div style="border:1px solid var(--line);border-radius:6px;'
            'background:var(--surface);padding:14px 16px;color:var(--mut);'
            'font-size:12px;">No active service notices.</div>'
        )
        return

    rows = []
    for issue in issues:
        status = issue["status_key"]
        color_var = f"var(--{status})"
        evidence = issue.get("evidence") or ""
        rows.append(
            f'<article class="notice">'
            f'<span class="bar" style="background:{color_var}"></span>'
            f'<div class="ttl">'
            f'<span class="name">{html.escape(issue["service"])}</span>'
            f'<span class="sub">{html.escape(evidence)}</span>'
            f"</div>"
            f'<div class="meta-col">'
            f'<div><span class="k">Started</span>'
            f'<span class="tnum">{html.escape(issue["started_utc"])}</span></div>'
            f'<div><span class="k">Ref</span>'
            f'<span class="tnum">{html.escape(issue["incident_id"])}</span></div>'
            f'<div><span class="k">Owner</span>'
            f'{html.escape(issue["owner"])}</div>'
            f"</div>"
            f'{_badge(status, _BADGE_LABELS[status] if status != "red" else "Major issue")}'
            f'<p class="instr">{html.escape(issue["support_instruction"])}</p>'
            f"</article>"
        )
    st.html(f'<section class="notices">{"".join(rows)}</section>')


def render_service_card(svc: dict, view_fields: dict, key: str) -> bool:
    status = svc["status"]
    selected = (
        st.session_state.get("selected_service") == svc["service"]
    )
    sel_cls = " selected" if selected else ""
    badge_label = (
        "Major" if status == "red"
        else _BADGE_LABELS.get(status, status)
    )
    ribbon_html = _ribbon(svc.get("ribbon", ["green"] * 24))
    spark_html = _spark(
        svc.get("traffic_series", []),
        f"var(--{status})",
        height=18,
    )
    stats_html = (
        f'<div class="stats">'
        f'<span><b>C</b> {svc["calls"]}</span>'
        f'<span><b>E</b> {svc["emails"]}</span>'
        f'<span><b>T</b> {svc["tickets"]}</span>'
        f"</div>"
    )
    card_html = (
        f'<article class="card{sel_cls}" data-status="{status}">'
        f'<span class="stripe"></span>'
        f'<div class="head">'
        f'<span class="name">{html.escape(svc["service"])}</span>'
        f"{_badge(status, badge_label)}"
        f"</div>"
        f'<p class="impact">{html.escape(svc["impact_text"])}</p>'
        f"{ribbon_html}"
        f"{spark_html}"
        f'<div class="foot">'
        f"{stats_html}"
        f'<span class="chk">↻ {html.escape(svc["last_checked"])}</span>'
        f"</div>"
        f"</article>"
    )
    st.html(card_html)
    return st.button("View details", key=key, use_container_width=True)


def _build_ticket_note(svc: dict) -> str:
    lines = [
        "=== Caller Handling Note ===",
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


def _ticket_note_html(svc: dict) -> str:
    raw = _build_ticket_note(svc)
    escaped = html.escape(raw)
    # Header
    escaped = escaped.replace(
        "=== Caller Handling Note ===",
        '<span class="hdr">=== Caller Handling Note ===</span>',
    )
    # Labels at line starts
    label_re = re.compile(
        r"^(Service:|Status:|Reference:|Told caller:|To collect:|Do NOT promise:|Escalation:)",
        re.MULTILINE,
    )
    escaped = label_re.sub(r'<span class="k">\1</span>', escaped)
    return escaped


def _evidence_with_codes(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(
        r"([A-Z]+-[A-Z]-\d+)",
        r'<span style="color:var(--red)">\1</span>',
        escaped,
    )


def render_detail_panel(svc: dict, view_fields: dict, base_time=None):
    status = svc["status"]
    color_var = f"var(--{status})"
    started = ""
    age = ""
    if svc.get("timeline"):
        first = svc["timeline"][0]
        started = f' · started {html.escape(first["time"])} UTC'
    badge_label = "Major issue" if status == "red" else _BADGE_LABELS.get(status, status)

    workflows_html = ""
    if svc.get("affected_workflows"):
        items = "".join(
            f"<li>{html.escape(w)}</li>" for w in svc["affected_workflows"]
        )
        workflows_html = (
            '<p class="dlabel">Affected workflows</p>'
            f'<ul class="workflows">{items}</ul>'
        )

    host_module_html = ""
    if view_fields.get("show_host_status"):
        host_module_html = (
            '<p class="dlabel">Host / module</p>'
            f'<div class="v mono">host={html.escape(svc.get("host_status",""))} · '
            f'module={html.escape(svc.get("module_status",""))}</div>'
        )

    if view_fields.get("show_technical_evidence"):
        evidence_html = (
            '<p class="dlabel">Technical evidence</p>'
            f'<p class="v mono" style="line-height:1.6;">'
            f'{_evidence_with_codes(svc.get("technical_evidence","no data"))}</p>'
        )
    else:
        evidence_html = (
            '<p class="dlabel">Caller reports</p>'
            f'<p>{html.escape(svc.get("support_evidence","no data"))}</p>'
        )

    collect_items = svc.get("what_to_collect") or ["Nothing specific"]
    collect_html = "".join(
        f"<li>{html.escape(item)}</li>" for item in collect_items
    )
    donts_html = "".join(
        f"<li>{html.escape(item)}</li>" for item in svc.get("what_not_to_do", [])
    )

    # Timeline ribbon + events
    ribbon_html = _ribbon(svc.get("ribbon", ["green"] * 24), cls="timeline")
    if base_time is not None:
        from datetime import timedelta
        scale_times = [
            (base_time - timedelta(minutes=120)).strftime("%H:%M"),
            (base_time - timedelta(minutes=100)).strftime("%H:%M"),
            (base_time - timedelta(minutes=70)).strftime("%H:%M"),
            (base_time - timedelta(minutes=40)).strftime("%H:%M"),
            (base_time - timedelta(minutes=10)).strftime("%H:%M"),
            "now",
        ]
    else:
        scale_times = ["-2h", "", "", "", "", "now"]
    scale_html = "".join(f"<span>{s}</span>" for s in scale_times)

    events_html = ""
    if svc.get("timeline"):
        rows = []
        for ev in svc["timeline"]:
            est = ev.get("status", "grey")
            rows.append(
                f'<span class="t">{html.escape(ev["time"])}</span>'
                f'<span class="d {est}">{html.escape(ev["description"])}</span>'
            )
        events_html = (
            f'<div class="timeline-events">{"".join(rows)}</div>'
        )

    panel_html = (
        f'<section class="detail">'
        f'<header class="detail-head">'
        f'<div class="l">'
        f'<span class="stripe" style="background:{color_var}"></span>'
        f'<h3>{html.escape(svc["service"])}</h3>'
        f"{_badge(status, badge_label)}"
        f'<span class="id">{html.escape(svc.get("incident_id") or "")}{started}</span>'
        f"</div>"
        f'<div class="actions">'
        f"<button>Open ticket</button>"
        f"<button>Subscribe</button>"
        f'<button class="primary">Copy ticket note</button>'
        f"</div>"
        f"</header>"
        f'<div class="detail-body">'
        f'<div class="dcol">'
        f'<p class="dlabel">User impact</p>'
        f'<p>{html.escape(svc.get("impact_text",""))}</p>'
        f'<p class="dlabel">System status</p>'
        f'<p class="v">{html.escape(svc.get("host_module_plain",""))}</p>'
        f"{host_module_html}"
        f"{evidence_html}"
        f"{workflows_html}"
        f"</div>"
        f'<div class="dcol">'
        f'<p class="dlabel">What to say to caller</p>'
        f'<div class="say">{html.escape(svc.get("what_to_say",""))}</div>'
        f'<p class="dlabel">What to collect</p>'
        f'<ul class="checklist">{collect_html}</ul>'
        f'<p class="dlabel">What NOT to do</p>'
        f'<ul class="donts">{donts_html}</ul>'
        f"</div>"
        f'<div class="dcol">'
        f'<p class="dlabel">Copy / paste ticket note</p>'
        f'<pre class="ticket-note">{_ticket_note_html(svc)}</pre>'
        f"</div>"
        f"</div>"
        f'<div class="timeline-wrap">'
        f'<div style="display:flex;align-items:baseline;justify-content:space-between;">'
        f'<p class="dlabel" style="margin:0;">Incident timeline · last 2h</p>'
        f'<span class="mono" style="font-size:10px;color:var(--mut-2);">'
        f"5-min resolution</span>"
        f"</div>"
        f"{ribbon_html}"
        f'<div class="timeline-scale">{scale_html}</div>'
        f"{events_html}"
        f"</div>"
        f"</section>"
    )
    st.html(panel_html)


def render_signal_table(evidence_rows: list[dict], services_data: list[dict]):
    svc_map = {s["service"]: s for s in services_data}
    rows = []
    for r in evidence_rows:
        svc = svc_map.get(r["Service"])
        if not svc:
            continue
        status = svc["status"]
        evidence = r["Monitor Evidence"]
        evidence_cls = "evidence"
        if "synthetic check" in evidence:
            evidence_cls += " muted"
        manual_cell = "—"
        if r["Manual Flag"] == "Yes":
            manual_cell = (
                f'<span class="badge {status}" '
                f'style="font-size:9.5px;padding:2px 6px;">Yes</span>'
            )
        rows.append(
            f"<tr>"
            f'<td class="svc">{html.escape(r["Service"])}</td>'
            f"<td>{_badge(status, 'Major' if status == 'red' else _BADGE_LABELS[status])}</td>"
            f'<td class="num">{r["Calls (1h)"]}</td>'
            f'<td class="num">{r["Emails (1h)"]}</td>'
            f'<td class="num">{r["Tickets (1h)"]}</td>'
            f"<td>{manual_cell}</td>"
            f'<td class="{evidence_cls}">{html.escape(evidence)}</td>'
            f'<td class="num">{html.escape(r["Confidence"])}</td>'
            f"</tr>"
        )
    table_html = (
        f'<section class="signal"><table class="signal-table">'
        f"<thead><tr>"
        f"<th>Service</th><th>Status</th>"
        f'<th style="text-align:right;">Calls</th>'
        f'<th style="text-align:right;">Emails</th>'
        f'<th style="text-align:right;">Tickets</th>'
        f"<th>Manual flag</th><th>Monitor evidence</th>"
        f'<th style="text-align:right;">Conf.</th>'
        f"</tr></thead>"
        f'<tbody>{"".join(rows)}</tbody>'
        f"</table></section>"
    )
    st.html(table_html)


# ── Compact widget components (unchanged) ─────────────────────────────────────

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
        f"padding:8px 0 12px;border-bottom:1px solid var(--line);margin-bottom:12px;"
        f'flex-wrap:wrap;">'
        f'<span style="font-weight:700;font-size:15px;color:var(--ink);">Support Radar</span>'
        f'<span style="font-size:18px;color:{color};">{STATUS_DOT.get(metrics["overall_status"], "●")}</span>'
        f'<span style="font-size:12px;color:var(--red);">{red_count} red</span>'
        f'<span style="font-size:12px;color:var(--orange);">{orange_count} orange</span>'
        f'<span style="font-size:12px;color:var(--mut);">{metrics["visibility_issues"]} grey</span>'
        f'<span style="font-size:11px;color:var(--mut-2);margin-left:auto;">'
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
            badge = f' <span style="font-size:10px;color:var(--mut);">{svc["calls"] + svc["tickets"]}</span>'
        html_parts.append(
            f'<div style="background:var(--surface);border:1.5px solid {color};border-radius:6px;'
            f"padding:5px 10px;display:flex;align-items:center;gap:5px;"
            f'font-size:12px;font-weight:500;color:var(--ink);white-space:nowrap;">'
            f'<span style="font-size:14px;color:{color};">{dot}</span>'
            f"{short}{badge}"
            f"</div>"
        )

    if show_healthy and green_svcs:
        html_parts.append(
            f'<span style="font-size:11px;color:var(--mut-2);margin-left:4px;">'
            f"{len(green_svcs)} healthy</span>"
        )
    elif not show_healthy and green_svcs:
        html_parts.append(
            f'<span style="font-size:11px;color:var(--mut-2);margin-left:4px;">'
            f"{len(green_svcs)} healthy services hidden</span>"
        )

    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)

    visible_svcs = sorted_svcs if show_healthy else non_green
    if not visible_svcs:
        st.info("All services are healthy.")
        return None

    st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
    cols = st.columns(min(len(visible_svcs), 10))
    for i, svc in enumerate(visible_svcs):
        short = SHORT_NAMES.get(svc["service"], svc["service"])
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
