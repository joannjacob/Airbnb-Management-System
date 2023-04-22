CREATE DATABASE IF NOT EXISTS airbnb;

USE airbnb;

DROP TABLE IF EXISTS Countries;

CREATE TABLE Countries (
  country_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) UNIQUE
);

DROP TABLE IF EXISTS States;

CREATE TABLE States (
  state_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) UNIQUE,
  country_id INT NOT NULL,
  FOREIGN KEY (country_id) REFERENCES Countries(country_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Cities;

CREATE TABLE Cities (
  city_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) UNIQUE,
  state_id INT NOT NULL,
  FOREIGN KEY (state_id) REFERENCES States(state_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Neighbourhoods;

CREATE TABLE Neighbourhoods (
    neighbourhood_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city_id INT NOT NULL,
    CONSTRAINT unique_neighbourhood_name_city UNIQUE (name, city_id),
    FOREIGN KEY (city_id) REFERENCES Cities (city_id)
);

DROP TABLE IF EXISTS PropertyTypes;

CREATE TABLE PropertyTypes (
  property_type_name VARCHAR(255) PRIMARY KEY
);

DROP TABLE IF EXISTS RoomTypes;

CREATE TABLE RoomTypes (
  room_type_name VARCHAR(255) PRIMARY KEY
);

DROP TABLE IF EXISTS Users; 

CREATE TABLE Users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS Hosts;

CREATE TABLE Hosts (
  user_id INT NOT NULL,
  host_about TEXT,
  host_location VARCHAR(255),
  host_is_superhost BOOLEAN DEFAULT FALSE,
  host_total_listings_count INT DEFAULT 0,
  host_neighbourhood INT,
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (host_neighbourhood) REFERENCES Neighbourhoods(neighbourhood_id) 
			ON DELETE SET NULL ON UPDATE CASCADE
);

DROP TABLE IF EXISTS Guests;

CREATE TABLE Guests (
  user_id INT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Listings;

CREATE TABLE Listings (
  listing_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL DEFAULT 'Not available',
  price FLOAT,
  latitude FLOAT,
  longitude FLOAT,
  minimum_nights INT,
  maximum_nights INT,
  description TEXT,
  occupancy INT,
  bedrooms INT,
  bathrooms INT,
  license VARCHAR(200) NOT NULL,
  has_availability BOOLEAN DEFAULT FALSE,
  amenities TEXT,
  host_id INT NOT NULL,
  neighbourhood_id INT,
  property_type_name VARCHAR(255),
  room_type_name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT unique_listing_name_host UNIQUE (name, host_id),
  FOREIGN KEY (host_id) REFERENCES Hosts(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (neighbourhood_id) REFERENCES Neighbourhoods(neighbourhood_id) 
			ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (property_type_name) REFERENCES PropertyTypes(property_type_name)
			ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (room_type_name) REFERENCES RoomTypes(room_type_name)
			ON DELETE SET NULL ON UPDATE CASCADE
);

DROP TABLE IF EXISTS Bookings;

CREATE TABLE Bookings (
  booking_id INT AUTO_INCREMENT PRIMARY KEY,
  booking_name VARCHAR(64) NOT NULL,
  checkin_date DATE NOT NULL,
  checkout_date DATE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  user_id INT NOT NULL,
  listing_id INT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES Guests(user_id) ON DELETE CASCADE,
  FOREIGN KEY (listing_id) REFERENCES Listings(listing_id) ON DELETE CASCADE,
  UNIQUE (user_id, booking_name)
);

DROP TABLE IF EXISTS Reviews;

CREATE TABLE Reviews (
  review_id INT AUTO_INCREMENT PRIMARY KEY,
  review_comment TEXT NOT NULL,
  rating INT,
  booking_id INT,
  user_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id) ON DELETE SET NULL,
  FOREIGN KEY (user_id) REFERENCES Guests(user_id) ON DELETE SET NULL
);

-- Triggers

DROP TRIGGER IF EXISTS update_host_total_listings_count;

DELIMITER //
CREATE TRIGGER update_host_total_listings_count
AFTER INSERT ON Listings
FOR EACH ROW
BEGIN
  UPDATE Hosts 
  SET host_total_listings_count = (SELECT COUNT(*) FROM Listings WHERE host_id = NEW.host_id)
  WHERE user_id = NEW.host_id;
END //
DELIMITER ;


DROP TRIGGER IF EXISTS update_host_total_listings_count_on_delete;

DELIMITER //
CREATE TRIGGER update_host_total_listings_count_on_delete
AFTER DELETE ON Listings
FOR EACH ROW
BEGIN
    UPDATE Hosts
    SET host_total_listings_count = (SELECT COUNT(*) FROM Listings WHERE host_id = OLD.host_id)
    WHERE Hosts.user_id = OLD.host_id;
END //
DELIMITER ;

/* 
-- This logic does not apply to imported data from Inside Airbnb
DROP TRIGGER IF EXISTS update_host_is_superhost;

DELIMITER //
CREATE TRIGGER update_host_is_superhost
BEFORE UPDATE ON Hosts
FOR EACH ROW
BEGIN
    IF NEW.host_total_listings_count > 5 THEN
        SET NEW.host_is_superhost = 1;
    END IF;
END //
DELIMITER ;
*/

-- Procedures

DROP PROCEDURE IF EXISTS search_listings;

DELIMITER //
CREATE PROCEDURE search_listings (
  IN neighbourhood INT,
  IN min_price INT,
  IN max_price INT,
  IN checkin_date DATE,
  IN checkout_date DATE
)
BEGIN
  SELECT l.*
  FROM Listings l
  JOIN Neighbourhoods n ON l.neighbourhood_id = n.neighbourhood_id
  WHERE n.neighbourhood_id = neighbourhood
    AND l.price BETWEEN min_price AND max_price
    AND l.has_availability = TRUE
    AND NOT EXISTS (
      SELECT *
      FROM Bookings b
      WHERE b.listing_id = l.listing_id
        AND (b.checkin_date <= checkout_date AND b.checkout_date >= checkin_date)
    );
END //
DELIMITER ;

-- Functions

DROP FUNCTION IF EXISTS avg_listing_rating;

DELIMITER //
CREATE FUNCTION avg_listing_rating(listing_id_p INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE avg_rating DECIMAL(10,2);
	SELECT AVG(r.rating) INTO avg_rating 
    FROM Listings l 
    INNER JOIN Bookings b ON l.listing_id = b.listing_id 
    INNER JOIN Reviews r ON b.booking_id = r.booking_id 
    WHERE l.listing_id = listing_id_p;
	RETURN avg_rating;
END //
DELIMITER ;



-- Select statements

-- Tables that are populated by the admin of the application
SELECT * FROM Countries;
SELECT * FROM States;
SELECT * FROM Cities;
SELECT * FROM Neighbourhoods;
SELECT * FROM RoomTypes;
SELECT * FROM PropertyTypes;

-- User structure

SELECT * FROM Users;
SELECT COUNT(*) FROM Users;
-- Modify email based on user
SELECT * FROM Users WHERE email = 'sriram@airbnb.com';
SELECT * FROM Users WHERE email = 'joann@airbnb.com';
SELECT * FROM Users WHERE email = 'host@airbnb.com';

SELECT * FROM Guests;
SELECT * FROM Guests WHERE user_id = (SELECT user_id FROM Users WHERE email = 'sriram@airbnb.com');

SELECT * FROM Hosts;
SELECT COUNT(*) FROM Hosts;
-- Modify email based on user
SELECT * FROM Hosts WHERE user_id = (SELECT user_id FROM Users WHERE email = 'joann@airbnb.com');
SELECT * FROM Hosts WHERE user_id = (SELECT user_id FROM Users WHERE email = 'host@airbnb.com');
-- DELETE FROM Users WHERE email = 'host@airbnb.com';

-- Listings, Bookings and  Reviews

SELECT * FROM Listings;
SELECT COUNT(*) FROM Listings;
-- Modify email based on user
SELECT * FROM Listings WHERE host_id = (SELECT user_id FROM Users WHERE email = 'host@airbnb.com');

SELECT * FROM Bookings;
SELECT * FROM Reviews;

