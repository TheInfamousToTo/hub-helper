FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Configure Git to handle directory ownership issues
RUN git config --global --add safe.directory '*' && \
    git config --global user.name "Hub Helper" && \
    git config --global user.email "hub-helper@automation.local"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for projects (will be mounted)
RUN mkdir -p /projects

# Expose port
EXPOSE 5414

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "app.py"]
