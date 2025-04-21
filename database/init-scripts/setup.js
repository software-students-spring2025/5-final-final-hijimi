// 在 ecomm 数据库里造一个示例集合
db = db.getSiblingDB('ecomm');
db.createCollection('users');
db.users.insertMany([
  { _id: 1, name: "Alice" , preference: ["laptop", "mouse"]},
  { _id: 2, name: "Bob"   , preference: ["keyboard", "headphone"]},
]);
