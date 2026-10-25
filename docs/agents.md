# Configured agent reference

Role, goal, and backstory text are maintained in [`config/agents.yaml`](../config/agents.yaml)
and loaded through `AgentFactory`. Use the corresponding factory example below
to instantiate each configured CrewAI agent:

| Agent | Goal | Factory example |
|---|---|---|
| Project Manager | Coordinate delivery, decisions, and evidence-based project status. | `AgentFactory().create("project_manager")` |
| Delivery Agent | Assess delivery progress, sprint outcomes, milestones, and release readiness. | `AgentFactory().create("delivery")` |
| Risk Agent | Identify, score, prioritize, and mitigate project risks. | `AgentFactory().create("risk")` |
| Resource Agent | Evaluate capacity, utilization, forecasts, and skill gaps. | `AgentFactory().create("resource")` |
| Dependency Agent | Trace cross-team dependencies, blockers, critical paths, and impact. | `AgentFactory().create("dependency")` |
| Financial Agent | Review spend, budget variance, estimate-at-completion, and funding decisions. | `AgentFactory().create("financial")` |
| Governance Agent | Check project evidence against controls and governance rules. | `AgentFactory().create("governance")` |
| Approval Agent | Route recommendations to an authorized human; never self-approve. | `AgentFactory().create("approval")` |
| Reporting Agent | Produce concise, traceable status and executive reporting. | `AgentFactory().create("reporting")` |
| Audit Agent | Ensure decisions, evidence, approver identity, and outcomes are traceable. | `AgentFactory().create("audit")` |
| Vendor Agent | Assess supplier commitments, delivery, performance, and commercial exposure. | `AgentFactory().create("vendor")` |
| Change Control Agent | Assess scope, schedule, cost, risk, and approval impact of changes. | `AgentFactory().create("change_control")` |
| Executive Briefing Agent | Prepare decision-oriented sponsor and steering committee briefings. | `AgentFactory().create("executive_briefing")` |

Import once and create any named agent:

```python
from agents.factory import AgentFactory

agents = AgentFactory()
delivery_agent = agents.create("delivery")
```
