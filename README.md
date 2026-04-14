# M'angCaape - Food Ordering System

A complete Food Ordering System built with Django (Python) that follows **Object-Oriented Programming (OOP)** principles and the **MVC (Model-View-Controller)** architecture.

## Features

- **Full CRUD Operations** for Food Items and Orders
- **Shopping Cart** with add/remove/update functionality
- **Order Management** with status tracking
- **Admin Dashboard** with order statistics

## OOP Principles Demonstrated

- **Abstraction**: Abstract base classes (`BaseModel`, `BaseOrder`) for common logic
- **Encapsulation**: Protected/private attributes with helper methods (`_calculate_total()`, `_validate_cart()`)
- **Inheritance**: Child classes inherit from parent classes (`FoodItem` → `Meal`/`Drink`, `Order` → `OnlineOrder`)
- **Polymorphism**: Methods behave differently depending on the class (e.g., `calculate_price()`)

## Project Structure

```
food_ordering_system/
├── manage.py
├── settings.py              # Django settings with .env support
├── .env                     # Environment variables
├── foodapp/
│   ├── models/
│   │   ├── base_models.py   # Abstract base classes
│   │   ├── food_model.py    # FoodItem, Meal, Drink
│   │   ├── order_model.py   # Order, OrderItem, OnlineOrder
│   │   └── cart_model.py    # Cart, CartItem
│   ├── controllers/
│   │   ├── food_controller.py
│   │   ├── order_controller.py
│   │   └── cart_controller.py
│   ├── services/
│   │   ├── food_service.py
│   │   ├── order_service.py
│   │   └── cart_service.py
│   ├── templates/foodapp/
│   │   ├── base.html
│   │   ├── menu.html
│   │   ├── cart.html
│   │   ├── order_list.html
│   │   ├── order_detail.html
│   │   ├── order_form.html
│   │   ├── order_confirmation.html
│   │   ├── food_detail.html
│   │   ├── food_form.html
│   │   ├── checkout.html
│   │   └── order_statistics.html
│   └── urls.py
├── templates/
│   └── base.html           # Base template
├── static/                  # Static files
└── media/                   # Media files
```

## Prerequisites

- Python 3.8+
- MySQL Server
- pip

## Installation

1. **Clone or download the project**

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install django mysqlclient django-environ crispyforms-bootstrap4
   ```

4. **Configure Environment Variables**

   Edit the `.env` file with your MySQL credentials:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=food_ordering_db
   DB_USER=root
   DB_PASSWORD=your-password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```

5. **Create the Database**

   Log in to MySQL and create the database:
   ```sql
   CREATE DATABASE food_ordering_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run Migrations**
   ```bash
   cd food_ordering_system
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a Superuser** (optional)
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Access the Application**

   Open your browser and navigate to:
   - Main App: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Usage

### Menu & Ordering
1. Browse the menu at `/menu/`
2. Add items to your cart
3. View your cart at `/cart/`
4. Proceed to checkout at `/checkout/`
5. Place your order

### Order Management
1. View all orders at `/orders/`
2. Click on an order to view details
3. Update order status as needed

### Admin Dashboard
1. Navigate to `/orders/statistics/`
2. View order statistics and recent orders

## Key Classes and Design Patterns

### Models (MVC - Model)
- `BaseModel`: Abstract base class with common fields and soft delete
- `FoodItem`: Core food item model
- `Meal`, `Drink`: Specialized food items (inheritance)
- `Order`, `OnlineOrder`: Order models with polymorphic behavior
- `Cart`, `CartItem`: Shopping cart functionality

### Controllers (MVC - Controller)
- `FoodController`: Handles food item CRUD operations
- `OrderController`: Manages order processing
- `CartController`: Handles cart operations

### Services (Business Logic)
- `FoodService`: Business logic for food items
- `OrderService`: Business logic for orders
- `CartService`: Business logic for cart operations

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **JavaScript**: jQuery (for AJAX)
- **Environment**: django-environ

## License

This project is for educational purposes.

## Author

Built with ❤️ using Django
