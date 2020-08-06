-- tables
-- Table: client
CREATE TABLE client (
    id int NOT NULL AUTO_INCREMENT,
    first_name varchar(128) NOT NULL,
    last_name varchar(128) NOT NULL,
    client_email varchar(128) NOT NULL,
    google_id varchar(256) NOT NULL,
    client_image varchar(256) NOT NULL,
    role_type varchar(65) NOT NULL,
    CONSTRAINT client_pk PRIMARY KEY (id)
);

-- Table: payment_details
CREATE TABLE payment_details (
    id int NOT NULL AUTO_INCREMENT,
    reservation_id int NOT NULL,
    value int NOT NULL,
    days int NOT NULL,
    total int NOT NULL,
    CONSTRAINT payment_details_pk PRIMARY KEY (id)
);

-- Table: reservation
CREATE TABLE reservation (
    id int NOT NULL AUTO_INCREMENT,
    client_id int NOT NULL,
    room_id int NOT NULL,
    date_in date NOT NULL,
    date_out date NOT NULL,
    CONSTRAINT reservation_pk PRIMARY KEY (id)
);

-- Table: room
CREATE TABLE room (
    id int NOT NULL AUTO_INCREMENT,
    room_type_id int NOT NULL,
    room_status varchar(128) NOT NULL,
    room_num int NOT NULL,
    CONSTRAINT room_pk PRIMARY KEY (id)
);

-- Table: room_type
CREATE TABLE room_type (
    id int NOT NULL AUTO_INCREMENT,
    type_name varchar(64) NOT NULL,
    price int NOT NULL,
    CONSTRAINT room_type_pk PRIMARY KEY (id)
);

-- foreign keys
-- Reference: payment_details_reservation (table: payment_details)
ALTER TABLE payment_details ADD CONSTRAINT payment_details_reservation FOREIGN KEY payment_details_reservation (reservation_id)
    REFERENCES reservation (id);

-- Reference: reservation_client (table: reservation)
ALTER TABLE reservation ADD CONSTRAINT reservation_client FOREIGN KEY reservation_client (client_id)
    REFERENCES client (id);

-- Reference: reservation_room (table: reservation)
ALTER TABLE reservation ADD CONSTRAINT reservation_room FOREIGN KEY reservation_room (room_id)
    REFERENCES room (id);

-- Reference: room_room_type (table: room)
ALTER TABLE room ADD CONSTRAINT room_room_type FOREIGN KEY room_room_type (room_type_id)
    REFERENCES room_type (id);

-- Triggers to automatically populate/delete specific payment_details tables after reservation inserts

DELIMITER $$

CREATE TRIGGER `after_reservation_insert` AFTER INSERT ON `reservation` FOR EACH ROW
BEGIN
    INSERT INTO payment_details(reservation_id, value, days, total)  
    SELECT NEW.id, price, datediff(date_out,date_in), price * (datediff(date_out,date_in))
        FROM room, room_type, reservation
            WHERE room.id = (SELECT room_id FROM reservation WHERE reservation.id = NEW.id)
            AND room_type_id = room_type.id
            AND reservation.id = NEW.id; 
       
END $$

CREATE TRIGGER `before_reservation_delete` BEFORE DELETE ON `reservation` FOR EACH ROW
BEGIN
    DELETE FROM payment_details WHERE reservation_id = OLD.id;
END $$

DELIMITER ;

-- End of file.