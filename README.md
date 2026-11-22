## Shoppy
Shoppy is an e-commerce web app that allows you to operate as a vendor or buyer.

## Installation
-1. Clone the Repository
-2. Create a Virtual Environment and Activate It
-python -m venv venv
-venv\Scripts\activate
-3. Install the Required Dependencies
-pip install -r requirements.txt

## Configuration
-Make your own .env file
-Example
-DB_NAME=shoppy_db
-DB_USER=User
-DB_PASSWORD=choose_a_password
-DB_HOST=localhost
-DB_PORT=3306

-Open .env and replace the placeholder values with your actual configuration — in particular, -set a secure password for DB_PASSWORD.

## Database Setup
-1. Create the MySQL Database and User
-Log into MySQL as root (or an admin user) and run:
-sqlCREATE DATABASE shoppy_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-CREATE USER 'shoppy_db'@'localhost' IDENTIFIED BY 'choose_a_password';
-GRANT ALL PRIVILEGES ON shoppy_db.* TO 'shoppy_db'@'localhost';
-FLUSH PRIVILEGES;
-EXIT;

-Replace choose_a_password with the same password you set in your .env file.

-2. Run Migrations
-python manage.py makemigrations
-Apply all migrations to create the database tables from the models:
-python manage.py migrate
-3. Create a Superuser (Admin Account)
-python manage.py createsuperuser
-Set up an admin account for the Django admin panel and user authentication:
-You will be prompted to enter a username, email address, and password.

## Twitter setup
-1. **Twitter Developer Account**: You'll need a Twitter Developer account. If you don't have one, sign up at [developer.twitter.com](https://developer.twitter.com)
-2. Set your own Key and Secret
-CONSUMER_KEY = 'your_actual_consumer_key'  # Replace 'your_key'
-CONSUMER_SECRET = 'your_actual_consumer_secret'  # Replace 'your_secret'

## Running the App
-Start the development server:
-python manage.py runserver
-The app will be available at http://127.0.0.1:8000.
-The Django admin panel is available at http://127.0.0.1:8000/admin.