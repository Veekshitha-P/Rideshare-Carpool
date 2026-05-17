-- ================================================================
--  Carpooling Coordinator — MySQL Database Schema
--  Run: mysql -u root -p < database/schema.sql
-- ================================================================

CREATE DATABASE IF NOT EXISTS carpooling_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE carpooling_db;

-- Drop tables in reverse FK order for clean re-run
-- bookings must be dropped FIRST (it references rides, riders, drivers)
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS rides;
DROP TABLE IF EXISTS riders;
DROP TABLE IF EXISTS drivers;

-- ----------------------------------------------------------------
-- Table 1: drivers
-- ----------------------------------------------------------------
CREATE TABLE drivers (
  id           INT          AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,
  phone        VARCHAR(20)  NOT NULL,
  email        VARCHAR(150) NOT NULL UNIQUE,
  vehicle      VARCHAR(100) NOT NULL,
  license_no   VARCHAR(50)  NOT NULL UNIQUE,
  created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------
-- Table 2: riders
-- ----------------------------------------------------------------
CREATE TABLE riders (
  id           INT          AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,
  phone        VARCHAR(20)  NOT NULL,
  email        VARCHAR(150) NOT NULL UNIQUE,
  created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------
-- Table 3: rides  (main CRUD table — links drivers + riders)
-- ----------------------------------------------------------------
CREATE TABLE rides (
  id              INT          AUTO_INCREMENT PRIMARY KEY,
  driver_id       INT          NOT NULL,
  rider_id        INT,
  pickup_point    VARCHAR(200) NOT NULL,
  dropoff_point   VARCHAR(200) NOT NULL,
  departure_time  DATETIME     NOT NULL,
  total_seats     TINYINT      NOT NULL DEFAULT 3,
  seats_available TINYINT      NOT NULL DEFAULT 3,
  fare_per_seat   DECIMAL(7,2) NOT NULL,
  status          ENUM('available','full','completed','cancelled')
                               NOT NULL DEFAULT 'available',
  created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
                               ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE CASCADE,
  FOREIGN KEY (rider_id)  REFERENCES riders(id)  ON DELETE SET NULL
);

-- ----------------------------------------------------------------
-- Table 4: bookings  (tracks ride bookings — links rides + riders + drivers)
-- ----------------------------------------------------------------
CREATE TABLE bookings (
  booking_id     INT           AUTO_INCREMENT PRIMARY KEY,
  ride_id        INT           NOT NULL,
  rider_id       INT           NOT NULL,
  driver_id      INT           NOT NULL,
  pickup_location  VARCHAR(255),
  dropoff_location VARCHAR(255),
  fare           DECIMAL(10,2),
  seats_booked   INT           NOT NULL DEFAULT 1,
  booking_status ENUM('confirmed','cancelled') NOT NULL DEFAULT 'confirmed',
  booked_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ride_id)   REFERENCES rides(id)   ON DELETE CASCADE,
  FOREIGN KEY (rider_id)  REFERENCES riders(id)  ON DELETE CASCADE,
  FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE CASCADE
);

-- ================================================================
--  Sample Data
-- ================================================================
INSERT INTO drivers (name, phone, email, vehicle, license_no) VALUES
  ('Arjun Mehta',  '9876543210', 'arjun@mail.com', 'Honda City - Silver',   'KA01AB1234'),
  ('Priya Sharma', '9123456789', 'priya@mail.com', 'Maruti Swift - White',  'KA02CD5678'),
  ('Ravi Kumar',   '9988776655', 'ravi@mail.com',  'Hyundai i20 - Blue',    'KA03EF9012'),
  ('Sneha Patel',  '9765432108', 'sneha@mail.com', 'Toyota Innova - Black', 'KA04GH3456');

INSERT INTO riders (name, phone, email) VALUES
  ('Divya Nair',  '9871234560', 'divya@mail.com'),
  ('Karan Joshi', '9654321087', 'karan@mail.com'),
  ('Ananya Roy',  '9345678012', 'ananya@mail.com'),
  ('Manav Gupta', '9012345670', 'manav@mail.com'),
  ('Pooja Singh', '9887654321', 'pooja@mail.com');

INSERT INTO rides (driver_id, rider_id, pickup_point, dropoff_point, departure_time, total_seats, seats_available, fare_per_seat, status) VALUES
  (1, NULL, 'Koramangala, Bangalore', 'Electronic City, Bangalore', '2025-05-10 08:30:00', 3, 3, 80.00,  'available'),
  (2, 1,    'Indiranagar, Bangalore', 'Whitefield, Bangalore',      '2025-05-10 09:00:00', 2, 1, 60.00,  'available'),
  (3, NULL, 'HSR Layout, Bangalore',  'MG Road, Bangalore',         '2025-05-10 07:45:00', 4, 4, 50.00,  'available'),
  (4, 2,    'Jayanagar, Bangalore',   'Hebbal, Bangalore',          '2025-05-09 08:00:00', 6, 4, 70.00,  'available'),
  (1, 3,    'BTM Layout, Bangalore',  'Marathahalli, Bangalore',    '2025-05-09 09:30:00', 3, 2, 55.00,  'completed'),
  (2, NULL, 'Yelahanka, Bangalore',   'Silk Board, Bangalore',      '2025-05-11 07:00:00', 2, 2, 90.00,  'available'),
  (3, 4,    'Rajajinagar, Bangalore', 'Outer Ring Road, Bangalore', '2025-05-08 08:15:00', 3, 0, 65.00,  'full'),
  (4, NULL, 'JP Nagar, Bangalore',    'Airport Road, Bangalore',    '2025-05-11 05:30:00', 6, 6, 120.00, 'available');

-- bookings table starts empty (filled by the app when users book rides)