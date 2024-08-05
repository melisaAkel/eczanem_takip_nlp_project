CREATE DATABASE IF NOT EXISTS eczanemtakipdb;

USE eczanemtakipdb;

CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    surname VARCHAR(80) NOT NULL,
    name VARCHAR(80) NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    mail VARCHAR(120) UNIQUE NOT NULL
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
    public_number VARCHAR(80) NOT NULL,  -- Added publicNumber
    name VARCHAR(80) NOT NULL,
    brand VARCHAR(80) NOT NULL,
    form VARCHAR(80),
    reorder_level INT NOT NULL,
    barcode VARCHAR(80) NOT NULL,
    equivalent_medicine_group VARCHAR(80)  -- Added equivalent_medicine_group
);

CREATE TABLE active_ingredient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    amount VARCHAR(80) NOT NULL,
    medicine_id INT NOT NULL,
    FOREIGN KEY (medicine_id) REFERENCES medicine(id)
);

CREATE TABLE medicine_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT NOT NULL,
    supplier_id INT NOT NULL,
    expiry_date DATE NOT NULL,
    quantity INT NOT NULL,
    storage_conditions VARCHAR(255),
    FOREIGN KEY (medicine_id) REFERENCES medicine(id),
    FOREIGN KEY (supplier_id) REFERENCES supplier(id),
    UNIQUE (medicine_id, supplier_id, expiry_date)
);

CREATE TABLE user_medicine (
    user_id INT NOT NULL,
    medicine_id INT NOT NULL,
    PRIMARY KEY (user_id, medicine_id),
    FOREIGN KEY (user_id) REFERENCES User(id),
    FOREIGN KEY (medicine_id) REFERENCES medicine(id)
);
