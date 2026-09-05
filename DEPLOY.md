# Деплой в продакшн 

Разносим на два поддомена одного домена:
- `yourdomain.com` — фронтенд (статика)
- `api.yourdomain.com` — backend

Почему не на один домен: у фронтенда есть страница `/profile` (React Router),
а у backend — эндпоинт `GET /profile`. На одном домене они бы конфликтовали.

## Что понадобится

1. **VPS** (Ubuntu 22/24), минимум 1 ГБ RAM. Варианты: Timeweb Cloud, Selectel,
   Hetzner CX22 — что угодно с root-доступом по SSH.
2. **Домен** — любой регистратор (reg.ru, Namecheap и т.д.).
3. **Бот в Telegram** — токен от [@BotFather](https://t.me/BotFather), если ещё нет.

## 1. DNS

В панели управления доменом добавь две A-записи, обе указывают на IP твоего VPS:

| Тип | Имя  | Значение     |
|-----|------|--------------|
| A   | @    | IP твоего VPS |
| A   | api  | IP твоего VPS |

Подожди 5–30 минут, пока DNS обновится (проверить: `ping yourdomain.com`).

## 2. Подготовка сервера

Подключись по SSH и поставь Docker:

```bash
curl -fsSL https://get.docker.com | sh
apt install -y git
```

Склонируй репозиторий:

```bash
git clone https://github.com/studalbert/mini_app_recipes.git
cd mini_app_recipes
```

## 3. Настройка окружения

```bash
cp .env.prod.example .env
nano .env   # заполни POSTGRES_PASSWORD своим паролем

cp recipe-app-backend/.env.prod.example recipe-app-backend/.env
nano recipe-app-backend/.env
# заполни: тот же POSTGRES_PASSWORD что и выше,
# TELEGRAM_BOT_TOKEN — токен от BotFather,
# APP_SECRET_KEY — любая случайная строка
```

## 4. Правим Nginx-конфиг под свой домен

```bash
sed -i 's/yourdomain.com/ТВОЙ_ДОМЕН/g' deploy/nginx/app.conf
```

Замени `ТВОЙ_ДОМЕН` на реальный, например `example.com`. Скрипт сам заменит
и `yourdomain.com`, и `api.yourdomain.com` (второй просто получит тот же корень).

## 5. Собираем фронтенд

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

cd recipe-app-frontend
echo "VITE_API_URL=https://api.ТВОЙ_ДОМЕН" > .env
npm ci
npm run build
cd ..
```

После этого в `recipe-app-frontend/dist/` лежит собранная статика — её и монтирует Nginx.

## 6. Получаем HTTPS-сертификат и запускаем всё

```bash
chmod +x deploy/init-letsencrypt.sh
./deploy/init-letsencrypt.sh ТВОЙ_ДОМЕН api.ТВОЙ_ДОМЕН твой@email.com
```

Скрипт сам поднимет весь стек (Postgres, backend, nginx) и получит сертификат.
Если что-то пошло не так — смотри `docker compose -f docker-compose.prod.yml logs`.

## 7. Проверка

```bash
curl https://api.ТВОЙ_ДОМЕН/health
```

Должно вернуть `{"status":"ok"}`. Открой `https://ТВОЙ_ДОМЕН` в браузере — должна открыться лента.

## 8. Регистрация Mini App в Telegram

1. Напиши [@BotFather](https://t.me/BotFather) → `/mybots` → выбери своего бота
2. `Bot Settings` → `Menu Button` → `Configure Menu Button`
3. Укажи URL: `https://ТВОЙ_ДОМЕН`
4. Открой бота в Telegram — снизу должна появиться кнопка меню, открывающая Mini App

## Обновление после изменений в коде

```bash
cd mini_app_recipes
git pull

# backend
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d backend

# frontend (пересобрать статику)
cd recipe-app-frontend && npm run build && cd ..
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## Продление сертификата

Происходит автоматически — контейнер `certbot` в фоне раз в 12 часов проверяет
срок действия и продлевает при необходимости. Вручную ничего делать не нужно.

## Бэкапы

Минимум стоит настроить дамп Postgres по расписанию:

```bash
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U recipe_user recipe_db > backup_$(date +%F).sql
```

Добавь эту команду в cron (`crontab -e`), например раз в сутки.
