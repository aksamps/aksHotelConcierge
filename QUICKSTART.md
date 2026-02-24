# Hotel Concierge - Quick Start Guide

## 🚀 Quick Start (Docker Compose)

### Prerequisites
- Docker & Docker Compose installed

### Start the Application

```bash
# Navigate to project directory
cd aksHotelConcierge

# Build and start all services
docker-compose up --build
```

The application will be available at:
- **Web Interface**: http://localhost:3000
- **Node.js API**: http://localhost:3000/api
- **Python API**: http://localhost:5000/api
- **MySQL**: localhost:3306

### Access MySQL Database

```bash
docker exec -it hotel-concierge-mysql mysql -u root -ppassword hotel_concierge
```

### Stop Services

```bash
docker-compose down
```

### Clean Up (Remove Volumes)

```bash
docker-compose down -v
```

---

## 📋 Manual Setup (Local Development)

### Prerequisites
- Node.js 16+
- Python 3.9+
- MySQL 8.0

### Step 1: Set up MySQL

```bash
mysql -u root -p
CREATE DATABASE hotel_concierge;
USE hotel_concierge;
source init.sql;
```

### Step 2: Set up Python Flask API

```bash
cd python_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
```

Flask server will run on http://localhost:5000

### Step 3: Set up Node.js Server (New Terminal)

```bash
# Navigate to project root
cd ..

# Install dependencies
npm install

# Start the server
npm start
```

Node.js server will run on http://localhost:3000

### Step 4: Open Application

Open your browser and navigate to:
```
http://localhost:3000
```

---

## 🎯 Common Tasks

### View All Rooms
```bash
curl http://localhost:3000/api/rooms
```

### Check In a Guest
```bash
curl -X POST http://localhost:3000/api/rooms/1/checkin \
  -H "Content-Type: application/json" \
  -d '{"guest_name": "John Doe"}'
```

### Check Out a Guest
```bash
curl -X POST http://localhost:3000/api/rooms/1/checkout
```

### Update Room Status
```bash
curl -X PUT http://localhost:3000/api/rooms/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "maintenance"}'
```

### Get Status Summary
```bash
curl http://localhost:3000/api/rooms/status/summary
```

### View Database
```bash
docker exec -it hotel-concierge-mysql mysql -u root -ppassword hotel_concierge
SELECT * FROM rooms;
SELECT * FROM room_status_logs;
```

---

## 🔧 Troubleshooting

### Port Already in Use
Change the port in `docker-compose.yml`:
```yaml
ports:
  - "8000:3000"  # Change 8000 to any available port
```

### MySQL Connection Failed
- Ensure MySQL container is healthy: `docker-compose ps`
- Check MySQL logs: `docker-compose logs mysql-db`
- Wait 10-15 seconds for MySQL to be ready after starting

### WebSocket Connection Issues
- Check browser console (F12) for errors
- Verify Node.js is running: `docker-compose logs nodejs-app`
- Check firewall settings

### Python API Connection Failed
- Verify python-app container is running: `docker-compose ps`
- Check Python logs: `docker-compose logs python-app`
- Ensure PYTHON_API environment variable is set: `http://python-app:5000`

---

## 📁 Key Files

- **server.js**: Node.js Express server with WebSocket support
- **python_app/app.py**: Flask API for room management
- **public/index.html**: Frontend web interface
- **docker-compose.yml**: Docker Compose configuration
- **init.sql**: Database initialization script

---

## 🌐 Features Overview

### Real-Time Room Monitoring
- See room status updates in real-time
- Connection status indicator
- Live guest information

### Room Management
- Check in guests with name and timestamp
- Check out guests
- Update room status (occupied/vacant/maintenance)
- View room details and history

### Status Summary
- Total rooms count
- Number of occupied rooms
- Number of vacant rooms
- Number of rooms in maintenance

---

## 📚 Further Reading

See [SETUP.md](SETUP.md) for detailed documentation on:
- Full API documentation
- Database schema
- Architecture overview
- Security considerations
- Performance optimization
- Development guidelines

---

## 💡 Tips

1. **Sample Data**: Database is initialized with 12 sample rooms
2. **WebSocket Auto-Reconnect**: Frontend automatically reconnects if connection is lost
3. **Responsive Design**: Works on desktop and mobile browsers
4. **Docker Health Checks**: Services have built-in health checks

---

## 🆘 Need Help?

1. Check `SETUP.md` for detailed documentation
2. Review Docker logs: `docker-compose logs -f`
3. Verify all services are running: `docker-compose ps`
4. Check browser console for frontend errors (F12)

---

**Happy Hotel Managing! 🏨**
