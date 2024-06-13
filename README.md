# Test Case Prioritization Handover Document
This system is a Flask-based web application that provides test report management, including user registration, login, task report creation, editing, deletion, and comparison.

## Startup Steps

### Start the Server in VS Code

1. **Open VS Code**

   Open VS Code and ensure your project files are in the workspace.

2. **Open `server.py` File**

   Find the `server.py` file in the project directory and click to open it.

3. **Run the Server**

   In the opened `server.py` file, right-click in the file content area and select “Run Python File” or simply click the green run button (with a play symbol) in the top-right corner.

   Upon successful execution, the terminal will display something like:
   ```plaintext
   * Running on http://0.0.0.0:5010/ (Press CTRL+C to quit)


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
