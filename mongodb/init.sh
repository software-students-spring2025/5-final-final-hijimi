#!/bin/bash

# 等待 MongoDB 启动完成
sleep 5

echo "Inserting data into MongoDB..."

mongo <<EOF
use ecommerce

var data = cat('/data/init_data.json');
var parsed = JSON.parse(data);

db.users.insertMany(parsed.users);
db.products.insertMany(parsed.products);
db.interactions.insertMany(parsed.interactions);

EOF

echo "Data insertion complete."
