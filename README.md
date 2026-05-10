# Support Desk Incident Radar

A synthetic Streamlit mockup dashboard for demonstrating an early-warning support desk incident radar. It translates technical and operational signals into customer-service guidance — without connecting to any real systems or containing any real data.

## Purpose

This dashboard shows how a support desk can monitor service/module health, detect known issues, and provide clear guidance to agents handling customer calls. It demonstrates that a host/system can be technically **up** while one internal module or workflow is **degraded or down**.

## Architecture Concept

The intended safe architecture separates monitoring from display:

```
Approved monitoring checks / synthetic tests
        ↓
Structured JSON status output
        ↓
Dashboard reads status data (read-only)
        ↓
Support desk sees compact lights and guidance
```

**The dashboard should not directly access** production systems, restricted application internals, patient/customer records, or databases. It is a read-only viewer that consumes pre-computed status data produced by approved monitoring checks or synthetic tests running in a separate, controlled environment.

A JSON status payload could include fields such as:

- `service` — human-readable service name
- `status` — one of `green`, `orange`, `red`, `grey`, `blue`
- `last_checked` — timestamp of the most recent check
- `impact_text` — user-facing summary of current impact
- `support_instruction` — guidance for support desk agents
- `incident_id` — reference ID for active incidents
- `affected_workflows` — list of workflows within the blast radius
- `technical_evidence` — safe technical detail where disclosure is permitted

This separation ensures the dashboard never needs credentials, direct network access, or query access to operational systems. The monitoring layer owns the checks; the dashboard owns the display.

**The current mockup is synthetic-only.** All data is generated in-process for demonstration. In a real deployment, `mock_data.py` would be replaced by a module that reads the JSON output of your monitoring layer.

## Features

- **10 service/module cards**: Login/Authentication, Search, Document Generation, Printing, Messaging, Integrations, Data Updates, Reporting, File Shares, Ticketing System
- **5 pre-built scenarios**: Normal day, Printing/document generation incident, Login degradation, Integration/data delay, Unknown monitoring status
- **3 view modes**: Support desk (simplified, caller-facing), Manager (confidence + timeline), Technical (full details including host/module status and technical evidence)
- **2 display modes**: Compact widget (small service lights for support-desk screens) and Full dashboard (complete view with metrics, notices, cards, and signal table)
- **Status filter**: Filter cards by Red, Orange, Grey, Blue, or Green
- **Top summary metrics**: Overall status, known incidents, visibility issues, planned maintenance, tickets last hour, call spike percentage, last updated
- **Active service notices**: Separates confirmed incidents (red/orange) from visibility issues (grey) and planned maintenance (blue)
- **Detail panel**: User impact, system status, incident ID, affected workflows, caller reports or technical evidence, what to say to caller, what to collect, what not to do, escalation
- **Copy/paste ticket note**: Pre-formatted caller handling note for ticket system entry
- **Timeline**: Incident evolution for each service
- **Signal evidence table**: Calls, emails, tickets, manual flags, technical check state

## Status Rules

| Color  | Meaning            |
|--------|--------------------|
| Green  | Normal / Healthy   |
| Orange | Degraded / Warning |
| Red    | Major Issue        |
| Grey   | Unknown / No Data  |
| Blue   | Planned Maintenance|

## Requirements

- Python 3.10+
- Streamlit >= 1.33.0
- NumPy
- Pandas

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Dashboard

```bash
streamlit run app.py
```

## Project Structure

| File            | Purpose                                      |
|-----------------|----------------------------------------------|
| `app.py`        | Main Streamlit application and page layout   |
| `mock_data.py`  | Synthetic data generation (all mock data)    |
| `scenarios.py`  | 5 pre-built incident scenario definitions    |
| `scoring.py`    | Status filtering, sorting, and view mode logic|
| `components.py` | Reusable UI components (cards, panels, tables)|
| `requirements.txt` | Python dependencies                              |
| `README.md`     | This file                                    |

## Suggested Demo Flow

This sequence tells a realistic support-desk story using the pre-built scenarios:

1. **Start with "Normal day"** — All 10 services green. Show the summary metrics and note the calm state. Explain that this is the baseline the support desk sees on a typical day.

2. **Switch to "Printing / document generation incident"** — Two services change: Printing goes red, Document generation goes orange. Point out:
   - The overall status changes to red.
   - Known Incidents shows 2, Visibility Issues shows 0.
   - The Active Service Notices panel lists both affected services with incident IDs and support instructions.

3. **Click "View details" on Printing** — The detail panel opens. Walk through:
   - **User Impact** and **System Status** (plain-language, not raw host/module labels).
   - **Affected Workflows** showing the blast radius (printed documents, labels, physical output queue, batch print jobs).
   - **Caller Reports** describing what agents are hearing from users.
   - **What to say / What to collect / What NOT to do** — the support guidance.
   - **Copy/Paste Ticket Note** — show how an agent copies this into the ticket system.

4. **Switch view mode to "Technical"** — The same detail panel now shows:
   - Raw **Host Status** and **Module Status** labels.
   - **Technical Evidence** with specific error codes, node names, and metrics.
   - **Incident Timeline** with the progression from green → orange → red.

5. **Switch to "Unknown monitoring status"** — Multiple services go grey. Point out:
   - Visibility Issues metric shows 4 (not counted as Known Incidents).
   - Grey services appear in Active Service Notices but are clearly labeled "Unknown" — not confirmed incidents.
   - The support guidance says "Monitoring data is unavailable" and instructs agents to collect caller details.

6. **Use the Status Filter** — Filter to only "Red" or only "Grey" to show how agents can focus on specific severity levels.

7. **Click "Refresh mock data"** — Show that the data regenerates with new timestamps and counts while keeping the same scenario structure.

## Compact Widget Mode

The compact widget mode is intended for a support-desk screen where agents only need small service lights until something requires attention. It shows:

- A one-line summary header with overall status and counts (red, orange, grey)
- Small clickable service buttons with short names and status dots
- A "Show healthy services" checkbox to collapse green services into a summary line
- Clicking a service light opens a compact detail panel with user impact, system status, what to say, what to collect, and a copy/paste ticket note
- Affected workflows, caller reports, and technical evidence are tucked into expanders

Switch to "Full dashboard" mode to see the complete view with metrics, active service notices, large service cards, and the signal evidence table.

## Important Notes

- **All data is synthetic.** No real systems, no real customer/patient data.
- **No external connections.** Everything runs locally with mock data.
- **Built for demonstration purposes only.** This is a mockup to show how an early-warning support dashboard could work.
- The dashboard intentionally separates **host status** (infrastructure-level) from **module status** (application-level) to demonstrate that a server can be up while a specific service is degraded.
