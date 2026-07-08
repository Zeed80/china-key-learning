# ПРОЕКТ ЕЩЕ В ПРОЦЕССЕ РАЗРАБОТКИ

# China Key Learning

China Key Learning - web-приложение для обучения ключам упрощенного китайского языка. Сейчас проект сфокусирован на 214 ключах Kangxi: быстрый обзор формы, адаптивная тренировка, экзамен на 20 вопросов, отслеживание прогресса и админка для редактирования учебного контента.

## Для чего это

Цель проекта - сделать систему "натаскивания" на китайские ключи:

- сначала пользователь просматривает все ключи с кратким смыслом, формами, похожими начертаниями и примерами;
- затем тренируется в режиме выбора ответа;
- слабые ключи появляются чаще, сильные - реже, но не исчезают из ротации;
- экзамен проверяет 20 вопросов без подсказок и показывает правильные ответы только после завершения;
- общий балл обучения по 10-балльной шкале считается отдельно от экзамена и учитывает mastery, число уверенно запомненных ключей и точность экзаменов.

## Что уже есть

- Авторизация по email/password.
- Роли `user` и `admin`.
- База из 214 ключей.
- Русские описания, мнемоники, варианты формы, похожие ключи и примеры в иероглифах.
- Адаптивная тренировка с отложенным переходом: после ответа символ остается на экране до `Space`, стрелок или кнопки `Далее`.
- Экзамен на 20 вопросов: результат отображается как `N/20`, разбор появляется после завершения.
- Панель прогресса с общим score `/10`.
- Светлая и темная тема.
- Адаптивный UI для desktop, tablet и mobile.
- Админка контента.
- Docker Compose и локальный установщик.

## Стек

- Backend: FastAPI, SQLAlchemy 2, Pydantic, JWT auth.
- Frontend: Vite, React, TypeScript, TanStack Query, lucide-react.
- Data: PostgreSQL в Docker, SQLite для локального режима.
- Infra: Docker Compose.

## Быстрый запуск одной командой

Рекомендуемый способ - Docker Compose:

```bash
git clone https://github.com/Zeed80/china-key-learning.git
cd china-key-learning
./scripts/install.sh --docker
```

После запуска:

- Frontend: http://localhost:5173
- Backend: http://localhost:8001
- Admin login: `admin@example.com`
- Admin password: `admin12345`

Для собственного пароля администратора:

```bash
ADMIN_EMAIL="you@example.com" ADMIN_PASSWORD="change-this-password" ./scripts/install.sh --docker
```

## Автозапуск после перезагрузки сервера

Для постоянного сервера используйте Docker-режим с systemd-автозапуском:

```bash
ADMIN_EMAIL="you@example.com" ADMIN_PASSWORD="change-this-password" SECRET_KEY="change-this-secret" ./scripts/install.sh --docker --autostart
```

Если приложение открывается с другого устройства в сети, передайте IP сервера:

```bash
HOST_IP=192.168.1.246 ADMIN_EMAIL="you@example.com" ADMIN_PASSWORD="change-this-password" SECRET_KEY="change-this-secret" ./scripts/install.sh --docker --autostart
```

Что это делает:

- добавляет Docker restart policy `unless-stopped` для PostgreSQL, Redis, backend и frontend;
- создает `.runtime/docker.env` с параметрами запуска;
- устанавливает и включает systemd-unit `china-key-learning.service`;
- при reboot systemd заново выполнит `docker compose -f infra/docker-compose.yml --env-file .runtime/docker.env up -d`.

Проверить автозапуск:

```bash
systemctl status china-key-learning.service
docker compose -f infra/docker-compose.yml ps
```

Отключить автозапуск:

```bash
sudo systemctl disable --now china-key-learning.service
```

## Локальный запуск без Docker

Установщик создаст Python virtualenv, поставит backend-зависимости, выполнит `npm ci`, соберет frontend, засеет базу и запустит dev-серверы:

```bash
./scripts/install.sh --local
```

По умолчанию:

- Backend: http://localhost:8001
- Frontend: http://localhost:5173
- SQLite база: `backend/dev.sqlite3`
- Логи: `.runtime/backend.log`, `.runtime/frontend.log`

Если приложение открывается с другого устройства в сети, передайте IP хоста:

```bash
HOST_IP=192.168.1.246 ./scripts/install.sh --local
```

Можно только установить зависимости и засеять базу без запуска серверов:

```bash
./scripts/install.sh --local --no-start
```

## Ручной запуск backend

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.db.seed --admin-email admin@example.com --admin-password admin12345
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Ручной запуск frontend

```bash
cd frontend
npm ci
VITE_API_URL=http://localhost:8001 npm run dev -- --host 0.0.0.0 --port 5173
```

## Docker Compose вручную

```bash
ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=admin12345 docker compose -f infra/docker-compose.yml up --build
```

Остановить:

```bash
docker compose -f infra/docker-compose.yml down
```

Удалить также PostgreSQL volume:

```bash
docker compose -f infra/docker-compose.yml down -v
```

## Основные сценарии

### 1. Обзор ключей

Откройте `Ключи`. Можно листать стрелками влево/вправо. На карточке показываются:

- крупный глиф;
- номер и число черт;
- краткий смысл;
- мнемоника;
- похожие формы с подсветкой отличий;
- примеры и предложения.

### 2. Тренировка

Откройте `Тренировка`, выберите ответ. После ответа:

- символ остается на экране;
- выбранный и правильный ответы подсвечиваются;
- объяснение относится именно к текущему символу;
- переход дальше делается кнопкой `Далее`, `Space` или стрелками.

### 3. Экзамен

Откройте `Экзамен` и ответьте на 20 вопросов. Во время экзамена правильные ответы не показываются. После завершения появится:

- результат `N/20`;
- список вопросов;
- ваш ответ;
- правильный ответ;
- список слабых ключей для повторения.

### 4. Админка

Администратор может редактировать:

- значения RU/EN;
- описание;
- мнемонику;
- usage;
- варианты формы;
- примеры;
- похожие формы.

## Проверки качества

Backend:

```bash
cd backend
python3 -m pytest -q
python3 -m app.db.content_audit
```

Frontend:

```bash
cd frontend
npm run build
npm run test
npm audit
```

Content audit должен возвращать примерно:

```text
{'radicals': 214, 'examples': 428, 'confusables': 214, 'fallback_examples': 0}
```

## Структура проекта

```text
backend/              FastAPI backend
  app/api/            API endpoints
  app/db/             session, seed, content audit
  app/models/         SQLAlchemy models
  app/schemas/        Pydantic contracts
  app/services/       learning/training/exam logic
frontend/             React/Vite frontend
  src/components/     shared UI components
  src/pages/          screens
  src/styles/         CSS design system
infra/                Docker Compose
scripts/install.sh    one-command installer
docs/                 design and learning notes
```

## Важные замечания

- Проект находится в активной разработке, API и схема данных могут меняться.
- Fallback-глифы сейчас генерируются как SVG с CJK font text. Для production-качества графики следующим шагом стоит подключить настоящие stroke-order/vector assets.
- Дефолтный пароль `admin12345` подходит только для локальной разработки. Для публичного сервера обязательно задайте `ADMIN_PASSWORD` и `SECRET_KEY`.

## Лицензирование контента

Базовые ключи и учебные описания находятся внутри проекта. Для будущего подключения внешних stroke-order assets нужно отдельно проверить лицензию источника данных.
