db = db.getSiblingDB('ecommerce');

db.users.insertMany([
  { user_id: "u1", name: "Alice" },
  { user_id: "u2", name: "Bob" }
]);

db.products.insertMany([
  { product_id: "p1", name: "Laptop" },
  { product_id: "p2", name: "Headphones" },
  { product_id: "p3", name: "Backpack" }
]);

db.interactions.insertMany([
  { user_id: "u1", product_id: "p1", action: "view" },
  { user_id: "u1", product_id: "p2", action: "purchase" },
  { user_id: "u2", product_id: "p2", action: "view" },
  { user_id: "u2", product_id: "p3", action: "purchase" }
]);
