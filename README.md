# Coderr Backend

A Django REST Framework backend for a freelance marketplace platform where business users can offer services and customers can order and review them.

## Tech Stack

- Python 3.12
- Django 6.0
- Django REST Framework 3.16
- PostgreSQL (via Docker)
- Token Authentication
- Gunicorn + Nginx

## Getting Started (Docker)

### 1. Clone the repository

```bash
git clone <repository-url>
cd coderr
```

### 2. Set up environment variables

```bash
cp .env.docker .env
```

Edit `.env` and set `SECRET_KEY` and `DB_PASSWORD`.

### 3. Start the containers

```bash
docker compose up --build
```

Migrations and static file collection run automatically on startup.
The API is available at `http://localhost:8000/api/`

### 4. Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### Useful commands

```bash
# Stop containers
docker compose down

# View logs
docker compose logs web
docker compose logs db

# Reset database completely
docker compose down -v
docker compose up -d --build

# Flush data only (keep schema)
docker compose exec web python manage.py flush --noinput

# Run tests
docker compose exec web python manage.py test
```

## API Endpoints

### Auth

| Method | Endpoint             | Description             |
| ------ | -------------------- | ----------------------- |
| POST   | `/api/registration/` | Register a new user     |
| POST   | `/api/login/`        | Login and receive token |

### Profiles

| Method | Endpoint                  | Description                |
| ------ | ------------------------- | -------------------------- |
| GET    | `/api/profile/<user_id>/` | Get profile                |
| PATCH  | `/api/profile/<user_id>/` | Update own profile         |
| GET    | `/api/profiles/business/` | List all business profiles |
| GET    | `/api/profiles/customer/` | List all customer profiles |

### Offers

| Method | Endpoint                  | Description                  |
| ------ | ------------------------- | ---------------------------- |
| GET    | `/api/offers/`            | List all offers (public)     |
| POST   | `/api/offers/`            | Create offer (business only) |
| GET    | `/api/offers/<id>/`       | Get single offer             |
| PATCH  | `/api/offers/<id>/`       | Update offer (creator only)  |
| DELETE | `/api/offers/<id>/`       | Delete offer (creator only)  |
| GET    | `/api/offerdetails/<id>/` | Get single offer detail      |

### Orders

| Method | Endpoint                                         | Description                    |
| ------ | ------------------------------------------------ | ------------------------------ |
| GET    | `/api/orders/`                                   | List own orders                |
| POST   | `/api/orders/`                                   | Create order (customer only)   |
| PATCH  | `/api/orders/<id>/`                              | Update order status (business) |
| DELETE | `/api/orders/<id>/`                              | Delete order (admin only)      |
| GET    | `/api/order-count/<business_user_id>/`           | Count in-progress orders       |
| GET    | `/api/completed-order-count/<business_user_id>/` | Count completed orders         |

### Reviews

| Method | Endpoint             | Description                   |
| ------ | -------------------- | ----------------------------- |
| GET    | `/api/reviews/`      | List all reviews              |
| POST   | `/api/reviews/`      | Create review (customer only) |
| PATCH  | `/api/reviews/<id>/` | Update own review             |
| DELETE | `/api/reviews/<id>/` | Delete own review             |

### Statistics

| Method | Endpoint          | Description                  |
| ------ | ----------------- | ---------------------------- |
| GET    | `/api/base-info/` | Platform statistics (public) |

## Frontend

The frontend was provided by the [Developer Akademie](https://github.com/Developer-Akademie-Backendkurs/project.Coderr.git) as part of the backend course. Forked and included under `frontend/`, served via Nginx on the same VPS.

## Authentication

Token-based authentication. Include the token in every request header:

```http
Authorization: Token <your-token>
```

Tokens are returned on registration and login.

## User Types

- **Business** – can create offers and update order status
- **Customer** – can create orders and write reviews

## Production

Deployed on an IONOS VPS (Ubuntu 24.04):

- API: <https://api.mohamed-touzani.de/api/>
- Frontend: <https://coderr.mohamed-touzani.de>
- Nginx as reverse proxy with HTTPS (Let's Encrypt)
- PostgreSQL data persisted in a Docker volume
