FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache build-base netcat-openbsd

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "bncapi.asgi:application"]