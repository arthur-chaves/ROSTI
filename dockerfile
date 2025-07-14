# Lightweight Python base image
FROM python:3.9-slim

# Working directory inside the container
WORKDIR /usr/streamlit/app

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required system dependencies (e.g., psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and .env file
COPY src/ ./
COPY .env ./

# Expose Streamlit port
EXPOSE 8501

# Command to run Streamlit on port 8501, listening on all interfaces
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
