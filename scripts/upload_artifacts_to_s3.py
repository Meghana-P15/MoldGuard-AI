from pathlib import Path
import argparse
import boto3

DEFAULT_FILES = [
    "risk_model.joblib",
    "energy_model.joblib",
    "ood_model.joblib",
    "metadata.json",
    "demo_metrics.json",
]


def main(bucket: str, prefix: str, model_dir: str):
    s3 = boto3.client("s3")
    root = Path(model_dir)
    prefix = prefix.strip("/")

    for name in DEFAULT_FILES:
        path = root / name
        if not path.exists():
            print(f"skip: {path} does not exist")
            continue
        key = f"{prefix}/{name}" if prefix else name
        s3.upload_file(str(path), bucket, key)
        print(f"uploaded {path} -> s3://{bucket}/{key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", default="models")
    parser.add_argument("--model-dir", default="ai/models")
    args = parser.parse_args()
    main(args.bucket, args.prefix, args.model_dir)
