# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application code into the container
COPY . .

# Install any necessary dependencies (you may need to adjust the package name)
RUN pip install -r requirements.txt

# Expose the port your FastAPI application is running on (default is 8000)
EXPOSE 8000

# Command to run your FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
