# 1. Базовый образ Python
FROM python:3.11-slim

# 2. Переменная окружения для отключения буфера (чтобы логи писались сразу)
ENV PYTHONUNBUFFERED=1

# 3. Установка рабочих директорий
WORKDIR /app

# 4. Копируем зависимости отдельно для кеширования
COPY requirements.txt .

# 5. Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копируем всё приложение (включая handlers/)
COPY . .

# 7. Указываем команду запуска
CMD ["python", "main.py"]
