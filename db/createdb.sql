CREATE TABLE users(
    user_id INTEGER PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(255),
    language_code VARCHAR(5),
    is_notification_on BOOLEAN DEFAULT FALSE,
    notification_time TIME DEFAULT (TIME('22:00:00')),
    created DATETIME DEFAULT (DATETIME('now', 'localtime'))
);

CREATE TABLE skills(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    spent_hours DECIMAL(10, 2) CHECK(spent_hours >= 0),
    description TEXT,
    FOREIGN KEY(owner_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
);