#!/bin/bash

# Autentica como o usuário admin
mongosh --host localhost -u "admin" -p "adminpassword" --authenticationDatabase "admin" <<EOF
use admin
db.createUser({
  user: "admin",
  pwd: "adminpassword",
  roles: [{ role: "root", db: "admin" }]
})
use api
db.createUser({
  user: "admin",
  pwd: "adminpassword",
  roles: [{ role: "readWrite", db: "api" }]
})
EOF
