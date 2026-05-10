"""Scenario definitions for Support Desk Incident Radar.

Each scenario defines the status of every service, producing a distinct
support-desk situation. All data is synthetic.
"""

from datetime import datetime, timezone

from mock_data import SERVICES, generate_service_data, generate_timeline_events

SCENARIOS = {
    "Normal day": {
        "description": "All services healthy. Minor background noise only.",
        "services": {
            "Login / Authentication": "green",
            "Search": "green",
            "Document generation": "green",
            "Printing": "green",
            "Messaging": "green",
            "Integrations": "green",
            "Data updates": "green",
            "Reporting": "green",
            "File shares": "green",
            "Ticketing system": "green",
        },
    },
    "Printing / document generation incident": {
        "description": "Document generation queue is backed up. Printing is down. Other services normal.",
        "services": {
            "Login / Authentication": "green",
            "Search": "green",
            "Document generation": "orange",
            "Printing": "red",
            "Messaging": "green",
            "Integrations": "green",
            "Data updates": "green",
            "Reporting": "green",
            "File shares": "green",
            "Ticketing system": "green",
        },
    },
    "Login degradation": {
        "description": "Authentication service experiencing intermittent timeouts. Cascading minor impact on dependent services.",
        "services": {
            "Login / Authentication": "orange",
            "Search": "green",
            "Document generation": "green",
            "Printing": "green",
            "Messaging": "orange",
            "Integrations": "green",
            "Data updates": "green",
            "Reporting": "green",
            "File shares": "orange",
            "Ticketing system": "green",
        },
    },
    "Integration / data delay": {
        "description": "Third-party integration API is slow. Data update pipelines are delayed. Reporting affected.",
        "services": {
            "Login / Authentication": "green",
            "Search": "green",
            "Document generation": "green",
            "Printing": "green",
            "Messaging": "green",
            "Integrations": "red",
            "Data updates": "orange",
            "Reporting": "orange",
            "File shares": "green",
            "Ticketing system": "green",
        },
    },
    "Unknown monitoring status": {
        "description": "Monitoring agents unresponsive on several nodes. Multiple services show unknown status.",
        "services": {
            "Login / Authentication": "green",
            "Search": "green",
            "Document generation": "green",
            "Printing": "green",
            "Messaging": "green",
            "Integrations": "grey",
            "Data updates": "grey",
            "Reporting": "grey",
            "File shares": "grey",
            "Ticketing system": "green",
        },
    },
}


def load_scenario(name: str, base_time: datetime | None = None) -> dict:
    if name not in SCENARIOS:
        name = "Normal day"

    scenario = SCENARIOS[name]
    if base_time is None:
        base_time = datetime.now(timezone.utc)

    services_data = []
    for service in SERVICES:
        status = scenario["services"].get(service, "green")
        svc = generate_service_data(service, status, base_time)
        svc["timeline"] = generate_timeline_events(service, status, base_time)
        services_data.append(svc)

    return {
        "name": name,
        "description": scenario["description"],
        "services": services_data,
        "base_time": base_time,
    }
