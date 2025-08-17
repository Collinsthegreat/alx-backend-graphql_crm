# ALX Backend GraphQL CRM

A Django-based CRM system built following modern Django development standards and best practices with
GraphQL API integration.

## Project Overview

This project demonstrates the integration of GraphQL with Django using `graphene-django`, implementing
a clean, modular architecture leveraging GraphQL's flexible querying capabilities.

---

## Features

### 1. GraphQL API

- **Query** and **mutate** data with a single endpoint
- **Strongly-typed** schema with clear input validations
- **Real-time** data fetching with subscriptions (coming soon)

### 2. Core Models

- **Customers**: Manage customer information with contact details
- **Products**: Track product inventory and pricing
- **Orders**: Handle customer orders with product associations

### 3. Advanced Features

- **Bulk Operations**: Create multiple customers in a single request
- **Data Validation**: Comprehensive input validation and error handling
- **Filtering & Sorting**: Powerful query capabilities with filtering and ordering
- **Pagination**: Efficient data loading with cursor-based pagination

## Technology Stack

- **Framework** : Django 5.2+
- **GraphQL** : graphene-django
- **Database** : PostgreSQL (recommended) / SQLite (development)
- **Python** : 3.12

---

## Project Structure

```text
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/
│   ├── __init__.py
│   ├── asgi.py
│   ├── schema.py              # GraphQL schema definition
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL configuration
│   └── wsgi.py
├── crm/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── schema.py              # CRM-specific GraphQL schema
│   ├── tests.py
│   └── views.py
├── db.sqlite3
├── manage.py
├── README.md
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**

    ```bash
    git clone [https://github.com/yourusername/alx-backend-graphql_crm.git](https://github.com/yourusername/alx-backend-graphql_crm.git)
    cd alx-backend-graphql_crm
    ```

2. Create and activate virtual environment

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install Dependencies

    ```bash
    pip install -r requirements.txt
    ```

4. Configure environment variables

    ```bash
    cp .env.example .env
    # Edit .env with your configuration
    ```

5. Run Migrations

    ```bash
    python manage.py makemigrations
    python manage.py migrate

6. Create superuser (optional)

    ```bash
    python manage.py createsuperuser
    ```

7. Start Development Server

    ```bash
    python manage.py runserver
    ```

8. Access GraphiQL interface

    ```bash
    http://localhost:8000/graphql/
    ```

---

## API Documentation

### Example Queries

#### Get all customers

```graphql
{
  allCustomers {
    edges {
      node {
        id
        name
        email
        phone
      }
    }
  }
}
```

#### Filter products by price range

```graphql
{
  allProducts(filter: { priceGte: 100, priceLte: 1000 }) {
    edges {
      node {
        id
        name
        price
        stock
      }
    }
  }
}
```

### Example Mutations

#### Create a new customer

```graphql
mutation {
  createCustomer(input: {
    name: "John Doe",
    email: "<john@example.com>",
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
    }
    message
    success
  }
}
```

#### Create a new order

```graphql
mutation {
  createOrder(input: {
    customerId: "1",
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
    }
    message
    success
  }
}
```

### Filtering Capabilities

#### Customers

- Filter by name (case-insensitive)
- Filter by email (case-insensitive)
- Filter by creation date range
- Filter by phone number pattern

#### Products

- Filter by name (case-insensitive)
- Filter by price range
- Filter by stock level
- Find low stock items

#### Orders

- Filter by total amount range
- Filter by order date range
- Filter by customer name
- Filter by product name or ID

### Development

#### Running Tests

```bash
python manage.py test
```

---

## Testing the Setup

### 1. Accessing GraphQL

1. **GraphiQL Interface** : Visit <http://localhost:8000/graphql/>
2. **GraphQL Endpoint** : `POST` requests to <http://localhost:8000/graphql/>

### 2. Run Your First Query

In the GraphiQL interface, run:

```graphql
{
  hello
}
```

Expected response:

```json
{
  "data": {
    "hello": "Hello, GraphQL!"
  }
}
```

### CRM Status Query

```graphql
{
  crmStatus
}
```

Expected response:

```json
{
  "data": {
    "crmStatus": "CRM module is ready for GraphQL operations"
  }
}
```

---

## License

This project is developed for educational purposes as part of the ALX Software Engineering Backend
Specialization program.

---
