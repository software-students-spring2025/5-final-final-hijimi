// database/init-scripts/setup.js
db = db.getSiblingDB('ecommerce');

// Create collections
db.createCollection('users');
db.createCollection('products');
db.createCollection('interactions');

// Insert sample data
db.products.insertMany([
  // Sample products
  { 
    id: 1, 
    name: "Smartphone X", 
    category: "Electronics", 
    price: 799.99, 
    features: ["5G", "OLED", "Waterproof"] 
  },
  // Add more products...
]);

// Add indexes for faster queries
db.products.createIndex({ category: 1 });
db.interactions.createIndex({ userId: 1 });
db.interactions.createIndex({ productId: 1 });