import string
import random
from datetime import datetime
from flask import Flask, g
from functools import wraps
from flask import *
import sqlite3

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = sqlite3.connect('db/watchparty.sqlite3')
        db.row_factory = sqlite3.Row
        setattr(g, '_database', db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    db = get_db()
    cursor = db.execute(query, args)
    rows = cursor.fetchall()
    db.commit()
    cursor.close()
    if rows:
        if one: 
            return rows[0]
        return rows
    return None

## home page route
@app.route('/')
def home():
    return render_template('home_page.html')

## login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database to check if the user exists and the password is correct
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Successful login, redirect to home page or dashboard
            return redirect(url_for('home_page'))
        else:
            # Failed login, set error message
            error = "Invalid username or password. Please try again."
    return render_template('login_page.html', error=error)

## signup route
# this page is not working
app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists in the database
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            error = "Username already exists. Please choose a different username."
        else:
            # Insert new user into the database
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            cursor.close()
            return redirect(url_for('login_page'))  # Redirect to login page after successful signup

    return render_template('signup.html', error=error)


@app.route('/profile')
@app.route('/room')
@app.route('/room/<chat_id>')
def index(chat_id=None):
    return app.send_static_file('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return app.send_static_file('404.html'), 404



# -------------------------------- API ROUTES ----------------------------------

def new_user():
    name = "Unnamed User #" + ''.join(random.choices(string.digits, k=6))
    password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    api_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))
    u = query_db('insert into users (name, password, api_key) ' + 
        'values (?, ?, ?) returning id, name, password, api_key',
        (name, password, api_key),
        one=True)
    return u

def get_user_from_cookie(request):
    user_id = request.cookies.get('user_id')
    password = request.cookies.get('user_password')
    if user_id and password:
        return query_db('select * from users where id = ? and password = ?', [user_id, password], one=True)
    return None

def validate_user_api_key(req):
    api_key = req.headers['Api-Key']
    if api_key:
        return query_db('select * from users where api_key = ?', [api_key], one=True)
    return None

@app.route('/api/signup', methods = ['POST'])
def signup():
    print("signup")
    if request.method == 'POST':
        user = new_user()
        print(user['api_key'])
        return {'api_key': user['api_key'], 'user_id': user['id'], 'user_name': user['name']}
    return {'Status: unable to create the user!'}, 401

'''
@app.route('/api/login', methods = ['POST'])
def login():
    print("login")
    if request.method == 'POST':
        name = request.headers['userName']
        password = request.headers['password']
        print(name, password)
        u = query_db('select id, api_key, name from users where name = ? and password = ?', [name, password], one=True)
        if not u:
            return {'api_key': ''}
        return {'api_key': u[1], 'user_id': u[0], 'user_name': u[2]}
    return {'api_key': ''}
'''

@app.route('/api/rooms/new', methods=['POST'])
def create_room():
    print("create room")
    user = validate_user_api_key(request)
    if not user:
        return app.send_static_file('404.html'), 401

    if (request.method == 'POST'):
        name = "Unnamed Room " + ''.join(random.choices(string.digits, k=6))
        room = query_db('insert into rooms (name) values (?) returning id', [name], one=True)            
        return {'room_id': room["id"]}
    
@app.route('/api/room/messages', methods=['GET'])
def get_all_messages():
    out = {}
    user = validate_user_api_key(request)
    if not user:
        return app.send_static_file('404.html'), 401
    if request.method == 'GET':
        room_id = request.args['room_id']
        msgs = query_db('select m.id, u.name, m.body from messages m, users u '
                       'where m.room_id = ? and m.user_id = u.id order by m.id', [room_id], one=False)
        if not msgs:
            return out
        for msg in msgs:
            out[msg[0]] = {'id': msg[0], 'name': msg[1], 'body': msg[2]}
    return out, 200

@app.route('/api/room/post', methods=['POST'])
def post_message():
    user = validate_user_api_key(request)
    if not user:
        return app.send_static_file('404.html'), 401
    if request.method == 'POST':
        u = query_db('insert into messages (user_id, room_id, body) ' + 
            'values (?, ?, ?) returning id, user_id, room_id, body',
            (request.headers['User-Id'], request.args['room_id'], request.args['body']), one=True)
        return {'status': 'Success'}, 200

@app.route('/api/update/username', methods=['POST'])
def update_username():
    user = validate_user_api_key(request)
    if not user:
        return app.send_static_file('404.html'), 401
    
    if request.method == 'POST':
        temp = query_db('update users set name = ? where api_key = ? returning id, name',
            (request.args['user_name'], request.headers['Api-Key']),
            one=True
        )
        return {'name': temp['name']}
    return {}

@app.route('/api/update/password', methods=['POST'])
def update_password():
    user = validate_user_api_key(request)
    if not user:
        return app.send_static_file('404.html'), 401
    
    if request.method == 'POST':
        temp = query_db('update users set password = ? where api_key = ? returning id, name',
            (request.headers['password'], request.headers['Api-Key']),
            one=True
        )
        return {}, 200
    return {'Status': 'Failed for Unknown Reasons'}, 403

@app.route('/api/rooms', methods=['GET'])
def get_all_rooms():
    out = {}
    user = validate_user_api_key(request)
    if not user:
        return app.send_static_file('404.html'), 401
    if request.method == 'GET':
        rooms = query_db('select * from rooms')
        
        for msg in rooms:
            out[msg['id']] = {'name': msg['name']}
    return out, 200

@app.route('/api/update/room', methods=['POST'])
def update_room():
    user = validate_user_api_key(request)
    if not user:
        return app.send_static_file('404.html'), 401
    
    if request.method == 'POST':
        temp = query_db('update rooms set name = ? where id = ? returning id, name',
            (request.args['name'], request.args['room_id']),
            one=True
        )
        return {}, 200
    return app.send_static_file('404.html'), 401


@app.route('/api/signup/details', methods = ['POST'])
def signup_details():
    print("signup")
    if request.method == 'POST':
        api_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))
        user = query_db('insert into users (name, password, api_key) ' + 
        'values (?, ?, ?) returning id, name, password, api_key',
        (request.headers['userName'], request.headers['Password'], api_key),
        one=True)
        return {'api_key': user['api_key'], 'user_id': user['id'], 'user_name': user['name']}
    return {'Status: unable to create the user!'}, 401


@app.route('/api/error', methods = ['POST'])
def panic():
    return app.send_static_file('404.html'), 404
