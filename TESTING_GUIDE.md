# Hotel Concierge - Quick Testing Guide

## Starting the Application

```bash
# From the project directory
docker-compose up --build

# First run: Wait 30-60 seconds for database to initialize
# MySQL will auto-create all tables and populate sample data
```

## Application URLs

- **Frontend**: http://localhost:3000
- **Node.js API**: http://localhost:3000/api
- **Python API**: http://localhost:5000/api (internal)
- **Health Check**: http://localhost:3000/health

## Testing the Reservation System

### Step 1: Open the Application
1. Navigate to http://localhost:3000
2. Verify the page loads and room list appears
3. Check that connection status shows "Connected" (green indicator)

### Step 2: Search Available Rooms
1. Scroll down to "Book a Room" section
2. Click on "Check-In" date picker
3. Select a date (tomorrow or later)
4. Click on "Check-Out" date picker
5. Select a date 2+ days after check-in
6. Click "Search Available Rooms" button
7. Room list should update to show only available rooms

### Step 3: Make a Reservation
1. Click "Book Now" button on any available room
2. Fill in the reservation modal:
   - **Guest Name**: Enter any name (required)
   - **Email**: Optional, but try entering a valid email
   - **Number of Guests**: 1-5
   - **Special Requests**: Optional (e.g., "High floor", "Pool view")
3. Verify dates are correct (should auto-fill from search)
4. Click "Confirm Reservation"
5. Look for success notification

### Step 4: Verify Real-Time Updates
1. After making a reservation:
   - Room should disappear from availability list (booked)
   - Success notification should appear
   - Open another browser tab at http://localhost:3000
   - That tab should see the new reservation in real-time
   - Connection status should remain "Connected"

### Step 5: Check Existing Reservations
Open browser console (F12) and run:
```javascript
fetch('/api/reservations').then(r => r.json()).then(d => console.log(d))
```

Should show sample reservations:
- Room 1: Alice Williams
- Room 2: Bob Brown
- Room 5: Carol Davis
- Room 7: David Miller
- Room 9: Emma Wilson

## Sample Test Cases

### Test Case 1: Search Available Rooms
**Dates**: Today + 5 days to Today + 10 days
**Expected**: Rooms 3, 4, 8, 11, 12 should be available (others are booked)

### Test Case 2: Overlapping Dates
**Dates**: Tomorrow to Tomorrow + 2 days
**Expected**: Rooms 1, 7 are booked; others available

### Test Case 3: Full Room Booking
**Step 1**: Search for dates Tomorrow to Tomorrow + 3 days
**Step 2**: Book Room 5 (Carol Davis has it next week, should be available)
**Step 3**: Immediately search same dates in another tab
**Step 4**: Room 5 should disappear from availability list

### Test Case 4: WebSocket Real-Time
**Step 1**: Open two browser tabs both at http://localhost:3000
**Step 2**: In Tab 1, search for available rooms (Tomorrow to Tomorrow + 5 days)
**Step 3**: In Tab 1, book Room 8
**Step 4**: In Tab 2, immediately search same dates
**Step 5**: Room 8 should NOT appear in Tab 2 (real-time update)

## API Testing with cURL

### Check Room Availability
```bash
curl "http://localhost:3000/api/rooms/availability?check_in=2024-03-10&check_out=2024-03-15"
```

### Get All Reservations
```bash
curl "http://localhost:3000/api/reservations"
```

### Create New Reservation
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
    "special_requests": "Late checkout"
  }'
```

### Cancel Reservation
```bash
curl -X POST http://localhost:3000/api/reservations/1/cancel \
  -H "Content-Type: application/json" \
  -d '{"cancellation_reason": "Test cancellation"}'
```

## Troubleshooting

### Issue: "No rooms available" after search
- **Cause**: All rooms might be booked for those dates
- **Solution**: Try dates from 7+ days in future
- **Check**: See sample reservations list above for booked dates

### Issue: Reservation fails with 400 error
- **Cause**: Invalid data format
- **Check**: 
  - Guest name is not empty
  - Check-out date is after check-in date
  - Email format is valid (if provided)
  - Dates are YYYY-MM-DD format

### Issue: WebSocket not updating across tabs
- **Cause**: WebSocket disconnected
- **Check**: Connection status indicator at top
- **Solution**: 
  - Refresh the page
  - Check Docker is still running (`docker ps`)
  - Check server logs: `docker-compose logs -f node`

### Issue: Database tables not created
- **Cause**: Container initialization incomplete
- **Solution**:
  - Wait 60 seconds after `docker-compose up`
  - Check MySQL logs: `docker-compose logs mysql`
  - Recreate containers: `docker-compose down && docker-compose up --build`

### Issue: Python API error (502 Bad Gateway)
- **Cause**: Python service not responding
- **Check**: `docker-compose logs python`
- **Solution**: Restart services: `docker-compose restart python`

## Files Modified for Reservations Feature

1. **python_app/app.py**
   - Added 4 database tables (auto-create)
   - Added 6 API endpoints
   - Date validation and conflict checking

2. **server.js**
   - Added 5 reservation proxy endpoints
   - WebSocket broadcasts for reservation events
   - Date range validation

3. **public/index.html**
   - Added date range search UI
   - Added reservation modal
   - Added JavaScript functions for search, booking, WebSocket handling
   - Updated room card display logic

4. **init.sql**
   - Added 5 sample reservations

5. **API_TESTS.rest**
   - Added 8 new test cases for reservations

## Expected Behavior Summary

| Action | Expected Result |
|--------|-----------------|
| Load page | 12 rooms listed, connection shows connected |
| Search without dates | Error notification |
| Search valid date range | Available rooms display |
| Click Book Now | Modal opens with pre-filled dates |
| Submit incomplete form | Error notification |
| Submit valid reservation | Success notification, room disappears |
| Open another tab | New reservation visible in real-time |
| Cancel reservation | Room becomes available again |
| WebSocket disconnects | Reconnect attempt shown, eventually reconnects |

## Log Files (Inside Docker)

```bash
# View Node.js server logs
docker-compose logs -f node

# View Python API logs
docker-compose logs -f python

# View MySQL logs
docker-compose logs -f mysql

# View all services
docker-compose logs -f
```

## Database Connection (Inside Container)

```bash
# Connect to MySQL directly
docker-compose exec mysql mysql -u root -photel_password

# View reservations
USE hotel_concierge;
SELECT * FROM reservations;
SELECT * FROM reservation_logs;
```

---

**Ready to test?** Start with Step 1 above and work through the test cases systematically!
