from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "ai/moldguard_ai/runtime.py",
    "ai/moldguard_ai/optimizer.py",
    "ai/moldguard_ai/guardrails.py",
    "ai/training/optuna_tuning.py",
    "ai/models/risk_model.joblib",
    "ai/models/energy_model.joblib",
    "ai/models/ood_model.joblib",
    "backend/app/main.py",
    "backend/app/services/agent_service.py",
    "frontend/src/App.tsx",
    "frontend/src/components/AgentTimeline.tsx",
    "agentic/main.py",
    "agentic/observability.py",
    "agentic/agents/supervisor.py",
    "agentic/tools/safety_tools.py",
    "knowledge/demo_process_guidance.md",
    "infrastructure/agentcore/README.md",
    "infrastructure/observability/README.md",
    "infrastructure/sagemaker/training/Dockerfile",
    "infrastructure/sagemaker/inference/Dockerfile",
    "infrastructure/sagemaker/MODEL_REGISTRY.md",
    "scripts/launch_sagemaker_training.py",
    "scripts/register_sagemaker_model.py",
]

missing = [p for p in REQUIRED if not (ROOT / p).exists()]
if missing:
    print("Missing required files:")
    for item in missing:
        print(" -", item)
    sys.exit(1)

print("Required files: OK")

compile_result = subprocess.run(
    [sys.executable, "-m", "compileall", "-q", "."],
    cwd=ROOT,
)
if compile_result.returncode:
    sys.exit(compile_result.returncode)
print("Python syntax: OK")

test_result = subprocess.run(
    [sys.executable, "-m", "pytest", "backend/tests", "-q"],
    cwd=ROOT,
)
sys.exit(test_result.returncode)
