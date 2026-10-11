from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("moldguard.observability")


def configure_observability() -> None:
    """Configure optional Strands/OpenTelemetry exporters.

    AgentCore Runtime can provide the global OTEL provider. When an OTLP endpoint
    is explicitly configured, StrandsTelemetry adds an OTLP exporter. A console
    exporter can be enabled locally with MOLDGUARD_OTEL_CONSOLE=true.
    """
    try:
        from strands.telemetry import StrandsTelemetry

        telemetry = StrandsTelemetry()
        if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
            telemetry.setup_otlp_exporter()
        if os.getenv("MOLDGUARD_OTEL_CONSOLE", "false").lower() == "true":
            telemetry.setup_console_exporter()
    except Exception as exc:  # Observability must not make inference unavailable.
        logger.warning("OTEL setup skipped: %s", exc)


def current_trace_context() -> dict[str, Any]:
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context()
        if not ctx or not ctx.is_valid:
            return {"trace_id": None, "span_id": None}
        return {
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "016x"),
        }
    except Exception:
        return {"trace_id": None, "span_id": None}


def set_current_span_attributes(**attrs: Any) -> None:
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        for key, value in attrs.items():
            if value is not None:
                span.set_attribute(key, value)
    except Exception:
        return
