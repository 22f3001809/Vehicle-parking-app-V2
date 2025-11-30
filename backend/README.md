#### Used for Testing Purpose
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

