# MoldGuard AI v4 — Complete Agentic + MLOps Architecture

MoldGuard AI is an injection-molding decision-support system designed to prevent avoidable plastic scrap and energy waste **before production begins**.

The v4 repository now matches the full architecture:

- React + Vite + TypeScript Decision Cockpit
- FastAPI backend
- Amazon Bedrock AgentCore Runtime
- Strands Supervisor + Quality + Optimization + Knowledge agents
- XGBoost quality-risk model + SHAP
- XGBoost energy model
- IsolationForest OOD detector
- vectorized multi-objective optimizer
- RAG/SOP evidence retrieval
- deterministic non-overridable Safety Gate
- S3 model/data storage path
- SageMaker custom training job
- optional Optuna tuning inside the training job
- SageMaker Model Registry registration path
- DynamoDB audit history including agent session/trace IDs
- CloudWatch / OpenTelemetry observability support
- Amplify/App Runner deployment path


## Real dataset package

This build includes the team-provided real dataset files:

```text
ai/data/modelo.xlsx
ai/data/test_dataset.csv
```

The old packaged `demo_injection_molding.csv` has been removed. The model artifacts
must be retrained after validating the real column mappings before reporting
real-world metrics.

## Runtime architecture

```text
Factory operator
   ↓
React Decision Cockpit / Amplify
   ↓ HTTPS
FastAPI / App Runner
   ↓
Amazon Bedrock AgentCore Runtime
   ↓
Strands Supervisor
   ├── Quality Guardian Agent -> risk XGBoost + SHAP + OOD
   ├── Optimization Agent -> energy XGBoost + optimizer + impact
   └── Knowledge Agent -> RAG / SOP evidence
   ↓
Deterministic verifier + Safety Gate
   ↓
DynamoDB audit record + CloudWatch trace
   ↓
Human-reviewed recommendation
```

## Training / registry architecture

```text
Real canonical dataset
   ↓
Amazon S3
   ↓
SageMaker custom training image
   ├── risk model
   ├── energy model
   ├── OOD model
   └── optional Optuna tuning
   ↓
model.tar.gz + metrics in S3
   ↓
custom inference image in ECR
   ↓
SageMaker Model Registry
```

## Local development

```bash
python -m venv .venv
pip install -r requirements.txt
python -m ai.training.generate_demo_data
python -m ai.training.train_all
uvicorn backend.app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Local agent mode requires no Bedrock/AgentCore runtime:

```env
AGENT_MODE=local
```

## Deploy Phase 4 agents

```bash
npm install -g @aws/agentcore
pip install -r agentic/requirements.txt
agentcore configure -e agentic/main.py
agentcore deploy --dry-run
agentcore deploy
agentcore status
```

Then configure App Runner:

```env
AGENT_MODE=agentcore
AGENTCORE_RUNTIME_ARN=<runtime ARN>
AGENTCORE_QUALIFIER=DEFAULT
AWS_REGION=<region>
```

## Deploy the MLOps path

Follow:
- `infrastructure/sagemaker/README.md`
- `infrastructure/sagemaker/MODEL_REGISTRY.md`
- `infrastructure/observability/README.md`

## Scientific integrity

The packaged artifacts may still be demo/smoke-test models until your team replaces them with real-data-trained artifacts. Do not report demo metrics as factory performance.

## Safety

MoldGuard is decision support, not direct machine control. The LLM/agent layer cannot override the deterministic Safety Gate, configured parameter bounds, OOD checks or the human-review requirement.

See `CHANGE_MANIFEST_V4_COMPLETE.md` for everything added to close the architecture gaps.
