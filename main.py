from flask import Flask
from markupsafe import escape
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import abort
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
        if do_the_login(request.form['username'], request.form['password']):
            session['username'] = request.form['username'] 
            return render_template('homepage.html',page=url_for('homepage'))
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

@app.route('/home')
@login_required
def homepage():
    return render_template('homepage.html',page=url_for('homepage'))

@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    if request.method == 'POST':
        picture = upload_file(request.files, app.config['UPLOAD_FOLDER'])
        data = dict(request.form)
        #https://stackoverflow.com/questions/40414526/how-to-read-multipart-form-data-in-flaskpicture = upload_file(request.files, app.config['UPLOAD_FOLDER'])
        if add_books(data['isbn'], data['name'], data['author'], data['date'], data['description'], picture, data['quantityRange'], data['retailRange'], data['tradeRange']):
            return render_template('homepage.html',page=url_for('homepage'), message='Book added.')
        else:
            return render_template('add_stock.html',page=url_for('add_stock'), error='Invalid book.')
    else:
        return render_template('add_stock.html',page=url_for('add_stock'))