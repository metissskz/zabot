# 1. Базовый образ Python
FROM python:3.11-slim

# 2. Отключаем буферизацию вывода (полезно для логов)
ENV PYTHONUNBUFFERED=1

# 3. Устанавливаем рабочую директорию
WORKDIR /app

# 4. Обновляем pip и устанавливаем системные зависимости
RUN apt-get update && apt-get install -y build-essential libpq-dev && pip install --upgrade pip

# 5. Копируем только requirements для кеширования слоёв
COPY requirements.txt .

# 6. Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# 7. Копируем всё приложение
COPY . .

# 8. Указываем команду запуска (бота)
CMD ["python", "main.py"]
