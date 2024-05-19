import mysql.connector
import csv

myConnection = mysql.connector.connect(user = 'root', password = 'mysqladmin123', 
                                       host = 'localhost', database = 'RealEstate')

cursorObject = myConnection.cursor()

"""
with open('finaldata/society.csv', 'r') as file:
    csv_filereader = csv.reader(file)
    header_flag = True
    for row in csv_filereader:
        if(header_flag):
            header_flag = False
            continue

        Society_ID,Society_Name,Email,Phone,Address = [elem for elem in row]
        
        cursorObject.execute('insert into Society values (%s, %s, %s, %s, %s)',
                             (Society_ID,Society_Name,Email,Phone,Address))

myConnection.commit()
"""
"""
with open('finaldata/agencies.csv', 'r') as file:
    csv_filereader = csv.reader(file)
    header_flag = True
    for row in csv_filereader:
        if(header_flag):
            header_flag = False
            continue

        agencyID,agencyName,email,phone,address = [elem for elem in row]
        
        cursorObject.execute('insert into Agency values (%s, %s, %s, %s, %s)',
                             (agencyID,agencyName,email,phone,address))

myConnection.commit()
"""
"""
with open('finaldata/agents.csv', 'r') as file:
    csv_filereader = csv.reader(file)
    header_flag = True
    for row in csv_filereader:
        if(header_flag):
            header_flag = False
            continue

        agentID,firstName,lastName,email,phone,address,agencyID = [elem for elem in row]
        
        cursorObject.execute('insert into Agent values (%s, %s, %s, %s, %s, %s, %s)',
                             (agentID,firstName,lastName,email,phone,address,agencyID))

myConnection.commit()
"""
"""
with open('finaldata/features.csv', 'r') as file:
    csv_filereader = csv.reader(file)
    header_flag = True
    for row in csv_filereader:
        if(header_flag):
            header_flag = False
            continue

        Feature_ID,Feature_Name = [elem for elem in row]
        
        cursorObject.execute('insert into Feature values (%s, %s)',
                             (Feature_ID,Feature_Name))

myConnection.commit()
"""
"""
with open('finaldata/user.csv', 'r') as file:
    csv_filereader = csv.reader(file)
    header_flag = True
    for row in csv_filereader:
        if(header_flag):
            header_flag = False
            continue

        userID,username,email = [elem for elem in row]
        
        cursorObject.execute('insert into User values (%s, %s, %s)',
                             (userID,username,email))

myConnection.commit()
"""
"""
with open('finaldata/userprofile.csv', 'r') as file:
    csv_filereader = csv.reader(file)
    header_flag = True
    for row in csv_filereader:
        if(header_flag):
            header_flag = False
            continue

        profileID,firstName,lastName,dateOfBirth,gender,phoneNumber,address,userID = [elem for elem in row]
        
        cursorObject.execute('insert into UserProfile values (%s, %s, %s, %s, %s, %s, %s, %s)',
                             (profileID,firstName,lastName,dateOfBirth,gender,phoneNumber,address,userID))

myConnection.commit()
"""
"""
with open('finaldata/amenity_preference.csv', 'r') as file:
    csv_filereader = csv.reader(file)
    header_flag = True
    for row in csv_filereader:
        if(header_flag):
            header_flag = False
            continue

        userID,Feature_ID = [elem for elem in row]
        
        cursorObject.execute('insert into AmenityPreference values (%s, %s)',
                             (userID,Feature_ID))

myConnection.commit()
"""
"""
with open('finaldata/favorites.csv', 'r') as file:
    csv_filereader = csv.reader(file)
    header_flag = True
    for row in csv_filereader:
        if(header_flag):
            header_flag = False
            continue

        userID,PROP_ID = [elem for elem in row]
        
        cursorObject.execute('insert into Favourites values (%s, %s)',
                             (userID,PROP_ID))

myConnection.commit()
"""