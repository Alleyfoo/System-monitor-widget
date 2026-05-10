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
    "red": "Major incident declared. Engineering team is actively working on it. Refer to incident {incident_id}.",
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
    "orange": [
        "Caller name",
        "Contact number",
        "Exact error message if any",
        "Time issue started",
    ],
    "red": [
        "Caller name",
        "Contact number",
        "Impact description",
        "Whether they want incident updates",
    ],
    "grey": [
        "Caller name",
        "Contact number",
        "Full description of the issue",
        "Screenshots if available",
    ],
    "blue": [
        "Caller name",
        "Contact number",
        "Urgency level if before maintenance end",
    ],
}

WHAT_NOT_TO_DO = {
    "green": ["Don't escalate unnecessarily"],
    "orange": [
        "Don't promise a fix time",
        "Don't suggest workarounds unless confirmed",
    ],
    "red": [
        "Don't promise a fix time",
        "Don't transfer to engineering directly",
        "Don't suggest the caller try again immediately",
    ],
    "grey": ["Don't guess the status", "Don't tell the caller 'everything is fine'"],
    "blue": [
        "Don't tell callers to bypass maintenance",
        "Don't promise early completion",
    ],
}

HOST_MODULE_TRANSLATION = {
    (
        "up",
        "green",
    ): "The main system is reachable and the service is operating normally.",
    (
        "up",
        "orange",
    ): "The main system appears reachable, but this workflow is experiencing slowdowns.",
    ("up", "red"): "The main system appears reachable, but this workflow is failing.",
    (
        "degraded",
        "red",
    ): "The underlying host is degraded and this workflow is failing.",
    (
        "up",
        "grey",
    ): "The main system appears reachable, but we cannot confirm the current state of this service.",
    (
        "up",
        "blue",
    ): "The main system is reachable. This service is undergoing planned maintenance.",
}

SERVICE_EVIDENCE = {
    "Printing": {
        "orange": "Print spooler queue depth at 340 jobs (normal: <50). Multiple users reporting 'stuck in queue' status.",
        "red": "Print spooler service crashed on nodes PRN-01 and PRN-02. 47 failed jobs in last 15 minutes. Error: SPOOL-E-001.",
    },
    "Document generation": {
        "orange": "Template rendering latency at 8.2s (baseline: 1.5s). Queue backlog of 120 pending documents.",
        "red": "Document renderer returning HTTP 503 on 60% of requests. Disk utilization on DOC-GEN-01 at 98%.",
    },
    "Login / Authentication": {
        "orange": "Auth service P95 latency at 4.7s (baseline: 0.8s). Intermittent timeout errors on 12% of login attempts.",
        "red": "Authentication service returning 503 errors. LDAP connection pool exhausted. 85% of login attempts failing.",
    },
    "Integrations": {
        "orange": "Third-party API response time at 12s (SLA: 3s). Retry rate at 22%.",
        "red": "Third-party integration endpoint returning HTTP 500. Circuit breaker open after 50 consecutive failures.",
    },
    "Data updates": {
        "orange": "Data pipeline ETL-04 running 45 minutes behind schedule. 2300 records pending processing.",
        "red": "Data pipeline ETL-04 stalled. Kafka consumer lag at 15000 messages. Last successful commit 2 hours ago.",
    },
    "Reporting": {
        "orange": "Report generation queue depth at 85 (normal: <20). Average generation time 4x baseline.",
        "red": "Report engine database connection pool exhausted. 95% of scheduled reports failed in last hour.",
    },
    "Messaging": {
        "orange": "Message broker queue depth at 8500 (warning threshold: 5000). Delivery latency increasing.",
        "red": "Message broker node MSG-02 offline. 3400 undelivered messages queued. Failover not triggered.",
    },
    "Search": {
        "orange": "Search index rebuild in progress. Query latency at 3.2s (baseline: 0.4s). Index freshness: 45 min behind.",
        "red": "Elasticsearch cluster degraded — 2 of 5 data nodes unresponsive. Search queries returning partial results.",
    },
    "File shares": {
        "orange": "File server FS-03 latency at 800ms (baseline: 50ms). SMB connection retry rate at 15%.",
        "red": "File server FS-03 filesystem mounted read-only after disk error. All write operations failing.",
    },
    "Ticketing system": {
        "orange": "Ticket creation API latency at 5s (baseline: 0.3s). Database connection pool at 90% utilization.",
        "red": "Ticketing system database replication lag at 12 minutes. New tickets not visible to agents.",
    },
}


def _seeded_random(seed: str) -> np.random.Generator:
    digest = int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16)
    return np.random.default_rng(digest)


def generate_incident_id(index: int) -> str:
    return f"INC-{2026:04d}-{index + 1000:04d}"


def generate_incident_id_for_service(service: str, base_time: datetime) -> str:
    rng = _seeded_random(f"incid-{service}-{base_time.isoformat()}")
    num = int(rng.integers(1000, 9999))
    return f"INC-{base_time.year:04d}-{num:04d}"


def generate_service_data(
    service: str, status: str, base_time: datetime, incident_id: str = ""
) -> dict:
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

    host_status = (
        "up" if status != "red" else rng.choice(["up", "degraded"], p=[0.6, 0.4])
    )
    module_status = status if status != "grey" else "unknown"

    impact_text = {
        "green": "No user impact detected",
        "orange": "Some users may experience slowness or intermittent errors",
        "red": "Users unable to complete tasks. High impact.",
        "grey": "Unable to determine current impact",
        "blue": "Service temporarily unavailable during maintenance window",
    }[status]

    last_checked = (base_time - timedelta(minutes=int(rng.integers(1, 15)))).strftime(
        "%H:%M"
    )

    translation_key = (host_status, status if status != "grey" else "grey")
    host_module_plain = HOST_MODULE_TRANSLATION.get(
        translation_key,
        "System status information is unavailable.",
    )

    evidence_source = "no data"
    if status != "grey":
        svc_evidence = SERVICE_EVIDENCE.get(service, {})
        evidence_source = svc_evidence.get(
            status, "synthetic check — all monitors nominal"
        )

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
        "host_module_plain": host_module_plain,
        "evidence_source": evidence_source,
        "incident_id": incident_id,
        "what_to_say": WHAT_TO_SAY[status].format(
            service=service, maintenance_end="14:00"
        ),
        "what_to_collect": WHAT_TO_COLLECT[status],
        "what_not_to_do": WHAT_NOT_TO_DO[status],
        "support_instruction": SUPPORT_GUIDANCE[status].format(
            incident_id=incident_id, maintenance_end="14:00"
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
        ts = base_time - timedelta(
            minutes=(num_events - i) * 15 + int(rng.integers(-5, 5))
        )
        events.append(
            {
                "time": ts.strftime("%H:%M"),
                "status": statuses[i],
                "description": descriptions[statuses[i]],
            }
        )
    return events


def generate_signal_evidence(services_data: list[dict]) -> list[dict]:
    rows = []
    for svc in services_data:
        rows.append(
            {
                "Service": svc["service"],
                "Calls (1h)": svc["calls"],
                "Emails (1h)": svc["emails"],
                "Tickets (1h)": svc["tickets"],
                "Manual Flag": "Yes" if svc["manual_flags"] else "-",
                "Check State": svc["evidence_source"],
                "Confidence": f'{svc["confidence"]:.0%}',
            }
        )
    return rows


def generate_summary_metrics(services_data: list[dict], base_time: datetime) -> dict:
    red_count = sum(1 for s in services_data if s["status"] == "red")
    orange_count = sum(1 for s in services_data if s["status"] == "orange")
    grey_count = sum(1 for s in services_data if s["status"] == "grey")
    blue_count = sum(1 for s in services_data if s["status"] == "blue")

    if red_count > 0:
        overall = "red"
    elif orange_count > 0:
        overall = "orange"
    elif grey_count > 1:
        overall = "orange"
    else:
        overall = "green"

    known_incidents = red_count + orange_count
    visibility_issues = grey_count
    planned_maintenance = blue_count
    total_tickets = sum(s["tickets"] for s in services_data)
    total_calls = sum(s["calls"] for s in services_data)
    normal_calls = len(services_data) * 2
    call_spike = round((total_calls - normal_calls) / max(normal_calls, 1) * 100)

    return {
        "overall_status": overall,
        "overall_label": STATUS_LABELS[overall],
        "overall_color": STATUS_COLORS[overall],
        "known_incidents": known_incidents,
        "visibility_issues": visibility_issues,
        "planned_maintenance": planned_maintenance,
        "tickets_last_hour": total_tickets,
        "call_spike_pct": call_spike,
        "last_updated": base_time.strftime("%Y-%m-%d %H:%M"),
    }


def generate_known_issues(services_data: list[dict], base_time: datetime) -> list[dict]:
    issues = []
    for idx, svc in enumerate(services_data):
        if svc["status"] in ("red", "orange", "grey", "blue"):
            started = (base_time - timedelta(minutes=30 + idx * 15)).strftime("%H:%M")
            issues.append(
                {
                    "incident_id": svc["incident_id"],
                    "title": f"{svc['service']} — {svc['status_label']}",
                    "status": svc["status_label"],
                    "status_color": svc["status_color"],
                    "started": started,
                    "affected_service": svc["service"],
                    "owner": (
                        "Platform Engineering"
                        if svc["status"] == "red"
                        else "Service Ops"
                    ),
                    "support_instruction": svc["support_instruction"],
                }
            )
    return issues
