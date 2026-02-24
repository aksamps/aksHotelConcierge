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

-- Insert sample reservations
INSERT INTO reservations (room_id, guest_name, guest_email, check_in_date, check_out_date, number_of_guests, special_requests, status, created_at) VALUES
(1, 'Alice Williams', 'alice@example.com', DATE_ADD(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 3 DAY), 2, 'High floor preferred', 'confirmed', NOW()),
(2, 'Bob Brown', 'bob@example.com', DATE_ADD(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 5 DAY), 1, 'Non-smoking room', 'confirmed', NOW()),
(5, 'Carol Davis', 'carol@example.com', DATE_ADD(CURDATE(), INTERVAL 4 DAY), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 3, 'Late checkout needed', 'confirmed', NOW()),
(7, 'David Miller', 'david@example.com', DATE_ADD(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 2 DAY), 1, '', 'confirmed', NOW()),
(9, 'Emma Wilson', 'emma@example.com', DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 8 DAY), 2, 'Birthday party', 'confirmed', NOW());
