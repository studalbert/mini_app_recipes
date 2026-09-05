FROM python:3.12-slim

WORKDIR /app

# Ставим зависимости отдельным слоем — чтобы Docker кэшировал их
# и не переустанавливал при каждом изменении кода приложения
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Папка для загруженных фото — монтируется как volume в docker-compose,
# создаём здесь на случай первого запуска без volume
RUN mkdir -p /app/uploads

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
