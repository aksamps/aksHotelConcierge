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
                status ENUM('occupied', 'vacant', 'maintenance') DEFAULT 'vacant',
                check_in_time DATETIME,
                check_out_time DATETIME,
                guest_name VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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
        
        mysql.connection.commit()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

@app.before_request
def before_request():
    """Initialize database on first request"""
    init_db()

# ==================== ROOM ENDPOINTS ====================

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all rooms with their current status"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM rooms ORDER BY room_number')
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
    """Get a specific room by ID"""
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM rooms WHERE id = %s', (room_id,))
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
    """Update room status (occupied/vacant/maintenance)"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['occupied', 'vacant', 'maintenance']:
            return jsonify({'error': 'Invalid status'}), 400
        
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
            SET status = 'occupied', 
                guest_name = %s, 
                check_in_time = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (guest_name, room_id))
        
        # Log the status change
        cursor.execute('''
            INSERT INTO room_status_logs (room_id, previous_status, new_status, changed_by)
            VALUES (%s, 'vacant', 'occupied', %s)
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
            VALUES (%s, 'occupied', 'vacant', %s)
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
