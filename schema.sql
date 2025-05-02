-- Schemat bazy danych
CREATE DATABASE IF NOT EXISTS unitermdb DEFAULT CHARACTER SET utf8mb4;
USE unitermdb;

DROP TABLE IF EXISTS uniterms;
CREATE TABLE uniterms (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    description  VARCHAR(250),
    a            VARCHAR(250),
    b            VARCHAR(250),
    cond         VARCHAR(250),
    orientation  CHAR(1)   DEFAULT 'H',
    seq_str      VARCHAR(250),
    bracket_on   CHAR(1)   DEFAULT 'A'
);
