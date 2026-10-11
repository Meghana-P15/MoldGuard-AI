# AWS deployment

## Minimal hackathon deployment

### 1. S3
Create a bucket for:
- datasets
- trained models
- metrics

Upload only files you are allowed to redistribute.

### 2. SageMaker AI
Use the S3 dataset to run training/evaluation or a notebook job. Export final `risk_model.joblib`, `energy_model.joblib`, and `metadata.json`.

### 3. DynamoDB
Deploy the included CloudFormation template:

```bash
aws cloudformation deploy   --template-file infrastructure/dynamodb.yaml   --stack-name moldguard-data
```

Then set:
```env
USE_DYNAMODB=true
DYNAMODB_TABLE=MoldGuardPredictions
AWS_REGION=ap-south-1
```

### 4. Backend / App Runner
Build from the repository root:

```bash
docker build -f backend/Dockerfile -t moldguard-api .
docker run -p 8000:8000 moldguard-api
```

Push the image to ECR and connect it to App Runner, or connect App Runner directly to your repository with an equivalent build.

### 5. Frontend / Amplify Hosting
Set:
```env
VITE_API_BASE_URL=https://YOUR-APP-RUNNER-URL
```

Connect the `frontend` folder to Amplify Hosting.

### 6. CloudWatch
App Runner emits service logs. Show a real request in the demo and the matching log entry.

## IAM
Use least privilege. Do not give the application AdministratorAccess.
