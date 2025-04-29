# Use an official Python runtime as a parent image 
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Run the training script during the build (optional, adjust as needed)
# This assumes your training saves a model file that recommender.py uses
# RUN python train.py

# Define environment variable
ENV MONGO_URI="mongodb://mongodb:27017/mydatabase"

# Make port 80 available to the world outside this container (if needed, e.g., for health checks)
# EXPOSE 80 

# Run recommender.py when the container launches
# Adjust this CMD depending on how the recommender is used (e.g., runs as a service, or just provides functions)
CMD ["python", "recommender.py"] 