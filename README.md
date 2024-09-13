Этот проект - дипломная работа студентов группы Py53-onl.

Ссылка на сайт:
https://diplom-t24j.onrender.com/

Описание:
Сайт социальной сети с профилями, группами, новостями, комментами и внутренней почтой и групповым чатом на websocket.

Технологии:

Языки программирования: Python v3.10, JavaScript
Дополнительно: HTML5, CSS3
Framework: Django, ReactJS
Database: SQLLite

Размещение:
Сайт размещен на бесплтном хостинге Render.

Разработчики:
https://github.com/ViktoriaKonoplyanik
https://github.com/fedyaslonn
https://github.com/Danya2kk
https://github.com/sajicklevo

Для локальной загрузки требуется:
1.Загрузить сайт на ПК.
2. Установить виртуальное окружение с Python v3.10
3. Установить библиотеки. (в проекте использовался poetry)
   Для этого cfyxfkf нужно установить poetry - pip install poetry
   Затем для устновки всех библиотек  -   poetry install
4. Для запуска в wsgi можно запустить проект через manage.py  (python manage.py runserver)
   для запуска в asgi запускаемся через runserver.py  python runserver.py 
  ( при запуске проекта в локальном виде  на адресе "0.0.0.0:8000"  нужно для входа использовать адрес "localhost:8000")

   Дополнительно. Команда длля запуска сайта на сервере или через Docker 
   # Команда для запуска приложения
CMD ["poetry", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "socnet.asgi:application", "--bind", "0.0.0.0:8000"]



