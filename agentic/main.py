from __future__ import annotations

import uuid

from bedrock_agentcore import BedrockAgentCoreApp

from agentic.schemas import AgentRequest
from agentic.local_orchestrator import run_local_agentic_analysis
from agentic.agents.supervisor import supervisor_investigation
from agentic.observability import (
    configure_observability,
    current_trace_context,
    set_current_span_attributes,
)

configure_observability()
app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload):
    """Amazon Bedrock AgentCore Runtime entrypoint.

    Flow:
      1. Strands Supervisor delegates to Quality, Optimization and Knowledge agents.
      2. Deterministic verifier recomputes ML/optimization/RAG outputs.
      3. Non-overridable Safety Gate decides whether a recommendation can be shown.
      4. OTEL trace/span identifiers are returned for audit correlation.
    """
    request = AgentRequest.model_validate(payload)
    agent_run_id = str(uuid.uuid4())

    set_current_span_attributes(
        **{
            "moldguard.run_id": agent_run_id,
            "moldguard.machine_id": request.batch.machine_id,
            "moldguard.material_code": request.batch.material_code,
            "moldguard.phase": "agentic-v4",
        }
    )

    # True multi-agent investigation: supervisor delegates to specialist agents.
    agent_summary = ""
    try:
        agent_summary = supervisor_investigation(
            {
                "objective": request.objective,
                "batch": request.batch.model_dump(),
            }
        )
    except Exception as exc:
        agent_summary = (
            "Strands supervisor was unavailable; deterministic verification continued. "
            f"Reason: {type(exc).__name__}."
        )

    # Authoritative verifier/safety layer. This intentionally rechecks all numbers.
    response = run_local_agentic_analysis(request)
    response["run_id"] = agent_run_id
    response["mode"] = "agentcore-strands-verified"
    response["supervisor_summary"] = agent_summary or response["supervisor_summary"]
    response["agent_investigation_completed"] = bool(agent_summary)

    trace_ctx = current_trace_context()
    response["agent_trace_id"] = trace_ctx["trace_id"]
    response["agent_span_id"] = trace_ctx["span_id"]

    # Make the sequence visible in the UI/audit history.
    response["timeline"].insert(
        0,
        {
            "step": 0,
            "actor": "Strands Supervisor Agent",
            "status": "DONE" if agent_summary else "REVIEW",
            "title": "Specialist investigation completed",
            "detail": (
                "Supervisor delegated to Quality, Optimization and Knowledge agents; "
                "deterministic verification followed."
            ),
        },
    )
    return response


if __name__ == "__main__":
    app.run()
