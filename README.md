# Репозиторий 
https://github.com/nusatov/graduate_work

alembic revision --autogenerate -m 'initial'

alembic upgrade head

## Статус workflow
![Build](https://github.com/nusatov/ugc_sprint_2/actions/workflows/build.yml/badge.svg)

# Сервис оплаты, авторизации, выдачи контента, UGC.

## Описание
  - Сервис авторизации.
  - Сервис выдачи контента.
  - Интеграция сервиса авторизации в сервис выдачи контента.
  - Микросервис работает с парой(access, refresh) JWT токенов.
  - Позволяет авторизоваться с помощью аккаунтов (VK, Google, Yandex).
  - Трассировка запросов с помощью Jaeger (+ RequestID от Nginx - прокидываем по сервисам - видим по какому запросу происходит движение между сервисами).
  - Сервис логирования.
  - CI-CD(Проверка кода с помощью flake8, mypy).

## Стек
  - FastAPI, Postgres, SQLAlchemy, JSON Web Tokens(JWT).

## Запуск:
- заполняем .env в корне проекта (по примеру env.example)
- docker-compose:
    - docker-compose up --build -d

## Запуск тестов:
- заполняем .env в /auth_api/tests/functional/ и /movies_api/tests/functional/ (по примерам env.example)
- docker-compose:
    - docker-compose -f docker-compose_auth_tests.yaml up --build -d
    - docker-compose -f docker-compose_movies_tests.yaml up --build -d

## Дополнительно:
- http://127.0.0.1/api/v1/auth/openapi/ - Swagger auth_api
- http://127.0.0.1/api/v1/billing/openapi/ - Swagger billing_api
- http://127.0.0.1/api/v1/billing/admin/  - Admin panel billing
- http://127.0.0.1/api/v1/movies/openapi/  - Swagger movies_api
- http://127.0.0.1/api/v1/admin_panel/  - Admin panel movies
