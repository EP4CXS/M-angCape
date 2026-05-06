
A complete Food Ordering System built with Django (Python) that follows **Object-Oriented Programming (OOP)** principles and the **MVC (Model-View-Controller)** architectures.

## Features

- **Shopping Cart** with add/remove/update functionality
- **Order Management** with status tracking
- **Admin Dashboard** with order statistics

## Installation

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  
   ```

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

## License

This project is for educational purposes.

