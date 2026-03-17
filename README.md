# Coderr Backend

A Django REST Framework backend for a freelance marketplace platform where business users can offer services and customers can order and review them.

## Tech Stack

- Python 3.x
- Django 6.0
- Django REST Framework 3.16
- SQLite (development)
- Token Authentication

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd coderr
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`

## API Endpoints

### Auth Endpoints

| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| POST   | `/api/registration/` | Register a new user      |
| POST   | `/api/login/`        | Login and receive token  |

### Profiles

| Method | Endpoint                    | Description                   |
| ------ | --------------------------- | ----------------------------- |
| GET    | `/api/profile/<user_id>/`   | Get profile                   |
| PATCH  | `/api/profile/<user_id>/`   | Update own profile            |
| GET    | `/api/profiles/business/`   | List all business profiles    |
| GET    | `/api/profiles/customer/`   | List all customer profiles    |

### Offers

| Method | Endpoint                    | Description                        |
| ------ | --------------------------- | ---------------------------------- |
| GET    | `/api/offers/`              | List all offers (public)           |
| POST   | `/api/offers/`              | Create offer (business only)       |
| GET    | `/api/offers/<id>/`         | Get single offer                   |
| PATCH  | `/api/offers/<id>/`         | Update offer (creator only)        |
| DELETE | `/api/offers/<id>/`         | Delete offer (creator only)        |
| GET    | `/api/offerdetails/<id>/`   | Get single offer detail            |

### Orders

| Method | Endpoint                                        | Description                      |
| ------ | ----------------------------------------------- | -------------------------------- |
| GET    | `/api/orders/`                                  | List own orders                  |
| POST   | `/api/orders/`                                  | Create order (customer only)     |
| PATCH  | `/api/orders/<id>/`                             | Update order status (business)   |
| DELETE | `/api/orders/<id>/`                             | Delete order (admin only)        |
| GET    | `/api/order-count/<business_user_id>/`          | Count in-progress orders         |
| GET    | `/api/completed-order-count/<business_user_id>/`| Count completed orders           |

### Reviews

| Method | Endpoint             | Description                  |
| ------ | -------------------- | ---------------------------- |
| GET    | `/api/reviews/`      | List all reviews             |
| POST   | `/api/reviews/`      | Create review (customer only)|
| PATCH  | `/api/reviews/<id>/` | Update own review            |
| DELETE | `/api/reviews/<id>/` | Delete own review            |

### Statistics

| Method | Endpoint          | Description                   |
| ------ | ----------------- | ----------------------------- |
| GET    | `/api/base-info/` | Platform statistics (public)  |

## Authentication

The API uses token-based authentication. Include the token in every request header:

```http
Authorization: Token <your-token>
```

Tokens are returned on registration and login.

## User Types

- **Business** – can create offers and update order status
- **Customer** – can create orders and write reviews

## Running Tests

```bash
python manage.py test
```

With coverage:

```bash
python -m coverage run manage.py test
python -m coverage report
```
