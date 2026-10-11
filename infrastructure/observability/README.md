# MoldGuard AgentCore + CloudWatch Observability

MoldGuard now emits trace-compatible Strands/OpenTelemetry telemetry and returns the active trace/span ID when AgentCore tracing is enabled.

## Dependencies already included

`agentic/requirements.txt` contains:

```text
strands-agents[otel]>=1.0
aws-opentelemetry-distro>=0.18.0
opentelemetry-api>=1.28
```

## AgentCore Runtime

AgentCore Runtime provides built-in operational metrics. For detailed agent/tool spans in CloudWatch GenAI Observability:

1. Open **CloudWatch → Settings / Transaction Search** and enable Transaction Search for the account/region.
2. Ensure AgentCore Runtime observability / log delivery is enabled for the deployed runtime.
3. Redeploy the agent after adding the OTEL dependencies.
4. Invoke a new session through `/api/agent/run`.
5. Open **CloudWatch → GenAI Observability** and select the MoldGuard runtime service.

The response contains:

```text
agent_session_id
agent_trace_id
agent_span_id
```

Use those identifiers to correlate the UI/DynamoDB audit record with CloudWatch traces.

## Local OTEL debugging

To print spans locally:

```bash
MOLDGUARD_OTEL_CONSOLE=true python agentic/main.py
```

If you have an OTLP endpoint:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://YOUR-ENDPOINT
python agentic/main.py
```

`agentic/observability.py` configures the Strands exporter when an OTLP endpoint is supplied and reads the active OpenTelemetry trace/span context.

## What CloudWatch should show in the demo

- Supervisor Agent execution
- specialist/tool calls
- runtime/session count
- latency and duration
- errors
- token/model activity when emitted by the framework/runtime
- custom MoldGuard run attributes

The deterministic Safety Gate remains outside the LLM's authority even though its execution is part of the same traced request.
