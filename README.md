# VIKMO Python/Django Intern Assignment

## Overview

This project implements a Sales Order & Inventory Management System for an auto-parts distributor.

The system supports:

* Product management
* Inventory management
* Dealer management
* Order management
* Stock validation
* Inventory deduction
* Order lifecycle management
* Channel synchronization

Built using:

* Python
* Django
* Django REST Framework
* SQLite

---

## Features

### Product Management

* Create products
* Update products
* Delete products
* Search using unique SKU

### Inventory Management

* One inventory record per product
* Manual inventory adjustments supported

### Dealer Management

* Dealer creation and management
* Multiple orders per dealer

### Order Management

* Draft → Confirmed → Delivered workflow
* Auto-generated order numbers
* Order item management
* Historical pricing preservation

### Stock Validation

* Prevents ordering more than available stock
* Returns validation errors when stock is insufficient

### Concurrency Protection

* Uses transaction.atomic()
* Uses select_for_update()
* Prevents overselling under concurrent requests

### Auto Calculations

* line_total = quantity × unit_price
* total_amount = sum of all line totals

### Channel Sync

* Imports products from channel_feed.json
* Creates new products
* Updates existing products
* Updates inventory quantities
* Idempotent sync

---

## Setup

### Create Virtual Environment

python -m venv venv

### Activate Environment

Windows:

venv\Scripts\activate

### Install Dependencies

pip install -r requirements.txt

### Run Migrations

python manage.py migrations

python manage.py migrate

### Start Server

python manage.py runserver

---

## API Endpoints

### Products

GET /api/products/

POST /api/products/

### Dealers

GET /api/dealers/

POST /api/dealers/

### Inventory

GET /api/inventory/

POST /api/inventory/

### Orders

GET /api/orders/

POST /api/orders/

### Confirm Order

POST /api/orders/{id}/confirm/

### Deliver Order

POST /api/orders/{id}/deliver/

### Channel Sync

POST /api/sync/channel/

---

## Design Decisions

See DESIGN.md for detailed explanations of:

* Database relationships
* Concurrency strategy
* Locking strategy
* Channel synchronization
* Conflict resolution

# Sync products
curl.exe -X POST http://127.0.0.1:8000/api/sync/channel/

# Confirm order
curl.exe -X POST http://127.0.0.1:8000/api/orders/10/confirm/

# Deliver order
curl.exe -X POST http://127.0.0.1:8000/api/orders/10/deliver/

## Running Tests

The API was manually tested using:

- Django REST Framework Browsable API
- curl commands

Scenarios tested:

- Successful order flow
- Insufficient stock validation
- Invalid status transitions
- Channel sync idempotency

## Database

Database used: SQLite

Migration files are included in the repository.

## Example Requests

### Confirm Order

Request:

```bash
curl.exe -X POST http://127.0.0.1:8000/api/orders/10/confirm/
```

Response:

```json
{
  "message": "Order confirmed successfully"
}
```

### Channel Sync

Request:

```bash
curl.exe -X POST http://127.0.0.1:8000/api/sync/channel/
```

Response:

```json
{
  "created": 0,
  "updated": 200
}
```

## Repository

GitHub Repository:
https://github.com/Anas1125/Anas_Mohamed_Sali_VIKMO_Assignment
