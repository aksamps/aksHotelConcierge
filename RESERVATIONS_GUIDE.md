# Hotel Concierge - Room Reservations Feature Guide

## Overview

The application now supports complete room reservation functionality with real-time WebSocket updates. Guests can search for available rooms by date range, make reservations, and the system displays real-time status updates across all connected clients.

## Features Added

### 1. Room Availability Search
- **Endpoint**: `GET /api/rooms/availability?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD`
- **Frontend**: Date range selector with "Search Available Rooms" button
- **Returns**: List of rooms available for the selected dates
- **Logic**: Checks against existing reservations for date conflicts

### 2. Reservation Creation
- **Endpoint**: `POST /api/reservations`
- **Required Fields**:
  - `room_id`: ID of room to reserve
  - `guest_name`: Guest's full name
  - `guest_email`: Guest's email address
  - `check_in_date`: YYYY-MM-DD format
  - `check_out_date`: YYYY-MM-DD format
  - `number_of_guests`: Integer 1+
  - `special_requests`: Optional text field

- **Validation**:
  - Check-out date must be after check-in date
  - No overlapping reservations for the same room
  - Email format validation

### 3. Real-Time Updates via WebSocket
- **Room Status Updates**: Broadcast when rooms change status
- **Reservation Created**: Broadcast when new reservation is confirmed
- **Reservation Cancelled**: Broadcast when existing reservation is cancelled

### 4. Database Tables

#### reservations
```sql
CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    guest_name VARCHAR(255) NOT NULL,
    guest_email VARCHAR(255),
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_guests INT,
    special_requests TEXT,
    status ENUM('confirmed', 'cancelled', 'completed') DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    INDEX idx_room_dates (room_id, check_in_date, check_out_date),
    INDEX idx_dates (check_in_date, check_out_date),
    CHECK (check_out_date > check_in_date)
);
```

#### reservation_logs
```sql
CREATE TABLE reservation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT NOT NULL,
    action VARCHAR(50),
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id)
);
```

## Frontend Usage

### 1. Search for Available Rooms
1. Select "Check-In" date (today or later)
2. Select "Check-Out" date (after check-in date)
3. Click "Search Available Rooms"
4. Available rooms will display with "Book Now" button

### 2. Make a Reservation
1. Click "Book Now" on desired room
2. Enter guest information:
   - Guest Name (required)
   - Email (optional)
   - Number of Guests (default: 1)
   - Special Requests (optional)
3. Verify dates are correct
4. Click "Confirm Reservation"
5. Confirmation notification will appear

### 3. Real-Time Updates
- When any user makes a reservation, all connected clients see:
  - Room availability updates
  - Notification of new reservation
  - Updated room list

## API Endpoints

### Search Available Rooms
```bash
GET /api/rooms/availability?check_in=2024-03-10&check_out=2024-03-15
```

**Response:**
```json
{
  "success": true,
  "rooms": [
    {
      "id": 1,
      "room_number": "101",
      "floor": 1,
      "availability": "available"
    }
  ]
}
```

### Create Reservation
```bash
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

**Response:**
```json
{
  "success": true,
  "reservation": {
    "id": 5,
    "room_id": 1,
    "guest_name": "John Doe",
    "check_in_date": "2024-03-10",
    "check_out_date": "2024-03-15",
    "status": "confirmed"
  }
}
```

### Get All Reservations
```bash
GET /api/reservations
```

### Get Specific Reservation
```bash
GET /api/reservations/{reservation_id}
```

### Get Room's Reservations
```bash
GET /api/reservations/room/{room_id}
```

### Cancel Reservation
```bash
POST /api/reservations/{reservation_id}/cancel
Content-Type: application/json

{
  "cancellation_reason": "Guest request"
}
```

## WebSocket Messages

### Reservation Created
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

### Reservation Cancelled
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

## Testing

### Sample Data
The application includes 5 sample reservations:
- Room 1: Alice Williams (Tomorrow to +3 days)
- Room 2: Bob Brown (Tomorrow +1 day to +4 days)
- Room 5: Carol Davis (Tomorrow +3 days to +6 days)
- Room 7: David Miller (Tomorrow to Tomorrow +1 day)
- Room 9: Emma Wilson (Tomorrow +4 days to +7 days)

### Using REST Client
See `API_TESTS.rest` for complete API test examples:
- Search availability
- Create reservations
- Cancel reservations
- Retrieve reservation data

### Using Frontend
1. Open http://localhost:3000
2. Scroll down to "Book a Room" section
3. Select dates and search
4. Click "Book Now" and fill in guest details
5. Submit and see real-time updates

## Architecture

### Backend Processing
1. **Node.js Server** (port 3000)
   - Receives API requests
   - Proxies to Python API
   - Broadcasts WebSocket events to all clients

2. **Python Flask API** (port 5000)
   - Handles business logic
   - Validates date conflicts
   - Manages database operations

3. **MySQL Database** (port 3306)
   - Stores reservations
   - Maintains audit logs
   - Enforces date constraints

### Frontend Processing
1. User selects dates and searches
2. JavaScript calls `/api/rooms/availability`
3. Display available rooms with "Book Now" buttons
4. On click, open reservation modal
5. Submit reservation to `/api/reservations`
6. Receive confirmation via API response
7. WebSocket broadcasts update to all connected clients
8. Real-time notifications displayed

## Troubleshooting

### "No rooms available" message
- Check that check-out date is after check-in date
- Verify rooms aren't already booked for those dates
- See sample reservations above

### Reservation fails
- Ensure all required fields are filled
- Check email format if provided
- Verify date range is valid
- Check browser console for error details

### WebSocket not updating
- Verify connection status indicator is green
- Check browser console for WebSocket errors
- Ensure server is running (`docker-compose up`)
- Refresh page to reconnect

## Notes

- All dates use YYYY-MM-DD format
- Minimum check-in date is today
- Database automatically creates tables on startup
- Sample reservations use relative dates (based on current date)
- Special requests are stored but don't affect availability
- Cancellations are soft-deletes (marked as cancelled, not removed)
