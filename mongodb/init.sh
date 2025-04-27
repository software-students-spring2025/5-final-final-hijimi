#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status
set -x  # Print commands and their arguments as they are executed (verbose)

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to start..."
until mongosh --host mongodb --eval "print('MongoDB connection successful!')" > /dev/null 2>&1; do
  echo "Waiting for MongoDB connection..."
  sleep 2
done

echo "MongoDB started, initializing data..."

# Import the sample data from the mounted JSON file
mongoimport --host mongodb --db "${MONGO_INITDB_DATABASE:-mydatabase}" --collection products --drop --file /docker-entrypoint-initdb.d/init_data.json --jsonArray --jsonArray --maintainInsertionOrder --arrayId products

# Import users data
mongoimport --host mongodb --db "${MONGO_INITDB_DATABASE:-mydatabase}" --collection users --drop --file /docker-entrypoint-initdb.d/init_data.json --jsonArray --maintainInsertionOrder --arrayId users

# Import interactions data
mongoimport --host mongodb --db "${MONGO_INITDB_DATABASE:-mydatabase}" --collection interactions --drop --file /docker-entrypoint-initdb.d/init_data.json --jsonArray --maintainInsertionOrder --arrayId interactions

# Create indexes for better query performance
mongosh --host mongodb --db "${MONGO_INITDB_DATABASE:-mydatabase}" <<EOF
  // Create index on user_id field in interactions collection
  db.interactions.createIndex({ user_id: 1 });
  
  // Create index on product_id field in interactions collection
  db.interactions.createIndex({ product_id: 1 });
  
  // Create index on user preferences
  db.users.createIndex({ preferences: 1 });
  
  // Create compound index on interaction type and timestamp
  db.interactions.createIndex({ type: 1, timestamp: -1 });
  
  // Create index on rating for sorting products
  db.products.createIndex({ rating: -1 });
  
  // Create index on price for sorting products
  db.products.createIndex({ price: 1 });
  
  // Create index on name for sorting products
  db.products.createIndex({ name: 1 });
  
  // Create index on categories array for category filtering
  db.products.createIndex({ categories: 1 });
  
  // Create index on brand for brand filtering
  db.products.createIndex({ brand: 1 });
  
  // Create text index on multiple fields for search functionality
  db.products.createIndex(
    { 
      name: "text", 
      description: "text", 
      brand: "text",
      categories: "text"
    },
    {
      weights: {
        name: 10,
        brand: 5,
        categories: 3,
        description: 1
      },
      name: "product_search_index"
    }
  );
  
  // Create compound indexes for common query patterns
  db.products.createIndex({ brand: 1, rating: -1 });
  db.products.createIndex({ categories: 1, rating: -1 });
  db.products.createIndex({ brand: 1, categories: 1, rating: -1 });

  // Print confirmation of all created indexes
  print("Created indexes for products collection:");
  db.products.getIndexes().forEach(idx => print(" - " + idx.name));
  
  print("Created indexes for users collection:");
  db.users.getIndexes().forEach(idx => print(" - " + idx.name));
  
  print("Created indexes for interactions collection:");
  db.interactions.getIndexes().forEach(idx => print(" - " + idx.name));
  
  // Verify the data was imported correctly
  print("Products count: " + db.products.countDocuments());
  print("Users count: " + db.users.countDocuments());
  print("Interactions count: " + db.interactions.countDocuments());
EOF

echo "MongoDB initialization completed successfully!" 