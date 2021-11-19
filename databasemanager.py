#from markupsafe import escape  #I HAVE TO USE THIS
import traceback
import sqlite3
import hashlib
from processing import remove_picture

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
        cur.execute("SELECT count(*) FROM books WHERE isbn=?;", (isbn,))
        if(int(cur.fetchone()[0]))>0:                                               
            return "The book already exists."
        else:
            cur.execute("INSERT INTO books (isbn, name, author, date, description, picture, quantity, retail_price, trade_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (isbn, name, author, date, description, picture, quantity, retail_price, trade_price))
            con.commit()
            return True
    except Exception:
        traceback.print_exc()
        return "Invalid book."
        
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
        cur.execute("SELECT name, picture, isbn, retail_price, quantity FROM books WHERE quantity>0")
        
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
        
def display_books_checkout(cart):
    try:
        isbnQuery = ""
        for isbn in cart.keys():
            isbnQuery = isbnQuery + "'" + isbn + "', "
        
        print(isbnQuery[:-2])
        
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT name, isbn, quantity, picture FROM books WHERE isbn IN (" + isbnQuery[:-2] + ");")
        rows = cur.fetchall()
        return rows
    except Exception:
        traceback.print_exc()
        
def buy_books (books):
    try:    
        error = []
        isError = False
        for isbn in books.keys():
            con = sqlite3.connect('bookshop.db')
            cur = con.cursor()
            cur.execute("SELECT count(*), isbn FROM books WHERE isbn=? AND quantity>=?;", (isbn, books.get(isbn)[0]))
            book = cur.fetchone()
            if(int(book[0]))<=0: 
                isError = True
                error.append([isbn, books.get(isbn)[2]])
        
        if isError: #If there is an error
            return error
        else:
            return True
    except Exception:
        traceback.print_exc()
        
def sell_books(book):
    try:
        for isbn in book.keys():
            print(isbn)
            con = sqlite3.connect('bookshop.db')
            cur = con.cursor()
            cur.execute("UPDATE books SET quantity = quantity - ? WHERE isbn = ?", (book.get(isbn)[0],isbn))
            con.commit()
    except Exception:
        traceback.print_exc()
        

def delete_book_stock_level(isbn, upload_folder):
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT picture FROM books WHERE isbn=?;", (isbn,))
        picture = cur.fetchone()[0]
        cur.execute("DELETE FROM books WHERE isbn=?",(isbn,))
        con.commit()
        remove_picture(picture, upload_folder)
    except Exception:
        traceback.print_exc()