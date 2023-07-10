# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY telegram_api.py .
COPY .env .
COPY telegram_auth3.session .


# Expose the container port
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "telegram_api:app", "--host", "0.0.0.0", "--port", "8000"]