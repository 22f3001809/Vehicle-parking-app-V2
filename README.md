# ParkNxtV2

This is a Vehicle Parking Management System built using Flask, Vue.js, SQLite and Redis for caching and task scheduling. It allows users to book parking spots, check-in/check-out, and provides admin with tools to manage parking lots and view analytics.

## Features

**User:**
- Register, login, and browse parking lots
- Search and book parking spots
- Check-in/Check-out with auto cost calculation
- View reservation history and profile management
- Export parking history as CSV

**Admin:**
- Dashboard with statistics and analytics
- Create, update, delete parking lots
- Monitor all users, reservations, and occupancy
- Daily revenue reports and revenue tracking
- Performance optimization with caching

**System:**
- JWT authentication and authorization
- Redis caching and Celery task queue
- Email and Google Chat notifications
- Automated daily reminders and monthly reports

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
