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

CREATE TABLE supplier (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    contact_info VARCHAR(255)
);

CREATE TABLE medicine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    public_number VARCHAR(80) NOT NULL,
    name VARCHAR(80) NOT NULL,
    brand VARCHAR(80) NOT NULL,
    form VARCHAR(80),
    barcode VARCHAR(80) NOT NULL,
    equivalent_medicine_group VARCHAR(80)
);

CREATE TABLE active_ingredient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    amount VARCHAR(80) NOT NULL
);

CREATE TABLE medicine_active_ingredient (
    medicine_id INT,
    active_ingredient_id INT,
    PRIMARY KEY (medicine_id, active_ingredient_id),
    FOREIGN KEY (medicine_id) REFERENCES medicine(id),
    FOREIGN KEY (active_ingredient_id) REFERENCES active_ingredient(id)
);

CREATE TABLE medicine_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT NOT NULL,
    supplier_id INT NOT NULL,
    user_id INT NOT NULL,
    expiry_date DATE NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (medicine_id) REFERENCES medicine(id),
    FOREIGN KEY (supplier_id) REFERENCES supplier(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE user_medicine (
    user_id INT NOT NULL,
    medicine_id INT NOT NULL,
    PRIMARY KEY (user_id, medicine_id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (medicine_id) REFERENCES medicine(id)
);
DELIMITER //

CREATE TRIGGER after_medicine_stock_insert
AFTER INSERT ON medicine_stock
FOR EACH ROW
BEGIN
    DECLARE cnt INT;
    SELECT COUNT(*) INTO cnt FROM user_medicine WHERE user_id = NEW.user_id AND medicine_id = NEW.medicine_id;
    IF cnt = 0 THEN
        INSERT INTO user_medicine (user_id, medicine_id) VALUES (NEW.user_id, NEW.medicine_id);
    END IF;
END //

DELIMITER ;
