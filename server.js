'use strict';

const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Routes
app.get('/api/hotels', (req, res) => {
    res.json({ message: 'List of hotels' });
});

app.get('/api/hotels/:id', (req, res) => {
    const id = req.params.id;
    res.json({ message: `Details for hotel with ID: ${id}` });
});

app.post('/api/hotels', (req, res) => {
    const newHotel = req.body;
    res.status(201).json({ message: 'Hotel created', hotel: newHotel });
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});