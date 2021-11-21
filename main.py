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
    if user_id is None:
        g.user = None
    else:
        g.user='set'

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.route('/')
def loginredirect():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        type = do_the_login(request.form['username'], request.form['password'])
        if type:
            session['username'] = request.form['username'] 
            session['type'] = type
            return redirect(url_for('homepage'))
        else:
            return render_template('login.html',page=url_for('login'), error='Wrong username or password.')
    else:
        if 'success' in session:    #If register successfully
            success = session["success"]
            session.pop("success")
        else:
            success=""
        return render_template('login.html',page=url_for('login'), success=success)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if add_accounts(request.form['username'], request.form['password']):
            session["success"] = "Account added."
            return redirect(url_for('login'))
        else:
            return render_template('register.html',page=url_for('register'), error='Invalid account.')
    else:
        return render_template('register.html',page=url_for('register'))

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))    
    
@app.route('/homepage')
@login_required
def homepage():
    rows = display_books_homepage()
    if 'error' in session:
        error = session["error"]
        session.pop("error")
    else:
        error=""
    return render_template('homepage.html', books = rows, type = session['type'], error=error, isShoppingCart=True)
    

@app.route('/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    if request.method == 'POST':
        picture = upload_file(request.files, app.config['UPLOAD_FOLDER'])
        data = dict(request.form)
        #https://stackoverflow.com/questions/40414526/how-to-read-multipart-form-data-in-flaskpicture = upload_file(request.files, app.config['UPLOAD_FOLDER'])
        result = add_books(data['isbn'], data['name'], data['author'], data['date'], data['description'], picture, data['quantityRange'], data['retailRange'], data['tradeRange'])        
        if result == True:
            return redirect(url_for('homepage'))
        else:
            return render_template('add_stock.html',page=url_for('add_stock'), error=result)
    else:
        return render_template('add_stock.html',page=url_for('add_stock'))
    
@app.route('/add_to_cart/<isbn>/<quantity>/<name>')
@login_required
def add_to_cart(isbn, quantity, name):
    price = get_price(isbn)
    if 'cart_books' in session: #verifies if there is already books in the cart
        if isbn in session["cart_books"]: #verifies if the book we are trying to add already exists in the cart
            if int(quantity)>session["cart_books"][isbn][0]: #verifies if there are enough quantity of the book we want to add
                session["cart_books"][isbn][0] += 1
                session["total_price"] += price
                session["total_quantity"] += 1
            else:
                session["error"] = "Book not available."
        else:
            session["cart_books"][isbn] = [1, price, name]
            session["total_price"] += price
            session["total_quantity"] += 1
    else:
        session["cart_books"] = { isbn: [1, price, name] }
        session["total_price"] = price
        session["total_quantity"] = 1
    print(session["cart_books"])
    print(session["total_price"])
    print(session["total_quantity"])
    print (quantity)
    print(session["cart_books"][isbn][0])
    return redirect(url_for('homepage'))


@app.route('/stock_level')
@login_required
def stock_level():
    if session["type"] == "admin":
        rows = display_books_stock_level()
        return render_template('stock_level.html', books = rows)
    return redirect(url_for('homepage'))


@app.route('/delete_book_stock/<isbn>')
@login_required
def delete_book_stock(isbn):
    delete_book_stock_level(isbn, app.config['UPLOAD_FOLDER'])
    return redirect(url_for('stock_level'))


@app.route('/quantity_book_stock/<isbn>', methods=['GET', 'POST'])
@login_required
def quantity_book_stock(isbn):
    if request.method == 'POST':
        change_book_quantity(request.form['quant'], isbn)
    return redirect(url_for('stock_level'))


@app.route('/delete_book_shopping_cart/<isbn>')
@login_required
def delete_book(isbn):
    session["cart_books"][isbn][0] -= 1 
    session["total_price"] -= session["cart_books"][isbn][1]
    session["total_quantity"] -= 1
    
    if session["cart_books"][isbn][0]==0:
        del session["cart_books"][isbn]
    
    if session["total_quantity"]==0:
        session.pop("total_quantity")
        session.pop("cart_books")
        session.pop("total_price")
    return redirect(url_for('homepage'))


@app.route('/checkout')
@login_required
def checkout():
    rows = display_books_checkout(session["cart_books"])
    if session["total_quantity"] == 1:
        session["postage_cost"] = 3
    else:
        session["postage_cost"] = 2 + (1*session["total_quantity"])
    session["total_cost"] = session["total_price"] + session["postage_cost"]
    return render_template('checkout.html', books = rows, type = session['type'])
    

@app.route('/payment_successful')
@login_required
def payment_successful():
    results = buy_books(session["cart_books"])
    if results == True:
        sell_books(session["cart_books"])
        session.pop("total_quantity")
        session.pop("cart_books")
        session.pop("total_price")
        return render_template('payment_successful.html')
    else:
        session["error"] = "The quantity you select for the following book(s) is no longer available, please add them again: " 
        for book in results:
            session["total_price"] -= session["cart_books"][book[0]][1] * session["cart_books"][book[0]][0]
            session["total_quantity"] -= session["cart_books"][book[0]][0]
            del session["cart_books"][book[0]]
            session["error"] = session["error"] + book[1]
        
        return redirect(url_for('homepage'))
        
    

    