FROM python:3.11-slim

WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code + lab app
COPY shared/ /app/shared/
COPY module-01-prompt-leakage/01-explore/lab/app/ /app/module-01-prompt-leakage/01-explore/lab/app/

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--app-dir", "/app/module-01-prompt-leakage/01-explore/lab/app", "--host", "0.0.0.0", "--port", "8001"]
