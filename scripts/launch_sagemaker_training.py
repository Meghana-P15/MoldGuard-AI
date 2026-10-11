from __future__ import annotations

import argparse
import time

import boto3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--role-arn", required=True)
    parser.add_argument("--image-uri", required=True, help="ECR URI for MoldGuard training image")
    parser.add_argument("--train-s3-uri", required=True, help="S3 prefix containing canonical CSV files")
    parser.add_argument("--output-s3-uri", required=True)
    parser.add_argument("--region", default="ap-south-1")
    parser.add_argument("--instance-type", default="ml.m5.large")
    parser.add_argument("--optuna-trials", type=int, default=0)
    args = parser.parse_args()

    client = boto3.client("sagemaker", region_name=args.region)
    job_name = f"moldguard-training-{int(time.time())}"

    client.create_training_job(
        TrainingJobName=job_name,
        RoleArn=args.role_arn,
        AlgorithmSpecification={
            "TrainingImage": args.image_uri,
            "TrainingInputMode": "File",
        },
        InputDataConfig=[
            {
                "ChannelName": "train",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": args.train_s3_uri,
                        "S3DataDistributionType": "FullyReplicated",
                    }
                },
                "ContentType": "text/csv",
            }
        ],
        OutputDataConfig={"S3OutputPath": args.output_s3_uri},
        ResourceConfig={
            "InstanceType": args.instance_type,
            "InstanceCount": 1,
            "VolumeSizeInGB": 20,
        },
        StoppingCondition={"MaxRuntimeInSeconds": 3600},
        Environment={
            "MOLDGUARD_OPTUNA_TRIALS": str(args.optuna_trials),
        },
        Tags=[
            {"Key": "Project", "Value": "MoldGuard-AI"},
            {"Key": "Track", "Value": "Waste-and-Energy"},
        ],
    )

    print(job_name)
    print(f"Open SageMaker Training jobs to watch: {job_name}")


if __name__ == "__main__":
    main()
