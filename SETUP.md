# Hotel Concierge - Real-Time Room Status Monitor

A full-stack application for managing hotel rooms with real-time status updates using WebSockets, Node.js, Python, MySQL, and Docker.

## Features

- **Real-Time Room Status**: WebSocket-powered real-time updates of room occupancy status
- **Guest Management**: Check-in and check-out functionality with guest information
- **Status Tracking**: Track room status as occupied, vacant, or maintenance
- **RESTful API**: Complete REST API for room operations
- **Database Logging**: All status changes are logged in the database
- **Containerized**: Full Docker and Docker Compose support
- **Responsive UI**: Modern, responsive web interface for room monitoring

## Architecture

### Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla WebSocket API)
- **Backend**: Node.js with Express.js and WebSocket support
- **Python API**: Flask with MySQL integration
- **Database**: MySQL 8.0
- **Containerization**: Docker & Docker Compose

### Components

1. **Node.js Server** (Port 3000)
   - Express API server
   - WebSocket server for real-time updates
   - Static file serving (frontend)
   - Communication with Python API

2. **Python Flask API** (Port 5000)
   - Room management operations
   - MySQL database operations
   - Room status and check-in/check-out logic

3. **MySQL Database** (Port 3306)
   - Persistent data storage
   - Room information and guest details
   - Status change logs

## Project Structure

```
aksHotelConcierge/
├── server.js                 # Node.js Express server with WebSocket
├── package.json             # Node.js dependencies
├── Dockerfile              # Docker image for Node.js app
├── docker-compose.yml      # Docker Compose orchestration
├── .env.example            # Environment variables example
├── init.sql                # Database initialization script
├── public/
│   └── index.html          # Frontend web interface
├── python_app/
│   ├── app.py              # Flask Python application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Docker image for Python app
└── README.md               # This file
```

## Getting Started

### Prerequisites

- Docker & Docker Compose (recommended)
- OR: Node.js 16+, Python 3.9+, MySQL 8.0

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aksHotelConcierge
   ```

2. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Web UI: http://localhost:3000
   - Node.js API: http://localhost:3000/api
   - Python API: http://localhost:5000/api
   - MySQL: localhost:3306

4. **Stop the services**
   ```bash
   docker-compose down
   ```

### Option 2: Manual Setup (Local Development)

#### Step 1: Set up MySQL Database

```bash
mysql -u root -p
CREATE DATABASE hotel_concierge;
USE hotel_concierge;
source init.sql;
```

#### Step 2: Set up Python Flask API

```bash
cd python_app
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

#### Step 3: Set up Node.js Server

```bash
# In a new terminal
npm install
npm start
```

#### Step 4: Access the Application

- Open http://localhost:3000 in your browser

## API Endpoints

### Room Management

#### Get All Rooms
```
GET /api/rooms
```

Response:
```json
{
  "success": true,
  "rooms": [
    {
      "id": 1,
      "room_number": "101",
      "floor": 1,
      "status": "vacant",
      "guest_name": null,
      "check_in_time": null
    }
  ],
  "count": 12,
  "timestamp": "2024-02-24T10:30:00Z"
}
```

#### Get Room by ID
```
GET /api/rooms/:id
```

#### Create New Room
```
POST /api/rooms
Content-Type: application/json

{
  "id": 1,
  "room_number": "101",
  "floor": 1,
  "status": "vacant",
  "guest_name": "John Doe"
}
```

#### Update Room Status
```
PUT /api/rooms/:id/status
Content-Type: application/json

{
  "status": "occupied"
}
```

Valid statuses: `occupied`, `vacant`, `maintenance`

#### Check In Guest
```
POST /api/rooms/:id/checkin
Content-Type: application/json

{
  "guest_name": "John Doe"
}
```

#### Check Out Guest
```
POST /api/rooms/:id/checkout
```

#### Get Status Summary
```
GET /api/rooms/status/summary
```

Response:
```json
{
  "success": true,
  "summary": [
    {"status": "occupied", "count": 3},
    {"status": "vacant", "count": 8},
    {"status": "maintenance", "count": 1}
  ],
  "timestamp": "2024-02-24T10:30:00Z"
}
```

### Health Checks

#### Node.js Health
```
GET /health
```

#### Python API Health
```
GET /health
```

## WebSocket Messages

The frontend connects to the WebSocket server at the same host and port as the HTTP server.

### Message Format

**Room Status Update**:
```json
{
  "type": "room_status_update",
  "roomId": 1,
  "status": "occupied",
  "timestamp": "2024-02-24T10:30:00Z"
}
```

## Environment Variables

See `.env.example` for available options:

```env
# Node.js
PORT=3000
NODE_ENV=production
PYTHON_API=http://python-app:5000

# MySQL
MYSQL_HOST=mysql-db
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=hotel_concierge

# Flask
FLASK_ENV=production
FLASK_APP=app.py
```

## Database Schema

### rooms table
```sql
CREATE TABLE rooms (
  id INT PRIMARY KEY,
  room_number VARCHAR(10) UNIQUE NOT NULL,
  floor INT NOT NULL,
  status ENUM('occupied', 'vacant', 'maintenance') DEFAULT 'vacant',
  check_in_time DATETIME,
  check_out_time DATETIME,
  guest_name VARCHAR(100),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### room_status_logs table
```sql
CREATE TABLE room_status_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  room_id INT NOT NULL,
  previous_status VARCHAR(20),
  new_status VARCHAR(20) NOT NULL,
  changed_by VARCHAR(100),
  changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (room_id) REFERENCES rooms(id)
);
```

## Features in Detail

### Real-Time Updates
- WebSocket connection for instant room status updates
- Automatic reconnection with exponential backoff
- Connection status indicator in UI

### Guest Management
- Check-in with guest name and automatic timestamp
- Check-out functionality
- Guest information display in room cards

### Status Tracking
- Occupied: Room has an active guest
- Vacant: Room is available for booking
- Maintenance: Room is under maintenance
- All status changes are logged with timestamp

### Responsive UI
- Mobile-friendly design
- Real-time status updates across all connected clients
- Room status cards with guest information
- Summary statistics (total, occupied, vacant, maintenance)
- Quick check-in/check-out buttons

## Docker Compose Services

### mysql-db
- Image: mysql:8.0
- Port: 3306
- Database: hotel_concierge
- Root password: password

### python-app
- Flask API server
- Port: 5000
- Depends on: mysql-db

### nodejs-app
- Express.js WebSocket server
- Port: 3000
- Depends on: python-app

## Logs and Debugging

### View Docker Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nodejs-app
docker-compose logs -f python-app
docker-compose logs -f mysql-db
```

### MySQL Connection
```bash
# Access MySQL container
docker exec -it hotel-concierge-mysql mysql -u root -ppassword hotel_concierge

# View rooms
SELECT * FROM rooms;

# View status logs
SELECT * FROM room_status_logs;
```

## Troubleshooting

### Connection Refused to Python API
- Ensure python-app container is running: `docker-compose ps`
- Check logs: `docker-compose logs python-app`
- Verify PYTHON_API environment variable is set correctly

### WebSocket Connection Issues
- Check browser console for WebSocket errors
- Verify firewall allows WebSocket connections
- Check Node.js server logs: `docker-compose logs nodejs-app`

### MySQL Connection Errors
- Verify MySQL is running: `docker-compose ps`
- Check MySQL logs: `docker-compose logs mysql-db`
- Ensure correct credentials in environment variables
- Wait for MySQL to be healthy before starting other services

### Port Already in Use
- Change port in docker-compose.yml or environment variables
- Kill process using the port:
  ```bash
  # Linux/macOS
  lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9
  
  # Windows
  netstat -ano | findstr :3000
  taskkill /PID <PID> /F
  ```

## Performance Considerations

- **Database Indexing**: Room ID is indexed for fast lookups
- **WebSocket Broadcasting**: Efficiently broadcasts updates to all connected clients
- **Connection Pooling**: MySQL connections are pooled for better performance
- **Horizontal Scaling**: Multiple Node.js instances can share the same Python API and database

## Security Considerations

For production use:
1. Change default MySQL password in docker-compose.yml
2. Set secure Node.js and Flask environment variables
3. Use HTTPS/WSS instead of HTTP/WS
4. Implement authentication and authorization
5. Use environment variables for sensitive data
6. Enable MySQL SSL connections
7. Implement rate limiting on API endpoints
8. Add input validation and sanitization

## Development

### Adding New Features

1. **New API Endpoint**: Add route in `python_app/app.py` and corresponding endpoint in `server.js`
2. **Frontend Changes**: Update `public/index.html` with new UI and WebSocket handlers
3. **Database Changes**: Modify schema in `init.sql` and update models

### Testing

```bash
# Test Python API
curl http://localhost:5000/api/rooms

# Test Node.js API
curl http://localhost:3000/api/rooms

# Test WebSocket (requires wscat)
wscat -c ws://localhost:3000
```

## License

MIT

## Author

aksamps

## Support

For issues and questions, please open an issue in the repository.
