FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared ./shared
COPY service-c ./service-c

ENV SERVICE_NAME=service-c
ENV PYTHONPATH=/app

EXPOSE 8003

CMD ["uvicorn", "service-c.main:app", "--host", "0.0.0.0", "--port", "8003"]
