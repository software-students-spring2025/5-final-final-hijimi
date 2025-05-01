#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status
set -x  # Print commands and their arguments as they are executed (verbose)

# Wait for MongoDB to start
sleep 10

echo "MongoDB initialization starting..."

# Set database name
DB_NAME=${MONGO_INITDB_DATABASE:-mydatabase}
echo "Using database: $DB_NAME"

# Extract collections from init_data.json
echo "Extracting collections from init_data.json..."
jq -c '.products' /init_data.json > /tmp/products.json
jq -c '.users' /init_data.json > /tmp/users.json
jq -c '.interactions' /init_data.json > /tmp/interactions.json

# Check files exist
ls -la /tmp/

# Import each collection individually
echo "Importing products collection..."
mongoimport --host localhost --db "$DB_NAME" --collection products --file /tmp/products.json --jsonArray

echo "Importing users collection..."
mongoimport --host localhost --db "$DB_NAME" --collection users --file /tmp/users.json --jsonArray

echo "Importing interactions collection..."
mongoimport --host localhost --db "$DB_NAME" --collection interactions --file /tmp/interactions.json --jsonArray

# Verify data was imported
echo "Verifying data import:"
mongosh --quiet localhost/"$DB_NAME" --eval "db.products.count()"
mongosh --quiet localhost/"$DB_NAME" --eval "db.users.count()"
mongosh --quiet localhost/"$DB_NAME" --eval "db.interactions.count()"

# Clean up temporary files
rm /tmp/products.json /tmp/users.json /tmp/interactions.json

echo "MongoDB initialization complete." 