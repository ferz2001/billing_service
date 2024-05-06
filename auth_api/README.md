Сслыка на репозиторий https://github.com/Ruslanch0s/Auth_sprint_1

# Architecture diagram

**draw.io
**: https://drive.google.com/file/d/1eMwKgWFhyopHsc9GkP5Ya1oPjt3P8ihe/view?usp=sharing

**Роли пользователей:**

1) Неавторизованному анонимному пользователю доступно
    - /signup
    - /signin

2) Авторизованому пользователю без роли доступно
    - /refresh_tokens
    - /login_history
    - /change_password
    - /change_login
    - /logout_all
    - /logout_me

3) `admin` доступно все.

# Quickstart

1) Скопировать `.env.example` в `.env` и настроить.
2) Для запуска AuthService, PostgreSQL, Redis, Nginx использовать команду:

    docker compose up --build

3)
Документация [http://127.0.0.1/api/v1/openapi](http://127.0.0.1/api/v1/openapi)
4) Добавить пользователя с ролью `admin` из консоли командой:

    docker exec -it auth_service python cli.py

# Процесс разработки

## Подготовка

1) Создать виртуальное окружение

    python -m venv venv

2) Установить зависимости командой

    pip install -r requirements.txt

## Миграции PostgreSQL

Для работы с миграциями используется Alembic

Миграции хранятся в папке `Auth_sprint_1/src/migration/versions/`

Создать новую миграцию миграцию:

    alembic revision --autogenerate -m "First migration"

Проверить миграцию

    alembic check

Применить миграцию

    alembic upgrade head

## Запуск тестов

Из директории `/tests/functional`

1) Скопировать `.env.example` в `.env` и настроить.
2) Использовать команду

    docker compose up --build

# Changelog

- Регистрация нового пользователя
- Получение авторизационных токенов по логину и паролю
- Обновление авторизационных токенов
- Выход из аккаунта на текущем устройстве
- Выход из аккаунта на всех устройствах
- Смена логина
- Смена пароля
- История входов в аккаунт
- Создание суперпользователя через cli
- Создание роли
- Изменение роли
- Назначение роли
- Просмотр всех ролей
- Удаление роли
- Назначить роль пользователю
- Удаление роли у пользователя
- Получить все свои роли
- Авторизация через социальные сети (Yandex, VK, Google)
- Список привязанных соц сетей
- Удаление привязанной соц сети
