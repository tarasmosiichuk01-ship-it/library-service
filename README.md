# Library service API

API service for library management written on DRF

## Running with Docker

1. Clone the repository git clone https://github.com/tarasmosiichuk01-ship-it/library-service.git
2. cd library-service
3. Create `.env` file based on `.env.example`
4. Run the following command:

```bash
docker-compose up --build
```

## Running locally (without Docker)

1. Clone the repository git clone https://github.com/tarasmosiichuk01-ship-it/library-service.git
2. cd library-service
3. Create `.env` file based on `.env.example`
4. Run the following commands:

```bash
pip install -r requirements.txt
python manage.py migrate
docker run -d -p 6379:6379 redis
celery -A library_service worker --loglevel=info --pool=solo
celery -A library_service beat --loglevel=info
python manage.py runserver
```

## Getting access

- create user via /api/user/users/
- get access token via /api/user/users/token/

## Running tests

Run all tests:
```bash
python manage.py test
```

## Features

- JWT authentication for secure access
- Book management (CRUD operations for admins)
- Borrowing system with inventory tracking
- Online payments via Stripe
- Automatic fine calculation for overdue borrowings
- Telegram notifications for administrators:
  - New borrowing created
  - Overdue borrowings (daily check)
  - Successful payment
- Background tasks via Celery + Redis
- API documentation via Swagger