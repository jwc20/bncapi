#!/bin/bash

# Setup development database
echo "Setting up development database..."

# Create databases
docker exec -it api-db psql -U postgres -c "CREATE DATABASE bncapi_dev;"
docker exec -it api-db psql -U postgres -c "CREATE DATABASE bncapi_test;"

echo "Databases created successfully!"

# Run Django migrations
echo "Running Django migrations..."
docker exec -it bncapi-container python manage.py migrate

echo "Development database setup complete!"
