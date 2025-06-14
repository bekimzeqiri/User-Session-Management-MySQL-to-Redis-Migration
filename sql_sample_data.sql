-- Sample data for testing the migration
USE user_session_management;

-- Insert sample users
INSERT INTO users (username, email, password_hash, created_at, last_login_at) VALUES
('john_doe', 'john.doe@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBbJ2wYJA2WKe2', '2025-01-15 10:30:00', '2025-05-26 09:15:00'),
('jane_smith', 'jane.smith@email.com', '$2b$12$8k7dZ9h5v2nB1mC3xF4jKe9pQ6wR8tY7uI2oP5lA3sD6fG9hJ1kL4', '2025-02-20 14:22:30', '2025-05-25 16:45:30'),
('bob_wilson', 'bob.wilson@email.com', '$2b$12$3n9kL2mX7vQ4wE8rT5yU6pA1sD9fG7hJ2kL5nB8cV4xZ6tR9mQ3p', '2025-03-10 09:45:15', '2025-05-24 12:30:45'),
('alice_brown', 'alice.brown@email.com', '$2b$12$7pQ1wE4rT8yU2iO9kL6nB5cV8xZ1tR4mQ7pA3sD6fG9hJ5kL8nB2', '2025-04-05 11:20:00', '2025-05-26 08:20:10'),
('charlie_davis', 'charlie.davis@email.com', '$2b$12$9hJ2kL5nB8cV1xZ4tR7mQ0pA6sD3fG6hJ9kL2nB5cV8xZ7tR4mQ1', '2025-04-18 16:30:45', '2025-05-25 20:10:30'),
('diana_miller', 'diana.miller@email.com', '$2b$12$1kL4nB7cV0xZ3tR6mQ9pA2sD5fG8hJ1kL4nB7cV0xZ6tR9mQ2pA5', '2025-05-01 13:15:20', '2025-05-26 07:45:15'),
('evan_garcia', 'evan.garcia@email.com', '$2b$12$4nB7cV0xZ6tR9mQ2pA5sD8fG1hJ4nB7cV0xZ9tR2mQ5pA8sD1fG4', '2025-05-10 08:40:30', '2025-05-25 19:25:40'),
('fiona_martinez', 'fiona.martinez@email.com', '$2b$12$7cV0xZ9tR2mQ5pA8sD1fG4hJ7cV0xZ2tR5mQ8pA1sD4fG7hJ0cV3', '2025-05-15 12:10:15', '2025-05-26 11:30:20');

-- Insert user preferences
INSERT INTO user_preferences (user_id, theme, language, notifications_enabled, updated_at) VALUES
(1, 'dark', 'en', TRUE, '2025-05-20 10:30:00'),
(2, 'light', 'es', TRUE, '2025-05-18 14:22:30'),
(3, 'dark', 'fr', FALSE, '2025-05-19 09:45:15'),
(4, 'light', 'en', TRUE, '2025-05-21 11:20:00'),
(5, 'dark', 'de', FALSE, '2025-05-22 16:30:45'),
(6, 'light', 'en', TRUE, '2025-05-23 13:15:20'),
(7, 'dark', 'pt', TRUE, '2025-05-24 08:40:30'),
(8, 'light', 'it', FALSE, '2025-05-25 12:10:15');

-- Insert active user sessions (expires in the future)
INSERT INTO user_sessions (session_id, user_id, ip_address, user_agent, created_at, expires_at, last_activity_at) VALUES
('sess_1a2b3c4d5e6f7g8h', 1, '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '2025-05-26 09:15:00', '2025-05-27 09:15:00', '2025-05-26 14:30:00'),
('sess_2b3c4d5e6f7g8h9i', 2, '192.168.1.101', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', '2025-05-25 16:45:30', '2025-05-26 16:45:30', '2025-05-26 10:20:15'),
('sess_3c4d5e6f7g8h9i0j', 3, '10.0.0.150', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36', '2025-05-24 12:30:45', '2025-05-27 12:30:45', '2025-05-26 11:45:30'),
('sess_4d5e6f7g8h9i0j1k', 4, '203.0.113.25', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15', '2025-05-26 08:20:10', '2025-05-28 08:20:10', '2025-05-26 13:10:45'),
('sess_5e6f7g8h9i0j1k2l', 5, '198.51.100.75', 'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/115.0', '2025-05-25 20:10:30', '2025-05-26 20:10:30', '2025-05-26 09:55:20'),
('sess_6f7g8h9i0j1k2l3m', 6, '172.16.0.200', 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15', '2025-05-26 07:45:15', '2025-05-27 19:45:15', '2025-05-26 12:20:30'),
('sess_7g8h9i0j1k2l3m4n', 7, '192.168.1.102', 'Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0', '2025-05-25 19:25:40', '2025-05-27 07:25:40', '2025-05-26 08:40:15'),
('sess_8h9i0j1k2l3m4n5o', 8, '10.1.1.50', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15', '2025-05-26 11:30:20', '2025-05-28 11:30:20', '2025-05-26 15:15:45');

-- Insert session data (shopping cart, preferences, etc.)
INSERT INTO session_data (session_id, attribute_key, attribute_value, created_at) VALUES
-- John's session data
('sess_1a2b3c4d5e6f7g8h', 'cart_items', '{"products": [{"id": "P001", "name": "Laptop", "quantity": 1, "price": 999.99}, {"id": "P002", "name": "Mouse", "quantity": 2, "price": 29.99}]}', '2025-05-26 09:20:00'),
('sess_1a2b3c4d5e6f7g8h', 'last_viewed_category', 'Electronics', '2025-05-26 10:15:00'),
('sess_1a2b3c4d5e6f7g8h', 'discount_code', 'SAVE10', '2025-05-26 11:30:00'),

-- Jane's session data
('sess_2b3c4d5e6f7g8h9i', 'cart_items', '{"products": [{"id": "P003", "name": "Book", "quantity": 3, "price": 15.99}]}', '2025-05-25 17:00:00'),
('sess_2b3c4d5e6f7g8h9i', 'wishlist', '["P004", "P005", "P006"]', '2025-05-25 18:20:00'),
('sess_2b3c4d5e6f7g8h9i', 'search_history', '["programming books", "python tutorial", "web development"]', '2025-05-26 09:10:00'),

-- Bob's session data
('sess_3c4d5e6f7g8h9i0j', 'cart_items', '{"products": [{"id": "P007", "name": "Headphones", "quantity": 1, "price": 199.99}]}', '2025-05-24 13:00:00'),
('sess_3c4d5e6f7g8h9i0j', 'recently_viewed', '["P007", "P008", "P009"]', '2025-05-25 14:30:00'),

-- Alice's session data
('sess_4d5e6f7g8h9i0j1k', 'cart_items', '{"products": []}', '2025-05-26 08:25:00'),
('sess_4d5e6f7g8h9i0j1k', 'newsletter_popup_shown', 'true', '2025-05-26 08:30:00'),
('sess_4d5e6f7g8h9i0j1k', 'onboarding_step', '3', '2025-05-26 09:00:00'),

-- Charlie's session data
('sess_5e6f7g8h9i0j1k2l', 'cart_items', '{"products": [{"id": "P010", "name": "Smartphone", "quantity": 1, "price": 799.99}, {"id": "P011", "name": "Case", "quantity": 1, "price": 24.99}]}', '2025-05-25 20:15:00'),
('sess_5e6f7g8h9i0j1k2l', 'payment_method', 'credit_card', '2025-05-25 21:00:00'),

-- Diana's session data
('sess_6f7g8h9i0j1k2l3m', 'cart_items', '{"products": [{"id": "P012", "name": "Tablet", "quantity": 1, "price": 399.99}]}', '2025-05-26 08:00:00'),
('sess_6f7g8h9i0j1k2l3m', 'comparison_list', '["P012", "P013", "P014"]', '2025-05-26 09:30:00'),

-- Evan's session data
('sess_7g8h9i0j1k2l3m4n', 'cart_items', '{"products": []}', '2025-05-25 19:30:00'),
('sess_7g8h9i0j1k2l3m4n', 'tour_completed', 'true', '2025-05-25 20:00:00'),
('sess_7g8h9i0j1k2l3m4n', 'feedback_given', 'false', '2025-05-26 07:15:00'),

-- Fiona's session data
('sess_8h9i0j1k2l3m4n5o', 'cart_items', '{"products": [{"id": "P015", "name": "Camera", "quantity": 1, "price": 599.99}]}', '2025-05-26 11:45:00'),
('sess_8h9i0j1k2l3m4n5o', 'shipping_preference', 'express', '2025-05-26 12:00:00'),
('sess_8h9i0j1k2l3m4n5o', 'loyalty_points', '1250', '2025-05-26 12:30:00');
