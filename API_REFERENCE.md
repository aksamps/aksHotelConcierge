# Hotel Concierge API Reference

## Base URLs
- Node.js Server: `http://localhost:3000`
- Python API: `http://localhost:5000` (internal, proxied through Node.js)
- WebSocket: `ws://localhost:3000`

## Health Check Endpoints

### Server Health
```
GET /health
```
Returns: `{"status": "ok", "timestamp": "..."}`

### Python API Health
```
GET http://localhost:5000/health
```
Returns: `{"status": "ok", "uptime": ...}`

---

## Room Management Endpoints

### Get All Rooms
```
GET /api/rooms
```
Returns list of all 12 rooms with status.

### Get Single Room
```
GET /api/rooms/:room_id
```
Parameters: 
- `room_id`: Integer (1-12)

### Get Room Status Summary
```
GET /api/rooms/status/summary
```
Returns counts: occupied, vacant, maintenance.

### Create New Room
```
POST /api/rooms
Content-Type: application/json

{
  "id": 13,
  "room_number": "305",
  "floor": 3,
  "status": "vacant",
  "guest_name": null
}
```

### Update Room Status
```
PUT /api/rooms/:room_id/status
Content-Type: application/json

{
  "status": "occupied" | "vacant" | "maintenance"
}
```

### Check In Guest
```
POST /api/rooms/:room_id/checkin
Content-Type: application/json

{
  "guest_name": "John Doe"
}
```

### Check Out Guest
```
POST /api/rooms/:room_id/checkout
```

---

## Reservation Endpoints

### Search Available Rooms by Date Range
```
GET /api/rooms/availability?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD
```
Query Parameters:
- `check_in`: Check-in date (required, YYYY-MM-DD format)
- `check_out`: Check-out date (required, YYYY-MM-DD format)

Returns:
```json
{
  "success": true,
  "rooms": [
    {
      "id": 1,
      "room_number": "101",
      "floor": 1,
      "availability": "available" | "reserved"
    }
  ]
}
```

**Error Response** (if dates invalid):
```json
{
  "success": false,
  "error": "Check-out date must be after check-in date"
}
```

---

### Create Reservation
```
POST /api/reservations
Content-Type: application/json

{
  "room_id": 1,
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "check_in_date": "2024-03-10",
  "check_out_date": "2024-03-15",
  "number_of_guests": 2,
  "special_requests": "High floor preferred"
}
```

All fields except `guest_email` and `special_requests` are required.

Returns:
```json
{
  "success": true,
  "reservation": {
    "id": 5,
    "room_id": 1,
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "check_in_date": "2024-03-10",
    "check_out_date": "2024-03-15",
    "number_of_guests": 2,
    "special_requests": "High floor preferred",
    "status": "confirmed",
    "created_at": "2024-02-24T10:30:00Z"
  }
}
```

**Error Response** (if booking conflict):
```json
{
  "success": false,
  "error": "Room is not available for selected dates"
}
```

---

### Get All Reservations
```
GET /api/reservations
```

Returns:
```json
{
  "success": true,
  "reservations": [
    {
      "id": 1,
      "room_id": 1,
      "guest_name": "Alice Williams",
      "check_in_date": "2024-03-01",
      "check_out_date": "2024-03-03",
      "status": "confirmed",
      "created_at": "2024-02-24T10:15:00Z"
    }
  ]
}
```

---

### Get Specific Reservation
```
GET /api/reservations/:reservation_id
```

Parameters:
- `reservation_id`: Integer

Returns single reservation object (same structure as above).

---

### Get Room's Reservations
```
GET /api/reservations/room/:room_id
```

Parameters:
- `room_id`: Integer (1-12)

Returns array of all reservations for that room.

---

### Cancel Reservation
```
POST /api/reservations/:reservation_id/cancel
Content-Type: application/json

{
  "cancellation_reason": "Guest requested cancellation"
}
```

Parameters:
- `reservation_id`: Integer

Returns:
```json
{
  "success": true,
  "reservation": {
    "id": 1,
    "room_id": 1,
    "guest_name": "Alice Williams",
    "status": "cancelled"
  }
}
```

---

## WebSocket Connection

### Connect
```javascript
const ws = new WebSocket('ws://localhost:3000');
```

### Listen for Events

#### Room Status Update
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'room_status_update') {
    console.log('Room status:', data.room_id, data.status);
  }
};
```

Message Format:
```json
{
  "type": "room_status_update",
  "room_id": 1,
  "status": "occupied",
  "guest_name": "John Doe",
  "timestamp": "2024-02-24T10:30:00Z"
}
```

#### Reservation Created
```javascript
if (data.type === 'reservation_created') {
  console.log('New reservation:', data.reservation);
}
```

Message Format:
```json
{
  "type": "reservation_created",
  "reservation": {
    "id": 5,
    "room_id": 1,
    "guest_name": "John Doe",
    "check_in_date": "2024-03-10",
    "check_out_date": "2024-03-15",
    "status": "confirmed"
  },
  "timestamp": "2024-02-24T10:30:00Z"
}
```

#### Reservation Cancelled
```javascript
if (data.type === 'reservation_cancelled') {
  console.log('Cancelled:', data.reservation);
}
```

Message Format:
```json
{
  "type": "reservation_cancelled",
  "reservation": {
    "id": 5,
    "room_id": 1,
    "status": "cancelled"
  },
  "timestamp": "2024-02-24T10:30:00Z"
}
```

---

## Response Format

All endpoints return responses with this structure:

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "timestamp": "2024-02-24T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Description of the error",
  "timestamp": "2024-02-24T10:30:00Z"
}
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 404 | Not Found (room/reservation doesn't exist) |
| 409 | Conflict (booking conflict) |
| 500 | Server Error |

---

## Sample Requests

### cURL: Search Availability
```bash
curl "http://localhost:3000/api/rooms/availability?check_in=2024-03-10&check_out=2024-03-15"
```

### cURL: Create Reservation
```bash
curl -X POST http://localhost:3000/api/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "guest_name": "Test User",
    "guest_email": "test@example.com",
    "check_in_date": "2024-03-10",
    "check_out_date": "2024-03-15",
    "number_of_guests": 2,
    "special_requests": ""
  }'
```

### cURL: Get All Reservations
```bash
curl "http://localhost:3000/api/reservations"
```

### cURL: Cancel Reservation
```bash
curl -X POST http://localhost:3000/api/reservations/1/cancel \
  -H "Content-Type: application/json" \
  -d '{"cancellation_reason": "Guest cancelled"}'
```

### JavaScript: Search Availability
```javascript
const checkIn = '2024-03-10';
const checkOut = '2024-03-15';

fetch(`/api/rooms/availability?check_in=${checkIn}&check_out=${checkOut}`)
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log('Available rooms:', data.rooms);
    } else {
      console.error('Error:', data.error);
    }
  });
```

### JavaScript: Create Reservation
```javascript
const reservation = {
  room_id: 1,
  guest_name: 'John Doe',
  guest_email: 'john@example.com',
  check_in_date: '2024-03-10',
  check_out_date: '2024-03-15',
  number_of_guests: 2,
  special_requests: 'High floor preferred'
};

fetch('/api/reservations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(reservation)
})
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log('Reservation created:', data.reservation);
    } else {
      console.error('Error:', data.error);
    }
  });
```

---

## Rate Limiting

No rate limiting is currently implemented. For production use, consider adding rate limiting at the reverse proxy level.

## Authentication

No authentication is currently required. For production use, implement:
- JWT token-based authentication
- User roles (admin, staff, guest)
- Permission-based access control

## CORS

CORS is enabled for all origins. For production, restrict to specific domains in server.js:
```javascript
const corsOptions = {
  origin: ['https://yourdomain.com'],
  credentials: true
};
```

---

## Data Limits

- Guest Name: 255 characters max
- Email: 255 characters max
- Special Requests: 1000 characters max
- Number of Guests: 1-5

---

## Timezone

All dates use YYYY-MM-DD format (date only, no time).
All timestamps use ISO 8601 format with timezone (Z indicates UTC).

---

## Database Schema Reference

### rooms table
- id (INT, PK)
- room_number (VARCHAR)
- floor (INT)
- status (ENUM: vacant, occupied, maintenance)
- guest_name (VARCHAR, nullable)

### reservations table
- id (INT, PK, auto-increment)
- room_id (INT, FK)
- guest_name (VARCHAR, required)
- guest_email (VARCHAR, nullable)
- check_in_date (DATE, required)
- check_out_date (DATE, required)
- number_of_guests (INT)
- special_requests (TEXT)
- status (ENUM: confirmed, cancelled, completed)
- created_at (TIMESTAMP)
- Indexes: idx_room_dates, idx_dates
- Check: check_out_date > check_in_date

### reservation_logs table
- id (INT, PK, auto-increment)
- reservation_id (INT, FK)
- action (VARCHAR)
- details (JSON)
- created_at (TIMESTAMP)

---

For more details, see:
- RESERVATIONS_GUIDE.md - Feature overview
- TESTING_GUIDE.md - Testing instructions
- API_TESTS.rest - Runnable test examples
