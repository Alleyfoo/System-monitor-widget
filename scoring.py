"""Status scoring and filtering logic for Support Desk Incident Radar."""


def filter_services_by_status(services: list[dict], status_filter: str) -> list[dict]:
    if status_filter == "All":
        return services
    return [s for s in services if s["status"] == status_filter.lower()]


def get_status_sort_order(status: str) -> int:
    return {"red": 0, "orange": 1, "grey": 2, "blue": 3, "green": 4}.get(status, 5)


def sort_services_by_severity(services: list[dict]) -> list[dict]:
    return sorted(services, key=lambda s: get_status_sort_order(s["status"]))


def get_view_mode_fields(view_mode: str) -> dict:
    if view_mode == "Technical":
        return {
            "show_host_status": True,
            "show_module_status": True,
            "show_evidence_source": True,
            "show_confidence": True,
            "show_timeline": True,
            "label_style": "technical",
        }
    elif view_mode == "Manager":
        return {
            "show_host_status": False,
            "show_module_status": False,
            "show_evidence_source": False,
            "show_confidence": True,
            "show_timeline": True,
            "label_style": "manager",
        }
    else:
        return {
            "show_host_status": False,
            "show_module_status": False,
            "show_evidence_source": False,
            "show_confidence": False,
            "show_timeline": False,
            "label_style": "support",
        }
