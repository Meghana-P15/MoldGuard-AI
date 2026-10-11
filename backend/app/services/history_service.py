from __future__ import annotations
from datetime import datetime, timezone
import uuid
import boto3

from backend.app.config import settings


class HistoryService:
    _memory = []

    @classmethod
    def save(cls, kind: str, payload: dict, result: dict) -> dict:
        item = {
            "prediction_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "input": payload,
            "result": result,
        }

        if settings.use_dynamodb:
            table = boto3.resource("dynamodb", region_name=settings.aws_region).Table(
                settings.dynamodb_table
            )
            # DynamoDB does not accept native float. Convert via JSON-safe string roundtrip.
            import json
            from decimal import Decimal
            safe = json.loads(json.dumps(item), parse_float=Decimal)
            table.put_item(Item=safe)
        else:
            cls._memory.insert(0, item)
            cls._memory = cls._memory[:100]

        return item

    @classmethod
    def list(cls, limit: int = 20):
        limit = max(1, min(limit, 100))
        if settings.use_dynamodb:
            table = boto3.resource("dynamodb", region_name=settings.aws_region).Table(
                settings.dynamodb_table
            )
            resp = table.scan(Limit=limit)
            items = resp.get("Items", [])
            items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return items[:limit]
        return cls._memory[:limit]
