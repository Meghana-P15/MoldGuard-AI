from __future__ import annotations

import json
import uuid
from typing import Any, Dict

import boto3

from agentic.schemas import AgentRequest
from agentic.local_orchestrator import run_local_agentic_analysis
from backend.app.config import settings


class AgentService:
    @staticmethod
    def _read_agentcore_response(response: dict) -> Dict[str, Any]:
        body = response.get("response")
        if body is None:
            raise RuntimeError("AgentCore response did not contain 'response'.")

        if hasattr(body, "read"):
            raw = body.read()
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            return json.loads(raw)

        chunks = []
        try:
            for chunk in body:
                if isinstance(chunk, bytes):
                    chunks.append(chunk.decode("utf-8"))
                elif isinstance(chunk, str):
                    chunks.append(chunk)
                elif isinstance(chunk, dict):
                    data = chunk.get("bytes") or chunk.get("chunk") or chunk
                    if isinstance(data, bytes):
                        chunks.append(data.decode("utf-8"))
                    elif isinstance(data, str):
                        chunks.append(data)
            if chunks:
                return json.loads("".join(chunks))
        except TypeError:
            pass

        raise RuntimeError("Unsupported AgentCore response body format.")

    @classmethod
    def run(cls, request: AgentRequest) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())

        if (
            settings.agent_mode.lower() != "agentcore"
            or not settings.agentcore_runtime_arn
        ):
            result = run_local_agentic_analysis(request)
            result["mode"] = "local-deterministic-orchestrator"
            result["agent_session_id"] = session_id
            result["agent_trace_id"] = None
            result["agent_span_id"] = None
            result["agent_investigation_completed"] = False
            return result

        client = boto3.client(
            "bedrock-agentcore",
            region_name=settings.aws_region,
        )

        response = client.invoke_agent_runtime(
            agentRuntimeArn=settings.agentcore_runtime_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(request.model_dump()).encode("utf-8"),
            qualifier=settings.agentcore_qualifier,
        )

        result = cls._read_agentcore_response(response)
        result["mode"] = result.get("mode", "agentcore-strands-verified")
        result["agent_session_id"] = session_id
        return result
