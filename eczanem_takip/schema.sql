CREATE DATABASE IF NOT EXISTS eczanemtakipdb;
USE eczanemtakipdb;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    surname VARCHAR(80) NOT NULL,
    name VARCHAR(80) NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL
);

DROP TABLE IF EXISTS medicine_stock;
DROP TABLE IF EXISTS active_ingredient;
DROP TABLE IF EXISTS user_medicine;
DROP TABLE IF EXISTS medicine;
DROP TABLE IF EXISTS supplier;
DROP TABLE IF EXISTS medicine_sales;

CREATE TABLE supplier (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    contact_info VARCHAR(255)
);

CREATE TABLE medicine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    public_number VARCHAR(80) NOT NULL,
    atc_code VARCHAR(200) NOT NULL,
    report_type ENUM('KIRMIZI', 'MOR','TURUNCU', 'YEŞİL', 'NORMAL') DEFAULT 'NORMAL',
    name VARCHAR(200) NOT NULL,
    brand VARCHAR(200) NOT NULL,
    form VARCHAR(200),
    barcode VARCHAR(200) NOT NULL UNIQUE,
    equivalent_medicine_group VARCHAR(80)
);

CREATE TABLE report (
    date DATE NOT NULL,
    doctor_speciality VARCHAR(80) NOT NULL,
    report_type ENUM('KIRMIZI', 'MOR','TURUNCU', 'YEŞİL', 'NORMAL') DEFAULT 'NORMAL',
    type ENUM('AYAKTAN', 'YATAN') DEFAULT 'AYAKTAN'
);

CREATE TABLE active_ingredient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL
);

CREATE TABLE medicine_active_ingredient (
    medicine_id INT,
    active_ingredient_id INT,
    PRIMARY KEY (medicine_id, active_ingredient_id),
    FOREIGN KEY (medicine_id) REFERENCES medicine(id) ON DELETE CASCADE,
    FOREIGN KEY (active_ingredient_id) REFERENCES active_ingredient(id)
);

CREATE TABLE medicine_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT NOT NULL,
    supplier_id INT NOT NULL,
    user_id INT NOT NULL,
    expiry_date DATE,
    quantity INT NOT NULL,
    FOREIGN KEY (medicine_id) REFERENCES medicine(id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES supplier(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE medicine_sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    medicine_id INT NOT NULL,
    customer_name VARCHAR(80),
    sale_date DATE NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (medicine_id) REFERENCES medicine(id) ON DELETE CASCADE
);

DELIMITER //

CREATE TRIGGER after_medicine_sale_insert
AFTER INSERT ON medicine_sales
FOR EACH ROW
BEGIN
    DECLARE remaining_quantity INT;
    DECLARE required_quantity INT DEFAULT NEW.quantity;
    DECLARE current_stock_id INT;

    DECLARE done INT DEFAULT 0;
    DECLARE stock_cursor CURSOR FOR
        SELECT id, quantity FROM medicine_stock
        WHERE medicine_id = NEW.medicine_id AND user_id = NEW.user_id AND quantity > 0
        ORDER BY expiry_date ASC;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN stock_cursor;

    read_loop: LOOP
        FETCH stock_cursor INTO current_stock_id, remaining_quantity;
        IF done THEN
            LEAVE read_loop;
        END IF;

        IF remaining_quantity >= required_quantity THEN
            UPDATE medicine_stock SET quantity = quantity - required_quantity WHERE id = current_stock_id;
            SET required_quantity = 0;
        ELSE
            UPDATE medicine_stock SET quantity = 0 WHERE id = current_stock_id;
            SET required_quantity = required_quantity - remaining_quantity;
        END IF;

        IF required_quantity = 0 THEN
            LEAVE read_loop;
        END IF;
    END LOOP;

    CLOSE stock_cursor;

    IF required_quantity > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Not enough stock to complete the sale';
    END IF;
END //

DELIMITER ;
ALTER DATABASE eczanemtakipdb CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
ALTER TABLE medicine CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE active_ingredient CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
