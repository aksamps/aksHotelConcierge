# Hotel Concierge Application Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT BROWSERS                                 │
│                      (Web UI at localhost:3000)                          │
└────────────────┬────────────────────────────────────────────────────────┘
                 │
                 │ HTTP & WebSocket
                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    NODE.JS EXPRESS SERVER                               │
│                    (Port 3000, localhost:3000)                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ • Express.js Web Framework                                        │  │
│  │ • WebSocket Server (ws library)                                   │  │
│  │ • Static File Serving (public/index.html)                         │  │
│  │ • CORS Middleware                                                 │  │
│  │ • REST API Endpoints                                              │  │
│  │ • Broadcasting Room Status Updates                                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                 │                                         │
│              HTTP Requests      │      WebSocket Connections             │
│              to Python API      │      to Clients                        │
└─────────────────────────────────┼───────────────────────────────────────┘
                                  │
                                  │ HTTP (Port 5000)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   PYTHON FLASK REST API                                  │
│              (Port 5000, http://python-app:5000)                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ • Flask Web Framework                                             │  │
│  │ • Room Management Endpoints                                       │  │
│  │ • Guest Check-in/Check-out Logic                                 │  │
│  │ • MySQL Database Operations                                       │  │
│  │ • Status Logging & Audit Trail                                    │  │
│  │ • Error Handling                                                  │  │
│  │ • CORS Support                                                    │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                 │                                         │
│                                 │ SQL Queries                             │
│                                 ▼                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                    MySQL Connection (Port 3306)
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        MYSQL DATABASE                                    │
│                   (Port 3306, localhost:3306)                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Database: hotel_concierge                                         │  │
│  │ ┌─────────────────────────────────────────────────────────────┐  │  │
│  │ │ TABLE: rooms                                                │  │  │
│  │ │ - id (INT PRIMARY KEY)                                      │  │  │
│  │ │ - room_number (VARCHAR)                                     │  │  │
│  │ │ - floor (INT)                                               │  │  │
│  │ │ - status (ENUM)                                             │  │  │
│  │ │ - guest_name (VARCHAR)                                      │  │  │
│  │ │ - check_in_time, check_out_time (DATETIME)                 │  │  │
│  │ │ - created_at, updated_at (DATETIME)                        │  │  │
│  │ └─────────────────────────────────────────────────────────────┘  │  │
│  │ ┌─────────────────────────────────────────────────────────────┐  │  │
│  │ │ TABLE: room_status_logs                                     │  │  │
│  │ │ - id (INT AUTO_INCREMENT PRIMARY KEY)                       │  │  │
│  │ │ - room_id (INT FOREIGN KEY)                                 │  │  │
│  │ │ - previous_status, new_status (VARCHAR)                     │  │  │
│  │ │ - changed_by (VARCHAR)                                      │  │  │
│  │ │ - changed_at (DATETIME)                                     │  │  │
│  │ └─────────────────────────────────────────────────────────────┘  │  │
│  │                                                                   │  │
│  │ Persistent Volume: mysql_data                                    │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Docker Compose Services

```
┌────────────────────────────────────────────────────────────────┐
│              DOCKER COMPOSE ENVIRONMENT                        │
│                (hotel-network bridge)                          │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   mysql-db   │  │  python-app  │  │ nodejs-app   │        │
│  │              │  │              │  │              │        │
│  │ Port: 3306   │  │ Port: 5000   │  │ Port: 3000   │        │
│  │ Health: 30s  │  │ Health: 30s  │  │ Health: 30s  │        │
│  │              │  │              │  │              │        │
│  │ Depends:     │  │ Depends:     │  │ Depends:     │        │
│  │   None       │  │ mysql-db✓    │  │ python-app✓  │        │
│  │              │  │              │  │              │        │
│  │ Volume:      │  │ Mount: app   │  │ Mount: public│        │
│  │ mysql_data   │  │              │  │              │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│        │                   │                   │              │
│        └───────────────────┼───────────────────┘              │
│                            │                                  │
│                    Shared Network                             │
│                   (Hostname Resolution)                       │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────────┐
│  Browser Client  │
│  (Web UI)        │
└────────┬─────────┘
         │
         │ 1. Initial Load & WebSocket Connect
         │
         ▼
    ┌─────────────────────────────────────┐
    │ Node.js Express Server (port 3000)   │
    │                                     │
    │ Serves static files (index.html)    │
    │ Establishes WebSocket connection    │
    └─────────┬───────────────────────────┘
              │
      ┌───────┴────────┐
      │                │
      │ 2. Room Data   │ 3. Broadcast Updates
      │ Request        │ to WebSocket Clients
      │                │
      ▼                ▼
  ┌─────────────────────┐      ┌──────────────────┐
  │ Python Flask API    │      │ Connected Clients│
  │ (port 5000)         │      │ Receive Updates  │
  │                     │      │ Real-time        │
  │ • GET /api/rooms    │      │ status changes   │
  │ • PUT /status       │      └──────────────────┘
  │ • POST /checkin     │
  │ • POST /checkout    │
  │ • GET /summary      │
  └─────────┬───────────┘
            │
            │ 4. Database Queries
            │
            ▼
     ┌────────────────────┐
     │ MySQL Database     │
     │ (port 3306)        │
     │                    │
     │ • Rooms data       │
     │ • Status logs      │
     │ • Guest info       │
     │ • Timestamps       │
     └────────────────────┘
```

## WebSocket Message Flow

```
Browser Client                          Node.js Server
     │                                       │
     │  1. WebSocket Connection              │
     ├──────────────────────────────────────►│
     │                                       │
     │  2. Connection Established            │
     │◄──────────────────────────────────────┤
     │                                       │
     │  3. User performs action              │
     │     (check-in/status update)          │
     │     ↓                                 │
     │  4. HTTP Request to /api/rooms/:id    │
     ├──────────────────────────────────────►│
     │                                       │ 5. Forward to Python API
     │                                       ├────────────────────────►
     │                                       │  Python API
     │                                       │  │ 6. Update Database
     │                                       │  │
     │                                       │  │ 7. Return Response
     │                                       │◄────────────────────────
     │  8. HTTP Response                     │
     │◄──────────────────────────────────────┤
     │                                       │
     │                                       │ 9. Broadcast to All
     │  10. WebSocket Update Event           │    Connected Clients
     │◄──────────────────────────────────────┤
     │    (room status changed)              │
     │                                       │
     │  Update Local State                   │
     │  ↓                                    │
     │  Re-render UI                         │
```

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  DEVELOPMENT SETUP                         │
│                                                            │
│  Option 1: Docker Compose                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ docker-compose up --build                            │ │
│  │ • All services in one command                        │ │
│  │ • Network isolation                                  │ │
│  │ • Volume persistence                                │ │
│  │ • Health checks                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Option 2: Manual Setup                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Terminal 1: MySQL                                    │ │
│  │ Terminal 2: Python Flask (port 5000)                │ │
│  │ Terminal 3: Node.js Express (port 3000)             │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                  PRODUCTION DEPLOYMENT                     │
│                                                            │
│  Docker Swarm / Kubernetes                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ • Multiple replicas of each service                 │ │
│  │ • Load balancing across instances                   │ │
│  │ • Auto-scaling based on demand                      │ │
│  │ • Persistent storage for MySQL                      │ │
│  │ • Health checks and auto-healing                    │ │
│  │ • Logging and monitoring                            │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

## Technology Stack Visualization

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                        │
│  ┌─────────────────────────────────────────────────────┐│
│  │ HTML5, CSS3, Vanilla JavaScript                    ││
│  │ • WebSocket API                                    ││
│  │ • Responsive Design                                ││
│  │ • Real-time Status Updates                         ││
│  └─────────────────────────────────────────────────────┘│
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                    API LAYER                            │
│  ┌──────────────────────┐  ┌──────────────────────────┐│
│  │ Node.js + Express    │  │ Python + Flask           ││
│  │ • WebSocket Server   │  │ • REST API Endpoints     ││
│  │ • Request Handling   │  │ • Business Logic         ││
│  │ • Broadcasting       │  │ • Database Operations    ││
│  └──────────────────────┘  └──────────────────────────┘│
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                  DATA LAYER                             │
│  ┌─────────────────────────────────────────────────────┐│
│  │ MySQL 8.0 Database                                 ││
│  │ • Relational Data Storage                          ││
│  │ • ACID Transactions                                ││
│  │ • Persistent Storage                               ││
│  └─────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

## Network Topology

```
Internet
   │
   │ TCP/IP
   │
   ▼
┌─────────────┐
│   Host      │
│  Machine    │
│ (Windows)   │
└────────┬────┘
         │
   ┌─────┴──────┐
   │             │
   ▼             ▼
┌──────────┐  ┌──────────┐
│localhost │  │ localhost│
│:3000     │  │ :5000   │
│          │  │          │
│Node.js   │  │ Python  │
│Express   │  │ Flask   │
└──────────┘  └──────────┘
   │             │
   │             │
   └──────┬──────┘
          │
          ▼
    ┌──────────────┐
    │  localhost   │
    │  :3306       │
    │              │
    │    MySQL     │
    │              │
    └──────────────┘
```

## Request-Response Cycle

```
1. User Opens Browser
   http://localhost:3000
         │
         ▼
2. Server Serves index.html
   ┌─────────────────────────┐
   │ • HTML Structure        │
   │ • CSS Styling           │
   │ • JavaScript Code       │
   └────────────┬────────────┘
                │
                ▼
3. JavaScript Establishes WebSocket Connection
   ┌──────────────────────────────┐
   │ ws://localhost:3000          │
   │ Connection: OPEN             │
   └──────────────┬───────────────┘
                  │
                  ▼
4. Fetch Initial Room Data
   ┌─────────────────────────────────────────┐
   │ GET /api/rooms (HTTP)                   │
   │ Response: Array of rooms with status    │
   └──────────────┬────────────────────────────┘
                  │
                  ▼
5. Render Room Cards on Page
   ┌──────────────────────────────────────┐
   │ • Room numbers                       │
   │ • Floor information                  │
   │ • Current status (occupied/vacant)   │
   │ • Guest name (if occupied)           │
   │ • Check-in/checkout buttons          │
   └──────────────┬───────────────────────┘
                  │
                  ▼
6. User Interaction (Check-in)
   ┌────────────────────────────────┐
   │ Click "Check In" button         │
   │ Enter guest name in modal       │
   └────────────┬──────────────────┘
                │
                ▼
7. Send Check-in Request
   ┌─────────────────────────────────────────┐
   │ POST /api/rooms/1/checkin               │
   │ {"guest_name": "John Doe"}              │
   └──────────────┬────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
8a. Node.js Forwards    8b. WebSocket Broadcast
    to Python API           to All Clients
    │                       │
    ▼                       │
9a. Python Updates      9b. Clients Update UI
    MySQL Database          │
                            ▼
    ┌────────────────────────────────────────┐
    │ 10. Real-time Update on All Screens    │
    │     Room 1: Now showing as "occupied"  │
    │     Guest name: "John Doe"             │
    │     Check-in time: [current time]      │
    └────────────────────────────────────────┘
```

---

## Component Interactions

```
┌───────────────────────────────────────────────────────────────┐
│ Browser Frontend                                              │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ • index.html (serves from Node.js)                      │  │
│ │ • WebSocket Connection Handler                          │  │
│ │ • Room Card Renderer                                    │  │
│ │ • Modal Dialog Handler                                  │  │
│ │ • Real-time Update Listener                             │  │
│ └──────────────┬──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│HTTP API  │ │WebSocket │ │Fetch     │
│Calls     │ │Messages  │ │Data      │
└─────┬────┘ └─────┬────┘ └─────┬────┘
      │            │            │
      │ ┌──────────┴────────────┘
      │ │
      ▼ ▼
 ┌──────────────────────────────┐
 │ Node.js Express Server       │
 │ ┌──────────────────────────┐ │
 │ │ • HTTP Route Handlers    │ │
 │ │ • WebSocket Server       │ │
 │ │ • CORS Middleware        │ │
 │ │ • Static File Serving    │ │
 │ │ • Python API Proxy       │ │
 │ │ • Broadcasting Logic     │ │
 │ └──────────────────────────┘ │
 └──────────────┬────────────────┘
                │
                ▼
       ┌────────────────────┐
       │ Python Flask API   │
       │ ┌────────────────┐ │
       │ │ • Room Routes  │ │
       │ │ • Check-in/Out │ │
       │ │ • Status Logic │ │
       │ │ • DB Queries   │ │
       │ │ • Logging      │ │
       │ └────────────────┘ │
       └────────────┬───────┘
                    │
                    ▼
           ┌─────────────────┐
           │ MySQL Database  │
           │ ┌───────────────┤
           │ │ rooms         │
           │ │ status_logs   │
           │ └───────────────┤
           └─────────────────┘
```

---

Generated: February 24, 2026
Status: Complete ✅
