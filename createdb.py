import sqlite3
import hashlib

def password_encode (password):
    salt = "2as3df4gh5jk6l"
    db_password = password+salt
    h = hashlib.md5(db_password.encode())
    return h.hexdigest()

con = sqlite3.connect('bookshop.db')
con.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,password TEXT NOT NULL, type TEXT NOT NULL)')
print("Table created successfully.")
con.close()

password = password_encode('p455w0rd')
con = sqlite3.connect('bookshop.db')
cur = con.cursor()
cur.execute("INSERT INTO users (username, password, type) VALUES (?,?,?),(?,?,?),(?,?,?)", ('customer1', password, 'customer', 'customer2', password, 'customer', 'admin', password, 'admin'))
con.commit()
con.close()

con = sqlite3.connect('bookshop.db')
con.execute('CREATE TABLE books (isbn VARCHAR[13] PRIMARY KEY , name TEXT NOT NULL, author TEXT NOT NULL, date DATE NOT NULL, description TEXT NOT NULL, picture TEXT NOT NULL, quantity INTEGER, retail_price FLOAT, trade_price FLOAT)')
print("Table created successfully.")
con.close()



