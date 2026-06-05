# 📘 Contacts API — FastAPI + Auth + JWT + Avatars

REST API для керування контактами з підтримкою аутентифікації, авторизації (JWT), аватарів користувачів (Cloudinary), CORS та обмеження запитів.  
Проєкт реалізовано на FastAPI, SQLAlchemy, SQLite/PostgreSQL (через Docker) та підтримує повний набір CRUD‑операцій, пошук і перевірку найближчих днів народження.

## 🚀 Функціонал

### Контакти

- Створення контакту
- Отримання списку всіх контактів поточного користувача
- Отримання контакту за ID (лише свого)
- Оновлення контакту
- Видалення контакту
- Пошук за ім’ям, прізвищем або email
- Виведення контактів, у яких день народження в найближчі 7 днів

### Користувачі та безпека

- Реєстрація користувача з перевіркою унікальності email
- Хешування пароля (пароль не зберігається у відкритому вигляді)
- Логін і отримання `access_token` (JWT)
- Авторизація через заголовок `Authorization: Bearer <token>`
- Доступ до контактів лише свого користувача
- Верифікація email через лист на реальну пошту
- Обмеження кількості запитів до `/users/me` (rate limiting)
- Оновлення аватара користувача (Cloudinary)
- Увімкнений CORS для REST API (для фронтенду на іншому домені/порті)

## 🛠 Технології

- Python 3.10+
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- SQLite / PostgreSQL (через Docker)
- Alembic (міграції)
- JWT (`python-jose`)
- Passlib (хешування паролів)
- Cloudinary (зберігання аватарів)
- Redis / slowapi (rate limiting, якщо використовується)
- Docker, Docker Compose

## 🔐 Аутентифікація, авторизація та email

### Реєстрація користувача

> ⚠ Потрібно використовувати реальний email, щоб отримати лист для верифікації.

```bash
curl -X POST \
  'http://127.0.0.1:8000/auth/signup' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "your_email@gmail.com",
    "password": "YourStrongPass123"
  }'
```

- Якщо користувач з таким email вже існує → `409 Conflict`
- У разі успіху → `201 Created` + дані користувача

### Логін (отримання JWT токена)

```bash
curl -X POST \
  'http://127.0.0.1:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "your_email@gmail.com",
    "password": "YourStrongPass123"
  }'
```

Приклад відповіді:

```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

### Поточний користувач `/users/me` (з rate limit)

```bash
curl -X GET \
  'http://127.0.0.1:8000/users/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

- Повертає дані поточного користувача
- Має обмеження кількості запитів (rate limiting)

### Верифікація email

- Після реєстрації на email надсилається лист із посиланням/токеном
- Користувач переходить за посиланням → `email` вважається підтвердженим (`is_verified = true`)
- Якщо використовується окремий endpoint типу `/auth/verify/{token}`, його можна описати у Swagger / OpenAPI

## 🖼 Аватар користувача (Cloudinary)

### Налаштування Cloudinary

У `.env` мають бути змінні (приклад):

```env
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>  # замінити плейсхолдери на реальні значення
```

### Оновлення аватара

```bash
curl -X PATCH \
  'http://127.0.0.1:8000/users/avatar' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -F 'file=@/path/to/avatar.png;type=image/png'
```

Приклад відповіді:

```json
{
  "avatar": "https://res.cloudinary.com/<cloud_name>/image/upload/.../user_17.png"
}
```

## 🌐 CORS

У застосунку увімкнено CORS, що дозволяє фронтенду (React, Vue тощо) звертатися до API з іншого домену/порту.  
Налаштовуються `allow_origins`, `allow_methods`, `allow_headers` відповідно до потреб клієнта.

## 📦 Установка та запуск (локально)

### Клонування репозиторію

```bash
git clone https://github.com/<your-username>/UMT-pythonweb-hw-11.git
cd UMT-pythonweb-hw-11
```

### Створення віртуального середовища

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### Встановлення залежностей

```bash
pip install -r requirements.txt
```

### Створення файлу `.env` (приклад)

```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

DATABASE_URL=sqlite+aiosqlite:///./contacts.db
# або PostgreSQL через Docker:
# DATABASE_URL=postgresql+psycopg2://user:password@db:5432/contacts

CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

### Запуск сервера

```bash
uvicorn app.main:app --reload
```

API:  
http://127.0.0.1:8000  

Swagger (документація):  
http://127.0.0.1:8000/docs

## 🐳 Запуск через Docker Compose

```bash
docker compose up --build
```

- Піднімається API
- Піднімається база (якщо використовується PostgreSQL)
- Усі секрети та конфіг беруться з `.env`

## 📚 Ендпоінти контактів (з авторизацією)

Усі запити нижче вимагають заголовок:

```http
Authorization: Bearer <JWT_TOKEN>
```

### ➤ POST `/contacts` — створити контакт

```bash
curl -X POST \
  'http://127.0.0.1:8000/contacts' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+3801234567",
    "birthday": "2000-06-02",
    "extra": "notes"
  }'
```

### ➤ GET `/contacts` — отримати всі контакти поточного користувача

```bash
curl -X GET \
  'http://127.0.0.1:8000/contacts' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

### ➤ GET `/contacts/{contact_id}` — отримати контакт за ID

```bash
curl -X GET \
  'http://127.0.0.1:8000/contacts/1' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

### ➤ PUT `/contacts/{contact_id}` — оновити контакт

```bash
curl -X PUT \
  'http://127.0.0.1:8000/contacts/1' \
  -H 'Authorization: Bearer <JWT_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "last_name": "Updated"
  }'
```

### ➤ DELETE `/contacts/{contact_id}` — видалити контакт

```bash
curl -X DELETE \
  'http://127.0.0.1:8000/contacts/1' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

### ➤ GET `/contacts/search` — пошук за полями

Параметри (усі необов’язкові):

- `first_name`
- `last_name`
- `email`

```bash
curl -X GET \
  "http://127.0.0.1:8000/contacts/search?first_name=Malva" \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

### ➤ GET `/contacts/birthdays` — дні народження у найближчі 7 днів

```bash
curl -X GET \
  'http://127.0.0.1:8000/contacts/birthdays' \
  -H 'Authorization: Bearer <JWT_TOKEN>'
```

## 🗂 Структура проєкту

```text
app/
 ├── main.py        # Точка входу FastAPI
 ├── models.py      # SQLAlchemy моделі
 ├── schemas.py     # Pydantic-схеми
 ├── crud.py        # Логіка доступу до даних (CRUD)
 ├── database.py    # Підключення до БД
 ├── auth/          # Аутентифікація, JWT, залежності безпеки
 ├── routers/       # Роутери для контактів, користувачів тощо
 └── services/      # Email, Cloudinary, rate limiting та інші сервіси
```

---
