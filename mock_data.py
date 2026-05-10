"""Synthetic data generation for Support Desk Incident Radar.

All data is mock data — no real systems, no real customer/patient data.
"""

import hashlib
from datetime import datetime, timedelta, timezone

import numpy as np

SERVICES = [
    "Login / Authentication",
    "Search",
    "Document generation",
    "Printing",
    "Messaging",
    "Integrations",
    "Data updates",
    "Reporting",
    "File shares",
    "Ticketing system",
]

STATUS_COLORS = {
    "green": "#16A34A",
    "orange": "#EA580C",
    "red": "#DC2626",
    "grey": "#9CA3AF",
    "blue": "#2563EB",
}

STATUS_LABELS = {
    "green": "Healthy",
    "orange": "Degraded",
    "red": "Major Issue",
    "grey": "Unknown",
    "blue": "Maintenance",
}

SUPPORT_GUIDANCE = {
    "green": "No action needed. Service is operating normally.",
    "orange": "Acknowledge the issue. We are aware and investigating. No ETA yet.",
    "red": "Major incident declared. Engineering team is actively working on it. Refer to incident #{incident_id}.",
    "grey": "Monitoring data is unavailable. Treat as potentially degraded. Collect caller details.",
    "blue": "Planned maintenance window. Expected to complete by {maintenance_end}.",
}

WHAT_TO_SAY = {
    "green": "Everything is running normally. Is there anything else I can help with?",
    "orange": "We're seeing some slowdowns with {service}. Our team is looking into it. I'll note your report.",
    "red": "We have an active incident for {service}. The team is working on a fix. I can add your details to the incident.",
    "grey": "We don't have current status data for {service}. Let me collect your information and we'll follow up.",
    "blue": "{service} is undergoing planned maintenance. It should be back by {maintenance_end}.",
}

WHAT_TO_COLLECT = {
    "green": [],
    "orange": ["Caller name", "Contact number", "Exact error message if any", "Time issue started"],
    "red": ["Caller name", "Contact number", "Impact description", "Whether they want incident updates"],
    "grey": ["Caller name", "Contact number", "Full description of the issue", "Screenshots if available"],
    "blue": ["Caller name", "Contact number", "Urgency level if before maintenance end"],
}

WHAT_NOT_TO_DO = {
    "green": ["Don't escalate unnecessarily"],
    "orange": ["Don't promise a fix time", "Don't suggest workarounds unless confirmed"],
    "red": ["Don't promise a fix time", "Don't transfer to engineering directly", "Don't suggest the caller try again immediately"],
    "grey": ["Don't guess the status", "Don't tell the caller 'everything is fine'"],
    "blue": ["Don't tell callers to bypass maintenance", "Don't promise early completion"],
}


def _seeded_random(seed: str) -> np.random.Generator:
    digest = int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16)
    return np.random.default_rng(digest)


def generate_incident_id(index: int) -> str:
    return f"INC-{2026:04d}-{index + 1000:04d}"


def generate_service_data(service: str, status: str, base_time: datetime) -> dict:
    rng = _seeded_random(f"svc-{service}-{status}-{base_time.isoformat()}")
    confidence = {
        "green": rng.uniform(0.85, 0.99),
        "orange": rng.uniform(0.60, 0.85),
        "red": rng.uniform(0.70, 0.95),
        "grey": rng.uniform(0.10, 0.40),
        "blue": rng.uniform(0.90, 0.99),
    }[status]

    calls = {
        "green": int(rng.integers(0, 5)),
        "orange": int(rng.integers(8, 30)),
        "red": int(rng.integers(25, 80)),
        "grey": int(rng.integers(2, 12)),
        "blue": int(rng.integers(1, 8)),
    }[status]

    emails = {
        "green": int(rng.integers(0, 3)),
        "orange": int(rng.integers(5, 20)),
        "red": int(rng.integers(15, 50)),
        "grey": int(rng.integers(1, 8)),
        "blue": int(rng.integers(1, 5)),
    }[status]

    tickets = {
        "green": int(rng.integers(0, 2)),
        "orange": int(rng.integers(3, 15)),
        "red": int(rng.integers(10, 35)),
        "grey": int(rng.integers(1, 6)),
        "blue": int(rng.integers(0, 3)),
    }[status]

    manual_flags = status in ("orange", "red")

    host_status = "up" if status != "red" else rng.choice(["up", "degraded"], p=[0.6, 0.4])
    module_status = status if status != "grey" else "unknown"

    impact_text = {
        "green": "No user impact detected",
        "orange": "Some users may experience slowness or intermittent errors",
        "red": "Users unable to complete tasks. High impact.",
        "grey": "Unable to determine current impact",
        "blue": "Service temporarily unavailable during maintenance window",
    }[status]

    last_checked = (base_time - timedelta(minutes=int(rng.integers(1, 15)))).strftime("%H:%M")

    return {
        "service": service,
        "status": status,
        "status_color": STATUS_COLORS[status],
        "status_label": STATUS_LABELS[status],
        "confidence": round(confidence, 2),
        "impact_text": impact_text,
        "last_checked": last_checked,
        "calls": calls,
        "emails": emails,
        "tickets": tickets,
        "manual_flags": manual_flags,
        "host_status": host_status,
        "module_status": module_status,
        "evidence_source": "synthetic check" if status != "grey" else "no data",
        "what_to_say": WHAT_TO_SAY[status].format(service=service, maintenance_end="14:00"),
        "what_to_collect": WHAT_TO_COLLECT[status],
        "what_not_to_do": WHAT_NOT_TO_DO[status],
        "support_instruction": SUPPORT_GUIDANCE[status].format(
            incident_id="INC-2026-1001", maintenance_end="14:00"
        ),
    }


def generate_timeline_events(
    service: str, status: str, base_time: datetime, num_events: int = 6
) -> list[dict]:
    rng = _seeded_random(f"tl-{service}-{status}-{base_time.isoformat()}")
    if status == "green":
        statuses = ["green"] * num_events
    elif status == "orange":
        statuses = (["green"] * 3 + ["orange"] * 3)[:num_events]
    elif status == "red":
        statuses = (["green"] * 2 + ["orange"] * 2 + ["red"] * 2)[:num_events]
    elif status == "grey":
        statuses = (["green"] * 3 + ["grey"] * 3)[:num_events]
    else:
        statuses = (["green"] * 2 + ["blue"] * 4)[:num_events]

    descriptions = {
        "green": "Service operating normally",
        "orange": "Degradation detected — increased latency",
        "red": "Major incident — service unavailable",
        "grey": "Monitoring data lost",
        "blue": "Maintenance window started",
    }

    events = []
    for i in range(num_events):
        ts = base_time - timedelta(minutes=(num_events - i) * 15 + int(rng.integers(-5, 5)))
        events.append({
            "time": ts.strftime("%H:%M"),
            "status": statuses[i],
            "description": descriptions[statuses[i]],
        })
    return events


def generate_signal_evidence(services_data: list[dict]) -> list[dict]:
    rows = []
    for svc in services_data:
        rows.append({
            "Service": svc["service"],
            "Calls (1h)": svc["calls"],
            "Emails (1h)": svc["emails"],
            "Tickets (1h)": svc["tickets"],
            "Manual Flag": "Yes" if svc["manual_flags"] else "-",
            "Check State": svc["evidence_source"],
            "Confidence": f'{svc["confidence"]:.0%}',
        })
    return rows


def generate_summary_metrics(services_data: list[dict], base_time: datetime) -> dict:
    red_count = sum(1 for s in services_data if s["status"] == "red")
    orange_count = sum(1 for s in services_data if s["status"] == "orange")
    grey_count = sum(1 for s in services_data if s["status"] == "grey")

    if red_count > 0:
        overall = "red"
    elif orange_count > 0:
        overall = "orange"
    elif grey_count > 1:
        overall = "orange"
    else:
        overall = "green"

    known_incidents = sum(1 for s in services_data if s["status"] in ("red", "orange"))
    warning_signals = orange_count + grey_count
    total_tickets = sum(s["tickets"] for s in services_data)
    total_calls = sum(s["calls"] for s in services_data)
    normal_calls = len(services_data) * 2
    call_spike = round((total_calls - normal_calls) / max(normal_calls, 1) * 100)

    return {
        "overall_status": overall,
        "overall_label": STATUS_LABELS[overall],
        "overall_color": STATUS_COLORS[overall],
        "known_incidents": known_incidents,
        "warning_signals": warning_signals,
        "tickets_last_hour": total_tickets,
        "call_spike_pct": call_spike,
        "last_updated": base_time.strftime("%Y-%m-%d %H:%M"),
    }


def generate_known_issues(services_data: list[dict], base_time: datetime) -> list[dict]:
    issues = []
    idx = 0
    for svc in services_data:
        if svc["status"] in ("red", "orange", "grey", "blue"):
            started = (base_time - timedelta(minutes=30 + idx * 15)).strftime("%H:%M")
            issues.append({
                "incident_id": generate_incident_id(idx),
                "title": f"{svc['service']} — {svc['status_label']}",
                "status": svc["status_label"],
                "status_color": svc["status_color"],
                "started": started,
                "affected_service": svc["service"],
                "owner": "Platform Engineering" if svc["status"] == "red" else "Service Ops",
                "support_instruction": svc["support_instruction"],
            })
            idx += 1
    return issues
