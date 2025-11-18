# Vehicle Parking App V2 - Backend

Flask API with JWT authentication for the Vehicle Parking Management System.

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the App
```bash
python app.py
```

The API will run on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login and get JWT token
- `GET /api/me` - Get current user info (requires token)

### Admin Routes (requires `is_admin: true` in JWT)
- `POST /api/admin/parking-lots` - Create parking lot
- `GET /api/admin/parking-lots` - View all parking lots
- `GET /api/admin/users` - View all users

### User Routes (requires JWT token)
- `GET /api/parking-lots` - View available parking lots
- `POST /api/parking-lots/<lot_id>/book` - Book a parking spot
- `POST /api/reservations/<id>/checkin` - Check in (mark as parked)
- `POST /api/reservations/<id>/release` - Release spot (checkout)
- `GET /api/my-reservations` - View your reservations

## How to Use JWT Tokens

### 1. Login to get token:
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... }
}
```

### 2. Use token in subsequent requests:
```bash
curl -X GET http://localhost:5000/api/parking-lots \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## Vue.js Integration

In your Vue.js frontend:

```javascript
// Store token after login
localStorage.setItem('token', response.data.access_token);

// Add to all API requests
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

## Database

SQLite database (`parking_app.db`) is automatically created on first run.

To reset database:
```bash
rm parking_app.db
python app.py
```
