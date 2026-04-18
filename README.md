# Billing App - Django Project

## 1. Project Overview
- Django-based billing/invoicing system
- Features: Product management, Billing, Invoice email, Purchase history

## 2. Prerequisites
- Python 3.8+
- Redis (for Celery - optional, runs synchronously with EAGER mode)

## 3. Installation

### Create & Activate Virtual Environment
python -m venv venv
Windows: venv\Scripts\activate
Linux/Mac: source venv/bin/activate

### Install Dependencies
pip install -r requirements.txt

### Database Setup

python manage.py migrate python manage.py createsuperuser

### Seed Sample Products (Optional)
python manage.py seed_products

## 4. Running the Application
python manage.py runserver

- Access admin: http://localhost:8000/admin
- Access billing: http://localhost:8000/billing/

## 5. Email Configuration (Gmail SMTP)

### Generate Gmail App Password
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Search "App Passwords" → Create new
4. Copy the 16-char password

### Update settings.py
Edit `billing_project/settings.py`:
- Line 65: EMAIL_HOST_USER = "your-email@gmail.com"
- Line 66: EMAIL_HOST_PASSWORD = "xxxx xxxx xxxx xxxx" (16-char App Password)


## 6. Project Structure
- billing/               - Main Django app
  - models.py            - Purchase, PurchaseItem, Product models
  - views.py            - API endpoints for billing
  - tasks.py            - Celery task for invoice email
  - urls.py             - URL routing
- billing_project/      - Django project settings
  - settings.py         - Configuration (email, celery, db)
  - celery.py           - Celery app setup

## 7. Features Usage
- Add products via admin (/admin)
- Create purchase via billing UI (/billing/)
- Invoice auto-emailed to customer
- View purchase history (/billing/history/)

## 8. Troubleshooting
- Email not sending → Check App Password, enable 2-Step Verification
- Silent failures → Check Django logs
- Redis not needed → CELERY_TASK_ALWAYS_EAGER=True runs synchronously