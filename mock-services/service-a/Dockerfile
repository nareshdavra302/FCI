FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared ./shared
COPY service-a ./service-a

ENV SERVICE_NAME=service-a
ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "service-a.main:app", "--host", "0.0.0.0", "--port", "8001"]
