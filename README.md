# bncapi

Backend Api for Benjamin and Charlotte game.

Mono-repo: https://github.com/jwc20/bnc-game

Docs: https://github.com/jwc20/bnc-docs


## Quick Start

```bash
# build and start docker containers
docker compose -f docker-compose.yml up -d --build

# setup the production database
./setup_dev_db.sh

# Stop when done
docker compose -f docker-compose.yml down
```

Alternatively, you can run the server without docker.

```bash
# start .venv
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Swagger

Access the Swagger OpenApi on http://0.0.0.0:8000/api/docs.


## Models

<img src="/db.png" alt="db erd" width="400">

## Custom Token Authentication

This project uses [custom knox token django app](https://github.com/jwc20/knoxtokens) tailored for Django-Ninja.
Knox gives you the same easy server-side control over logins that sessions do, but without storing tokens in plaintext like DRF’s default auth. 
Unlike JWTs, which are tricky to revoke once they’re out in the wild, Knox keeps only a hashed version on the server(database) so you can kill a single device’s login or all of them instantly. 
It’s a great fit for APIs that need secure, multi-device logins without the headache of managing JWT blacklists or heavy session state.
Since Knox tokens are stored in a securely hashed form, even if someone gets access to the database, they can’t use the stored token to log in.


## Dependencies

- [Django-Ninja](https://github.com/vitalik/django-ninja)
- [Django Channels](https://github.com/django/channels)
- [Channels-redis (Daphne)](https://github.com/django/channels_redis)
- [psycopg2-binary](https://github.com/psycopg/psycopg2)
- [django-cors-headers](https://github.com/adamchainz/django-cors-headers)
- [(Custom) Knox Token Authentication](https://github.com/jwc20/knoxtokens)
