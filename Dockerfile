# Используем базовый образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY pyproject.toml poetry.lock ./
COPY socnet/ socnet/

# Устанавливаем Poetry и зависимости
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install --no-root

# Копируем остальные файлы проекта
COPY . .

# Открываем порт для приложения
EXPOSE 8000

# Команда для запуска приложения
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "socnet.asgi:application", "--bind", "0.0.0.0:8000"]
