# Test Case Prioritization Handover Document
This system is a Flask-based web application that provides test report management, including user registration, login, task report creation, editing, deletion, and comparison.

## Startup Steps

### Start the Server in VS Code

1. **Open the Project Folder**

   - Navigate to the `testcasedb_UAT` project folder.
   - Right-click on the `testcasedb_UAT` folder.
   - Select "Open with Code" from the context menu.
     
		![image](https://github.com/A854949/TestCasePrioritization/assets/82749575/a77f9895-1aed-4c10-acde-577bb1f5b4eb)

2. **Open `server.py` File**

   Find the `server.py` file in the project directory and click to open it.

3. **Run the Server**

   In the opened `server.py` file, click the run button (with a play symbol) in the top-right corner.

   Upon successful execution, the terminal will display something like:
   ```plaintext
   * Running on http://15.34.25.120:5010/ (Press CTRL+C to quit)

### Access the Web Pages

1. **Open Browser**

   Open your preferred web browser.

2. **Access the Home Page**

   Enter the following URL in the address bar and visit:

   ```plaintext
   http://15.34.25.120:5010/

   You should see the home page load.

## Create Database and Tables (If setting up the server on another computer)

1. **Create Database**

   Log in to MySQL and create a database named `test`:
   ```sql
   CREATE DATABASE test;

2. **Create Tables**

   Switch to the `test` database and create the required tables:

   ```sql
   USE test;

USE test;

CREATE TABLE users (
    UUID VARCHAR(36) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    PRIMARY KEY (UUID)
);

CREATE TABLE taskReport (
    `Task ID` VARCHAR(50) NOT NULL,
    `Task Title` VARCHAR(100),
    `Testing Site` VARCHAR(100),
    `Start Date` DATE,
    `End Date` DATE,
    `Creator` VARCHAR(50),
    `Created_at` DATETIME,
    PRIMARY KEY (`Task ID`)
);

CREATE TABLE abc (
    `UUID` VARCHAR(36) NOT NULL,
    `Task ID` VARCHAR(50) NOT NULL,
    `Case Title` VARCHAR(100),
    `Pass/Fail` VARCHAR(10),
    `Tester` VARCHAR(50),
    `Platform Name` VARCHAR(50),
    `SKU` VARCHAR(50),
    `Hw Phase` VARCHAR(50),
    `OBS` VARCHAR(50),
    `Block Type` VARCHAR(50),
    `File` VARCHAR(50),
    `KAT/KUT` VARCHAR(50),
    `RTA` VARCHAR(50),
    `ATT/UAT` VARCHAR(50),
    `Run Cycle` VARCHAR(50),
    `Fail Cycle/Total Cycle` VARCHAR(50),
    `Case Note` TEXT,
    `Comments` TEXT,
    `Component List` TEXT,
    `Comment` TEXT,
    `Category` VARCHAR(50),
    PRIMARY KEY (`UUID`)
);

CREATE TABLE biosTaskReport (
    `BIOS Version` VARCHAR(50) NOT NULL,
    `Creator` VARCHAR(50),
    `Created_at` DATETIME,
    PRIMARY KEY (`BIOS Version`)
);

CREATE TABLE def (
    `UUID` VARCHAR(36) NOT NULL,
    `BIOS Version` VARCHAR(50) NOT NULL,
    `Test Case Number` VARCHAR(50),
    `Test Case Name` VARCHAR(100),
    `Result` VARCHAR(50),
    `Comment` TEXT,
    PRIMARY KEY (`UUID`)
);






   
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
