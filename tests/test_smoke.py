"""Smoke tests for generated service data integrity."""

from datetime import datetime, timezone

from mock_data import (
    SERVICES,
    generate_incident_id_for_service,
    generate_service_data,
)
from scenarios import SCENARIOS, load_scenario


def test_every_service_has_required_fields():
    base_time = datetime.now(timezone.utc)
    for service in SERVICES:
        for status in ("green", "orange", "red", "grey", "blue"):
            incident_id = ""
            if status != "green":
                incident_id = generate_incident_id_for_service(service, base_time)
            svc = generate_service_data(service, status, base_time, incident_id)

            assert "technical_evidence" in svc, (
                f"{service}/{status} missing technical_evidence"
            )
            assert "support_evidence" in svc, (
                f"{service}/{status} missing support_evidence"
            )
            assert "affected_workflows" in svc, (
                f"{service}/{status} missing affected_workflows"
            )
            assert "host_module_plain" in svc, (
                f"{service}/{status} missing host_module_plain"
            )
            assert "incident_id" in svc, (
                f"{service}/{status} missing incident_id"
            )

            if status != "green":
                assert svc["incident_id"] != "", (
                    f"{service}/{status} should have non-empty incident_id"
                )
                assert svc["incident_id"].startswith("INC-"), (
                    f"{service}/{status} incident_id should start with INC-"
                )
            else:
                assert svc["incident_id"] == "", (
                    f"{service}/green should have empty incident_id"
                )

            assert isinstance(svc["affected_workflows"], list), (
                f"{service}/{status} affected_workflows should be a list"
            )
            assert len(svc["affected_workflows"]) > 0, (
                f"{service}/{status} affected_workflows should not be empty"
            )


def test_all_scenarios_load_and_have_required_fields():
    base_time = datetime.now(timezone.utc)
    for name in SCENARIOS:
        scenario = load_scenario(name, base_time)
        assert "services" in scenario
        assert len(scenario["services"]) == len(SERVICES)

        for svc in scenario["services"]:
            assert "technical_evidence" in svc
            assert "support_evidence" in svc
            assert "affected_workflows" in svc
            assert "host_module_plain" in svc
            assert "incident_id" in svc
            assert "timeline" in svc

            if svc["status"] != "green":
                assert svc["incident_id"] != ""
                assert svc["incident_id"].startswith("INC-")
