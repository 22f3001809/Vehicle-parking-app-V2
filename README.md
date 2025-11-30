# ParkNxtV2

This is a Vehicle Parking Management System built using Flask, Vue.js, SQLite and Redis for caching and task scheduling. It allows users to book parking spots, check-in/check-out, and provides admin with tools to manage parking lots and view analytics.

## Project Structure

```
Vehicle-parking-app-V2/
├── backend/                          # Flask API server
│   ├── app.py                       # Main Flask application
│   ├── models.py                    # Database models (User, ParkingLot, Reservation, etc.)
│   ├── config.py                    # Configuration settings
│   ├── requirements.txt             # Python dependencies
│   ├── cache_config.py              # Redis caching configuration
│   ├── celery_app.py                # Celery task queue setup
│   ├── routes/                      # API route blueprints
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── user.py                 # User/regular user endpoints
│   │   └── admin.py                # Admin-only endpoints
│   ├── tasks/                       # Celery background tasks
│   │   ├── daily_reminders.py      # Daily reminder notifications
│   │   ├── monthly_report.py       # Monthly revenue reports
│   │   ├── email.py                # Email sending tasks
│   │   ├── csv_export.py           # CSV export tasks
│   │   └── gchat_notifications.py  # Google Chat notifications
│   └── utils/                       # Utility functions
│       ├── admin_setup.py          # Admin user initialization
│       └── cache_utils.py          # Cache invalidation utilities
│
├── frontend/                         # Vue 3 + Vite application
│   ├── src/
│   │   ├── App.vue                 # Root component
│   │   ├── main.js                 # Application entry point
│   │   ├── router/                 # Vue Router configuration
│   │   ├── store/                  # Vuex state management
│   │   │   ├── modules/
│   │   │   │   ├── auth.js        # Auth state
│   │   │   │   ├── admin.js       # Admin state
│   │   │   │   └── parking.js     # Parking state
│   │   │   └── index.js            # Store setup
│   │   ├── services/               # API service layer
│   │   │   └── api.js             # Axios API client
│   │   ├── components/             # Vue components
│   │   │   ├── NavBar.vue
│   │   │   ├── AppFooter.vue
│   │   │   ├── AlertMessage.vue
│   │   │   ├── LoadingOverlay.vue
│   │   │   └── CheckoutModal.vue
│   │   ├── views/                  # Page components
│   │   │   ├── Home.vue
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Profile.vue
│   │   │   ├── admin/              # Admin pages
│   │   │   └── user/               # User pages
│   │   ├── assets/                 # Static assets
│   │   │   └── styles/             # Global CSS
│   │   └── utils/                  # Utility functions
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── api-definition.yaml              # OpenAPI/Swagger specification
```

## Features

### User Features
-  User registration and authentication with JWT
-  Browse available parking lots with search functionality
-  Real-time parking spot availability
-  One-click parking spot booking
-  Check-in/Check-out with automatic cost calculation
-  Reservation history and filtering by status
-  Profile management with password change
-  Export parking history as CSV

### Admin Features
-  Admin dashboard with comprehensive statistics
-  Create, update, and delete parking lots
-  Manage parking spots dynamically
-  View all users and their reservation history
-  Monitor all reservations and spot occupancy
-  Daily revenue and booking reports (7-day overview)
-  Spot usage history and analytics
-  Cache management for performance optimization

### System Features
-  JWT-based authentication and authorization
-  Redis caching for improved performance
-  Celery task queue for background jobs
-  Email notifications via Gmail SMTP
-  Google Chat integration for alerts
-  Automatic daily reminders
-  Monthly revenue reports
-  Comprehensive error handling

## Tech Stack

### Backend
- **Frontend**: Vue.js 3, Vuex, Bootstrap 5

- **Backend**: Flask (Python)

- **Database**: SQLite (SQLAlchemy)

- **Authentication**: Flask-JWT-Extended

- **Async Tasks**: Celery, Redis


##  Installation

### 1. Clone the Repository
```bash
git clone https://github.com/22f3001809/Vehicle-parking-app-V2.git
cd Vehicle-parking-app-V2
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```
### Start Redis Server
```bash
redis-server
```

### Start Backend
```bash
cd backend
source venv/bin/activate 
python app.py
```

The Flask API will start on `http://localhost:5000`

### Start Frontend
```bash
cd frontend
npm run dev
```

The Vue application will start on `http://localhost:5173`

### Start Celery Worker
```bash
cd backend
celery -A celery_app worker -l info
```

### Start Celery Beat (for scheduled tasks)
```bash
cd backend
celery -A celery_app beat -l info
```

## API Documentation

A comprehensive OpenAPI/Swagger specification is available in `api-definition.yaml`. 

### API Endpoints

**Auth:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

**User:**
- `GET /api/user/parking-lots` - Get available parking lots
- `POST /api/user/parking-lots/{lot_id}/book` - Book a parking spot
- `POST /api/user/reservations/{id}/checkin` - Check in
- `POST /api/user/reservations/{id}/release` - Check out
- `GET /api/user/reservations` - View your reservations
- `GET /api/user/profile` - Get profile
- `PUT /api/user/profile` - Update profile
- `POST /api/user/export-csv` - Export history

**Admin:**
- `GET /api/admin/dashboard` - Admin dashboard stats
- `GET /api/admin/parking-lots` - Get all parking lots
- `POST /api/admin/parking-lots` - Create parking lot
- `GET /api/admin/users` - Get all users
- `GET /api/admin/reservations` - Get all reservations

See `openapi.yaml` for complete endpoint documentation with request/response schemas.
