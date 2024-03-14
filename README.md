# TestCasePrioritization
MySQL

CREATE TABLE testCase (
    `UUID` CHAR(36) NOT NULL,
    `Task ID` VARCHAR(20),
    `Case Title` TEXT,
    `Pass/Fail` VARCHAR(20),
    `Tester` VARCHAR(20),
    `Platform Name` VARCHAR(20),
    `SKU` VARCHAR(20),
    `Hw Phase` VARCHAR(20),
    `OBS` VARCHAR(50),
    `Block Type` VARCHAR(20),
    `File` VARCHAR(20),
    `KAT/KUT` VARCHAR(20),
    `RTA` VARCHAR(20),
    `ATT/UAT` VARCHAR(20),
    `Run Cycle` VARCHAR(20),
    `Fail Cycle/Total Cycle` VARCHAR(50),
    `Case Note` TEXT,
    `Comments` TEXT,
    `Component List` TEXT,
    `Comment` TEXT,
    `Category` VARCHAR(20),
    PRIMARY KEY (`UUID`)
);


DELIMITER $$

CREATE TRIGGER before_insert_abc
BEFORE INSERT ON abc
FOR EACH ROW
BEGIN
    IF NEW.UUID IS NULL OR NEW.UUID = '' THEN
        SET NEW.UUID = UUID();
    END IF;
END$$

DELIMITER ;

/

CREATE TABLE taskReport (
    `Task ID` VARCHAR(20) PRIMARY KEY NOT NULL,
    `Task Title` TEXT,
    `Testing Site` VARCHAR(50),
    `Owner` VARCHAR(20),
    `Start Date`	 VARCHAR(50),
	`End Date` VARCHAR(50)
);

/

CREATE TABLE users (
    `UUID` CHAR(36) PRIMARY KEY NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    UNIQUE (username),
    UNIQUE (email)
);

DELIMITER $$

CREATE TRIGGER before_insert_abc
BEFORE INSERT ON abc
FOR EACH ROW
BEGIN
    IF NEW.UUID IS NULL OR NEW.UUID = '' THEN
        SET NEW.UUID = UUID();
    END IF;
END$$

DELIMITER ;
