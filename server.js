'use strict';

const express = require('express');
const app = express();
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const axios = require('axios');
const path = require('path');

const PORT = process.env.PORT || 3000;
const PYTHON_API = process.env.PYTHON_API || 'http://python-app:5000';

// Middleware
app.use(express.json());
app.use(cors());
app.use(express.static('public'));

// Create HTTP server for WebSocket
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Store connected clients
const clients = new Set();

// WebSocket connection handler
wss.on('connection', (ws) => {
    console.log('New WebSocket client connected');
    clients.add(ws);

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            console.log('Received message:', data);
            // Broadcast to all clients
            broadcastToClients(data);
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    });

    ws.on('close', () => {
        console.log('WebSocket client disconnected');
        clients.delete(ws);
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
});

// Function to broadcast messages to all connected clients
function broadcastToClients(data) {
    clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(data));
        }
    });
}

// API Routes

// Get all rooms with status
app.get('/api/rooms', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API}/api/rooms`);
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching rooms:', error.message);
        res.status(500).json({ error: 'Failed to fetch rooms' });
    }
});

// Get room availability for date range (MUST be before /:id route)
app.get('/api/rooms/availability', async (req, res) => {
    try {
        const checkIn = req.query.check_in;
        const checkOut = req.query.check_out;
        
        if (!checkIn || !checkOut) {
            return res.status(400).json({ error: 'check_in and check_out dates required' });
        }
        
        const response = await axios.get(
            `${PYTHON_API}/api/rooms/availability?check_in=${checkIn}&check_out=${checkOut}`
        );
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching availability:', error.message);
        res.status(500).json({ error: 'Failed to fetch availability' });
    }
});

// Get room by ID
app.get('/api/rooms/:id', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API}/api/rooms/${req.params.id}`);
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching room:', error.message);
        res.status(500).json({ error: 'Failed to fetch room' });
    }
});

// ==================== RESERVATION ENDPOINTS ====================

// Get all reservations
app.get('/api/reservations', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API}/api/reservations`);
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching reservations:', error.message);
        res.status(500).json({ error: 'Failed to fetch reservations' });
    }
});

// Create new reservation
app.post('/api/reservations', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_API}/api/reservations`, req.body);
        
        // Broadcast reservation creation to all clients
        broadcastToClients({
            type: 'reservation_created',
            reservation: response.data,
            timestamp: new Date().toISOString()
        });
        
        // If there's a room status update, broadcast that too
        if (response.data.room_status_update) {
            broadcastToClients({
                type: 'room_status_update',
                roomId: response.data.room_status_update.room_id,
                status: response.data.room_status_update.new_status,
                previousStatus: response.data.room_status_update.previous_status,
                timestamp: new Date().toISOString()
            });
        }
        
        res.status(201).json(response.data);
    } catch (error) {
        console.error('Error creating reservation:', error.message);
        res.status(error.response?.status || 500).json({ 
            error: error.response?.data?.error || 'Failed to create reservation' 
        });
    }
});

// Get specific reservation
app.get('/api/reservations/:id', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API}/api/reservations/${req.params.id}`);
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching reservation:', error.message);
        res.status(500).json({ error: 'Failed to fetch reservation' });
    }
});

// Cancel reservation
app.post('/api/reservations/:id/cancel', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_API}/api/reservations/${req.params.id}/cancel`);
        
        // Broadcast cancellation to all clients
        broadcastToClients({
            type: 'reservation_cancelled',
            reservation_id: req.params.id,
            timestamp: new Date().toISOString()
        });
        
        res.json(response.data);
    } catch (error) {
        console.error('Error cancelling reservation:', error.message);
        res.status(500).json({ error: 'Failed to cancel reservation' });
    }
});

// Get room reservations
app.get('/api/reservations/room/:room_id', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API}/api/reservations/room/${req.params.room_id}`);
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching room reservations:', error.message);
        res.status(500).json({ error: 'Failed to fetch room reservations' });
    }
});

// Update room status
app.put('/api/rooms/:id/status', async (req, res) => {
    try {
        const { status } = req.body;
        const response = await axios.put(
            `${PYTHON_API}/api/rooms/${req.params.id}/status`,
            { status }
        );
        
        // Broadcast update to all WebSocket clients
        broadcastToClients({
            type: 'room_status_update',
            roomId: req.params.id,
            status: status,
            timestamp: new Date().toISOString()
        });
        
        res.json(response.data);
    } catch (error) {
        console.error('Error updating room status:', error.message);
        res.status(500).json({ error: 'Failed to update room status' });
    }
});

// Check in guest
app.post('/api/rooms/:id/checkin', async (req, res) => {
    try {
        const response = await axios.post(
            `${PYTHON_API}/api/rooms/${req.params.id}/checkin`,
            req.body
        );
        
        // Broadcast check-in to all clients
        broadcastToClients({
            type: 'guest_checkin',
            room_id: req.params.id,
            guest_name: req.body.guest_name,
            timestamp: new Date().toISOString()
        });
        
        res.json(response.data);
    } catch (error) {
        console.error('Error checking in guest:', error.message);
        res.status(500).json({ error: 'Failed to check in guest' });
    }
});

// Check out guest
app.post('/api/rooms/:id/checkout', async (req, res) => {
    try {
        const response = await axios.post(
            `${PYTHON_API}/api/rooms/${req.params.id}/checkout`
        );
        
        // Broadcast check-out to all clients
        broadcastToClients({
            type: 'guest_checkout',
            room_id: req.params.id,
            timestamp: new Date().toISOString()
        });
        
        res.json(response.data);
    } catch (error) {
        console.error('Error checking out guest:', error.message);
        res.status(500).json({ error: 'Failed to check out guest' });
    }
});

// Create new room
app.post('/api/rooms', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_API}/api/rooms`, req.body);
        res.status(201).json(response.data);
    } catch (error) {
        console.error('Error creating room:', error.message);
        res.status(500).json({ error: 'Failed to create room' });
    }
});

// Initialize database with sample data
app.post('/api/init', async (req, res) => {
    try {
        const response = await axios.post(`${PYTHON_API}/api/init`);
        res.status(201).json(response.data);
    } catch (error) {
        console.error('Error initializing database:', error.message);
        res.status(error.response?.status || 500).json({ 
            error: error.response?.data?.error || 'Failed to initialize database' 
        });
    }
});

// Serve frontend
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on port ${PORT}`);
    console.log(`WebSocket server is ready for connections`);
});