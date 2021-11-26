from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from databasemanager import *
from processing import *
from flask import g
import functools
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.before_request
def user_logged_in():
    user_id = session.get('username')
    if user_id is None:     #if there is no session for the user (the user did’t sign in)
        g.user = None       #set user to none
    else:
        g.user='set'        #set user to 'set'(the user logged in)

def login_required(view):       #function to verify if the user signed in
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:      #if the user doesnt have a sign in session 
            return redirect(url_for('login'))       #the user is redirect to the login page
        return view(**kwargs)
    return wrapped_view

@app.route('/')
def loginredirect():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':        
        type = do_the_login(request.form['username'], request.form['password'])     #check if the user exists and if so returns the type
        if type:        #if user exists    
            session['username'] = request.form['username']      #saves the username used in the login in a session
            session['type'] = type      #saves the type of user according to the account that did the login in a session
            return redirect(url_for('homepage'))        #goes to the homepage
        else:       
            return render_template('login.html',page=url_for('login'), error='Wrong username or password.')     #the username or password are not correct so it displays an error message in the login page
    else:       #if it's method 'GET'
        if 'success' in session:        #If the user registered successfully and was redirected to the login page
            success = session["success"]        #there will be a session with a success message
            session.pop("success")      #deletes the session to avoid repeting the success message
        else:
            success=""      
        return render_template('login.html',page=url_for('login'), success=success)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if add_accounts(request.form['username'], request.form['password']):        #checks if the username already exists and adds the account to the db if it doesn't exist using the add_accounts function
            session["success"] = "Account added."       #message that will be displayed in the login page      
            return redirect(url_for('login'))
        else:       #if the username already exists
            return render_template('register.html',page=url_for('register'), error='Invalid account.')      #shows an error message
    else:
        return render_template('register.html',page=url_for('register'))

@app.route('/logout')
@login_required
def logout():
    session.clear()     #deletes all the existing sessions
    return redirect(url_for('login'))       #goes to the login page
    
@app.route('/homepage')
@login_required
def homepage():
    rows = display_books_homepage()     #uses a function to get the books information 
    if 'error' in session:      #if a function sends a session error to the homepage      
        error = session["error"]
        session.pop("error")        #deletes the error
    else:
        error=""
    return render_template('homepage.html', books = rows, type = session['type'], error=error, isShoppingCart=True)
    
@app.route('/stock_level')
@login_required
def stock_level():
    if session["type"] == "customer":       #page not available for customers
        return redirect(url_for('homepage'))
    
    rows = display_books_stock_level()      #uses a function from the databasemanager.py file to get the books information 
    return render_template('stock_level.html', books = rows)

@app.route('/delete_book_stock/<isbn>')
@login_required
def delete_book_stock(isbn):
    if session["type"] == "customer":       #page not available for customers       
        return redirect(url_for('homepage'))
    
    delete_book_stock_level(isbn, app.config['UPLOAD_FOLDER'])
    return redirect(url_for('stock_level'))


@app.route('/quantity_book_stock/<isbn>', methods=['GET', 'POST'])
@login_required
def quantity_book_stock(isbn):
    if session["type"] == "customer":       #page not available for customers
        return redirect(url_for('homepage'))
    
    if request.method == 'POST':
        change_book_quantity(request.form['quant'], isbn)       #function to change the book quantity in stock
    return redirect(url_for('stock_level'))


@app.route('/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    if session["type"] == "customer":       #only an admin is able to see this route so if a user tries to access it he will be redirected to the homepage
        return redirect(url_for('homepage'))
    
    if request.method == 'POST':
        picture = upload_file(request.files, app.config['UPLOAD_FOLDER'])       #stores the picture and retuns its name
        data = dict(request.form)       #stores the data from the form
        #code inspired in https://stackoverflow.com/questions/40414526/how-to-read-multipart-form-data-in-flask
        result = add_books(data['isbn'], data['name'], data['author'], data['date'], data['description'], picture, data['quantityRange'], data['retailRange'], data['tradeRange'])      #adds the book with the form's values        
        if result == True:      #if all the fields are correct the user will go to the Homepage
            return redirect(url_for('homepage'))
        else:
            return render_template('add_stock.html',page=url_for('add_stock'), error=result)        #if there is any issue in the result it will be displayed an error message in the Add Stock page
    else:
        return render_template('add_stock.html',page=url_for('add_stock'))


@app.route('/add_to_cart/<isbn>/<quantity>/<name>')     
@login_required
def add_to_cart(isbn, quantity, name):      #function used to add items to the Shopping cart
    if session["type"] == "admin":      #page not available to admins
        return redirect(url_for('homepage'))
    
    price = get_price(isbn)     #gets the book price from the db
    if 'cart_books' in session:     #verifies if there is already books in the cart
        if isbn in session["cart_books"]:       #verifies if the book we are trying to add already exists in the cart
            if int(quantity)>session["cart_books"][isbn][0]:        #verifies if there are enough quantity of the book we want to add
                session["cart_books"][isbn][0] += 1     #adds 1 to the quantity of that book in the cart
                session["total_price"] += price     #adds the price of the book to the total price
                session["total_quantity"] += 1      #adds 1 to the total_quantity
            else:
                session["error"] = "Book not available."        #error message when there are not enough books in stock
        else:       #if the book is not in the cart yet
            session["cart_books"][isbn] = [1, price, name]      #sets the quantity of that book in the cart as 1
            session["total_price"] += price     #sets this book price as sum of the total price with the book’s price
            session["total_quantity"] += 1      #sets the total quantity of books in the cart as the total quantity plus 1
    else:       #if there aren't books in the cart
        session["cart_books"] = { isbn: [1, price, name] }      #sets the quantity of that book in the cart as 1
        session["total_price"] = price      #sets this book price as the total price
        session["total_quantity"] = 1       #sets the total quantity of books in the cart as 1
    return redirect(url_for('homepage'))


@app.route('/delete_book_shopping_cart/<isbn>')
@login_required
def delete_book(isbn):
    if session["type"] == "admin":      #page not available for admins 
        return redirect(url_for('homepage'))
    
    session["cart_books"][isbn][0] -= 1     #reduces 1 to the quantity of that book in the cart
    session["total_price"] -= session["cart_books"][isbn][1]        #subtracts the book price from the total price
    session["total_quantity"] -= 1      #reduces 1 to the total quantity books in the cart
    
    if session["cart_books"][isbn][0]==0:       #if the quantity of that book is 0 
        del session["cart_books"][isbn]     #deletes the session that keeps that book
    
    if session["total_quantity"]==0:        #if there are no books in the cart
        session.pop("total_quantity")       #deletes the session that keeps the total quantity of books in the cart
        session.pop("cart_books")       #deletes the session that of books in the cart
        session.pop("total_price")      #deletes the session that keeps the total price of the books in the cart
    return redirect(url_for('homepage'))

@app.route('/delete_shopping_cart')     #function to allow the user all the books in the shopping cart
@login_required
def delete_shopping_cart():
    if session["type"] == "admin":      #page not available for admins
        return redirect(url_for('homepage'))
    
    session.pop("total_quantity")       #deletes the session that keeps the total quantity of books in the cart
    session.pop("cart_books")       #deletes the session of all books in the cart
    session.pop("total_price")      #deletes the session that keeps the total price of the books in the cart
    return redirect(url_for('homepage'))


@app.route('/checkout')
@login_required
def checkout():     #display the books in the shopping cart, checks if there are enough books and calculates the postage cost
    if session["type"] == "admin" or 'cart_books' not in session:      #page not available for admins and users without the cart books session 
        return redirect(url_for('homepage'))
    if 'error' in session:          
        error = session["error"]
        session.pop("error")        #deletes the session error (to prevent the error from repeting)
    else:
        error=""
    results = books_available(session["cart_books"])      #verifies if there are enough books in the db 
    if results == True:       #if there are enough books  
        rows = display_books_checkout(session["cart_books"])        #uses a function from the databasemanager.py file to get the books information 
        if session["total_quantity"] == 1:      #if the cart only has 1 book
            session["postage_cost"] = 3     #the postage cost is 3 pounds
        else:       #if the shopping cart has more than 1 book 
            session["postage_cost"] = 2 + session["total_quantity"]     #calculate the postage cost
        session["total_cost"] = session["total_price"] + session["postage_cost"]        #sets the total cost as the sum of the cart total price and the postage cost
        return render_template('checkout.html', books = rows, type = session['type'], error=error)
            
    else :     #if there are not enough books
        session["error"] = "The quantity you select for the following book(s) is no longer available: " 
        for book in results:        #to show the books that are no longer in stock and set their quantity for the available quantity
            session["total_price"] = session["total_price"] - ((session["cart_books"][book[0]][0] - book[2]) * session["cart_books"][book[0]][1])        #removes the book's price       
            
            session["total_quantity"] -= (session["cart_books"][book[0]][0] - book[2])    #removes the book's quantity from the total quantity
            session["cart_books"][book[0]][0] = book[2]   #removes the quantity for the book we are checking 
            if book[2]==0:      #if the quantity is 0
                del session["cart_books"][book[0]]     #deletes the session that keeps that book
            session["error"] = session["error"] + book[1] + "; "       #error message with the names of the missing books
        if session["total_quantity"] == 0:      #if there are no books in the cart
            session.pop("total_quantity")       #deletes the session that keeps the total quantity of books in the cart
            session.pop("cart_books")       #deletes the session that has each book quantity 
            session.pop("total_price")      #deletes the session that keeps the total price of the books in the cart
            session["error"] = "Your books are no longer available."    
        return redirect(url_for('checkout'))
    

@app.route('/payment_successful')
@login_required
def payment_successful():
    if session["type"] == "admin":      #page not available for admins
        return redirect(url_for('homepage'))
    
    results = books_available(session["cart_books"])      #verifies if there are enough books in the db 
    if results == True:     #if there are enough books
        sell_books(session["cart_books"])       #calls a function to reduce the stock quantity of the books in the cart
        session.pop("total_quantity")       #deletes the session that keeps the total quantity of books in the cart
        session.pop("cart_books")       #deletes the session that of books in the cart
        session.pop("total_price")      #deletes the session that keeps the total price of the books in the cart
        return render_template('payment_successful.html')
    else:
        session["error"] = "The quantity you select for the following book(s) is no longer available, please add them again: " 
        for book in results:        #to show the books that are no longer in stock and removing them from the shopping cart
            session["total_price"] -= (session["cart_books"][book[0]][1] * session["cart_books"][book[0]][0])     #updates the total price      
            session["total_quantity"] -= session["cart_books"][book[0]][0]      #updates the total quantity of books in the cart
            del session["cart_books"][book[0]]      #deletes from the cart the books that are not available  
            session["error"] = session["error"] + book[1] + "; "       #error message with the names of the missing books
        if session["total_quantity"] == 0:      #if there are no books in the cart
            session.pop("total_quantity")       #deletes the session that keeps the total quantity of books in the cart
            session.pop("cart_books")       #deletes the session that of books in the cart
            session.pop("total_price")      #deletes the session that keeps the total price of the books in the cart        
        return redirect(url_for('homepage'))
        
    

    