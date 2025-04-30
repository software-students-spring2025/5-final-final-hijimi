#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status
set -x  # Print commands and their arguments as they are executed (verbose)

# Wait for MongoDB to start
sleep 5 

# Import data into collections
# Note: MONGO_INITDB_DATABASE is an environment variable set by the official mongo image

echo "MongoDB initialization starting..."

# Extract each collection from init_data.json to temporary files
echo "Extracting collections from init_data.json..."
jq -c '.products' /init_data.json > /tmp/products.json
jq -c '.users' /init_data.json > /tmp/users.json
jq -c '.interactions' /init_data.json > /tmp/interactions.json

# Check the extracted files
echo "Checking extracted files:"
echo "Products:"
cat /tmp/products.json
echo "Users:"
cat /tmp/users.json
echo "Interactions:"
cat /tmp/interactions.json

# Set database name
DB_NAME=${MONGO_INITDB_DATABASE:-mydatabase}
echo "Using database: $DB_NAME"

# Import each collection individually
echo "Importing products collection..."
mongoimport --uri "$MONGO_URI" --db "$DB_NAME" --collection products --file /tmp/products.json --jsonArray

echo "Importing users collection..."
mongoimport --uri "$MONGO_URI" --db "$DB_NAME" --collection users --file /tmp/users.json --jsonArray

echo "Importing interactions collection..."
mongoimport --uri "$MONGO_URI" --db "$DB_NAME" --collection interactions --file /tmp/interactions.json --jsonArray

# Verify data was imported
echo "Verifying data import:"
mongosh --quiet "$MONGO_URI/$DB_NAME" --eval "db.products.count()"
mongosh --quiet "$MONGO_URI/$DB_NAME" --eval "db.users.count()"
mongosh --quiet "$MONGO_URI/$DB_NAME" --eval "db.interactions.count()"

# Clean up temporary files
rm /tmp/products.json /tmp/users.json /tmp/interactions.json

echo "MongoDB initialization complete." 