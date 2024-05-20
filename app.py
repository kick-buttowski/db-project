'''
import string
import random
from datetime import datetime
from flask import Flask, g
from functools import wraps
from flask import Flask, render_page
import sqlite3
'''
import pymysql
from flask import Flask, jsonify, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# MySQL Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'haha'
app.config['MYSQL_DB'] = 'HavenQuest'
app.config['CURRENT_USER_ID'] = '1635'

FETCH_PROPERTY_CITY_AND_BEDROOMS = 'SELECT CITY, NUMBEDROOMS FROM PROPERTY GROUP BY CITY, NUMBEDROOMS'

LIMITED_PROPERTIES = """SELECT PROP.PROPERTYID,
        PROP.PROPERTYHEADING, 
        PROP.NUMFLOORS, 
        PROP.PROPERTYNAME, 
        PROP.CITY, 
        PROP.NUMBEDROOMS, 
        PROP.NUMBATHROOMS, 
        PROP.PURCHASE_PRICE, 
        PROP.AREA,
        (SELECT PROPERTYID FROM FAVOURITES FV WHERE FV.PROPERTYID = PROP.PROPERTYID AND FV.USERID = %s) AS FAVOURITE,
        CONCAT(AG.FIRSTNAME, ' ', AG.LASTNAME) AS AGENTNAME,
        SC.SOCIETYNAME 
        FROM PROPERTY AS PROP 
        INNER JOIN AGENT AG ON AG.AGENTID = PROP.AGENTID
        INNER JOIN SOCIETY SC ON SC.SOCIETYID = PROP.SOCIETYID 
        WHERE PROP.CITY = %s 
        AND PROP.NUMBEDROOMS = %s
        LIMIT %s"""
        
PROPERTIES_SELECT_QUERY = """SELECT PROP.PROPERTYID,
        PROP.PROPERTYHEADING, 
        PROP.NUMFLOORS, 
        PROP.PROPERTYNAME, 
        PROP.CITY, 
        PROP.NUMBEDROOMS, 
        PROP.NUMBATHROOMS, 
        PROP.PURCHASE_PRICE, 
        PROP.AREA,
        (SELECT PROPERTYID FROM FAVOURITES FV WHERE FV.PROPERTYID = PROP.PROPERTYID AND FV.USERID = %s) AS FAVOURITE,
        CONCAT(AG.FIRSTNAME, ' ', AG.LASTNAME) AS AGENTNAME,
        SC.SOCIETYNAME 
        FROM PROPERTY AS PROP
        {joins}
        {filters}
        {limit}"""
        
LIMIT_SELECT = """LIMIT {lim}"""

FETCH_INDIVIDUAL_PROPERTY = """SELECT PROP.*, SC.*, AG.*, AGC.*, 
        (SELECT PROPERTYID FROM FAVOURITES FV WHERE FV.PROPERTYID = PROP.PROPERTYID AND FV.USERID = %s) AS FAVOURITE 
        FROM PROPERTY AS PROP
        INNER JOIN AGENT AG ON AG.AGENTID = PROP.AGENTID
        INNER JOIN AGENCY AGC ON AGC.AGENCYID = AG.AGENCYID
        INNER JOIN SOCIETY SC ON SC.SOCIETYID = PROP.SOCIETYID
        WHERE PROP.PROPERTYID = %s"""
        
        
FETCH_CITIES = """SELECT DISTINCT(CITY) FROM PROPERTY"""

FETCH_NUMBEDROOMS = """SELECT DISTINCT(NUMBEDROOMS) FROM PROPERTY ORDER BY NUMBEDROOMS ASC"""

FETCH_NUMBEDROOMS_BY_CITY = """SELECT DISTINCT(NUMBEDROOMS) FROM PROPERTY WHERE CITY = %s ORDER BY NUMBEDROOMS ASC"""

FETCH_NUMBATHROOMS = """SELECT DISTINCT(NUMBATHROOMS) FROM PROPERTY ORDER BY NUMBATHROOMS ASC"""

FETCH_NUMBATHROOMS_BY_CITY = """SELECT DISTINCT(NUMBATHROOMS) FROM PROPERTY WHERE CITY = %s ORDER BY NUMBATHROOMS ASC"""

FETCH_SOCIETIES_BY_CITY = """SELECT DISTINCT(SOCIETYNAME) FROM SOCIETY SC 
                            INNER JOIN PROPERTY PROP ON PROP.SOCIETYID = SC.SOCIETYID AND PROP.CITY = %s"""
                            
FETCH_AGENCIES_BY_CITY = """SELECT DISTINCT(AGENCYNAME) FROM AGENCY AGC
							INNER JOIN AGENT AG ON AGC.AGENCYID = AG.AGENCYID
                            INNER JOIN PROPERTY PROP ON PROP.AGENTID = AG.AGENTID AND PROP.CITY = %s"""

INNER_JOIN_AGENCY_AGENTS = """INNER JOIN AGENCY AGC ON AGC.AGENCYID = AG.AGENCYID"""

INNER_JOIN_PROPERTY_AGENT = """INNER JOIN AGENT AG ON AG.AGENTID = PROP.AGENTID"""

INNER_JOIN_PROPERTY_SOCIETY = """INNER JOIN SOCIETY SC ON SC.SOCIETYID = PROP.SOCIETYID"""

all_bedrooms = dict()
cities = dict()
properties_home = list()


# Create MySQL Connection
db = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'],
    cursorclass=pymysql.cursors.DictCursor  # Use dictionary cursor for easy data access
)

cursor = db.cursor()
db.autocommit(True)


# --------------------------- ROUTES ---------------------------

@app.route('/')
def home():
    cursor = db.cursor()
    
    cursor.execute(FETCH_CITIES)
    cities = cursor.fetchall()
    
    return render_template('home_page.html', cities=cities)

@app.route('/api/random_properties', methods=['GET'])
def random_properties():
    # Fetches top 10 records of each city and creates a properties list of it
    cursor = db.cursor()
    
    if properties_home:
        return jsonify(properties_home), 200
    
    cursor.execute(FETCH_PROPERTY_CITY_AND_BEDROOMS)
    cities_and_bedrooms = cursor.fetchall()
    
    for city in cities_and_bedrooms:
        cursor.execute(LIMITED_PROPERTIES, (app.config['CURRENT_USER_ID'], city['CITY'], city['NUMBEDROOMS'], 2))
        fetched_properties = cursor.fetchall()
        
        for property in fetched_properties:
            properties_home.append(property)
    
    return jsonify(properties_home), 200


@app.route('/api/cities_and_bedrooms', methods=['GET'])
def cities_and_bedrooms():
    properties = list()
    cursor = db.cursor()
    
    for city in cities_and_bedrooms:
        cursor.execute(LIMITED_PROPERTIES, (app.config['CURRENT_USER_ID'], city['CITY'], city['NUMBEDROOMS'], 2))
        fetched_properties = cursor.fetchall()
        
        for property in fetched_properties:
            properties.append(property)
        
    return jsonify(properties), 200


@app.route('/individual_property')
def individual_property():
    # Loads the property page
    return render_template('individual_property.html')


@app.route('/api/fetch_ind_property', methods=['GET'])
def fetch_ind_property():
    # Hit the db and get individual proeprty details
    cursor = db.cursor()
    property_id = request.args.get('id')
    
    cursor.execute(FETCH_INDIVIDUAL_PROPERTY, (app.config['CURRENT_USER_ID'], property_id))
    property = cursor.fetchone()
    
    return jsonify(property), 200


@app.route('/api/bedrooms', methods=['GET'])
def bedrooms():
    # Hit the db and get no of bedrooms by city
    cursor = db.cursor()
    city = request.args.get('city')
    
    if city == 'nocity':
        cursor.execute(FETCH_NUMBEDROOMS)
        all_bedrooms = cursor.fetchall()
        return jsonify(all_bedrooms), 200
    
    cursor.execute(FETCH_NUMBEDROOMS_BY_CITY, (city))
    no_of_bedrooms = cursor.fetchall()
    
    return jsonify(no_of_bedrooms), 200

@app.route('/api/bathrooms', methods=['GET'])
def bathrooms():
    # Hit the db and get no of bathrooms by city
    cursor = db.cursor()
    city = request.args.get('city')
    
    if city == 'nocity':
        cursor.execute(FETCH_NUMBATHROOMS)
        all_bathrooms = cursor.fetchall()
        return jsonify(all_bathrooms), 200
    
    cursor.execute(FETCH_NUMBATHROOMS_BY_CITY, (city))
    no_of_bathrooms = cursor.fetchall()
    
    return jsonify(no_of_bathrooms), 200


@app.route('/api/agencies', methods=['GET'])
def agencies():
    cursor = db.cursor()
    city = request.args.get('city')
    
    cursor.execute(FETCH_AGENCIES_BY_CITY, (city))
    agencies = cursor.fetchall()
    
    return jsonify(agencies), 200


@app.route('/api/societies', methods=['GET'])
def societies():
    cursor = db.cursor()
    city = request.args.get('city')
    
    cursor.execute(FETCH_SOCIETIES_BY_CITY, (str(city)))
    societiesNames = cursor.fetchall()
    
    return jsonify(societiesNames), 200


@app.route('/filter', methods=['GET'])
def filter():
    cursor = db.cursor()
    filters = request.args.to_dict()
    
    joins = str()
    prop_filters = 'WHERE'
    
    local_join_agency_agents = INNER_JOIN_AGENCY_AGENTS
    local_join_prop_agents = INNER_JOIN_PROPERTY_AGENT
    local_join_prop_society = INNER_JOIN_PROPERTY_SOCIETY
    
    for (key, value) in filters.items():
        if key == 'minPrice' and value:
            prop_filters += f" purchase_price >= '{int(value)}' AND"
        elif key == 'maxPrice' and value:
            prop_filters += f" purchase_price <= '{int(value)}' AND"
        elif key == 'city' and value:
            prop_filters += f" city = '{str(value)}' AND"
        elif key == 'bedrooms' and value:
            prop_filters += f" numBedrooms = '{int(value)}' AND"
        elif key == 'bathrooms' and value:
            prop_filters += f" numBathrooms = '{int(value)}' AND"
        elif key == 'society' and value:
            local_join_prop_society += f" AND SC.SOCIETYNAME = '{str(value)}'"
        elif key == 'agency' and value:
            local_join_agency_agents += f" AND AGC.AGENCYNAME = '{str(value)}'"
        
    joins += local_join_prop_agents + "\n" + local_join_agency_agents + "\n" + local_join_prop_society
    sql_query = PROPERTIES_SELECT_QUERY.format(joins=joins, 
                                               filters=str() if prop_filters == 'WHERE' else prop_filters.rstrip("AND").rstrip(), 
                                               limit=LIMIT_SELECT.format(lim=100))
    
    print(sql_query)
    cursor.execute(sql_query, (app.config['CURRENT_USER_ID']))
    
    fetched_properties = cursor.fetchall()
    local_properties = list()
    
    for property in fetched_properties:
        local_properties.append(property)
        
    return jsonify(local_properties), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_user(username, password):
            # Redirect to home page or dashboard upon successful login
            return redirect(url_for('home'))
        else:
            # Authentication failed, display error message or redirect to login page
            return "Invalid username or password. Please try again."
    else:
        # Render login form
        return render_template('login_page.html')


@app.route('/logout')
def logout():
    # Clear session variables
    session.clear()
    # Redirect the user to the home page
    return redirect(url_for('home'))


## signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists in the database
        cursor = db.cursor()
        cursor.execute("SELECT * FROM User WHERE username = %s", (username))
        user = cursor.fetchone()

        if user:
            error = "Username already exists. Please choose a different username."
        else:
            # Insert new user into the database
            cursor.execute("INSERT INTO User (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            cursor.close()
            return redirect(url_for('login'))  # Redirect to login page after successful signup

    return render_template('signup.html', error=error)


@app.route('/profile/<username>', methods=['GET'])
def profile(username):
    cursor = db.cursor()
    # Fetch user details from the database using username
    cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
    user = cursor.fetchone()
    # Check if user exists
    if user:
        # Fetch user profile details using userID
        cursor.execute("SELECT * FROM UserProfile WHERE userID = %s", (user['userID'],))

        user_profile = cursor.fetchone()
        # Fetch amenity preferences for the user
        cursor.execute("SELECT f.featureName FROM AmenityPreference ap JOIN Feature f ON ap.featureID = f.featureID WHERE ap.userID = %s", (user['userID'],))
        amenities = cursor.fetchall()
        cursor.close()

        return render_template('profile_page.html', user=user, user_profile=user_profile, amenities=amenities)
    else:
        cursor.close()
        return "User not found", 404

# --------------------------- FUNCTIONS ---------------------------

# Function to authenticate user
def authenticate_user(username, password):
    # Query the database to retrieve user information
    cursor = db.cursor()
    cursor.execute("SELECT * FROM User WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        # User exists in the database
        session['logged_in'] = True  # Set session variable to mark user as logged in
        session['username'] = user['username']  # Optionally store user information in session
        return True
    else:
        # Invalid credentials
        return False


# --------------------------- ERROR + RUN APP + MISC ---------------------------


@app.errorhandler(404)
def page_not_found(e):
    return app.send_static_file('error.html'), 404


# run + debug on
if __name__ == "__main__":
    app.run(debug=True)

'''
@app.teardown_appcontext
def close_db(error):
    if hasattr(db, 'close'):
        db.close()
'''

'''
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
'''
