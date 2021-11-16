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
        return show_the_login_form()
    
def show_the_login_form():
    return render_template('login.html',page=url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if add_accounts(request.form['username'], request.form['password']):
            return render_template('login.html',page=url_for('login'), message='Account added.')
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
    return render_template('homepage.html', books = rows, type = session['type'])
    

@app.route('/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    if request.method == 'POST':
        picture = upload_file(request.files, app.config['UPLOAD_FOLDER'])
        data = dict(request.form)
        #https://stackoverflow.com/questions/40414526/how-to-read-multipart-form-data-in-flaskpicture = upload_file(request.files, app.config['UPLOAD_FOLDER'])
        if add_books(data['isbn'], data['name'], data['author'], data['date'], data['description'], picture, data['quantityRange'], data['retailRange'], data['tradeRange']):
            return redirect(url_for('homepage'))
        else:
            return render_template('add_stock.html',page=url_for('add_stock'), error='Invalid book.')
    else:
        return render_template('add_stock.html',page=url_for('add_stock'))
    
@app.route('/add_to_cart/<isbn>/<retail_price>/<quantity>')
@login_required
def add_to_cart(isbn, retail_price, quantity):
    if 'cart_books' in session:
        if isbn in session["cart_books"]:
            session["cart_books"][isbn][0] += 1 
        else:
            session["cart_books"][isbn] = [1, float(retail_price)]
            
        session["total_price"] += float(retail_price)
        session["total_quantity"] += 1
    else:
        session["cart_books"] = { isbn: [1, float(retail_price)] }
        session["total_price"] = float(retail_price)
        session["total_quantity"] = 1
    print(session["cart_books"])
    print(session["total_price"])
    print(session["total_quantity"])
    return redirect(url_for('homepage'))

@app.route('/stock_level')
@login_required
def stock_level():
    if session["type"] == "admin":
        rows = display_books_stock_level()
        return render_template('stock_level.html', books = rows)
    return redirect(url_for('homepage'))

@app.route('/delete_book/<isbn>')
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
    return render_template('checkout.html', books = rows)
    

@app.route('/payment_successful')
@login_required
def payment_successful():
    return render_template('payment_successful.html')
        
    

    