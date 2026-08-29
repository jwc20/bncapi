#!/bin/bash

echo "Running Django migrations..."
docker compose -f docker-compose.yml exec api python manage.py migrate

echo "SQLite database setup complete!"
