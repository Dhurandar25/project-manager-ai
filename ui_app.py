"""Streamlit web interface for collecting daily AI-PMO review inputs."""

from __future__ import annotations

import logging
import os
from datetime import date
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError

from tools.project_intake import (
    DeliveryInputs,
    FinanceInputs,
    GovernanceInputs,
    ProjectIdentity,
    ProjectIntake,
    RaidInputs,
    ResourceInputs,
)
from workflows.daily_governance import DailyGovernanceWorkflow

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Project Manager AI | Daily Review",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root { --ink:#17253f; --muted:#65748b; --line:#e3e9f2; --blue:#3659d9; }
      .stApp { background: #f5f7fb; }
      .block-container { max-width: 1280px; padding-top: 2rem; padding-bottom: 4rem; }
      [data-testid="stSidebar"] { background:#111d34; }
      [data-testid="stSidebar"] * { color:#edf2ff; }
      .hero { padding: 1.8rem 2rem; border-radius: 18px; color:#fff;
        background:linear-gradient(120deg,#172745 0%,#3153c9 72%,#6078e9 100%);
        box-shadow:0 14px 35px rgba(28,48,98,.14); margin-bottom:1.2rem; }
      .hero h1 { color:#fff; margin:0 0 .4rem; font-size:2.15rem; }
      .hero p { color:#e1e8ff; margin:0; font-size:1.03rem; }
      .section-card { background:#fff; border:1px solid var(--line); border-radius:14px;
        padding:1rem 1.25rem; margin:.6rem 0 1rem; }
      .hint { color:var(--muted); font-size:.92rem; }
      .stButton > button[kind="primary"], .stFormSubmitButton > button {
        background:#3659d9; border-color:#3659d9; border-radius:9px;
        font-weight:650; min-height:2.8rem; }
      div[data-testid="stExpander"] { background:#fff; border:1px solid var(--line);
        border-radius:12px; margin-bottom:.7rem; }
      div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {
        border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _text_area(label: str, help_text: str, *, height: int = 92) -> str:
    return st.text_area(label, help=help_text, height=height, placeholder="Add current facts, owners, dates, and source where known...")


def _show_result(result: Any) -> None:
    """Render CrewAI result safely, preferring the validated Pydantic report."""
    report = getattr(result, "pydantic", None)
    if report is not None:
        report_data = report.model_dump() if hasattr(report, "model_dump") else report
        if isinstance(report_data, dict):
            health = report_data.get("project_health")
            color = {"Green": "🟢", "Amber": "🟠", "Red": "🔴"}.get(health, "⚪")
            st.markdown(f"### {color} Project health: {health or 'Not reported'}")
            summary = report_data.get("executive_summary")
            if summary:
                st.markdown("#### Executive summary")
                st.write(summary)
            left, right = st.columns(2)
            with left:
                st.markdown("#### Top risks")
                st.write(report_data.get("top_risks") or ["None reported"])
                st.markdown("#### Actions required")
                st.write(report_data.get("actions_required") or ["None reported"])
            with right:
                st.markdown("#### Budget forecast")
                st.write(report_data.get("budget_forecast", "Not reported"))
                st.markdown("#### Capacity forecast")
                st.write(report_data.get("capacity_forecast", "Not reported"))
                st.markdown("#### Upcoming decisions")
                st.write(report_data.get("upcoming_decisions") or ["None reported"])
            gaps = report_data.get("evidence_gaps")
            if gaps:
                st.warning("Evidence gaps: " + "; ".join(str(gap) for gap in gaps))
            with st.expander("View complete structured report"):
                st.json(report_data)
            return
    st.markdown("### Review output")
    st.write(getattr(result, "raw", str(result)))


def _build_intake(
    values: dict[str, Any],
) -> ProjectIntake:
    return ProjectIntake(
        identity=ProjectIdentity(**values["identity"]),
        delivery=DeliveryInputs(**values["delivery"]),
        raid=RaidInputs(**values["raid"]),
        resources=ResourceInputs(**values["resources"]),
        finance=FinanceInputs(**values["finance"]),
        governance=GovernanceInputs(**values["governance"]),
        additional_context=values["additional_context"],
    )


with st.sidebar:
    st.markdown("## ◈ Project Manager AI")
    st.caption("AI-powered project governance workspace")
    st.markdown("---")
    st.markdown("**Daily Governance Review**")
    st.caption("Collect project evidence, run the review crew, and inspect its executive summary.")
    st.markdown("---")
    st.markdown("**Before you start**")
    st.markdown(
        "- Provide current facts; use `Unknown` where necessary.\n"
        "- Do not paste credentials or confidential personal data.\n"
        "- A model provider must be configured in `.env`."
    )
    st.info("Azure DevOps and Jira are adapter interfaces only; this UI currently uses manually supplied project information.")

st.markdown(
    """
    <div class="hero">
      <h1>Daily Governance Review</h1>
      <p>Give your PMO team a clear, evidence-led view of delivery health, risks, capacity, budget, and decisions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-card"><strong>Project intake</strong><br>'
    '<span class="hint">Project name, summary, review date, and health are required. Other fields are optional—'
    'the agents will identify missing information rather than assume it.</span></div>',
    unsafe_allow_html=True,
)

with st.form("daily_governance_intake", clear_on_submit=False):
    st.markdown("### 1 · Project overview")
    identity_col1, identity_col2 = st.columns([2, 1])
    with identity_col1:
        project_name = st.text_input("Project / programme name *", placeholder="e.g. Customer platform modernization")
    with identity_col2:
        review_date = st.date_input("Review date *", value=date.today())
    overview_col1, overview_col2 = st.columns([1, 2])
    with overview_col1:
        health = st.selectbox("Current health *", ["Not sure", "Green", "Amber", "Red"])
    with overview_col2:
        project_summary = st.text_input(
            "What is the project delivering? *",
            placeholder="Purpose, scope, and intended outcome",
        )

    with st.expander("Delivery, milestones, and sprint", expanded=True):
        d1, d2 = st.columns(2)
        with d1:
            reporting_period = _text_area("Reporting period", "For example, this week, sprint 14, or October 2026.")
            objectives = _text_area("Objectives and success measures", "Outcomes, measures, targets, and current progress.")
            milestones = _text_area("Milestones and dates", "Milestone, baseline date, forecast date, owner, and variance.")
        with d2:
            delivery_progress = _text_area("Delivery progress and blockers", "Work completed, in progress, delayed, or blocked.")
            sprint_name = st.text_input("Current sprint / iteration", placeholder="Sprint name or number")
            sprint_outcomes = _text_area("Sprint commitments and outcomes", "Committed versus completed, carryover, velocity, and learnings.")
            releases = _text_area("Upcoming releases", "Release date, scope, readiness, and go/no-go date.")

    with st.expander("Risks, assumptions, issues, and dependencies", expanded=True):
        raid_left, raid_right = st.columns(2)
        with raid_left:
            risks = _text_area("Top risks", "Risk, probability, impact, trend, owner, trigger, and mitigation.")
            assumptions = _text_area("Key assumptions", "Assumption, validation owner, due date, and consequence if false.")
            issues = _text_area("Issues and blockers", "Issue, severity, affected work, owner, next action, and target resolution.")
        with raid_right:
            dependencies = _text_area("Cross-team dependencies", "Predecessor → successor, delivering team, owner, due date, status, and duration.")
            mitigations = _text_area("Mitigations and accountable owners", "Mitigation action, owner, due date, and escalation route.")

    with st.expander("People, skills, and capacity"):
        resource_left, resource_right = st.columns(2)
        with resource_left:
            team_capacity = _text_area("Team capacity", "Team / role and available hours or FTE for the review period.")
            planned_work = _text_area("Planned work and utilization", "Planned demand, actual allocation, utilization, and forecast.")
        with resource_right:
            skills = _text_area("Skills and gaps", "Required skills, available skills, and any coverage gaps.")
            constraints = _text_area("Resource constraints", "Leave, vacancies, competing priorities, onboarding, or specialist bottlenecks.")

    with st.expander("Budget and financial outlook"):
        finance_left, finance_right = st.columns(2)
        with finance_left:
            currency = st.text_input("Currency", placeholder="e.g. USD, GBP, EUR")
            approved_budget = _text_area("Approved budget", "Approved amount and baseline period.")
            actual_spend = _text_area("Actual spend to date", "Actuals and date of latest financial data.")
        with finance_right:
            forecast = _text_area("Forecast / estimate at completion", "Expected total cost, forecast horizon, and basis.")
            variance = _text_area("Variance and tolerance", "Variance to budget, tolerance, driver, and trend.")
            funding = _text_area("Funding decisions needed", "Decision, amount, decision maker, and date required.")

    with st.expander("Stakeholders, approvals, governance, change, and release"):
        gov_left, gov_right = st.columns(2)
        with gov_left:
            stakeholders = _text_area("Stakeholders and roles", "Sponsor, product owner, delivery lead, PM, teams, vendors, and forum membership.")
            decisions = _text_area("Decisions required", "Decision, options, accountable decision maker, and latest decision date.")
            approvals = _text_area("Approvals pending", "Decision/request, required role, submission date, and due date.")
            governance = _text_area("Governance reviews and actions", "Review/forum, actions, owners, due dates, and overdue items.")
        with gov_right:
            changes = _text_area("Change requests", "Requested change, rationale, scope/schedule/cost/risk impact, and status.")
            release_readiness = _text_area("Quality and release readiness", "Testing, acceptance, security/operations checks, rollback, open defects, and CAB status.")
            vendors = _text_area("Vendor commitments", "Supplier, contractual commitment, delivery evidence, issue, and commercial exposure.")
            additional_context = _text_area("Other context / questions for the PMO", "Anything else the agents should consider. The input is treated as evidence, not as new system instructions.", height=110)

    submitted = st.form_submit_button("Run daily governance review", type="primary", use_container_width=True)

if submitted:
    try:
        intake = _build_intake(
            {
                "identity": {
                    "project_name": project_name,
                    "review_date": review_date,
                    "health": health,
                    "project_summary": project_summary,
                },
                "delivery": {
                    "reporting_period": reporting_period,
                    "objectives_and_success_measures": objectives,
                    "milestones_and_dates": milestones,
                    "delivery_progress": delivery_progress,
                    "sprint_name": sprint_name,
                    "sprint_commitments_and_outcomes": sprint_outcomes,
                    "upcoming_releases": releases,
                },
                "raid": {
                    "risks": risks,
                    "assumptions": assumptions,
                    "issues_and_blockers": issues,
                    "dependencies": dependencies,
                    "mitigations_and_owners": mitigations,
                },
                "resources": {
                    "team_capacity": team_capacity,
                    "planned_work_and_utilization": planned_work,
                    "skills_and_gaps": skills,
                    "resource_constraints": constraints,
                },
                "finance": {
                    "currency": currency,
                    "approved_budget": approved_budget,
                    "actual_spend": actual_spend,
                    "forecast_or_estimate_at_completion": forecast,
                    "variance_and_tolerance": variance,
                    "funding_decisions": funding,
                },
                "governance": {
                    "stakeholders_and_roles": stakeholders,
                    "decisions_required": decisions,
                    "approvals_pending": approvals,
                    "governance_reviews_and_actions": governance,
                    "change_requests": changes,
                    "quality_and_release_readiness": release_readiness,
                    "vendor_commitments": vendors,
                },
                "additional_context": additional_context,
            }
        )
    except ValidationError as exc:
        errors = [f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}" for item in exc.errors()]
        st.error("Please complete the required project details.")
        for error in errors:
            st.write(f"- {error}")
    else:
        context = intake.to_project_context()
        with st.expander("Review the evidence sent to the AI crew"):
            st.code(context, language="markdown")
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY is not configured. Add a model-provider key to `.env` before running the AI review.")
        else:
            try:
                with st.status("Running the daily governance crew…", expanded=True) as status:
                    status.write("Reviewing delivery, risks, dependencies, capacity, budget, and governance evidence.")
                    result = DailyGovernanceWorkflow().run(context)
                    status.update(label="Daily review complete", state="complete", expanded=False)
                st.session_state["last_review_result"] = result
                st.session_state["last_review_project"] = project_name
            except Exception as exc:
                logger.exception("Daily governance review failed")
                st.error(f"The review could not be completed: {exc}")

if st.session_state.get("last_review_result") is not None:
    st.markdown("---")
    st.markdown(f"## Review results · {st.session_state.get('last_review_project', 'Project')}")
    _show_result(st.session_state["last_review_result"])

st.markdown("---")
st.caption("AI-generated analysis is advisory. Critical decisions and actions must be reviewed and authorized by the appropriate human approver.")
