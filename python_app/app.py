"""
Hotel Concierge Python Application
Manages room status and database operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from datetime import datetime
import logging
import hashlib
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'mysql-db')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'hotel_concierge')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Initialize database tables
def init_db():
    """Initialize database tables if they don't exist"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Create rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INT PRIMARY KEY,
                room_number VARCHAR(10) UNIQUE NOT NULL,
                floor INT NOT NULL,
                status ENUM('vacant', 'reserved', 'checkedin', 'checkout') DEFAULT 'vacant',
                check_in_time DATETIME,
                check_out_time DATETIME,
                guest_name VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # Try to alter table if it exists to add new statuses
        try:
            cursor.execute('''
                ALTER TABLE rooms 
                MODIFY COLUMN status ENUM('vacant', 'reserved', 'checkedin', 'checkout') DEFAULT 'vacant'
            ''')
        except:
            pass  # Table might already have the correct schema
        
        # Create reservations table for date-based bookings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_id INT NOT NULL,
                guest_name VARCHAR(100) NOT NULL,
                guest_email VARCHAR(100),
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL,
                number_of_guests INT DEFAULT 1,
                special_requests TEXT,
                status ENUM('confirmed', 'cancelled', 'completed') DEFAULT 'confirmed',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms(id),
                INDEX idx_room_dates (room_id, check_in_date, check_out_date),
                INDEX idx_dates (check_in_date, check_out_date)
            )
        ''')
        
        # Create room_status_logs table for tracking changes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_status_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_id INT NOT NULL,
                previous_status VARCHAR(20),
                new_status VARCHAR(20) NOT NULL,
                changed_by VARCHAR(100),
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            )
        ''')
        
        # Create reservation_logs table for audit trail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservation_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reservation_id INT NOT NULL,
                action VARCHAR(50) NOT NULL,
                changed_by VARCHAR(100),
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reservation_id) REFERENCES reservations(id)
            )
        ''')

        # Create users table for authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        ''')

        # Create user_notifications table for per-user notification history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                message TEXT NOT NULL,
                notification_type VARCHAR(20),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_time (user_id, created_at DESC)
            )
        ''')
        
        mysql.connection.commit()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

@app.before_request
def before_request():
    """Initialize database on first request"""
    init_db()

# ==================== UTILITY FUNCTIONS ====================

def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt + password_hash

def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    salt = stored_hash[:32]  # First 32 chars are the salt
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return password_hash == stored_hash[32:]

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        # Validate input
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if username already exists
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            cursor.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Hash password and insert user
        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (%s, %s)',
            (username, password_hash)
        )
        mysql.connection.commit()
        user_id = cursor.lastrowid
        cursor.close()
        
        logger.info(f"User registered: {username}")
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user_id': user_id,
            'username': username,
            'timestamp': datetime.now().isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user with username and password"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            cursor.close()
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Update last login
        cursor.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s',
            (user['id'],)
        )
        mysql.connection.commit()
        cursor.close()
        
        logger.info(f"User logged in: {username}")
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user_id': user['id'],
            'username': user['username'],
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify', methods=['GET'])
def verify_session():
    """Verify if user session is valid (basic check)"""
    try:
        user_id = request.args.get('user_id')
        username = request.args.get('username')
        
        if not user_id or not username:
            return jsonify({'error': 'user_id and username required'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id, username FROM users WHERE id = %s AND username = %s', (user_id, username))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            return jsonify({'success': False, 'error': 'Invalid session'}), 401
        
        return jsonify({
            'success': True,
            'user_id': user['id'],
            'username': user['username']
        }), 200
    except Exception as e:
        logger.error(f"Error verifying session: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== USER NOTIFICATION ENDPOINTS ====================

@app.route('/api/user/notifications', methods=['GET'])
def get_user_notifications():
    """Get last 20 notifications for a user"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT id, message, notification_type, created_at 
            FROM user_notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 20
        ''', (user_id,))
        notifications = cursor.fetchall()
        cursor.close()
        
        logger.info(f"Retrieved {len(notifications)} notifications for user {user_id}")
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/notifications', methods=['POST'])
def add_user_notification():
    """Add a notification for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        message = data.get('message')
        notification_type = data.get('type', 'info')
        
        if not user_id or not message:
            return jsonify({'error': 'user_id and message required'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Verify user exists
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Delete oldest notification if we already have 20
        cursor.execute('''
            SELECT COUNT(*) as count FROM user_notifications WHERE user_id = %s
        ''', (user_id,))
        result = cursor.fetchone()
        if result['count'] >= 20:
            cursor.execute('''
                DELETE FROM user_notifications 
                WHERE user_id = %s AND id NOT IN (
                    SELECT id FROM user_notifications 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 19
                )
            ''', (user_id, user_id))
        
        # Insert new notification
        cursor.execute('''
            INSERT INTO user_notifications (user_id, message, notification_type)
            VALUES (%s, %s, %s)
        ''', (user_id, message, notification_type))
        mysql.connection.commit()
        notification_id = cursor.lastrowid
        cursor.close()
        
        logger.info(f"Added notification for user {user_id}")
        return jsonify({
            'success': True,
            'notification_id': notification_id,
            'message': 'Notification added',
            'timestamp': datetime.now().isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error adding notification: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== ROOM ENDPOINTS ====================

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all rooms with their current status and reservation dates"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get all rooms with their reservation information
        cursor.execute('''
            SELECT 
                r.*,
                res.check_in_date,
                res.check_out_date,
                res.guest_name as reserved_guest
            FROM rooms r
            LEFT JOIN reservations res ON r.id = res.room_id 
                AND res.status = 'confirmed'
            ORDER BY r.room_number
        ''')
        rooms = cursor.fetchall()
        cursor.close()
        
        logger.info(f"Retrieved {len(rooms)} rooms")
        return jsonify({
            'success': True,
            'rooms': rooms,
            'count': len(rooms),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching rooms: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """Get a specific room by ID with reservation details"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT 
                r.*,
                res.check_in_date,
                res.check_out_date,
                res.guest_name as reserved_guest
            FROM rooms r
            LEFT JOIN reservations res ON r.id = res.room_id 
                AND res.status = 'confirmed'
            WHERE r.id = %s
        ''', (room_id,))
        room = cursor.fetchone()
        cursor.close()
        
        if not room:
            return jsonify({'error': 'Room not found'}), 404
        
        logger.info(f"Retrieved room {room_id}")
        return jsonify({
            'success': True,
            'room': room,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching room {room_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms', methods=['POST'])
def create_room():
    """Create a new room"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id', 'room_number', 'floor']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            INSERT INTO rooms (id, room_number, floor, status, guest_name)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            data['id'],
            data['room_number'],
            data['floor'],
            data.get('status', 'vacant'),
            data.get('guest_name', '')
        ))
        mysql.connection.commit()
        cursor.close()
        
        logger.info(f"Created room {data['room_number']}")
        return jsonify({
            'success': True,
            'message': 'Room created successfully',
            'room': data,
            'timestamp': datetime.now().isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error creating room: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>/status', methods=['PUT'])
def update_room_status(room_id):
    """Update room status (vacant/reserved/checkedin/checkout)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['vacant', 'reserved', 'checkedin', 'checkout']:
            return jsonify({'error': 'Invalid status. Must be: vacant, reserved, checkedin, or checkout'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get current status
        cursor.execute('SELECT status FROM rooms WHERE id = %s', (room_id,))
        room = cursor.fetchone()
        if not room:
            return jsonify({'error': 'Room not found'}), 404
        
        previous_status = room['status']
        
        # Update room status
        cursor.execute('''
            UPDATE rooms SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (new_status, room_id))
        
        # Log status change
        cursor.execute('''
            INSERT INTO room_status_logs (room_id, previous_status, new_status, changed_by)
            VALUES (%s, %s, %s, %s)
        ''', (room_id, previous_status, new_status, 'system'))
        
        mysql.connection.commit()
        cursor.close()
        
        logger.info(f"Updated room {room_id} status from {previous_status} to {new_status}")
        return jsonify({
            'success': True,
            'message': f'Room status updated from {previous_status} to {new_status}',
            'room_id': room_id,
            'previous_status': previous_status,
            'new_status': new_status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error updating room status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>/checkin', methods=['POST'])
def check_in_room(room_id):
    """Check in a guest to a room"""
    try:
        data = request.get_json()
        guest_name = data.get('guest_name', 'Unknown')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            UPDATE rooms 
            SET status = 'checkedin', 
                guest_name = %s, 
                check_in_time = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (guest_name, room_id))
        
        # Log the status change
        cursor.execute('''
            INSERT INTO room_status_logs (room_id, previous_status, new_status, changed_by)
            VALUES (%s, 'vacant', 'checkedin', %s)
        ''', (room_id, guest_name))
        
        mysql.connection.commit()
        cursor.close()
        
        logger.info(f"Guest {guest_name} checked in to room {room_id}")
        return jsonify({
            'success': True,
            'message': f'Guest {guest_name} checked in successfully',
            'room_id': room_id,
            'guest_name': guest_name,
            'check_in_time': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error checking in guest: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>/checkout', methods=['POST'])
def check_out_room(room_id):
    """Check out a guest from a room"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT guest_name FROM rooms WHERE id = %s', (room_id,))
        room = cursor.fetchone()
        if not room:
            return jsonify({'error': 'Room not found'}), 404
        
        guest_name = room.get('guest_name', 'Unknown')
        
        cursor.execute('''
            UPDATE rooms 
            SET status = 'vacant', 
                guest_name = NULL, 
                check_out_time = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (room_id,))
        
        # Log the status change
        cursor.execute('''
            INSERT INTO room_status_logs (room_id, previous_status, new_status, changed_by)
            VALUES (%s, 'checkedin', 'vacant', %s)
        ''', (room_id, guest_name))
        
        mysql.connection.commit()
        cursor.close()
        
        logger.info(f"Guest {guest_name} checked out from room {room_id}")
        return jsonify({
            'success': True,
            'message': f'Guest checked out successfully',
            'room_id': room_id,
            'guest_name': guest_name,
            'check_out_time': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error checking out guest: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/status/summary', methods=['GET'])
def get_status_summary():
    """Get summary of room statuses"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM rooms 
            GROUP BY status
        ''')
        summary = cursor.fetchall()
        cursor.close()
        
        logger.info("Retrieved status summary")
        return jsonify({
            'success': True,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching status summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== RESERVATION ENDPOINTS ====================

@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    """Get all reservations"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT r.*, rm.room_number, rm.floor 
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE r.status = 'confirmed'
            ORDER BY r.check_in_date
        ''')
        reservations = cursor.fetchall()
        cursor.close()
        
        logger.info(f"Retrieved {len(reservations)} reservations")
        return jsonify({
            'success': True,
            'reservations': reservations,
            'count': len(reservations),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching reservations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/availability', methods=['GET'])
def get_room_availability():
    """Get available rooms for a specific date range"""
    try:
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')
        
        if not check_in or not check_out:
            return jsonify({'error': 'check_in and check_out dates required'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get all rooms with their reservation status
        cursor.execute('''
            SELECT r.*,
                   COUNT(res.id) as has_reservation,
                   CASE WHEN COUNT(res.id) > 0 THEN 'reserved' ELSE 'available' END as availability
            FROM rooms r
            LEFT JOIN reservations res ON r.id = res.room_id 
                AND res.status = 'confirmed'
                AND res.check_in_date < %s 
                AND res.check_out_date > %s
            GROUP BY r.id
            ORDER BY r.floor, r.room_number
        ''', (check_out, check_in))
        
        rooms = cursor.fetchall()
        cursor.close()
        
        logger.info(f"Retrieved availability for {check_in} to {check_out}")
        return jsonify({
            'success': True,
            'check_in_date': check_in,
            'check_out_date': check_out,
            'rooms': rooms,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching availability: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    """Create a new reservation for a room"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['room_id', 'guest_name', 'check_in_date', 'check_out_date']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        room_id = data['room_id']
        guest_name = data['guest_name']
        check_in = data['check_in_date']
        check_out = data['check_out_date']
        guest_email = data.get('guest_email', '')
        num_guests = data.get('number_of_guests', 1)
        special_requests = data.get('special_requests', '')
        
        # Validate date format and maximum stay duration
        try:
            from datetime import datetime as dt
            check_in_date = dt.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = dt.strptime(check_out, '%Y-%m-%d').date()
            
            # Validate dates are in correct order
            if check_in_date >= check_out_date:
                return jsonify({'error': 'Check-out date must be after check-in date'}), 400
            
            # Validate maximum stay is 2 days
            stay_duration = (check_out_date - check_in_date).days
            if stay_duration > 2:
                return jsonify({'error': f'Maximum stay is 2 days. Your selected duration is {stay_duration} days.'}), 400
        except ValueError as e:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if room exists
        cursor.execute('SELECT id FROM rooms WHERE id = %s', (room_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Room not found'}), 404
        
        # Check for conflicting reservations
        cursor.execute('''
            SELECT id FROM reservations 
            WHERE room_id = %s 
            AND status = 'confirmed'
            AND check_in_date < %s 
            AND check_out_date > %s
        ''', (room_id, check_out, check_in))
        
        if cursor.fetchone():
            return jsonify({'error': 'Room is not available for these dates'}), 409
        
        # Create reservation
        cursor.execute('''
            INSERT INTO reservations 
            (room_id, guest_name, guest_email, check_in_date, check_out_date, 
             number_of_guests, special_requests, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'confirmed')
        ''', (room_id, guest_name, guest_email, check_in, check_out, num_guests, special_requests))
        
        reservation_id = cursor.lastrowid
        
        # Get current room status
        cursor.execute('SELECT status FROM rooms WHERE id = %s', (room_id,))
        room = cursor.fetchone()
        previous_status = room['status'] if room else 'vacant'
        
        # Update room status to reserved
        cursor.execute('''
            UPDATE rooms SET status = 'reserved', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (room_id,))
        
        # Log the status change
        cursor.execute('''
            INSERT INTO room_status_logs (room_id, previous_status, new_status, changed_by)
            VALUES (%s, %s, %s, %s)
        ''', (room_id, previous_status, 'reserved', guest_name))
        
        # Log the reservation
        cursor.execute('''
            INSERT INTO reservation_logs (reservation_id, action, changed_by)
            VALUES (%s, 'created', %s)
        ''', (reservation_id, guest_name))
        
        mysql.connection.commit()
        cursor.close()
        
        logger.info(f"Created reservation {reservation_id} for guest {guest_name} in room {room_id}")
        return jsonify({
            'success': True,
            'message': 'Reservation created successfully',
            'reservation_id': reservation_id,
            'room_id': room_id,
            'guest_name': guest_name,
            'check_in_date': check_in,
            'check_out_date': check_out,
            'room_status_update': {
                'room_id': room_id,
                'previous_status': previous_status,
                'new_status': 'reserved'
            },
            'timestamp': datetime.now().isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error creating reservation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    """Get specific reservation"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT r.*, rm.room_number, rm.floor 
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            WHERE r.id = %s
        ''', (reservation_id,))
        reservation = cursor.fetchone()
        cursor.close()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        logger.info(f"Retrieved reservation {reservation_id}")
        return jsonify({
            'success': True,
            'reservation': reservation,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching reservation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservations/<int:reservation_id>/cancel', methods=['POST'])
def cancel_reservation(reservation_id):
    """Cancel a reservation"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get reservation
        cursor.execute('SELECT * FROM reservations WHERE id = %s', (reservation_id,))
        reservation = cursor.fetchone()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        if reservation['status'] != 'confirmed':
            return jsonify({'error': 'Only confirmed reservations can be cancelled'}), 400
        
        # Cancel reservation
        cursor.execute('''
            UPDATE reservations 
            SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (reservation_id,))
        
        # Log the cancellation
        cursor.execute('''
            INSERT INTO reservation_logs (reservation_id, action, changed_by)
            VALUES (%s, 'cancelled', %s)
        ''', (reservation_id, 'system'))
        
        mysql.connection.commit()
        cursor.close()
        
        logger.info(f"Cancelled reservation {reservation_id}")
        return jsonify({
            'success': True,
            'message': 'Reservation cancelled successfully',
            'reservation_id': reservation_id,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error cancelling reservation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservations/room/<int:room_id>', methods=['GET'])
def get_room_reservations(room_id):
    """Get all reservations for a specific room"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT * FROM reservations 
            WHERE room_id = %s AND status = 'confirmed'
            ORDER BY check_in_date
        ''', (room_id,))
        reservations = cursor.fetchall()
        cursor.close()
        
        logger.info(f"Retrieved reservations for room {room_id}")
        return jsonify({
            'success': True,
            'room_id': room_id,
            'reservations': reservations,
            'count': len(reservations),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching room reservations: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== INITIALIZATION ====================

@app.route('/api/init', methods=['POST'])
def initialize_data():
    """Initialize sample rooms for demo purposes"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if rooms already exist
        cursor.execute('SELECT COUNT(*) as count FROM rooms')
        result = cursor.fetchone()
        if result['count'] > 0:
            return jsonify({
                'success': True,
                'message': 'Database already initialized',
                'rooms_count': result['count']
            }), 200
        
        # Create sample rooms
        sample_rooms = [
            (101, '101', 1, 'vacant'),
            (102, '102', 1, 'vacant'),
            (103, '103', 1, 'vacant'),
            (104, '104', 1, 'vacant'),
            (105, '105', 1, 'vacant'),
            (201, '201', 2, 'vacant'),
            (202, '202', 2, 'vacant'),
            (203, '203', 2, 'vacant'),
            (204, '204', 2, 'vacant'),
            (205, '205', 2, 'vacant'),
            (301, '301', 3, 'vacant'),
            (302, '302', 3, 'vacant'),
            (303, '303', 3, 'vacant'),
            (304, '304', 3, 'vacant'),
            (305, '305', 3, 'vacant'),
        ]
        
        for room in sample_rooms:
            cursor.execute('''
                INSERT INTO rooms (id, room_number, floor, status)
                VALUES (%s, %s, %s, %s)
            ''', room)
        
        mysql.connection.commit()
        cursor.close()
        
        logger.info(f"Initialized {len(sample_rooms)} sample rooms")
        return jsonify({
            'success': True,
            'message': f'Initialized {len(sample_rooms)} sample rooms',
            'rooms_count': len(sample_rooms),
            'timestamp': datetime.now().isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error initializing data: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
