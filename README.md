# bncapi

```bash
# build and start development containers
docker compose -f docker-compose.yml up -d --build

# setup the production database
./setup_dev_db.sh

# Stop when done
docker compose -f docker-compose.yml down
```

![db erd](/db.png)