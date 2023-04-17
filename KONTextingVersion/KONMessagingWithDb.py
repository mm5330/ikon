from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import emoji
import psycopg2
from psycopg2 import Error
import pandas as pd
import random
from itertools import groupby


#Displays the current users in the Database
def showUsers():
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")

        cursor = connection.cursor()

        postgreSQL_select_Query = "select * from Users"

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from Users table using cursor.fetchall")
        user_records = cursor.fetchall() 

        print("Print each row and it's columns values")
        # print(user_records)
        for row in user_records:
           print("USERID = ", row[0])
           print("NAME = ", row[1])
           print("LOCATION  = ", row[2])
           print("LANGUAGE = ", row[3])
           print("REFERRAL_CODE = ", row[4])
           print("LAST_PLAYED = ", row[5])
           print("SCORE = ", row[6])



    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Displays the current responses in the Database
def showResponses():
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")

        cursor = connection.cursor()

        postgreSQL_select_Query = "select * from Responses"

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from Responses table using cursor.fetchall")
        user_records = cursor.fetchall() 

        print("Print each row and it's columns values")
        # print(user_records)
        for row in user_records:
           print("ResponseID = ", row[0])
           print("UserID = ", row[1])
           print("Region = ", row[2])
           print("Year 1 = ", row[3])
           print("Year 2  = ", row[4])
           print("Answer = ", row[5])
        


    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Displays the current combinations of questions in the Database
def showCombinations():
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")

        cursor = connection.cursor()

        postgreSQL_select_Query = "select * from Combinations"

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from Combinations table using cursor.fetchall")
        user_records = cursor.fetchall() 

        print("Print each row and it's columns values")
        # print(user_records)
        for row in user_records:
           print("CombID = ", row[0])
           print("Year1 = ", row[1])
           print("Year2  = ", row[2])
           print("Comb_Metric = ", row[3])
           print("Location = ", row[4])
         


    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Displays the current Satelite data in the Database
def showSatData():
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")

        cursor = connection.cursor()

        postgreSQL_select_Query = "select * from SatData"

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from SataData table using cursor.fetchall")
        user_records = cursor.fetchall() 

        print("Print each row and it's columns values")
        # print(user_records)
        for row in user_records:
           print("DataID = ", row[0])
           print("Year = ", row[1])
           print("Value  = ", row[2])
           print("Unit = ", row[3])
           print("Region = ", row[4])
           print("Country = ", row[5])
           print("Source = ", row[6])
           print("SourceName = ", row[7])
           print("SourceType = ", row[8])


    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Creates all necessary database structures in the Postgres database
def populateTables():
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")

        cursor = connection.cursor()
        # connection.setAutoCommit(true)
        
        create_table_query = '''
            CREATE TABLE Users
              (USERID BIGINT PRIMARY KEY     NOT NULL,
              NAME TEXT,
              LOCATION TEXT, 
              LANGUAGE TEXT, 
              REFERRAL_CODE TEXT, 
              LAST_PLAYED DATE,
              SCORE INT); 

              CREATE TABLE Responses
              (RESPONSEID SERIAL PRIMARY KEY,
              USERID BIGINT NOT NULL,
              REGION TEXT,
              YEAR1 INT,
              YEAR2 INT, 
              ANSWER INT);
              
               CREATE TABLE Combinations    
              (COMBID SERIAL PRIMARY KEY,
              YEAR1 INT, 
              YEAR2 INT, 
              SOURCETYPE TEXT, 
              LOCATION TEXT);

                CREATE TABLE SatData    
              (DataID SERIAL PRIMARY KEY,
              YEAR INT, 
              VALUE INT, 
              UNIT TEXT, 
              REGION TEXT,
              COUNTRY TEXT,
              SOURCE TEXT,
              SOURCENAME TEXT,
              SOURCETYPE TEXT);'''

              
        cursor.execute(create_table_query)
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while creating PostgreSQL table", error)
    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Imports Satelite Data from CSV into the Postgres database
def populateData(filename):
    data =  (pd.read_csv('filename'))
    print(data.iloc[0,0])
    for index, row in data.iterrows():
        print(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        insertdata(row[0], row[1], row[2], row[3], row[4], row[5],"PH", row[6])

#Clears all tables and deletes them from the Database
def resetTables():
    try:
        connection = psycopg2.connect(user = "postgres",
                                  password = "pwd",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "postgres")

        cursor = connection.cursor()
        cursor.execute("DROP TABLE Users")
        connection.commit()
        cursor.execute("DROP TABLE Responses")
        connection.commit()
        cursor.execute("DROP TABLE Combinations")
        connection.commit()
        cursor.execute("DROP TABLE SatData")
        connection.commit()

    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Inserts each row of Satelite data into the database, enter all entries
def insertdata(Y, V, U, R, C, S, SN, ST):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()

        postgres_insert_query = """ INSERT INTO SatData VALUES (DEFAULT, %s, %s,%s, %s, %s,%s,%s, %s)"""
        record_to_insert = (Y, V, U, R, C, S, SN, ST)
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        count = cursor.rowcount
        print (count, "Record inserted successfully into Satelite table")
        return

    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Failed to insert record into Satelite table", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Inserts combinations of years into the combinations table, 2 years, metric and location
def insertCombination(Y1,Y2,M, L):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()

        postgres_insert_query = """ INSERT INTO Combinations VALUES (DEFAULT, %s, %s,%s,%s)"""
        record_to_insert = (Y1, Y2, M, L)
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        count = cursor.rowcount
        print (count, "Record inserted successfully into Combination table")
        return

    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Failed to insert record into combination table", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Inserts a new user to the database, enter all entries
def insertUser(ID, N, LO, LA, RC, LP, S):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()

        postgres_insert_query = """ INSERT INTO Users VALUES (%s, %s, %s, %s,%s,%s, %s)"""
        record_to_insert = (ID, N, LO, LA, RC, LP, S)
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        count = cursor.rowcount
        print (count, "Record inserted successfully into mobile table")
        return

    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Failed to insert record into mobile table", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Checks if user exists in database given a user id/phone number
def findUser(UID):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from Users where UserID = %s"

        cursor.execute(postgreSQL_select_Query, (UID,))
        print("Selecting rows from Users table using cursor.fetchall")
        mobile_records = cursor.fetchall() 
        # row = mobile_records[0]
        # print("Print each row and it's columns values")
        # print(mobile_records)
        # question = "\n" + "Which year was worse for " + row[3] + "\n" + "1: " + str(row[1]) +"\n" + "2: " + str(row[2]) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        return (mobile_records[0])
        # for row in mobile_records:
        #    print("Id = ", row[0], )
        #    print("Model = ", row[1])
        #    print("Price  = ", row[2], "\n")

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


#Inserts user response into database, given user id, region, 2 years and answer
def insertresponse(UID,RE,Y1,Y2,ANS):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()

        postgres_insert_query = """ INSERT INTO Responses VALUES (DEFAULT,%s, %s, %s,%s,%s)"""
        record_to_insert = (UID,RE,Y1,Y2,ANS)
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        count = cursor.rowcount
        print (count, "Record inserted successfully into responses table")
        return

    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Failed to insert record into responses table", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Gets user score based on user id/Phone number
def getScore(user):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from Users where UserID = %s"

        cursor.execute(postgreSQL_select_Query, (user,))
        print("Selecting rows from SatData table using cursor.fetchall")
        mobile_records = cursor.fetchall() 
        # row = mobile_records[0]
        # print("Print each row and it's columns values")
        # print(mobile_records)
        # question = "\n" + "Which year was worse for " + row[3] + "\n" + "1: " + str(row[1]) +"\n" + "2: " + str(row[2]) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        return mobile_records[0][6]
        # for row in mobile_records:
        #    print("Id = ", row[0], )
        #    print("Model = ", row[1])
        #    print("Price  = ", row[2], "\n")

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Gets region of user based on User ID/Phone number
def getRegion(user):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from Users where UserID = %s"

        cursor.execute(postgreSQL_select_Query, (user,))
        print("Selecting rows from SatData table using cursor.fetchall")
        mobile_records = cursor.fetchall() 
        # row = mobile_records[0]
        # print("Print each row and it's columns values")
        # print(mobile_records)
        # question = "\n" + "Which year was worse for " + row[3] + "\n" + "1: " + str(row[1]) +"\n" + "2: " + str(row[2]) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        return mobile_records[0][2]
        # for row in mobile_records:
        #    print("Id = ", row[0], )
        #    print("Model = ", row[1])
        #    print("Price  = ", row[2], "\n")

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Updates user score given user ID and new Score
def updateScore(user, score):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()

        sql_update_query = """Update users set score = %s where userid = %s"""
        cursor.execute(sql_update_query, (score, user))
        connection.commit()
        count = cursor.rowcount
        print(count, "Record Updated successfully ")

        # connection.commit()
        # count = cursor.rowcount
        # print (count, "Record inserted successfully into mobile table")
        # return

    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Generates combination given Year 1 and Year 2
def getCombination(Y1, Y2):
    # try:
        # connection = psycopg2.connect(user = "postgres",
        #                               password = "pwd",
        #                               host = "127.0.0.1",
        #                               port = "5432",
        #                               database = "postgres")
        # cursor = connection.cursor()
        # postgreSQL_select_Query = "select * from Combinations where COMBID = %s "

        # cursor.execute(postgreSQL_select_Query, (CID,))
        # print("Selecting rows from Combinations table using cursor.fetchall")
        # mobile_records = cursor.fetchall() 
        # row = mobile_records[0]
        # print("Print each row and it's columns values")
        # print(mobile_records)
        # years = getYears(R)
        # print(years)
        # question = "\n" + "Which year was worse for " + row[3] + "\n" + "1: " + str(row[1]) +"\n" + "2: " + str(row[2]) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        question = "\n" + "Which year was worse?""\n" + "1: " + str(Y1) +"\n" + "2: " + str(Y2) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        
        return question
        # for row in mobile_records:
        #    print("Id = ", row[0], )
        #    print("Model = ", row[1])
        #    print("Price  = ", row[2], "\n")

    # except (Exception, psycopg2.Error) as error :
    #     print ("Error while fetching data from PostgreSQL", error)

    # finally:
    #     #closing database connection.
    #     if(connection):
    #         cursor.close()
    #         connection.close()
    #         print("PostgreSQL connection is closed")

    # sendMessage(count)

#Gets actual value from satelite data given year, region and sourcetype
def getRealValue(Y, R, ST):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from SatData where Year = %s AND REGION = %s AND SOURCETYPE = %s"

        cursor.execute(postgreSQL_select_Query, (Y,R,ST))
        print("Selecting rows from SatData table using cursor.fetchall")
        mobile_records = cursor.fetchall() 
        # row = mobile_records[0]
        # print("Print each row and it's columns values")
        # print(mobile_records)
        # question = "\n" + "Which year was worse for " + row[3] + "\n" + "1: " + str(row[1]) +"\n" + "2: " + str(row[2]) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        return mobile_records[0][2]
        # for row in mobile_records:
        #    print("Id = ", row[0], )
        #    print("Model = ", row[1])
        #    print("Price  = ", row[2], "\n")

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Gets actual source name from satelite data given year, region and sourcetype
def getSourceName(Y, R, ST):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from SatData where Year = %s AND REGION = %s AND SOURCETYPE = %s"

        cursor.execute(postgreSQL_select_Query, (Y,R,ST))
        print("Selecting rows from SatData table using cursor.fetchall")
        mobile_records = cursor.fetchall() 
        # row = mobile_records[0]
        # print("Print each row and it's columns values")
        # print(mobile_records)
        # question = "\n" + "Which year was worse for " + row[3] + "\n" + "1: " + str(row[1]) +"\n" + "2: " + str(row[2]) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        return mobile_records[0][6]
        # for row in mobile_records:
        #    print("Id = ", row[0], )
        #    print("Model = ", row[1])
        #    print("Price  = ", row[2], "\n")

    except (Exception, psycopg2.Error) as error:
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Randomly generates 2 years from the list of years available in satelite data
def getYears(R):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from SatData where REGION = %s"

        cursor.execute(postgreSQL_select_Query, (R,))
        print("Selecting rows from SatData table using cursor.fetchall")
        mobile_records = cursor.fetchall() 
        # row = mobile_records[0]
        # print("Print each row and it's columns values")
        # print(mobile_records)
        # question = "\n" + "Which year was worse for " + row[3] + "\n" + "1: " + str(row[1]) +"\n" + "2: " + str(row[2]) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        # return mobile_records[0]
        row = (random.sample(set(mobile_records), 2))
        return [row[0][1],row[1][1]]
        # for row in mobile_records:
        #    print("Id = ", row[0], )
        #    print("Model = ", row[1])
        #    print("Price  = ", row[2], "\n")

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#makes sure the years arent the same also checks if the user has already answered the question given User id and region
def findyears(UID, R):
    years = getYears(R)
    l = (getResponsefromtheseyears(UID, years[0],years[1]))
    if (l is not None or (years[0] == years[1])):
        while (l is not None or years[0] == years[1]):
            years = getYears(R)
            l = (getResponsefromtheseyears(UID, years[0],years[1]))
            if (l is None and years[0]!=years[1]):
                return years
    else:
        return years            

#gets user response given UserID and 2 years
def getResponsefromtheseyears(UID, Y1, Y2):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from Responses where UserID = %s AND YEAR1 = %s AND YEAR2 = %s"

        cursor.execute(postgreSQL_select_Query, (UID,Y1,Y2))
        print("Selecting rows from RESPONSES table using cursor.fetchall")
        mobile_records = cursor.fetchall() 
        # row = mobile_records[0]
        # print("Print each row and it's columns values")
        # print(mobile_records)
        # question = "\n" + "Which year was worse for " + row[3] + "\n" + "1: " + str(row[1]) +"\n" + "2: " + str(row[2]) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        return mobile_records[0]
        # for row in mobile_records:
        #    print("Id = ", row[0], )
        #    print("Model = ", row[1])
        #    print("Price  = ", row[2], "\n")

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#gets all responses for a particular question combination
def getallresponses(RE, Y1,Y2):
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from Responses where REGION = %s AND YEAR1 = %s AND YEAR2 = %s"

        cursor.execute(postgreSQL_select_Query, (RE,Y1,Y2))
        print("Selecting rows from SatData table using cursor.fetchall")
        mobile_records = cursor.fetchall() 

        a =[]
        for row in mobile_records:
            a.append(row[5])

        return a

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#Gets all user scores in the system
def getAllScores():
    try:
        connection = psycopg2.connect(user = "postgres",
                                      password = "pwd",
                                      host = "127.0.0.1",
                                      port = "5432",
                                      database = "postgres")
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from Users"

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from Users table using cursor.fetchall")
        mobile_records = cursor.fetchall() 

        a =[]
        for row in mobile_records:
            a.append(row[6])

        return a

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#returns rank for the current user given user id and all scores in the system
def getRank(UIDScore, allscores):
    print(UIDScore)
    print(allscores)
    count  = len(allscores)
    for s in allscores:
        if(s < UIDScore):
            count -=1
    print(count)
    return count

#Checks response and updates scores based on response
def checkResponse(UID, Y1,Y2,Rs,Re):
    #Check if true for weather station
    actualWeatherYear1 = getRealValue(Y1, Re, "Weather Station")
    actualWeatherYear2 = getRealValue(Y2, Re, "Weather Station")
    ans = "\n"
    if actualWeatherYear1>actualWeatherYear2:
        WW = Y1
    else:
        WW = Y2

    if(Rs == WW):
        ans = ans + ("Congrats: You matched with a local weather station " + getSourceName(Y1, Re, "Weather Station") + "\n")
        updateScore(UID, getScore(UID)+50)
        #Update Score

    #Check if true for satelite
    actualRainfallYear1 = getRealValue(Y1, Re, "Rainfall")
    actualRainfallYear2 = getRealValue(Y2, Re, "Rainfall")

    if(actualRainfallYear1>actualRainfallYear2):
        WR = Y1
    else:
        WR = Y2

    if(WR == Rs):
        ans = ans + ("Congrats: You matched with a Satelite "+getSourceName(Y1, Re, "Rainfall")+"\n")
        updateScore(UID, getScore(UID)+50)

        #update score
    #wisdom of crowds
    allresponses = getallresponses(Re,Y1,Y2)
    if(len(allresponses)>0):
        totalresponses = len(allresponses)
        if(Y1 == Rs):
            updateScore(UID, getScore(UID)+(allresponses.count(Y1)/totalresponses*100))
        elif(Y2 == Rs):
            updateScore(UID, getScore(UID)+(allresponses.count(Y2)/totalresponses*100))
        elif(Rs == 3):
            updateScore(UID, getScore(UID)+(allresponses.count(3)/totalresponses*100))
        elif(Rs == 4):
            updateScore(UID, getScore(UID)+(allresponses.count(4)/totalresponses*100))
        ans = ans +"You matched with someone with the same answer" + "\n"


    print(actualWeatherYear1, actualWeatherYear2)
    print(actualRainfallYear1, actualRainfallYear2)
    print(WW,WR)
    if(len(ans)< 10):
        ans = ans+"Sorry, you didn't match with anyone."
    return ans

        #Check if true for other responses. 

        # row = mobile_records[0]
        # print("Print each row and it's columns values")
        # print(mobile_records)
        # question = "\n" + "Which year was worse for " + row[3] + "\n" + "1: " + str(row[1]) +"\n" + "2: " + str(row[2]) +"\n" + "3: Same" + "\n" + "4: Don't Know" +"\n" + "5: Back to Main Menu" + "\n"
        # return mobile_records[0][2]
        # for row in mobile_records:
        #    print("Id = ", row[0], )
        #    print("Model = ", row[1])
        #    print("Price  = ", row[2], "\n")

    # except (Exception, psycopg2.Error) as error :
    #     print ("Error while fetching data from PostgreSQL", error)

    # finally:
    #     #closing database connection.
    #     if(connection):
    #         cursor.close()
    #         connection.close()
    #         print("PostgreSQL connection is closed")



app = Flask(__name__)

# count = 0
#Haseeb Account
# Your Account SID from twilio.com/console
# # Your Auth Token from twilio.com/console

# IRI Account
# Your Account SID from twilio.com/console
account_sid = "sid"
# Your Auth Token from twilio.com/console
auth_token  = "auth"



client = Client(account_sid, auth_token)


count = 1
winner = []
# count = 0
Submenu = False


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    global validResponse
    global count
    global years
    global Submenu
    # global Usercanplay


    validResponse = False
    # Usercanplay = True
    body = request.values.get('Body', None)
    print(str(request.values.get('From')))
    if((str(request.values.get('From'))[0:1]) == 'W' or (str(request.values.get('From'))[0:1]) == 'w'):
        fromNum = int(float(str(request.values.get('From'))[10:]))

    else:
        fromNum = int(float(str(request.values.get('From'))[1:]))


    print(body)
    print(fromNum)

    # Start our TwiML response
    resp = MessagingResponse()

    print(type(findUser(fromNum)))
    #existing user and still in the main menu
    if(findUser(fromNum) is not None) and Submenu == False:

        if body == "Start":
            resp.message("\n" + "Welcome to KON!")
            resp.message("Current Score: " + str(getScore(fromNum)) + "\n" + "Reply with selection:" + "\n" + "1: To start KON Game" + "\n" + "2: Check latest leaderboards" + "\n" + "3: Redeem points for rewards" +"\n")
        
        elif body == "1":
            years = findyears(fromNum,getRegion(fromNum))
            resp.message(getCombination(years[0], years[1]))
            Submenu = True
            count = count + 1
        elif body == "2":
            resp.message("Current Score: " + str(getScore(fromNum))+ "\n" + "Your current rank is: " + str(getRank(getScore(fromNum),getAllScores())))
            resp.message("\n" + "Reply with selection:" + "\n" + "1: To start KON Game" + "\n" + "2: Check latest leaderboards" + "\n" + "3: Redeem points for rewards" +"\n")
            # Submenu = True
        return str(resp)

        # #existing user and still in the submenu - playing the game
    elif(findUser(fromNum) is not None) and Submenu == True:
        if body == "1":
            msg = resp.message(checkResponse(fromNum, years[0],years[1], years[0], getRegion(fromNum)))
            insertresponse(fromNum,getRegion(fromNum),years[0], years[1],years[0])
        # Add a picture message
            # msg.media("https://www.iconfinder.com/icons/3088386/download/png/512")
            validResponse = True

        elif body == "2":
            msg = resp.message(checkResponse(fromNum, years[0],years[1], years[1], getRegion(fromNum)))
            insertresponse(fromNum,getRegion(fromNum),years[0], years[1],years[1])
            validResponse = True

        elif body == "3":
            msg = resp.message(checkResponse(fromNum, years[0],years[1], 3, getRegion(fromNum)))
            insertresponse(fromNum,getRegion(fromNum),years[0], years[1],3)
            validResponse = True

        elif body == "4":
            msg = resp.message(checkResponse(fromNum, years[0],years[1], 4, getRegion(fromNum)))
            insertresponse(fromNum,getRegion(fromNum),years[0], years[1],4)
            validResponse = True

        # elif body == "Start":
        #     resp.message("\n" + "Welcome to KON!")
        #     resp.message("Current Score: " + str(getScore(fromNum)) + "\n" + "Reply with selection:" + "\n" + "A: To start KON Game" + "\n" + "B: Check latest leaderboards" + "\n" + "C: Redeem points for rewards" +"\n")
        
        # elif body == "A":
        #     years = findyears(fromNum,getRegion(fromNum))
        #     resp.message(getCombination(years[0], years[1]))
        #     count = count + 1
        # elif body == "B":
        #     resp.message("Current Score: " + str(getScore(fromNum))+ "\n" + "Your current rank is: " + str(getRank(getScore(fromNum),getAllScores())))
        #     resp.message("\n" + "Reply with selection:" + "\n" + "A: To start KON Game" + "\n" + "B: Check latest leaderboards" + "\n" + "C: Redeem points for rewards" +"\n")
            
        elif body == "5":
            resp.message("\n" + "Reply with selection:" + "\n" + "1: To start KON Game" + "\n" + "2: Check latest leaderboards" + "\n" + "3: Redeem points for rewards" +"\n")
            Submenu = False

        #updating score and getting the next list of questions
        if(validResponse == True):
            years = findyears(fromNum,getRegion(fromNum))
            resp.message("Current Score: " + str(getScore(fromNum)) + getCombination(years[0], years[1]))
            count = count + 1
        
        return str(resp)
        #new user!
    else:
        print("New User!")
        if(body == "Start"):
            # Usercanplay = False
            resp.message("Hey New User!" + "\n" + "Welcome to KON")
            resp.message("Lets setup you account!" + "\n")
            resp.message("Can i get your location?" + "\n")
            resp.message("\n" + "Reply with selection:" + "\n" + "1: New York" + "\n" + "2: Boston" + "\n" + "3: Taiwan" +"\n"+"D: Other" +"\n")

        if body == "1":
            insertUser(fromNum, "Placeholder", "New York", "English", "Placeholder", "07/02/2020", 0)
            resp.message("Great," + "\n" + "You are all setup!" + "\n")
            resp.message('Just text "Start" to this number to start playing!')

        elif body == "2":
            insertUser(fromNum, "Placeholder", "Boston", "English", "Placeholder", "07/02/2020", 0)
            resp.message("Great," + "\n" + "You are all setup!" + "\n")
            resp.message('Just text "Start" to this number to start playing!')

        elif body == "3":
            insertUser(fromNum, "Placeholder", "Taiwan", "English", "Placeholder", "07/02/2020", 0)
            resp.message("Great," + "\n" + "You are all setup!" + "\n")
            resp.message('Just text "Start" to this number to start playing!')

        return str(resp)
        # elif body == "D":
        #     insertUser(fromNum, "Placeholder", "New York", "English", "Placeholder", "07/02/2020", 0)
    








# showUsers()
# showResponses()
# print(getAllScores())

# print(getScore(16468756700))
# def most_common(lst):
#     return max(set(lst), key=lst.count)


# print(most_common([2001,2002,3]))
# def test(l, e):
#     # return [len(list(group)) for key, group in groupby(a)]
#     return l.count(e)

# print(test([2001,2002,3, 2001], 2003))
# showCombinations()

# resetTables()
# populateTables()
# populateData('years.csv')


showUsers()
showResponses()
# showSatData()



# insertUser(16468756700, "Haseeb", "New York", "English", "HA95", "07/02/2020", 0)


# showUsers()
# showResponses()
# showCombinations()
# showSatData()

# print(getRealValue(2019, "Boston", "Weather Station"))
# print(getYears("New York"))
# checkResponse(2001,2004, 2001, "New York")
# print(getScore(16468756700))
# updateScore(16468756700, getScore(16468756700)+50)
# showUsers()



if __name__ == "__main__":
    app.run(debug=True)


# resetTables()
# populateTables()

# insertCombination(2004, 2012, "Rainfall", "Columbia")
# insertCombination(2004, 2008, "Rainfall", "Columbia")
# insertCombination(2008, 2004, "Rainfall", "Columbia")
# insertCombination(2008, 2012, "Rainfall", "Columbia")
# insertCombination(2012, 2004, "Rainfall", "Columbia")
# insertCombination(2012, 2008, "Rainfall", "Columbia")










    