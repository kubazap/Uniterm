CREATE DATABASE IF NOT EXISTS unitermdb
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;
USE unitermdb;

DROP TABLE IF EXISTS uniterms;
CREATE TABLE uniterms (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    description  VARCHAR(250),

    a            VARCHAR(250),     -- współczynnik A
    b            VARCHAR(250),     -- współczynnik B
    cond         VARCHAR(250),     -- warunek u

    x            VARCHAR(250),     -- współczynnik X
    y            VARCHAR(250),     -- ⇐ współczynnik Y
    cond2        VARCHAR(250),     -- ⇐   warunek u₂

    orientation  CHAR(1) DEFAULT 'H',   -- H / V
    bracket_on   CHAR(1) DEFAULT 'A'    -- A / B
) ENGINE = InnoDB;
