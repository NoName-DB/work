FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app/src

# Install dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./.env.example ./.env

EXPOSE 8000

CMD ["uvicorn", "business_template.main:app", "--host", "0.0.0.0", "--port", "8000"]
