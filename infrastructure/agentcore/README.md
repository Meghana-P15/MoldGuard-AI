# Deploy MoldGuard Phase 4 to Amazon Bedrock AgentCore Runtime

The deployable entrypoint is:

```text
agentic/main.py
```

It uses:
- `BedrockAgentCoreApp`
- Strands Agents
- Supervisor + specialist agents-as-tools
- deterministic MoldGuard ML/optimization/safety tools

## 1. Prerequisites

Install the current AgentCore CLI:

```bash
npm install -g @aws/agentcore
```

Configure AWS credentials and verify them:

```bash
aws sts get-caller-identity
```

Install Python runtime dependencies locally for development:

```bash
pip install -r agentic/requirements.txt
```

## 2. Choose a Bedrock model

Set an inference profile/model available in your selected AWS Region:

```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=global.anthropic.claude-sonnet-4-5-20250929-v1:0
```

PowerShell:

```powershell
$env:AWS_REGION="us-east-1"
$env:BEDROCK_MODEL_ID="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

Do not assume the sample model ID is available in every region. Check the
Bedrock console and replace it if necessary.

## 3. Configure the runtime

From repository root:

```bash
agentcore configure -e agentic/main.py
```

Use `--disable-memory` if prompted and you do not need AgentCore Memory for the
hackathon MVP.

## 4. Develop/test locally

```bash
agentcore dev
```

Or directly:

```bash
python agentic/main.py
```

## 5. Deploy

```bash
agentcore deploy --dry-run
agentcore deploy
agentcore status
```

Copy the runtime ARN shown by `agentcore status`.

## 6. Configure FastAPI

On App Runner set:

```text
AGENT_MODE=agentcore
AGENTCORE_RUNTIME_ARN=<runtime ARN>
AGENTCORE_QUALIFIER=DEFAULT
AWS_REGION=<same/appropriate region>
```

The App Runner IAM role needs:

```text
bedrock-agentcore:InvokeAgentRuntime
```

## 7. Verify

Use the AgentCore CLI:

```bash
agentcore invoke --prompt "Analyze a MoldGuard batch"
```

For the actual MoldGuard payload, test through FastAPI:

```text
POST /api/agent/run
```

## 8. Observability

Enable AgentCore/CloudWatch observability in AWS and show the resulting agent
trace in the hackathon demo:
- supervisor
- specialist calls
- latency
- errors
- tool activity

## Architecture note

The Strands supervisor provides orchestration and narrative synthesis. Numeric
predictions, optimizer output, OOD status and the Safety Gate remain
deterministic and cannot be overridden by the LLM.


## CloudWatch / AgentCore observability

MoldGuard includes Strands OTEL support and ADOT dependencies. After deployment, enable CloudWatch Transaction Search and AgentCore observability/log delivery, then invoke a new agent session. The `/api/agent/run` result will include `agent_session_id`, `agent_trace_id` and `agent_span_id` when tracing is active. See `infrastructure/observability/README.md`.
