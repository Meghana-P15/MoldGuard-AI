FROM python:3.12-slim

WORKDIR /opt/program
COPY requirements.txt /opt/program/requirements.txt
RUN pip install --no-cache-dir -r /opt/program/requirements.txt
COPY serve.py /opt/program/serve.py

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "serve:app"]
