# Use an official Python runtime as a parent image 
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the API requirements file into the container at /app
COPY api/requirements.txt .

# Install API dependencies
# --default-timeout is added to prevent potential pip install timeouts
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy the Recommender requirements file (needed because API imports recommender)
COPY recommender/requirements.txt ./recommender-requirements.txt
RUN pip install --no-cache-dir --default-timeout=100 -r recommender-requirements.txt
RUN rm recommender-requirements.txt # Clean up

# Copy the API and Recommender code into the container
COPY ./api /app/api
COPY ./recommender /app/recommender

# Add the project root to PYTHONPATH so imports like `from recommender import ...` work
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Define environment variable for the MongoDB connection string
# It uses 'mongodb' as the hostname, expecting it to be the service name in Docker Compose/Kubernetes
ENV MONGO_URI="mongodb://mongodb:27017/mydatabase"




# Make port 8000 available (as specified in docker-compose)
EXPOSE 8000

# Default command (will be overridden by docker-compose for development)
# Run from /app, targeting the app object within the api directory
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"] 
