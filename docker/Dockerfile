# docker/Dockerfile

# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file and install the dependencies
COPY /AuditLogFlask/requirements.txt .
# Copy SharedUtils
COPY /SharedUtils /app/SharedUtils

RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install ../SharedUtils
# Copy the application files
COPY /AuditLogFlask/app /app
COPY /AuditLogFlask/config /config
COPY /AuditLogFlask .

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 5000
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "main.py"]
#CMD ["flask", "run"]
