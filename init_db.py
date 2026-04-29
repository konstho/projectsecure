# Run once before starting the app:  python init_db.py
import sqlite3

conn = sqlite3.connect('shop.db')
c = conn.cursor()

c.executescript('''
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS reviews;
    DROP TABLE IF EXISTS orders;

    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    );

    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL
    );

    CREATE TABLE reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        username TEXT,
        content TEXT
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        product TEXT,
        total REAL,
        customer_name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        card_last4 TEXT
    );
''')

# Users — passwords stored in plaintext (intentional weakness)
c.executemany('INSERT INTO users (username, password) VALUES (?,?)', [
    ('admin', 'admin'),
    ('alice', 'password1'),
    ('bob',   'qwerty123'),
    ('clara', 'sunshine22'),
    ('david', 'letmein'),
])

c.executemany('INSERT INTO products (name, description, price) VALUES (?,?,?)', [
    ('Headphones', 'Wireless over-ear headphones with noise cancellation.', 89.99),
    ('Keyboard',   'Mechanical keyboard with RGB lighting.',                129.99),
    ('USB-C Hub',  'Seven-in-one hub with HDMI and card reader.',            49.99),
    ('Mouse',      'Silent wireless mouse with long battery life.',          34.99),
])

c.executemany('INSERT INTO reviews (product_id, username, content) VALUES (?,?,?)', [
    (1, 'alice', 'Love these headphones!'),
    (2, 'bob',   'Great keyboard, typing feels nice.'),
    (1, 'clara', 'Good sound but the cable is a bit short.'),
])

# Orders with realistic PII — this is what IDOR exposes
c.executemany('''INSERT INTO orders
    (username, product, total, customer_name, email, phone, address, card_last4)
    VALUES (?,?,?,?,?,?,?,?)''', [
    ('admin', 'Headphones + Keyboard', 219.98,
     'Karl Lindqvist', 'karl.lindqvist@shop.fi', '+358 40 123 4567',
     'Mannerheimintie 12, 00100 Helsinki', '4242'),

    ('alice', 'Headphones', 89.99,
     'Alice Virtanen', 'alice@email.com', '+358 50 987 6543',
     'Runeberginkatu 5 B 23, 00100 Helsinki', '1881'),

    ('bob', 'USB-C Hub', 49.99,
     'Bob Koskinen', 'bob@email.com', '+358 45 555 1234',
     'Iso Roobertinkatu 20, 00120 Helsinki', '5501'),

    ('clara', 'Mouse', 34.99,
     'Clara Nieminen', 'clara.n@gmail.com', '+358 40 222 3333',
     'Tehtaankatu 7, 00140 Helsinki', '9020'),

    ('david', 'Keyboard', 129.99,
     'David Heikkinen', 'd.heikki@outlook.com', '+358 44 777 8888',
     'Bulevardi 31, 00180 Helsinki', '3344'),
])

conn.commit()
conn.close()
print('Database ready.')
