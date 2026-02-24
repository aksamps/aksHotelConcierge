# 🏨 Hotel Concierge - Real-Time Room Status Monitor

A production-ready, full-stack hotel room management system with real-time status monitoring, guest management, and containerized deployment using Node.js, Python, MySQL, and Docker.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![Node.js](https://img.shields.io/badge/Node.js-16+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Documentation](#documentation)
- [Technologies](#technologies)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Real-Time Updates
- **WebSocket-based real-time room status monitoring** - See live updates across all connected clients
- **Automatic reconnection** - Built-in retry logic with exponential backoff
- **Connection status indicator** - Visual feedback on WebSocket connection state

### Room Management
- **Create and manage rooms** with floor information
- **Update room status** (occupied, vacant, maintenance)
- **Track guest information** including check-in/check-out times
- **View room details** with guest information and timestamps

### Guest Management
- **Check-in functionality** with guest name and automatic timestamp
- **Check-out functionality** with automatic cleanup
- **Guest information storage** and history tracking
- **Status change logging** for audit trail

### Database
- **Persistent MySQL storage** with proper schema design
- **Audit logging** of all status changes
- **Referential integrity** with foreign key constraints
- **Indexed queries** for optimal performance

### API
- **Complete REST API** for all room operations
- **Proper HTTP status codes** and error handling
- **JSON request/response format**
- **Health check endpoints** for monitoring

### Frontend
- **Modern, responsive web interface** - Works on desktop and mobile
- **Real-time status cards** with color-coded status indicators
- **Status summary dashboard** with statistics
- **Quick action buttons** for check-in/check-out
- **Modal dialogs** for operations
- **Guest information display**

### DevOps
- **Docker containerization** for all services
- **Docker Compose orchestration** - Single command startup
- **Health checks** for all services
- **Volume persistence** for data
- **Network isolation** between services
- **Helper scripts** for common commands

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR: Node.js 16+, Python 3.9+, MySQL 8.0

### Option 1: Docker Compose (Recommended - 2 minutes)

```bash
# Clone and navigate to directory
git clone <repository-url>
cd aksHotelConcierge

# Start all services
docker-compose up --build

# Open in browser
# http://localhost:3000
```

### Option 2: Manual Setup

#### Terminal 1: Python API
```bash
cd python_app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py  # Runs on port 5000
```

#### Terminal 2: Node.js Server
```bash
npm install
npm start  # Runs on port 3000
```

#### Terminal 3: MySQL (if not using Docker)
```sql
mysql -u root -p
CREATE DATABASE hotel_concierge;
USE hotel_concierge;
source init.sql;
```

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────┐
│   Web Browser (UI)          │
│   http://localhost:3000     │
└────────────┬────────────────┘
             │ HTTP & WebSocket
             ▼
┌─────────────────────────────┐
│ Node.js Express + WebSocket │
│    Room API & Broadcast     │
└────────────┬────────────────┘
             │ HTTP Proxy
             ▼
┌─────────────────────────────┐
│  Python Flask REST API      │
│   Room Management Logic     │
└────────────┬────────────────┘
             │ SQL Queries
             ▼
┌─────────────────────────────┐
│    MySQL 8.0 Database       │
│  Rooms & Status Audit Logs  │
└─────────────────────────────┘
```

For detailed architecture diagrams, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 📦 Installation

### Full Documentation
See [SETUP.md](SETUP.md) for comprehensive installation and configuration guide.

### Quick Docker Compose
```bash
docker-compose up --build
```

### Access Points
- **Web UI**: http://localhost:3000
- **Node.js API**: http://localhost:3000/api
- **Python API**: http://localhost:5000/api
- **MySQL**: localhost:3306

### Database Access
```bash
docker exec -it hotel-concierge-mysql mysql -u root -ppassword hotel_concierge
```

## 🎯 Usage

### Web Interface Features

1. **Room Status Monitor**
   - View all rooms with status (occupied/vacant/maintenance)
   - See guest information and check-in times
   - Real-time updates across all connected users

2. **Check-In Process**
   - Click "Check In" button on room card
   - Enter guest name
   - Confirm - room status automatically updates
   - Time-stamped check-in recorded

3. **Check-Out Process**
   - Click "Check Out" button on room card
   - Confirm check-out
   - Room automatically marked as vacant

4. **Status Summary**
   - Total rooms count
   - Occupied rooms count
   - Vacant rooms count
   - Maintenance rooms count
   - Real-time statistics

### Helper Scripts

#### Linux/Mac
```bash
./docker-help.sh start       # Start all services
./docker-help.sh stop        # Stop all services
./docker-help.sh logs        # View logs
./docker-help.sh mysql       # Access MySQL
./docker-help.sh help        # Show all commands
```

#### Windows
```bash
docker-help.bat start        # Start all services
docker-help.bat stop         # Stop all services
docker-help.bat logs         # View logs
docker-help.bat mysql        # Access MySQL
docker-help.bat help         # Show all commands
```

## 📚 API Documentation

### Base URLs
- Node.js: `http://localhost:3000`
- Python: `http://localhost:5000`

### Key Endpoints

#### Get All Rooms
```http
GET /api/rooms
```

#### Check In Guest
```http
POST /api/rooms/:id/checkin
Content-Type: application/json

{
  "guest_name": "John Doe"
}
```

#### Check Out Guest
```http
POST /api/rooms/:id/checkout
```

#### Update Room Status
```http
PUT /api/rooms/:id/status
Content-Type: application/json

{
  "status": "occupied"
}
```

#### Get Status Summary
```http
GET /api/rooms/status/summary
```

For complete API documentation with all endpoints and examples, see [SETUP.md](SETUP.md#api-endpoints) or use [API_TESTS.rest](API_TESTS.rest).

## 📖 Documentation

### Main Documentation Files

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide with common tasks
- **[SETUP.md](SETUP.md)** - Comprehensive setup and API documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and diagrams
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[API_TESTS.rest](API_TESTS.rest)** - API test collection

## 🛠️ Technologies

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- WebSocket API for real-time communication

### Backend
- **Node.js 16+** - JavaScript runtime
- **Express.js 4.18** - Web framework
- **ws 8.13** - WebSocket library
- **axios 1.4** - HTTP client

### Python API
- **Flask 2.3** - Python web framework
- **Flask-CORS 4.0** - CORS support
- **Flask-MySQLdb 1.0** - MySQL integration

### Database
- **MySQL 8.0** - Relational database

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration

## 📊 Project Structure

```
aksHotelConcierge/
├── server.js                 # Node.js Express server
├── package.json              # Node.js dependencies
├── Dockerfile                # Docker image for Node.js
├── docker-compose.yml        # Docker Compose configuration
├── docker-help.sh            # Linux/Mac helper script
├── docker-help.bat           # Windows helper script
├── init.sql                  # Database initialization
├── .env.example              # Environment variables template
│
├── public/
│   └── index.html            # Web frontend
│
├── python_app/
│   ├── app.py                # Flask REST API
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Docker image for Python
│
├── QUICKSTART.md             # Quick start guide
├── SETUP.md                  # Comprehensive setup guide
├── ARCHITECTURE.md           # Architecture diagrams
├── IMPLEMENTATION_SUMMARY.md # Implementation details
├── API_TESTS.rest            # API test collection
└── README.md                 # This file
```

## 🔒 Security

### Implemented
- CORS configuration
- Input validation
- Error handling
- Environment variable configuration
- Health checks

### Production Recommendations
1. Change default database password
2. Implement JWT authentication
3. Use HTTPS/WSS for secure connections
4. Add rate limiting
5. Implement input sanitization
6. Use environment variables for secrets
7. Enable MySQL SSL connections
8. Add API authentication tokens

See [SETUP.md](SETUP.md#security-considerations) for detailed security guidelines.

## 🚨 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Change port in docker-compose.yml or:
# Linux/Mac
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**MySQL Connection Failed**
- Ensure MySQL is running: `docker-compose ps`
- Wait 10-15 seconds for MySQL to be healthy
- Check logs: `docker-compose logs mysql-db`

**WebSocket Connection Issues**
- Check browser console (F12) for errors
- Verify Node.js is running: `docker-compose logs nodejs-app`
- Check firewall settings

For more troubleshooting, see [SETUP.md](SETUP.md#troubleshooting).

## 📈 Performance

- Efficient database indexing
- Connection pooling
- WebSocket broadcasting
- Lightweight frontend
- Optimized Docker images
- Health checks for monitoring

## 🎓 Learning Resources

This project demonstrates:
- WebSocket real-time communication
- Microservices architecture
- Docker containerization and orchestration
- REST API design
- Database design and relationships
- Full-stack JavaScript development
- Python web framework usage

## 🔄 Future Enhancements

- [ ] Authentication and authorization
- [ ] Room reservation system
- [ ] Housekeeping management
- [ ] Guest request system
- [ ] Analytics dashboard
- [ ] Mobile app (iOS/Android)
- [ ] PMS integration
- [ ] Payment gateway integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For issues, questions, or suggestions, please open an issue in the repository.

## 👨‍💻 Author

**aksamps** - [GitHub Profile](https://github.com/aksamps)

---

## 🎉 Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aksHotelConcierge
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Open in browser**
   ```
   http://localhost:3000
   ```

4. **Enjoy!** Real-time room monitoring is now active

---

**Made with ❤️ for hotel management**

Last Updated: February 24, 2026
Status: Production Ready ✅
- **Reviews & Ratings**: Leave feedback on your stay and read previous guest reviews.

## Setup Instructions
1. **Clone the Repository**:  
   `git clone https://github.com/aksamps/aksHotelConcierge.git`
2. **Install Dependencies**:  
   Navigate to the project directory and run:  
   `npm install`  
   or  
   `yarn install`
3. **Environment Variables**:  
   Create a `.env` file in the root directory and add your configuration variables.
4. **Run the Application**:  
   Start the application using:  
   `npm start`  
   or  
   `yarn start`

## Usage
- Navigate to the homepage to start booking your stay.
- Use the chat feature for assistance at any time.
- Explore available rooms and amenities before making your selection.

For detailed documentation, please refer to the [Wiki](https://github.com/aksamps/aksHotelConcierge/wiki).  

## Contributions
Feel free to submit issues or pull requests if you have suggestions for improvements!  

## License
This project is licensed under the MIT License.