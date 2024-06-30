# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOCAL_STORAGE_PATH=/mnt/data/fallback_data.json

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file and install the dependencies
COPY requirements1.txt /app/
RUN pip install --no-cache-dir -r requirements1.txt
#RUN pip install ../SharedUtils



# Copy the application files
COPY app /app
COPY config /config






# Expose port 5000
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "main.py"]