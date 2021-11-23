import traceback
import sqlite3
import hashlib
from processing import remove_picture

def password_encode (password):     #function to encode the user's password
    salt = "2as3df4gh5jk6l"
    db_password = password+salt 
    h = hashlib.md5(db_password.encode())
    return h.hexdigest()

def do_the_login(u,p):      #function to verify if a user is in the db
    con = sqlite3.connect('bookshop.db')        #connects with the db
    cur = con.cursor()
    cur.execute("SELECT count(*), type FROM users WHERE username=? AND password=?;", (u, password_encode(p)))       #query to check if the account exists and returns the type of account if it exists
    results = cur.fetchone()        #gets the first row
    if(int(results[0]))>0:      #if the first value of the row (count (*)) is bigger than 0 (the user exists)                                          
        return results[1]       #returns the type of the user
    else:       #the user doesn't exist
        return False

def add_books(isbn, name, author, date, description, picture, quantity, retail_price, trade_price):     #add books into the db
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT count(*) FROM books WHERE isbn=?;", (isbn,))        #returns the first row with that input
        if(int(cur.fetchone()[0]))>0:       #if the a book with that isbn already exists                                               
            return "The book already exists."
        else:       #if the a book with that isbn doesn't exist
            cur.execute("INSERT INTO books (isbn, name, author, date, description, picture, quantity, retail_price, trade_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (isbn, name, author, date, description, picture, quantity, retail_price, trade_price))        
            con.commit()
            con.close()
            return True
    except Exception:       #when there is an issue
        traceback.print_exc()
        return "Invalid book."
        
def add_accounts(username, password):
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT count(*) FROM users WHERE username=?;", (username,))
        if(int(cur.fetchone()[0]))>0:       #if the the account with that username already exists                                                
            return False
        else:
            cur.execute("INSERT INTO users (username, password, type) VALUES (?, ?, ?);", (username, password_encode(password),"customer"))     #creates into the db a new account
            con.commit()
            con.close()
        return True
    except Exception:
        traceback.print_exc()
        
def display_books_homepage():       #function that returns the books for the Homepage
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT name, picture, isbn, retail_price, quantity, description FROM books WHERE quantity>0")
        
        #https://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/
        rows = cur.fetchall()       #gets all rows
        return rows
    except Exception:
        traceback.print_exc()        
        
def display_books_stock_level():        #function that books for the Stock Level page
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT name, isbn, quantity, picture FROM books")
        rows = cur.fetchall()
        return rows
    except Exception:
        traceback.print_exc()
        
def display_books_checkout(cart):       #function that returns books for the Checkout page
    try:
        isbnQuery = ""
        for isbn in cart.keys():        #concatenate all the isbn's to be able to select their info in the query
            isbnQuery = isbnQuery + "'" + isbn + "', "
                
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT name, isbn, quantity, picture FROM books WHERE isbn IN (" + isbnQuery[:-2] + ");")
        rows = cur.fetchall()
        return rows
    except Exception:
        traceback.print_exc()
        
def buy_books (books):      #function that verifies all books to check if there are enough quantity in the db to buy
    try:    
        error = []
        isError = False
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        for isbn in books.keys():
            cur.execute("SELECT count(*), isbn FROM books WHERE isbn=? AND quantity>=?;", (isbn, books.get(isbn)[0]))
            book = cur.fetchone()       #gets the first row
            if(int(book[0]))<=0:        #if the book doen't have the necessary quantity of that book, the count is 0, so an error is raised 
                isError = True
                error.append([isbn, books.get(isbn)[2]])        #adds the book info into the error
        
        if isError: #If there is an error
            return error        #returns an array of arrays with the books that didn't have enough quantity
        else:
            return True
    except Exception:
        traceback.print_exc()
        
def sell_books(book):       #function to remove from the db the quantity of books sold
    try:
        con = sqlite3.connect('bookshop.db')
        for isbn in book.keys():        #update the book quantity
            con.execute("UPDATE books SET quantity = quantity - ? WHERE isbn = ?", (book.get(isbn)[0],isbn))
        con.commit()
        con.close()
    except Exception:
        traceback.print_exc()
        

def delete_book_stock_level(isbn, upload_folder):       #fuction to allow admins to delete books from the db
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT picture FROM books WHERE isbn=?;", (isbn,))
        picture = cur.fetchone()[0]     #gets the picture's path
        cur.execute("DELETE FROM books WHERE isbn=?",(isbn,))       #deletes the book 
        con.commit()
        con.close()
        remove_picture(picture, upload_folder)      #deletes the picture
    except Exception:
        traceback.print_exc()
        

def change_book_quantity(quant, isbn):      #fuction to allow admins to set a different quantity of books in the db      
    try:
        con = sqlite3.connect('bookshop.db')
        con.execute("UPDATE books SET quantity = ? WHERE isbn = ?", (quant,isbn))
        con.commit()
        con.close()
    except Exception:
        traceback.print_exc()  
        
    
def get_price(isbn):        #function to send the price of a book from the db
    try:
        con = sqlite3.connect('bookshop.db')
        cur = con.cursor()
        cur.execute("SELECT retail_price FROM books WHERE isbn = ?",(isbn,))
        price = cur.fetchone()[0]
        return price
    except Exception:
        traceback.print_exc()