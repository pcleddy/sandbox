#!/bin/bash
set -e

if [ ! -f .initialized ]; then
echo initializing container
source /run/secrets/creds

mysql --protocol=socket <<EOF
CREATE DATABASE IF NOT EXISTS wordpress;

DROP USER IF EXISTS '${WORDPRESS_DB_USER}'@'%';

CREATE USER '${WORDPRESS_DB_USER}'@'%' IDENTIFIED BY '${WORDPRESS_DB_PASSWORD}';
GRANT SELECT ON wordpress.* TO '${MYSQL_USER}'@'%';
EOF
touch .initialized
else
echo already initialized
fi
