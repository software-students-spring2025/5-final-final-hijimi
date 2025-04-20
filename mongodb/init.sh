#!/bin/bash

# Wait for MongoDB to start
sleep 5 

# Import data into collections
# Note: MONGO_INITDB_DATABASE is an environment variable set by the official mongo image

mongoimport --host localhost:27017 --db ${MONGO_INITDB_DATABASE:-mydatabase} --collection products --type json --file /init_data.json --jsonArray --drop
mongoimport --host localhost:27017 --db ${MONGO_INITDB_DATABASE:-mydatabase} --collection users --type json --file /init_data.json --jsonArray --drop
mongoimport --host localhost:27017 --db ${MONGO_INITDB_DATABASE:-mydatabase} --collection interactions --type json --file /init_data.json --jsonArray --drop

echo "MongoDB initialization complete." 