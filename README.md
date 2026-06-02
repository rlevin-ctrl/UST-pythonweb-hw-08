# 📘 Contacts API — FastAPI Application

REST API для керування контактами.  
Проєкт реалізовано на FastAPI, SQLAlchemy, SQLite та підтримує повний набір CRUD‑операцій, пошук і перевірку найближчих днів народження. [web:2][web:7]

## 🚀 Функціонал

- Створення контакту
- Отримання списку всіх контактів
- Отримання контакту за ID
- Оновлення контакту
- Видалення контакту
- Пошук за ім’ям, прізвищем або email
- Виведення контактів, у яких день народження в найближчі 7 днів

## 🛠 Технології

- Python 3.10+
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- SQLite [web:2][web:10]

## 📦 Установка та запуск

1. Клонування репозиторію:
   ```bash
   git clone https://github.com/<your-username>/UMT-pythonweb-hw-08.git
   cd UMT-pythonweb-hw-08
   ```

2. Створення віртуального середовища:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/Mac
   .venv\Scripts\activate      # Windows
   ```

3. Встановлення залежностей:
   ```bash
   pip install -r requirements.txt
   ```

4. Запуск сервера:
   ```bash
   uvicorn app.main:app --reload
   ```

API буде доступне за адресою:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)

Документація Swagger:  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) [web:2][web:10]

## 📚 Ендпоінти API

### ➤ POST `/contacts` — створити контакт

**Body (JSON):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+3801234567",
  "birthday": "2000-06-02",
  "extra": "notes"
}
```

### ➤ GET `/contacts` — отримати всі контакти

```bash
curl http://127.0.0.1:8000/contacts
```

### ➤ GET `/contacts/{contact_id}` — отримати контакт за ID

```bash
curl http://127.0.0.1:8000/contacts/1
```

### ➤ PUT `/contacts/{contact_id}` — оновити контакт

```bash
curl -X PUT http://127.0.0.1:8000/contacts/1 \
  -H "Content-Type: application/json" \
  -d '{"last_name": "Updated"}'
```

### ➤ DELETE `/contacts/{contact_id}` — видалити контакт

```bash
curl -X DELETE http://127.0.0.1:8000/contacts/1
```

### ➤ GET `/contacts/search` — пошук за полями

Параметри (усі необов’язкові):

- `first_name`
- `last_name`
- `email`

**Приклад:**
```bash
curl "http://127.0.0.1:8000/contacts/search?first_name=Malva"
```

### ➤ GET `/contacts/birthdays` — дні народження у найближчі 7 днів

```bash
curl http://127.0.0.1:8000/contacts/birthdays
```

## 🗂 Структура проєкту

```text
app/
 ├── main.py
 ├── models.py
 ├── schemas.py
 ├── crud.py
 ├── database.py
```