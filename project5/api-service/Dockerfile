# api-service/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run tests and check coverage
RUN pytest --cov=src tests/ --cov-report=term-missing --cov-fail-under=80

# Run the service
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]