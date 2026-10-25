# Project Manager AI

An extensible AI-powered Project Management Office (AI-PMO) starter repository.
CrewAI agents create evidence-based delivery and governance reviews; deterministic
services handle approval routing, risk scoring, and append-only decision records.
Human approval is a control boundary, not an AI-generated claim.

> **Operational note:** This repository provides a runnable CrewAI application
> scaffold and integration contracts. It is not a certified project-control,
> financial, safety, or compliance system. Connectors, identity verification,
> policy enforcement, and production deployment controls must be supplied and
> validated for the organization before production use.

## Architecture

```text
main.py
  -> command-line daily review entry
ui_app.py
  -> Streamlit project intake form
      -> ProjectIntake validation and evidence summary
      -> DailyGovernanceWorkflow
  -> DailyGovernanceWorkflow
      -> DailyGovernanceCrew (CrewAI kickoff)
          -> configured Project Manager agent
          -> configured Reporting agent
  -> tools/governance
      -> ApprovalEngine (approval_matrix.yaml)
      -> ApprovalMiddleware (human decision -> audit -> optional execution)
      -> AuditLogger (logs/audit/decisions.jsonl)
  -> tools/integrations (injected Azure DevOps, Jira, Teams, Outlook clients)
```

Agent and task prompts, approval routes, and governance thresholds live in
`config/`. Reusable analysis functions are deterministic Python services, and
executive reporting uses a validated Pydantic output model. The
project management, risk, resource, and dependency agents receive CrewAI tools
for risk scoring, capacity forecasting, skill-gap comparison, and critical-path
dependency analysis. The
external systems are injected; this repository contains no credentials and does
not make unauthenticated network calls.

## Repository map

```text
config/       Dynamic YAML for agents, tasks, approval routes, and rules
agents/       CrewAI agent factory; all 13 role definitions are in agents.yaml
tasks/        CrewAI task factory; all review task definitions are in tasks.yaml
tools/        Configuration, risk, dependency/resource intelligence, integrations
workflows/    Daily governance workflow entry
crews/        CrewAI crew composition and kickoff()
ui_app.py     Streamlit intake form for daily project governance reviews
logs/audit/   Append-only JSONL decision records at runtime
tests/        Focused pytest coverage for core governance services
docs/         Mermaid architecture and workflow diagrams
```

## Installation

Requires Python 3.11 or newer.

```powershell
cd project-manager-ai
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `OPENAI_API_KEY` and, if needed, `CREWAI_LLM` in `.env`. Never commit the
populated `.env` file. The model provider is configurable through CrewAI's model
string; verify the provider and model availability in your deployment.

## Configuration

* `config/agents.yaml`: role, goal, and backstory for all 13 agents.
* `config/tasks.yaml`: daily, RAID, sprint, dependency, capacity, budget,
  executive report, change, risk, release readiness, and human approval tasks.
* `config/approval_matrix.yaml`: mapping from decision classes to approver roles.
* `config/governance_rules.yaml`: risk scales, categories, and health conditions.

Configuration is loaded at application construction time. Invalid or missing
YAML is reported as an exception rather than silently replaced with defaults.
Customize project data by setting `PROJECT_CONTEXT` or calling the workflow with
an explicit data-backed context.

## Usage

Run the browser-based intake page from the repository root:

```powershell
streamlit run ui_app.py
```

The page collects project overview, delivery/sprint, RAID, capacity, finance,
stakeholder, governance, change, release, and vendor context. Only project name,
review date, health, and a short project summary are required; other fields can
be left empty. The crew will be told to identify missing data rather than invent
it. Review the evidence preview before submitting. A model provider must be
configured in `.env` locally or in the deployed app's Streamlit **Settings →
Secrets** as TOML, for example:

```toml
OPENAI_API_KEY = "your-provider-key"
CREWAI_LLM = "openai/gpt-4o-mini"
```

Secrets are read from Streamlit's managed secret store in the hosted app and
are not stored in the GitHub repository.

Run a daily governance review from the command line:

```powershell
python main.py
```

This composes the CrewAI crew and calls `Crew.kickoff()` through
`DailyGovernanceWorkflow`. Supply project facts in `PROJECT_CONTEXT`; otherwise
the review asks the agents to identify unavailable evidence. CrewAI `kickoff()`
requires a valid model-provider setup.

Example programmatic role usage:

```python
from agents.factory import AgentFactory

factory = AgentFactory()
dependency_agent = factory.create("dependency")
resource_agent = factory.create("resource")
```

There are 13 configured roles: Project Manager, Delivery, Risk, Resource,
Dependency, Financial, Governance, Approval, Reporting, Audit, Vendor, Change
Control, and Executive Briefing. Each has a YAML role, goal, and backstory and
can be instantiated through `AgentFactory.create(name)`.
See [docs/agents.md](docs/agents.md) for the complete goal and an example
factory invocation for every role.

Run the tests:

```powershell
python -m pytest
```

## Governance model

`ApprovalEngine` routes known decision types first (for example, release to CAB
and budget overrun to Sponsor), then routes high/critical risk to the configured
`high_risk` approver. Unknown low-risk requests use `low_risk`. Missing routes
raise an error, so critical/high risk cannot be approved through an implicit
fallback.

`ApprovalMiddleware` requests an explicit human outcome (`approved`, `rejected`,
or `deferred`), requires approver identity, writes the decision audit record, and
only then invokes an optional execution callback for an approved decision.
Rejected and deferred recommendations are not executed. The supplied callback
is an application boundary; secure identity checks and authorization must be
implemented by the host system.

CrewAI tasks support `human_input: true`; the configured `approval_gate` task
provides a conversational review gate. Use `ApprovalMiddleware` when an action
needs enforced role routing, durable audit, and execution ordering. Never rely
solely on free-form agent output as authorization.

## Integrations

* **Azure DevOps:** `AzureDevOpsService` defines work item, board, feature, epic,
  sprint, delivery metric, release, and pipeline methods over an injected client.
* **Jira:** `JiraService` queries stories, epics, sprint metrics, and releases
  using an injected Jira client.
* **Teams / Outlook:** notification services dispatch risk, daily summary,
  approval request, executive summary, and escalation messages over an injected
  transport.

These are interface/adaptation layers rather than preconfigured live
connectors. Supply authentication, retry policy, rate limiting, data mapping,
and observability in the integrating application. Keep secrets in a vault or
environment injection mechanism.

## Audit and decision traceability

`AuditLogger` appends JSON Lines records to `logs/audit/decisions.jsonl` with
UTC timestamp, decision, approver, outcome, workflow, agent source, and optional
metadata. Protect the audit directory with appropriate access controls, backups,
retention, and tamper-evidence controls in a deployed environment. Local file
append is not a substitute for an enterprise audit store.

## Roadmap

1. Implement authenticated Azure DevOps and Jira adapters with pagination and
   contract tests.
2. Add organizational identity resolution and RBAC for approval callbacks.
3. Add persistent audit storage, retention policy, and integrity verification.
4. Add structured project data models and source provenance for each metric.
5. Add integration, evaluation, and red-team testing against representative
   governance scenarios.
6. Add deployment packaging, monitoring, model governance, and incident runbooks.

## Diagrams

See [docs/diagrams.md](docs/diagrams.md) for the five requested Mermaid diagrams:
solution architecture, approval workflow, agent orchestration, governance
workflow, and AI-PMO architecture.
