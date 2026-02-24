-- Initialize Hotel Concierge Database

USE hotel_concierge;

-- Insert sample rooms
INSERT INTO rooms (id, room_number, floor, status, guest_name) VALUES
(1, '101', 1, 'vacant', NULL),
(2, '102', 1, 'vacant', NULL),
(3, '103', 1, 'occupied', 'John Doe'),
(4, '104', 1, 'maintenance', NULL),
(5, '201', 2, 'vacant', NULL),
(6, '202', 2, 'occupied', 'Jane Smith'),
(7, '203', 2, 'vacant', NULL),
(8, '204', 2, 'vacant', NULL),
(9, '301', 3, 'vacant', NULL),
(10, '302', 3, 'occupied', 'Robert Johnson'),
(11, '303', 3, 'vacant', NULL),
(12, '304', 3, 'maintenance', NULL);
