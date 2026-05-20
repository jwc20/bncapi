#!/bin/bash

# Setup development database (local, non-Docker environment)
# For Docker, run migrations inside the container:
#   docker exec -it bncapi-container python manage.py migrate
echo "Setting up development database..."

# Run Django migrations (SQLite db.sqlite3 will be created automatically)
echo "Running Django migrations..."
python manage.py migrate

echo "Development database setup complete!"
