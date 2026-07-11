FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY .env.example .env.example

# LOGGIFIRE
ENV LOGFIRE_TOKEN=""

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "-m", "src.api.mcp_server"]