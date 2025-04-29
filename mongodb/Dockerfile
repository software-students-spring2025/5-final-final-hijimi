FROM mongo:latest

# Install jq for JSON processing 
RUN apt-get update && apt-get install -y jq && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy initialization script and data
COPY init.sh /docker-entrypoint-initdb.d/init.sh
COPY init_data.json /init_data.json

# Make the init script executable
RUN chmod +x /docker-entrypoint-initdb.d/init.sh 