CREATE DATABASE RealEstate;
USE RealEstate;

CREATE TABLE Property (
    propertyID VARCHAR(255),
    description TEXT,
    propertyType VARCHAR(255),
    city VARCHAR(255),
    locality VARCHAR(255),
    ownType VARCHAR(255),
    numBedrooms DECIMAL(3,1),
    numBathrooms DECIMAL(3,1),
    numBalconies INT,
    propertyAge INT,
    numFloors INT,
    propertyName VARCHAR(255),
    listingType VARCHAR(255),
    mapDetails VARCHAR(255),
    propertyHeading VARCHAR(255),
    agentID VARCHAR(255),
    area VARCHAR(255),
    societyID INT,
    verified VARCHAR(255),
    rental_price INT,
    purchase_price INT,
    registerDate DATE,
    PRIMARY KEY (propertyID),
    FOREIGN KEY (societyID) REFERENCES Society(SocietyID),
    FOREIGN KEY (agentID) REFERENCES Agent(agentID)
);
SELECT *
FROM Property;
DROP TABLE Property;

CREATE TABLE Society (
    SocietyID INT,
    SocietyName VARCHAR(255),
    email VARCHAR(255),
    phoneNumber VARCHAR(255),
    address VARCHAR(255),
    PRIMARY KEY (SocietyID)
);
SELECT *
FROM Society;
DROP TABLE Society;

CREATE TABLE User (
    userID VARCHAR(255),
    username VARCHAR(255),
    email VARCHAR(255),
    PRIMARY KEY (userID)
);
SELECT *
FROM User;
DROP TABLE User;

CREATE TABLE UserProfile (
    profileID VARCHAR(255),
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    dateOfBirth DATE,
    gender VARCHAR(255),
    phoneNumber VARCHAR(255),
    address VARCHAR(255),
    userID VARCHAR(255),
    PRIMARY KEY (userID, profileID),
    FOREIGN KEY (userID) REFERENCES User(userID)
);
DROP TABLE UserProfile;
SELECT *
FROM UserProfile;

CREATE TABLE Feature (
    featureID VARCHAR(255),
    featureName VARCHAR(255),
    PRIMARY KEY (featureID)
);
SELECT *
FROM Feature;

CREATE TABLE Agent (
    agentID VARCHAR(255),
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(255),
    address VARCHAR(255),
    agencyID VARCHAR(255),
    PRIMARY KEY (agentID),
    FOREIGN KEY (agencyID) REFERENCES Agency(agencyID)
);
SELECT *
FROM Agent;

CREATE TABLE Agency 
(
    agencyID VARCHAR(255),
    agencyName VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(255),
    address VARCHAR(255),
    PRIMARY KEY (agencyID)
);
SELECT *
FROM Agency;

CREATE TABLE Favourites 
(
    userID VARCHAR(255),
    propertyID VARCHAR(255),
    PRIMARY KEY (userID, propertyID),
    FOREIGN KEY (userID) REFERENCES User(userID),
    FOREIGN KEY (propertyID) REFERENCES Property(propertyID)
);
SELECT *
FROM Favourites;

CREATE TABLE PropertyFeature (
    propertyID VARCHAR(255),
    featureID VARCHAR(255),
    PRIMARY KEY (propertyID, featureID),
    FOREIGN KEY (propertyID) REFERENCES Property(propertyID),
    FOREIGN KEY (featureID) REFERENCES Feature(featureID)
);
SELECT *
FROM PropertyFeature;

CREATE TABLE AmenityPreference (
    userID VARCHAR(255),
    featureID VARCHAR(255),
    PRIMARY KEY (userID, featureID),
    FOREIGN KEY (userID) REFERENCES User(userID),
    FOREIGN KEY (featureID) REFERENCES Feature(featureID)
);
SELECT *
FROM AmenityPreference;
DROP TABLE AmenityPreference;

SHOW TABLES;