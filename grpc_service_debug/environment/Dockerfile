FROM python:3.12-slim

WORKDIR /app

# Install pinned dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files (proto, pre-generated stubs, server)
COPY * /app/

CMD ["python", "server.py"]
