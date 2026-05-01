# 🚗 Carpooling Coordinator — DBMS Mini Project

A full-stack CRUD application built with **HTML/CSS/JS** frontend,
**FastAPI (Python)** backend, and **MySQL** database.

---

## 📁 Folder Structure

```
carpooling/
├── frontend/
│   ├── index.html      ← UI — tabs for Rides, Drivers, Riders
│   ├── style.css       ← Dark dashboard theme
│   └── app.js          ← All fetch() calls to FastAPI
│
├── backend/
│   ├── main.py         ← FastAPI app — all CRUD endpoints
│   ├── config.py       ← MySQL connection settings  ← EDIT THIS
│   └── requirements.txt
│
└── database/
    └── schema.sql      ← Create tables + insert sample data
```

---

## 🗄️ Database Schema

```
drivers  ─────────────────────────────────────
  id, name, phone, email, vehicle, license_no

riders  ──────────────────────────────────────
  id, name, phone, email

rides  ───────────────────────────────────────
  id, driver_id (FK), rider_id (FK),
  pickup_point, dropoff_point, departure_time,
  total_seats, seats_available, fare_per_seat, status
```

---

## ⚙️ Setup Instructions (Step by Step)

### Step 1 — Install Prerequisites

Make sure you have:
- **Python 3.10+** → https://python.org
- **MySQL 8+**     → https://dev.mysql.com/downloads/
- **VS Code** (or any editor)

---

### Step 2 — Set Up the Database

Open MySQL Workbench or your terminal:

```bash
mysql -u root -p
```

Then run the schema file:

```bash
mysql -u root -p < database/schema.sql
```

This will:
1. Create database `carpooling_db`
2. Create tables: `drivers`, `riders`, `rides`
3. Insert 8 sample rides with 4 drivers and 5 riders

✅ Verify: `USE carpooling_db; SHOW TABLES;`

---

### Step 3 — Configure Database Password

Open `backend/config.py` and update:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "YOUR_MYSQL_PASSWORD",   # ← change this
    "database": "carpooling_db",
}
```

---

### Step 4 — Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `fastapi`              — web framework
- `uvicorn`             — ASGI server to run FastAPI
- `mysql-connector-python` — MySQL driver
- `pydantic`            — data validation

---

### Step 5 — Start the FastAPI Server

```bash
cd backend
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✅ Test it: Open http://localhost:8000 → should show `{"message":"Carpooling Coordinator API is running 🚗"}`

✅ API Docs: Open http://localhost:8000/docs → interactive Swagger UI

---

### Step 6 — Open the Frontend

Just open the HTML file directly in your browser:

```
frontend/index.html  →  double-click or drag into Chrome/Firefox
```

> No server needed for the frontend — it runs as a plain HTML file
> and calls your FastAPI backend via fetch().

---

## 🔄 How Data Flows (Integration)

```
Browser (index.html)
   │
   │  fetch("http://localhost:8000/rides", { method: "POST", body: ... })
   ▼
FastAPI (main.py)  ←── Pydantic validates the JSON body
   │
   │  mysql.connector.connect(**DB_CONFIG)
   │  cursor.execute("INSERT INTO rides ...")
   ▼
MySQL (carpooling_db.rides)  ←── data stored permanently
   │
   └──► FastAPI returns { "message": "Ride created", "id": 9 }
         │
         └──► app.js shows ✓ success message + reloads table
```

---

## 🧪 CRUD Operations Summary

| Operation | HTTP Method | Endpoint         | SQL              |
|-----------|-------------|------------------|------------------|
| Create    | POST        | /rides           | INSERT INTO rides |
| Read      | GET         | /rides           | SELECT * FROM rides JOIN drivers |
| Update    | PUT         | /rides/{id}      | UPDATE rides SET ... WHERE id=? |
| Delete    | DELETE      | /rides/{id}      | DELETE FROM rides WHERE id=? |

Same pattern applies for `/drivers` and `/riders`.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| "API offline" in nav | Make sure `uvicorn main:app --reload` is running |
| MySQL connection error | Check password in `config.py` and that MySQL service is running |
| CORS error in browser | FastAPI already has CORS enabled for `*` — check the URL in `app.js` |
| Module not found | Run `pip install -r requirements.txt` again |
| Port 8000 in use | Use `uvicorn main:app --reload --port 8001` and update `API` in `app.js` |

---

## 📌 API Quick Reference

```
GET    /drivers           → list all drivers
POST   /drivers           → add driver
PUT    /drivers/{id}      → update driver
DELETE /drivers/{id}      → remove driver

GET    /riders            → list all riders
POST   /riders            → add rider
PUT    /riders/{id}       → update rider
DELETE /riders/{id}       → remove rider

GET    /rides             → list all rides (with JOIN)
POST   /rides             → post a new ride
PUT    /rides/{id}        → update ride
DELETE /rides/{id}        → delete ride
```
