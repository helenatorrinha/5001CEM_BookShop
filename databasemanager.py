#from markupsafe import escape
import traceback
import sqlite3
import hashlib

def password_encode (password):
    salt = "2as3df4gh5jk6l"
    db_password = password+salt
    h = hashlib.md5(db_password.encode())
    return h.hexdigest()

def do_the_login(u,p):
    con = sqlite3.connect('bookshop.db')
    cur = con.cursor()
    cur.execute("SELECT count(*), type FROM users WHERE username=? AND password=?;", (u, password_encode(p)))
    results = cur.fetchone()
    if(int(results[0]))>0:                                               
        return results[1]
    else:
        return False

def add_books(isbn, name, author, date, description, picture, quantity, retail_price, trade_price):
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("INSERT INTO books (isbn, name, author, date, description, picture, quantity, retail_price, trade_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (isbn, name, author, date, description, picture, quantity, retail_price, trade_price))
        con.commit()
        return True
    except Exception:
        traceback.print_exc()
        
def add_accounts(username, password):
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT count(*) FROM users WHERE username=?;", (username,))
        if(int(cur.fetchone()[0]))>0:                                               
            return False
        else:
            cur.execute("INSERT INTO users (username, password, type) VALUES (?, ?, ?);", (username, password_encode(password),"customer"))
            con.commit()
        return True
    except Exception:
        traceback.print_exc()
        
def display_books_homepage():
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT name, picture FROM books")
        
        #https://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/
        rows = cur.fetchall()
        return rows
    except Exception:
        traceback.print_exc()        
        
def display_books_stock_level():
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT name, isbn, quantity, picture FROM books")
        rows = cur.fetchall()
        return rows
    except Exception:
        traceback.print_exc()