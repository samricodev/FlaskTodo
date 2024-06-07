instructions = [
    'SET FOREIGN_KEY_CHECKS=0;',
    'DROP TABLE IF EXISTS todo;',
    'DROP TABLE IF EXISTS user;',
    'SET FOREIGN_KEY_CHECKS=1;',
    """
        CREATE TABLE user (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            paternal VARCHAR(100) NOT NULL,
            maternal VARCHAR(100) NOT NULL,
            birthdate DATE NOT NULL,
            phone VARCHAR(10) NOT NULL,
            email VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(150) NOT NULL,
            FOREIGN KEY (role) REFERENCES role (id)
        );
    """,
    """
        CREATE TABLE todo (
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_by INT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            description TEXT NOT NULL,
            completed BOOLEAN NOT NULL,
            FOREIGN KEY (created_by) REFERENCES user (id)
        );
    """,
    """
        CREATE TABLE  role (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL
        );
    """,
    """
        INSERT INTO role (name) VALUES ('admin');
    """,
    """
        INSERT INTO role (name) VALUES ('user');
    """,
    """
        INSERT INTO user (username, name, paternal, maternal, birthdate, phone, email, password, role)  values ('admin',)
    """
]