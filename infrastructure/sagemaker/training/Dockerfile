FROM python:3.12-slim

WORKDIR /opt/program
COPY infrastructure/sagemaker/training/requirements.txt /opt/program/requirements.txt
RUN pip install --no-cache-dir -r /opt/program/requirements.txt

COPY ai /opt/program/ai
COPY infrastructure/sagemaker/entrypoint.py /opt/program/entrypoint.py

ENV PYTHONPATH=/opt/program
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "/opt/program/entrypoint.py"]
