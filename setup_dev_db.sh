#!/bin/bash

# Setup production database
echo "Setting up production database..."

# Create databases
docker compose -f docker-compose.yml exec api-db psql -U postgres -c "CREATE DATABASE bncapi_dev;"
# docker compose -f docker-compose.prod.yml exec api-db psql -U postgres -c "CREATE DATABASE bncapi_test;"

echo "Databases created successfully!"

# Run Django migrations
echo "Running Django migrations..."
docker compose -f docker-compose.yml exec api python manage.py migrate

echo "Production database setup complete!"
