# Используем базовый образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY pyproject.toml poetry.lock ./
COPY socnet/ .

# Устанавливаем Poetry и зависимости
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install --no-root

# Устанавливаем зависимости вручную (если требуется)
RUN poetry add gunicorn

# Копируем остальные файлы проекта
COPY . .

# Открываем порт для приложения
EXPOSE 8000

# Проверяем установку gunicorn
RUN poetry run gunicorn --version

# Команда для запуска приложения
CMD ["poetry", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "socnet.asgi:application", "--bind", "0.0.0.0:8000"]