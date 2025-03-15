# MoneyBees 🐝💰
## Personal Finance Management Web Application

MoneyBees is a web-based personal finance management application that helps users track income and expenses, set monthly spending targets, and receive reminders for upcoming payments. It supports multi-currency transactions with real-time conversion and provides interactive financial insights through charts.

---

## Features

### 1️⃣ User Management
- Secure User Authentication (Email & Google Login)
- Password recovery via email verification

### 2️⃣ Expense & Income Tracking
- Add, edit, and delete income & expense transactions
- Transactions categorized for better financial tracking
- Filter records by date range and category

### 3️⃣ Multi-Currency Support
- Select a default currency
- Record transactions in different currencies
- Real-time currency conversion via Exchange Rates API

### 4️⃣ Budget & Financial Insights
- Pie charts for category-wise spending overview
- Bar charts for monthly income vs. expenses trend
- Set monthly expense targets per category & track progress

### 5️⃣ Automated Reminders & Notifications
- Set upcoming payments (e.g., loans, rent, bills)
- Email alerts 3 days before due dates

---

## Getting Started

### 1️⃣ Prerequisites
Before installing MoneyBees, ensure you have the following:

- Python 3.8+ installed
- Django 4.0+ installed
- A working SQLite database (or PostgreSQL for production)
- An Exchange Rates API key for currency conversion

### 2️⃣ Installation Steps

1. Clone the Repository: git clone https://stgit.dcs.gla.ac.uk/3004805p/moneybees.git 
2. Set Up Virtual Environment: python -m venv venv source venv/bin/activate
3. Install Dependencies: pip install -r requirements.txt
4. Set Up Database: python manage.py migrate
5. Create Superuser (For Admin Access): python manage.py createsuperuser
6. Run Development Server: python manage.py runserver



Now, visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to access MoneyBees!

---

## Usage Guide

### 1️⃣ User Login & Registration
- Sign up using email & password
- Google Sign-In option available
- Reset password using email verification

### 2️⃣ Managing Expenses & Income
- Navigate to "Add Expense" or "Add Income" page
- Fill in the amount, category, currency, and date
- Click **Save** to record the transaction

### 3️⃣ Setting Monthly Expense Targets
- Go to "Monthly Expense Target"
- Select a category and enter a target amount
- Track spending progress via progress bars

### 4️⃣ Viewing Financial Insights
- **Pie Chart**: Breakdown of expenses per category
- **Bar Graph**: Monthly income vs. expenses trend

### 5️⃣ Scheduling Upcoming Payments
- Add future payment reminders (e.g., rent, bills)
- Email notifications are sent 3 days before the due date

---

## System Architecture

### 🗄️ Backend
- **Django**: Python web framework
- **SQLite**: Default database (use PostgreSQL for production)
- **Django ORM**: For database management

### 🌍 Frontend
- **HTML**, **CSS**, **JavaScript**, **AJAX**
- **Chart.js**: For interactive charts and visualizations

### 🔗 API Integrations
- **Google OAuth 2.0**: For Google Login
- **Exchange Rates API**: For real-time currency conversion


