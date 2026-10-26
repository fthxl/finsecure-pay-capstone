# Base image: official Python 3.11 slim variant
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (for faster rebuilds when only code changes)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app.py .

# Tell Docker this container listens on port 8000
EXPOSE 8000

# The command that runs when the container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]