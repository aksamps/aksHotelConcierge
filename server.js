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