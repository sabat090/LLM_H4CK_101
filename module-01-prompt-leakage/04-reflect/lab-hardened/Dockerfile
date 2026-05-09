FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY module-01-prompt-leakage/04-reflect/lab-hardened/app/ /app/module-01-prompt-leakage/04-reflect/lab-hardened/app/

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--app-dir", "/app/module-01-prompt-leakage/04-reflect/lab-hardened/app", "--host", "0.0.0.0", "--port", "8010"]
