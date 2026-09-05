#!/bin/bash
# Первичная настройка HTTPS. Запускать ОДИН РАЗ перед первым `docker compose up`.
#
# Проблема "курицы и яйца": nginx-конфиг ссылается на сертификаты Let's Encrypt,
# которых ещё не существует — nginx с таким конфигом не запустится вообще.
# Решение: сначала создаём временный самоподписанный сертификат (чтобы nginx
# смог стартовать), поднимаем nginx, получаем через него настоящий сертификат
# от Let's Encrypt (он спрашивает по HTTP через /.well-known/acme-challenge/),
# и перезапускаем nginx уже с настоящим сертификатом.
#
# Использование:
#   chmod +x deploy/init-letsencrypt.sh
#   ./deploy/init-letsencrypt.sh yourdomain.com api.yourdomain.com your@email.com

set -e

if [ "$#" -ne 3 ]; then
    echo "Использование: $0 <домен-фронтенда> <домен-api> <email>"
    echo "Пример: $0 example.com api.example.com me@example.com"
    exit 1
fi

DOMAIN1=$1
DOMAIN2=$2
EMAIL=$3

echo "==> Проверь, что в deploy/nginx/app.conf 'yourdomain.com' заменён на $DOMAIN1"
echo "    (а 'api.yourdomain.com' — на $DOMAIN2), и нажми Enter для продолжения..."
read -r _

echo "==> Создаю временный самоподписанный сертификат..."
docker run --rm \
  -v recipe_app_certbot_certs:/etc/letsencrypt \
  alpine:3.20 sh -c "
    apk add --no-cache openssl >/dev/null &&
    mkdir -p /etc/letsencrypt/live/$DOMAIN1 &&
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
      -keyout /etc/letsencrypt/live/$DOMAIN1/privkey.pem \
      -out /etc/letsencrypt/live/$DOMAIN1/fullchain.pem \
      -subj '/CN=localhost'
  "

echo "==> Запускаю nginx с временным сертификатом..."
docker compose -f docker-compose.prod.yml up -d nginx

echo "==> Удаляю временный сертификат и запрашиваю настоящий у Let's Encrypt..."
docker compose -f docker-compose.prod.yml run --rm --entrypoint "\
  rm -rf /etc/letsencrypt/live/$DOMAIN1 /etc/letsencrypt/archive/$DOMAIN1 /etc/letsencrypt/renewal/$DOMAIN1.conf" certbot

docker compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
  -d $DOMAIN1 -d $DOMAIN2 \
  --email $EMAIL --agree-tos --no-eff-email" certbot

echo "==> Перезапускаю nginx с настоящим сертификатом..."
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "==> Готово! Проверь https://$DOMAIN1 и https://$DOMAIN2"
