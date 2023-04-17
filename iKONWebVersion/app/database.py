import psycopg2
from psycopg2.extras import RealDictCursor
import json


def konConnection():
    c = psycopg2.connect(user="USER",
                         password="PWD",
                         host="HOST",
                         port="5432",
                         database="konsms")
    return c


conn = konConnection()
cur = conn.cursor(cursor_factory=RealDictCursor)


def closeConnection():
    print("connection closed")
    cur.close()
    conn.close()


# cols: a list of column names
# args: a dict of (column: value) pairs
def select_by_query(table_name, cols, args, unique=True, is_or=False, is_view=False):
    select_cols = "*"
    if len(cols) > 0:
        select_cols = ", ".join(cols)
    columns = []
    values = []
    if args:
        for k, v in args.items():
            columns.append(str(k) + "=%s")
            value = "'" + str(v) + "'"
            values.append(value)
    where_clause = ""
    if len(columns) > 0:
        where_clause = " WHERE " + " AND ".join(columns)
    if is_or:
        where_clause = " WHERE " + " OR ".join(columns)
    if is_view:
        query = "SELECT " + select_cols + " FROM " + table_name + where_clause % tuple(values)
    else:
        query = "SELECT " + select_cols + " FROM \"" + table_name + "\"" + where_clause % tuple(values)
    cur.execute(query)
    if unique:
        res = cur.fetchone()
    else:
        res = cur.fetchall()
    return res


def insert_row_query(table_name, args):
    col_str = "(" + ", ".join(args.keys()) + ")"
    values = []
    for v in args.values():
        values.append("'" + str(v) + "'")
    val_str = "(" + ", ".join(values) + ")"
    # print("col_str: ", col_str)
    # print("val_str: ", val_str)
    query = "INSERT INTO " + "\"" + table_name + "\" " + col_str + " VALUES " + val_str
    cur.execute(query)
    conn.commit()


# Inserts a new user to the database, enter all entries
def insertUser(userid, username, score, deploymentid, referral_code):
    print("insertUser(userid, username, score=0, deploymentid=0) ",
          [userid, username, score, deploymentid, referral_code])
    insert_row_query("User", {"userid": userid, "username": username,
                              "score": score, "deploymentid": deploymentid,
                              "referral_code": referral_code})


def getUserByCode(referral_code):
    print("getReferralCode(referral_code) ", referral_code)
    res = select_by_query("User", ["userid"], {"referral_code": referral_code})
    return res


# Checks if user exists in database given a user id/phone number
def getUser(userid):
    print("getUser(userid) ", userid)
    res = select_by_query("User", ["userid"], {"userid": userid})
    return res


# check username exist or not
def getUserByUsername(username):
    print("getUserByUsername(username) ", username)
    res = select_by_query("User", ["userid"], {"username": username})
    return res


def getUserId(username):
    print("getUserId(username) ", username)
    res = select_by_query("User", ["userid"], {"username": username})
    return res["userid"]


def getUsername(userid):
    print("getUsername(userid) ", userid)
    res = select_by_query("User", ["username"], {"userid": userid})
    return res["username"]


# Get message script json from Deployment table
# version: web or sms
# return script dictionary
def getScript(deploymentid, version):
    print("getScript(deploymentid) ", deploymentid)
    res = select_by_query("Deployment", ["script_name"], {"deploymentid": deploymentid})
    script_name = res["script_name"]
    res_script = select_by_query("Script", ["content"], {"script_name": script_name, "version": version})
    script_content = res_script["content"]
    return json.loads(script_content)


def getUserDeployment(userid):
    print("getUserDeployment(userid) ", userid)
    res = select_by_query("User", ["deploymentid"], {"userid": userid})
    return res["deploymentid"]


# Inserts user response into database, given user id, region, 2 years and answer
def insertResponse(userid, year1, year2, answer):
    print("insertResponse(userid, year1, year2, answer)",
          [userid, year1, year2, answer])
    insert_row_query("Response",
                     {"userid": userid, "year1": year1, "year2": year2, "answer": answer})


# Gets user score based on user id/Phone number
def getUserScore(userid):
    print("getUserScore(userid) ", userid)
    res = select_by_query("User", ["score"], {"userid": userid})
    return res["score"]


# Updates user score given user ID and new Score
def setUserScore(user, score):
    print("setUserScore(user, score) ", [user, score])
    cur.execute("UPDATE \"User\" SET score = %s WHERE userid = '%s'" % (score, user))
    conn.commit()


# Gets actual value from satellite data given satellite/station source name
def getSatValue(source_name, year):
    print("getSatValue(source_name, year) ", [source_name, year])
    res = select_by_query("SatelliteData", ["value"], {"source_name": source_name, "year": year})
    if res:
        return res["value"]
    return 0


# Get satellite source name given deploymentid
def getSatSource(deploymentid):
    print("getSatSource(deploymentid) ", deploymentid)
    res = select_by_query("Deployment", ["sat_source"], {"deploymentid": deploymentid})
    return res["sat_source"]


def getStationSource(deploymentid):
    print("getStationSource(deploymentid) ", deploymentid)
    res = select_by_query("Deployment", ["station_source"], {"deploymentid": deploymentid})
    return res["station_source"]


# Get all the available years from satellite data given satellite and weather station source
# Return a list of years
def getYears(sat_source, station_source):
    print("getYears(sat_source, station_source) ", [sat_source, station_source])
    years = []
    res_sat = select_by_query("SatelliteData", ["year"], {"source_name": sat_source}, False)
    for r in res_sat:
        years.append(r["year"])
    res_sat = select_by_query("SatelliteData", ["year"], {"source_name": station_source}, False)
    for r in res_sat:
        years.append(r["year"])
    return years


# gets user responses given userid, two years
def getUserResponses(userid, year_1, year_2):
    print("getUserResponses(userid, year_1, year_2) ", [userid, year_1, year_2])
    # the result is not unique,
    # but this function is for evaluating whether the response exists,
    # so the first row is enough
    res = select_by_query("Response", ["userid"], {"userid": userid, "year1": year_1, "year2": year_2})
    return res


# gets all responses for a particular question combination for given deployment
# return a list of answers (1 for year1, 2 for year2, 3 for same, 4 for unknown)
def getDeployResponses(year_1, year_2, deploymentid):
    print("getDeployResponses(year_1, year_2, deploymentid) ", [year_1, year_2, deploymentid])
    # DeployResponse view
    res = select_by_query("DeployResponse", ["answer"],
                          {"year1": year_1, "year2": year_2, "deploymentid": deploymentid},
                          unique=False, is_view=True)
    responses = []
    for r in res:
        responses.append(r["answer"])
    return responses


# Gets all user scores for a given deployment
# return a list of scores
def getDeployScores(deploymentid):
    print("getDeployScores(deploymentid) ", deploymentid)
    res = select_by_query("User", ["score"], {"deploymentid": deploymentid}, False)
    scores = []
    for r in res:
        scores.append(r["score"])
    return scores


def getDeployUsers(deploymentid):
    print("getDeployUsers(deploymentid) ", deploymentid)
    res = select_by_query("User", [], {"deploymentid": deploymentid}, False)
    users = []
    for r in res:
        users.append(r)
    return users


def countDeployUsers(deploymentid):
    print("countDeployUsers(deploymentid)", deploymentid)
    res = select_by_query("User", ["count(*)"], {"deploymentid": deploymentid}, True)
    return res["count"]


# check if entry code exists
# return deploymentid
def getDeployByCode(entry_code):
    print("getDeployByCode(entry_code)", entry_code)
    res = select_by_query("Deployment", ["deploymentid"], {"entry_code": entry_code}, True)
    print(res)
    if res:
        return res["deploymentid"]


def getReferralNum(userid):
    print("getReferralNum(userid) ", userid)
    res = select_by_query("Referral", ["referral_num"], {"userid": userid})
    return res["referral_num"]


# increment number of referrals a user made
def updateReferralNum(referral_code):
    print("updateReferralNum(referral_code)")
    res = getUserByCode(referral_code)
    userid = res["userid"]
    num = getReferralNum(userid) + 1
    cur.execute("UPDATE \"Referral\" SET referral_num = %s WHERE userid = '%s'" % (num, userid))
    conn.commit()

# Imports Satellite Data from CSV into the Postgres database
# TODO: Satellite data will later be replaced by real time data from irs database
# def populateSatData(file_path):
#     connection = None
#     cursor = None
#     try:
#         connection = konConnection()
#         cursor = connection.cursor()
#         postgres_insert_query = """INSERT INTO "SatelliteData" VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)"""
#         data = (pd.read_csv(file_path))
#         for index, row in data.iterrows():
#             record_to_insert = (row[0], row[1], row[2], row[3], row[4], row[5], row[6])
#             cursor.execute(postgres_insert_query, record_to_insert)
#             connection.commit()
#         print("Record inserted successfully into Satellite table")
#         return
#     except (Exception, psycopg2.Error) as error:
#         if connection:
#             print("Failed to insert record into Satellite table", error)
#     finally:
#         # closing database connection.
#         if connection:
#             cursor.close()
#             connection.close()
#             print("PostgreSQL connection is closed")
