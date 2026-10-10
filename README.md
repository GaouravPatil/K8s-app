# Simple Flask + Postgres API

Minimalistic Python app with 3 APIs + health check.

## APIs

| Method | Endpoint      | Description       |
|--------|---------------|-------------------|
| GET    | `/`           | Health check      |
| POST   | `/users`      | Create a user     |
| GET    | `/users`      | List all users    |
| GET    | `/users/<id>` | Get one user      |

## Setup

1. Make sure Postgres is running and create DB:

```bash
createdb demo_db
# or: psql -U postgres -c "CREATE DATABASE demo_db;"
```

2. Install deps:

```bash
pip install -r requirements.txt
cp .env.example .env   # edit password if needed
```

3. Run:

```bash
python app.py
```

Table `users` is auto-created on startup.

## Test with curl

```bash
# health
curl http://localhost:5000/

# create
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Aarav","email":"aarav@example.com"}'

# list
curl http://localhost:5000/users

# get one
curl http://localhost:5000/users/1
```
# K8s-app
