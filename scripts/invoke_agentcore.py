from __future__ import annotations

import argparse
import json
import uuid

import boto3


def read_response(response):
    body = response["response"]
    if hasattr(body, "read"):
        raw = body.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return json.loads(raw)

    parts = []
    for chunk in body:
        if isinstance(chunk, bytes):
            parts.append(chunk.decode("utf-8"))
        else:
            parts.append(str(chunk))
    return json.loads("".join(parts))


def main(runtime_arn: str, region: str):
    payload = {
        "objective": (
            "Evaluate this planned batch and recommend lower-waste, "
            "lower-energy settings only when justified."
        ),
        "batch": {
            "Tinj": 240,
            "tinj": 1.7,
            "Pinj": 40,
            "Ph": 24,
            "Bp": 28,
            "th": 7,
            "cycles": 10000,
            "part_weight_g": 18.5,
            "machine_id": "DEMO-01",
            "material_code": "PP"
        }
    }

    client = boto3.client("bedrock-agentcore", region_name=region)
    response = client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=str(uuid.uuid4()),
        payload=json.dumps(payload).encode("utf-8"),
        qualifier="DEFAULT",
    )
    print(json.dumps(read_response(response), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arn", required=True)
    parser.add_argument("--region", default="us-east-1")
    args = parser.parse_args()
    main(args.arn, args.region)
