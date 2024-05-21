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
app.config['CURRENT_USER_ID'] = '6520'

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
        SC.SOCIETYNAME,
        CASE 
			WHEN PROP.PROPERTYTYPE = 'Independent/Builder Floor' THEN '/static/img/house_3.png'
			WHEN PROP.PROPERTYTYPE = 'Residential Apartment' THEN '/static/img/house_6.png'
			WHEN PROP.PROPERTYTYPE = 'Independent House/Villa' THEN '/static/img/house_1.png'
			WHEN PROP.PROPERTYTYPE = 'Residential Land' THEN '/static/img/house_7.png'
			WHEN PROP.PROPERTYTYPE = 'Studio Apartment' THEN '/static/img/house_8.png'
			WHEN PROP.PROPERTYTYPE = 'Serviced Apartments' THEN '/static/img/house_5.png'
			WHEN PROP.PROPERTYTYPE = 'Farm House' THEN '/static/img/house_4.png'
			WHEN PROP.PROPERTYTYPE = 'Other' THEN '/static/img/house_2.png'
			ELSE '/static/img/house_2.png'
		END AS IMG
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
        SC.SOCIETYNAME,
        CASE 
			WHEN PROP.PROPERTYTYPE = 'Independent/Builder Floor' THEN '/static/img/house_3.png'
			WHEN PROP.PROPERTYTYPE = 'Residential Apartment' THEN '/static/img/house_6.png'
			WHEN PROP.PROPERTYTYPE = 'Independent House/Villa' THEN '/static/img/house_1.png'
			WHEN PROP.PROPERTYTYPE = 'Residential Land' THEN '/static/img/house_7.png'
			WHEN PROP.PROPERTYTYPE = 'Studio Apartment' THEN '/static/img/house_8.png'
			WHEN PROP.PROPERTYTYPE = 'Serviced Apartments' THEN '/static/img/house_5.png'
			WHEN PROP.PROPERTYTYPE = 'Farm House' THEN '/static/img/house_4.png'
			WHEN PROP.PROPERTYTYPE = 'Other' THEN '/static/img/house_2.png'
			ELSE '/static/img/house_2.png'
		END AS IMG
        FROM PROPERTY AS PROP
        {joins}
        {filters}
        {groupby}
        {having}
        {limit}"""
        
LIMIT_SELECT = """LIMIT {lim}"""

FETCH_INDIVIDUAL_PROPERTY = """SELECT PROP.*, SC.*, AG.*, AGC.*, 
        CASE 
			WHEN PROP.PROPERTYTYPE = 'Independent/Builder Floor' THEN '/static/img/house_3.png'
			WHEN PROP.PROPERTYTYPE = 'Residential Apartment' THEN '/static/img/house_6.png'
			WHEN PROP.PROPERTYTYPE = 'Independent House/Villa' THEN '/static/img/house_1.png'
			WHEN PROP.PROPERTYTYPE = 'Residential Land' THEN '/static/img/house_7.png'
			WHEN PROP.PROPERTYTYPE = 'Studio Apartment' THEN '/static/img/house_8.png'
			WHEN PROP.PROPERTYTYPE = 'Serviced Apartments' THEN '/static/img/house_5.png'
			WHEN PROP.PROPERTYTYPE = 'Farm House' THEN '/static/img/house_4.png'
			WHEN PROP.PROPERTYTYPE = 'Other' THEN '/static/img/house_2.png'
			ELSE '/static/img/house_2.png'
		END AS IMG,
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

FETCH_PROPERTYTYPES = """SELECT DISTINCT(PROPERTYTYPE) FROM PROPERTY"""

FETCH_PROPERTYTYPES_BY_CITY = """SELECT DISTINCT(PROPERTYTYPE) FROM PROPERTY WHERE CITY = %s"""

FETCH_SOCIETIES_BY_CITY = """SELECT DISTINCT(SOCIETYNAME) FROM SOCIETY SC 
                            INNER JOIN PROPERTY PROP ON PROP.SOCIETYID = SC.SOCIETYID AND PROP.CITY = %s"""
                            
FETCH_AGENCIES_BY_CITY = """SELECT DISTINCT(AGENCYNAME) FROM AGENCY AGC
							INNER JOIN AGENT AG ON AGC.AGENCYID = AG.AGENCYID
                            INNER JOIN PROPERTY PROP ON PROP.AGENTID = AG.AGENTID AND PROP.CITY = %s"""
                            
FETCH_FEATURE_NAMES = """SELECT DISTINCT(FEATURENAME) FROM PROPERTY PROP
	INNER JOIN PROPERTYFEATURE PF ON PF.PROPERTYID = PROP.PROPERTYID
	INNER JOIN FEATURE FT ON FT.FEATUREID = PF.FEATUREID"""
 
FETCH_FEATURE_NAMES_BY_CITY = """SELECT DISTINCT(FEATURENAME) FROM PROPERTY PROP
	INNER JOIN PROPERTYFEATURE PF ON PF.PROPERTYID = PROP.PROPERTYID
	INNER JOIN FEATURE FT ON FT.FEATUREID = PF.FEATUREID
    WHERE PROP.CITY = %s"""
    
FETCH_INDIVIDUAL_PROPERTY_FEATURES = """SELECT DISTINCT(FT.FEATURENAME) FROM PROPERTY PROP
	INNER JOIN PROPERTYFEATURE PF ON PF.PROPERTYID = PROP.PROPERTYID AND PF.PROPERTYID = %s
    INNER JOIN FEATURE FT ON FT.FEATUREID = PF.FEATUREID"""
    
FETCH_AMENITY_PREF =  "SELECT f.featureName FROM AmenityPreference ap JOIN Feature f ON ap.featureID = f.featureID WHERE ap.userID = %s"

INNER_JOIN_AGENCY_AGENTS = """INNER JOIN AGENCY AGC ON AGC.AGENCYID = AG.AGENCYID"""

INNER_JOIN_PROPERTY_AGENT = """INNER JOIN AGENT AG ON AG.AGENTID = PROP.AGENTID"""

INNER_JOIN_PROPERTY_SOCIETY = """INNER JOIN SOCIETY SC ON SC.SOCIETYID = PROP.SOCIETYID"""

INNER_JOIN_PROPERTY_PROPFEATURES = """INNER JOIN PROPERTYFEATURE PF ON PF.PROPERTYID = PROP.PROPERTYID"""

INNER_JOIN_PROPERTY_FEATURE =  """INNER JOIN FEATURE FT ON FT.FEATUREID = PF.FEATUREID"""

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
    cursor.close()
    
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
            # print(f"'{property['PROPERTYID']}',")
            properties_home.append(property)
    
    cursor.close()
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
        
    cursor.close()
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
    
    cursor.close()
    return jsonify(property), 200


@app.route('/api/fetch_ind_property/features', methods=['GET'])
def fetch_ind_property_features():
    # Hit the db and get individual proeprty details
    cursor = db.cursor()
    property_id = request.args.get('id')
    
    cursor.execute(FETCH_INDIVIDUAL_PROPERTY_FEATURES, (property_id))
    features = cursor.fetchall()
    
    print(features)
    
    cursor.close()
    return jsonify(features), 200


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
    
    cursor.close()
    return jsonify(no_of_bedrooms), 200

@app.route('/api/feature-names', methods=['GET'])
def feature_names():
    cursor = db.cursor()
    city = request.args.get('city')
    
    if city == 'nocity':
        cursor.execute(FETCH_FEATURE_NAMES)
        all_features = cursor.fetchall()
        return jsonify(all_features), 200
    
    cursor.execute(FETCH_FEATURE_NAMES_BY_CITY, (city))
    features = cursor.fetchall()
    
    cursor.close()
    return jsonify(features), 200

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
    
    cursor.close()
    return jsonify(no_of_bathrooms), 200


@app.route('/api/property-type', methods=['GET'])
def property_types():
    cursor = db.cursor()
    city = request.args.get('city')
    
    if city == 'nocity':
        cursor.execute(FETCH_PROPERTYTYPES)
        all_prop_types = cursor.fetchall()
        return jsonify(all_prop_types), 200
    
    cursor.execute(FETCH_PROPERTYTYPES_BY_CITY, (city))
    prop_types = cursor.fetchall()
    
    cursor.close()
    return jsonify(prop_types), 200


@app.route('/api/agencies', methods=['GET'])
def agencies():
    cursor = db.cursor()
    city = request.args.get('city')
    
    cursor.execute(FETCH_AGENCIES_BY_CITY, (city))
    agencies = cursor.fetchall()
    
    cursor.close()
    return jsonify(agencies), 200


@app.route('/api/societies', methods=['GET'])
def societies():
    cursor = db.cursor()
    city = request.args.get('city')
    
    cursor.execute(FETCH_SOCIETIES_BY_CITY, (str(city)))
    societiesNames = cursor.fetchall()
    
    cursor.close()
    return jsonify(societiesNames), 200

@app.route('/api/amenity-pref', methods=['GET'])
def amenety_preferences():
    cursor = db.cursor()
    
    cursor.execute(FETCH_AMENITY_PREF, (app.config['CURRENT_USER_ID']))
    amenities = cursor.fetchall()
    cursor.close()
    
    return jsonify(amenities), 200


@app.route('/filter', methods=['GET'])
def filter():
    cursor = db.cursor()
    filters = request.args.to_dict()
    
    joins = str()
    groupby = 'GROUP BY'
    prop_filters = 'WHERE'
    having = 'HAVING'
    
    local_join_agency_agents = INNER_JOIN_AGENCY_AGENTS
    local_join_prop_agents = INNER_JOIN_PROPERTY_AGENT
    local_join_prop_society = INNER_JOIN_PROPERTY_SOCIETY
    local_join_prop_propfeatures = INNER_JOIN_PROPERTY_PROPFEATURES
    local_join_prop_feature = INNER_JOIN_PROPERTY_FEATURE
    
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
        elif key == 'propType' and value:
            prop_filters += f" propertyType = '{str(value)}' AND"
        elif key == 'selectedFeatures' and value:
            local_join_prop_feature += ' AND FT.FEATURENAME IN ('
            for feature in value.split(','):
                feature_name = feature.rstrip(' x')
                local_join_prop_feature += f"'{feature_name}', "
            local_join_prop_feature = local_join_prop_feature.rstrip(", ")
            local_join_prop_feature += ')'
            groupby += ' PROP.PROPERTYID'
            having += f" COUNT(DISTINCT FT.FEATURENAME) = {len(value.split(','))}"
        elif key == 'society' and value:
            local_join_prop_society += f" AND SC.SOCIETYNAME = '{str(value)}'"
        elif key == 'agency' and value:
            local_join_agency_agents += f" AND AGC.AGENCYNAME = '{str(value)}'"
        
    joins += local_join_prop_agents + "\n" + local_join_agency_agents + "\n" + local_join_prop_society + "\n" + \
        local_join_prop_propfeatures + "\n" + local_join_prop_feature
    
    sql_query = PROPERTIES_SELECT_QUERY.format(joins=joins, 
                                               filters=str() if prop_filters == 'WHERE' else prop_filters.rstrip().rstrip("AND"), 
                                               limit=LIMIT_SELECT.format(lim=100),
                                               groupby=str() if groupby == 'GROUP BY' else groupby,
                                               having=str() if having == 'HAVING' else having)
    
    print(sql_query)
    cursor.execute(sql_query, (app.config['CURRENT_USER_ID']))
    
    fetched_properties = cursor.fetchall()
    local_properties = list()
    
    for property in fetched_properties:
        local_properties.append(property)
        
    cursor.close()
        
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


@app.route('/profile', methods=['GET'])
def profile():
    cursor = db.cursor()
    # Fetch user details from the database using username
    cursor.execute("SELECT * FROM User WHERE username = %s", (session['username']))
    user = cursor.fetchone()
    # Check if user exists
    if user:
        # Fetch user profile details using userID
        cursor.execute("SELECT * FROM UserProfile WHERE userID = %s", (user['userID'],))

        user_profile = cursor.fetchone()
        # Fetch amenity preferences for the user
        print(user['userID'])
        cursor.execute(FETCH_AMENITY_PREF, (user['userID']))
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
        app.config['CURRENT_USER_ID'] = user['userID']
        return True
    else:
        # Invalid credentials
        return False


if __name__ == "__main__":
    app.run(debug=True)
