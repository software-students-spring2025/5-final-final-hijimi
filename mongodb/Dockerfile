FROM mongo:latest

# Copy initialization script and data
COPY init.sh /docker-entrypoint-initdb.d/init.sh
COPY init_data.json /init_data.json

# Make the init script executable
RUN chmod +x /docker-entrypoint-initdb.d/init.sh 