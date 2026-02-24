# Hotel Concierge - Booking System Updates

## Overview
The application has been enhanced with a complete reservation booking system that enforces a **maximum 2-day stay limit** for all reservations.

## Features Implemented

### 1. **Room Availability Search**
- Search rooms by check-in and check-out dates
- Visual display of available vs. unavailable rooms
- Shows number of available rooms and stay duration
- Dynamic date validation preventing bookings longer than 2 days

### 2. **Room Booking Interface**
- **Available rooms**: Display "BOOK NOW" button (green, prominent)
- **Unavailable rooms**: Display "NOT AVAILABLE" button (disabled, grayed out)
- Room cards show:
  - Room number and floor
  - Room type and capacity (2 guests)
  - Current status (vacant, occupied, maintenance)
  - Availability for selected dates

### 3. **Reservation Modal**
- Guest name and email fields
- Check-in and check-out date selection
- Number of guests (1-4)
- Special requests textarea
- **Maximum stay enforcement**: Check-out date automatically limited to 2 days from check-in
- Clear information banner showing "Maximum Stay: Reservations are limited to a maximum of 2 days"

### 4. **2-Day Maximum Stay Validation**
- **Client-side validation**: 
  - HTML5 input date constraints
  - JavaScript calculation preventing selection of dates >2 days apart
  - Real-time error messages
  
- **Server-side validation**:
  - Python backend validates stay duration
  - Returns error if duration exceeds 2 days
  - Calculates and reports actual duration in error messages

### 5. **Sample Data Initialization**
- Automatic creation of 15 sample rooms on first application load
- Rooms distributed across 3 floors (5 rooms per floor)
- All rooms initialized as "vacant"
- Rooms: 101-105 (Floor 1), 201-205 (Floor 2), 301-305 (Floor 3)

## API Endpoints

### New/Updated Endpoints

**POST /api/init**
- Initializes database with sample rooms
- Creates 15 vacant rooms across 3 floors
- Called automatically on first page load
- Returns: Room count and initialization status

**GET /api/rooms**
- Returns all rooms with current status
- Response includes: room_number, floor, status, guest_name, check_in_time

**GET /api/rooms/availability?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD**
- Returns available and reserved rooms for date range
- Shows availability status for each room
- Validates 2-day maximum automatically

**POST /api/reservations**
- Creates new reservation
- Validates:
  - Room exists
  - No conflicting reservations
  - **Stay duration ≤ 2 days** ✓
  - Valid date format
  - Check-out after check-in
- Returns: Reservation ID, details, and confirmation

**POST /api/rooms/:id/checkin**
- Updates room status to "occupied"
- Records guest name and check-in time
- Broadcasts update to all connected clients

**POST /api/rooms/:id/checkout**
- Updates room status to "vacant"
- Clears guest information
- Broadcasts update to all connected clients

## User Workflow

### Steps to Make a Reservation:

1. **Search for Available Rooms**
   - Enter check-in date
   - Enter check-out date (max 2 days later)
   - Click "Search Available Rooms"

2. **View Results**
   - Search results section shows:
     - Check-in and check-out dates
     - Length of stay (in days)
     - Number of available rooms
   - Room cards display with booking status

3. **Book a Room**
   - Click "BOOK NOW" on available room
   - Fill in reservation details:
     - Guest name (required)
     - Guest email
     - Check-in date (pre-filled)
     - Check-out date (pre-filled, max 2 days from check-in)
     - Number of guests
     - Special requests

4. **Confirm Booking**
   - Click "Book Room"
   - System validates all information
   - Reservation is created and confirmed
   - Success notification displayed
   - Search refreshes to show updated availability

## Technical Changes

### Files Modified

1. **public/index.html**
   - Added informative search section with date inputs
   - Added search results display area
   - Enhanced reservation modal with 2-day maximum stay banner
   - Added client-side 2-day validation
   - Improved room card UI with booking buttons
   - Added room type and capacity information
   - Implemented `updateMaxCheckOutDate()` function
   - Enhanced `confirmReservation()` with duration validation
   - Added database initialization on page load

2. **python_app/app.py**
   - Added `/api/init` endpoint for sample data creation
   - Enhanced `/api/reservations` POST with:
     - Date format validation
     - 2-day maximum stay enforcement
     - Detailed error messages

3. **server.js**
   - Fixed route ordering (availability route before :id route)
   - Added `/api/init` endpoint proxy
   - Added `/api/rooms/:id/checkin` endpoint
   - Added `/api/rooms/:id/checkout` endpoint
   - Added WebSocket broadcasting for check-in/checkout events

## Maximum 2-Day Stay Enforcement

### How It Works:

1. **HTML Date Input**: 
   - Check-out input has `max` attribute set to 2 days after check-in
   - User cannot select dates beyond this limit in the date picker

2. **JavaScript Event Listener**:
   - Listens to changes on check-in date
   - Dynamically updates check-out max date
   - Clears invalid check-out values

3. **Form Validation**:
   - Before submission, calculates actual stay duration
   - Prevents form submission if duration > 2 days
   - Shows error message with actual duration

4. **Backend Validation**:
   - Python server calculates (check_out_date - check_in_date).days
   - Rejects requests with duration > 2 days
   - Returns error: "Maximum stay is 2 days. Your selected duration is X days."

## Testing the System

### Via Browser UI:
1. Navigate to http://localhost:3000
2. Rooms will load automatically (15 sample rooms)
3. Select a check-in date (e.g., 2026-02-26)
4. Select a check-out date (e.g., 2026-02-28)
5. Click "Search Available Rooms"
6. Click "BOOK NOW" on any available room
7. Fill in guest details and click "Book Room"

### Via API (curl):
```bash
# Check availability
curl "http://localhost:3000/api/rooms/availability?check_in=2026-02-26&check_out=2026-02-28"

# Create reservation
curl -X POST http://localhost:3000/api/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 101,
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "check_in_date": "2026-02-26",
    "check_out_date": "2026-02-28",
    "number_of_guests": 2,
    "special_requests": "Late checkout if possible"
  }'
```

## Error Handling

### Client-Side Errors:
- Missing dates: "Please select both check-in and check-out dates"
- Invalid date order: "Check-out date must be after check-in date"
- Exceeds 2 days: "Maximum stay is 2 days. Your selected duration is X days."
- Missing guest name: "Please enter guest name"

### Server-Side Errors:
- Missing fields: "Missing required fields"
- Room not found: "Room not found"
- Conflicting reservations: "Room is not available for these dates"
- Duration exceeded: "Maximum stay is 2 days. Your selected duration is X days."

## Database Schema

### Reservations Table:
- id (auto-increment)
- room_id (foreign key)
- guest_name
- guest_email
- check_in_date (DATE)
- check_out_date (DATE)
- number_of_guests
- special_requests (TEXT)
- status (confirmed/cancelled/completed)
- created_at, updated_at

### Validation Constraints:
- check_out_date > check_in_date (enforced in Python code)
- (check_out_date - check_in_date) ≤ 2 days (enforced in Python code)
- No overlapping reservations for same room (enforced in SQL query)

## WebSocket Real-Time Updates

The system uses WebSocket to broadcast:
- **reservation_created**: Notifies all clients of new booking
- **reservation_cancelled**: Notifies all clients of cancellation
- **guest_checkin**: Notifies all clients when guest checks in
- **guest_checkout**: Notifies all clients when guest checks out
- **room_status_update**: Notifies all clients of room status changes

## Future Enhancements

- Payment processing integration
- Cancellation policies and fees
- Room discounts and promotions
- Guest loyalty program
- Email confirmations
- SMS notifications
- Calendar view of bookings
- Review and rating system
