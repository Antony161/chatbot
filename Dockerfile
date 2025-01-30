# Use the official Python slim image
FROM python:3.10-slim

# Install curl
RUN apt-get update && apt-get install -y curl

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Copy the .env file to the container
COPY .env .env

# Expose the port your app will run on
EXPOSE 8000

# Ensure Ollama API is accessible before starting Django
CMD ["bash", "-c", "until curl -s http://localhost:11434; do echo 'Waiting for Ollama API...'; sleep 2; done && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
