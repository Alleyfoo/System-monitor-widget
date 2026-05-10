# Support Desk Incident Radar

A synthetic Streamlit mockup dashboard for demonstrating an early-warning support desk incident radar. It translates technical and operational signals into customer-service guidance — without connecting to any real systems or containing any real data.

## Purpose

This dashboard shows how a support desk can monitor service/module health, detect known issues, and provide clear guidance to agents handling customer calls. It demonstrates that a host/system can be technically **up** while one internal module or workflow is **degraded or down**.

## Features

- **10 service/module cards**: Login/Authentication, Search, Document Generation, Printing, Messaging, Integrations, Data Updates, Reporting, File Shares, Ticketing System
- **5 pre-built scenarios**: Normal day, Printing/document generation incident, Login degradation, Integration/data delay, Unknown monitoring status
- **3 view modes**: Support desk (simplified), Manager (confidence + timeline), Technical (full details including host/module status and evidence source)
- **Status filter**: Filter cards by Red, Orange, Grey, Blue, or Green
- **Top summary metrics**: Overall status, known incidents, warning signals, tickets last hour, call spike percentage, last updated
- **Active known issues**: Incident title, status, start time, affected service, owner, incident ID, support instruction
- **Detail panel**: User impact, host status, module status, evidence, what to say to caller, what to collect, what not to do, escalation link
- **Timeline**: Incident evolution for each service
- **Signal evidence table**: Calls, emails, tickets, manual flags, synthetic check state

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
- Streamlit
- NumPy
- Pandas

Install dependencies:

```bash
pip install streamlit numpy pandas
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
| `README.md`     | This file                                    |

## Important Notes

- **All data is synthetic.** No real systems, no real customer/patient data.
- **No external connections.** Everything runs locally with mock data.
- **Built for demonstration purposes only.** This is a mockup to show how an early-warning support dashboard could work.
- The dashboard intentionally separates **host status** (infrastructure-level) from **module status** (application-level) to demonstrate that a server can be up while a specific service is degraded.
