# database/Dockerfile
FROM mongo:latest

# Add initialization scripts
COPY init-scripts/ /docker-entrypoint-initdb.d/

# Set default port
EXPOSE 27017