from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from backend.app.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "structured", None)
        if isinstance(extra, dict):
            payload.update(extra)
        return json.dumps(payload, default=str)


def _logger() -> logging.Logger:
    logger = logging.getLogger("moldguard")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    logger.propagate = False
    return logger


class MonitoringService:
    logger = _logger()
    _cloudwatch = None

    @classmethod
    def log(cls, event: str, **fields: Any) -> None:
        cls.logger.info(event, extra={"structured": {"event": event, **fields}})

    @classmethod
    def error(cls, event: str, **fields: Any) -> None:
        cls.logger.error(event, extra={"structured": {"event": event, **fields}})

    @classmethod
    def _client(cls):
        if not settings.enable_cloudwatch_metrics:
            return None
        if cls._cloudwatch is None:
            import boto3
            cls._cloudwatch = boto3.client("cloudwatch", region_name=settings.aws_region)
        return cls._cloudwatch

    @classmethod
    def metric(cls, name: str, value: float, unit: str = "Count", **dimensions: str) -> None:
        client = cls._client()
        if client is None:
            return
        try:
            dims = [{"Name": str(k), "Value": str(v)} for k, v in dimensions.items()]
            client.put_metric_data(
                Namespace=settings.cloudwatch_namespace,
                MetricData=[{
                    "MetricName": name,
                    "Value": float(value),
                    "Unit": unit,
                    "Dimensions": dims,
                }],
            )
        except Exception as exc:
            cls.error("cloudwatch_metric_error", metric=name, error=str(exc))
