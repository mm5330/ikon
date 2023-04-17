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
# fake_user: include fake user data, given that fake user ids have "fakeuser" prefix
def select_by_query(table_name, cols, args, unique=True, is_or=False, is_view=False, fake_user=True):
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
    if not fake_user:
        query += " AND \"userid\" NOT LIKE 'fakeuser%'"

    try:
        cur.execute(query)
        if unique:
            res = cur.fetchone()
        else:
            res = cur.fetchall()
        return res

    except Exception as e:
        conn.rollback()
        print('ERROR in "select_by_query";\n query: ' + query + ';\n error:' + repr(e))


def insert_row_query(table_name, args):
    col_str = "(" + ", ".join(args.keys()) + ")"
    values = []
    for v in args.values():
        values.append("'" + str(v) + "'")
    val_str = "(" + ", ".join(values) + ")"
    query = "INSERT INTO " + "\"" + table_name + "\" " + col_str + " VALUES " + val_str

    try:
        cur.execute(query)

    except Exception as e:
        conn.rollback()
        print('ERROR in "select_by_query";\n query: ' + query + ';\n error:' + repr(e))

    else:
        conn.commit()


# Inserts a new user to the database, enter all entries
def insertUser(userid, username, score, deploymentid):
    print("insertUser(userid, username, score=0, deploymentid=0) ",
          [userid, username, score, deploymentid])
    insert_row_query("User", {"userid": userid, "username": username,
                              "score": score, "deploymentid": deploymentid})


def getUserByCode(referral_code):
    print("getUserByCode(referral_code) ", referral_code)
    res = select_by_query("Referral", ["userid"], {"referral_code": referral_code})
    if res:
        return res["userid"]
    return res


def getReferralCode(userid, deploymentid):
    print("getReferralCode(userid, deploymentid) ", [userid, deploymentid])
    res = select_by_query("Referral", ["referral_code"], {"userid": userid, "deploymentid": deploymentid})
    return res["referral_code"]


# Obsolete
# Checks if user exists in database given a user id/phone number
def getUser(userid):
    print("getUser(userid) ", userid)
    res = select_by_query("User", ["userid"], {"userid": userid})
    return res


# check if user demographic info already exists
def getUserDemographic(userid, deploymentid):
    res = select_by_query("Demographic", ["gender"], {"userid": userid, "deploymentid": deploymentid})
    return res


# check username exist or not
def getUserByUsername(username):
    print("getUserByUsername(username) ", username)
    res = select_by_query("User", ["userid"], {"username": username})
    return res


# NOT IN USE
def getUserId(username):
    print("getUserId(username) ", username)
    res = select_by_query("User", ["userid"], {"username": username})
    return res["userid"]


# NOT IN USE need to change if use
def getUsername(userid):
    print("getUsername(userid) ", userid)
    res = select_by_query("User", ["username"], {"userid": userid})
    return res["username"]


# Get message script json from Deployment table
# version: web or sms
# return script dictionary
def getScript(deploymentid):
    print("getScript(deploymentid) ", deploymentid)
    res = select_by_query("Deployment", ["script_name"], {"deploymentid": deploymentid})
    script_name = res["script_name"]
    res_script = select_by_query("Script", ["content"], {"script_name": script_name})
    script_content = res_script["content"]
    return json.loads(script_content)


def insertUserScriptConfig(userid, config, deploymentid):
    print("insertUserScriptConfig(userid, config, deploymentid) ", [userid, config, deploymentid])
    insert_row_query("UserScriptConfig", {"userid": userid, "config": config, "deploymentid": deploymentid})


def getUserScriptConfig(userid, deploymentid):
    configs = []
    res = select_by_query("UserScriptConfig", ["config"], {"userid": userid, "deploymentid": deploymentid}, False)
    for r in res:
        configs.append(r["config"])
    return configs


# A user may be in different deployment.
# Get the largest (most recent) deployment id.
def getUserDeployment(userid):
    print("getUserDeployment(userid) ", userid)
    deployments = []
    res = select_by_query("User", ["deploymentid"], {"userid": userid}, False)
    for r in res:
        deployments.append(r["deploymentid"])
    return max(deployments)


def getDeploymentStartEndDate(deploymentid):
    print("getDeploymentEndDate(deploymentid) ", deploymentid)
    res = select_by_query("Deployment", ["start_date", "end_date"], {"deploymentid": deploymentid})
    return res["start_date"], res["end_date"]


# check if the year-pair already existed to avoid repeated messaging
def checkResponseExist(userid, year1, year2, deploymentid):
    print("checkResponseExist(userid, year1, year2, deploymentid)", [userid, year1, year2, deploymentid])
    res = select_by_query("Response", ["userid"], {"deploymentid": deploymentid, "userid": userid,
                                                   "year1": year1, "year2": year2})
    if res:
        return True
    return False


# Inserts user response into database, given user id, region, 2 years and answer
def insertResponse(userid, year1, year2, answer, points, deploymentid,
                   match_sat, match_wea, match_neighbour,
                   neighbour_answered, match_neighbour_real, neighbour_answered_real):
    print("insertResponse(userid, year1, year2, answer, points, deploymentid, "
          "match_sat, match_wea, match_neighbour, neighbour_answered)",
          [userid, year1, year2, answer, points, deploymentid,
           match_sat, match_wea, match_neighbour, neighbour_answered])

    insert_row_query("Response",
                     {"userid": userid, "year1": year1, "year2": year2, "answer": answer,
                      "points": points, "deploymentid": deploymentid,
                      "matchsat": match_sat, "matchwea": match_wea,
                      "matchneighbour": match_neighbour, "neighbouranswered": neighbour_answered,
                      "matchneighbour_real": match_neighbour_real, "neighbouranswered_real": neighbour_answered_real})


# Gets user score based on user id/Phone number
# return the score and the last update time
def getUserScore(userid, deploymentid):
    print("getUserScore(userid, deploymentid) ", [userid, deploymentid])
    res = select_by_query("User", ["score", "scorelastupdatetime"], {"userid": userid, "deploymentid": deploymentid})
    return res["score"], res["scorelastupdatetime"]


# Updates user score given user ID and new Score
def setUserScore(user, score, deploymentid):
    print("setUserScore(user, score) ", [user, score])
    try:
        cur.execute("UPDATE \"User\" SET score = %s WHERE userid = '%s' AND deploymentid = '%s'" % (score, user, deploymentid))
    except Exception as e:
        conn.rollback()
        print('ERROR in "setUserScore(user, score)" ' + str([user, score]) + ';\n error:' + repr(e))
    else:
        conn.commit()


# Gets actual value from satellite data given satellite/station source name
# return None if no data found for the input year
def getSatValue(source_name, year):
    print("getSatValue(source_name, year) ", [source_name, year])
    res = select_by_query("Data", ["value"], {"source_name": source_name, "year": year})
    if res:
        return res["value"]
    return None


# Get satellite source name given deploymentid
def getSatSource(deploymentid):
    print("getSatSource(deploymentid) ", deploymentid)
    res = select_by_query("Deployment", ["sat_source"], {"deploymentid": deploymentid})
    return res["sat_source"]


def getStationSource(deploymentid):
    print("getStationSource(deploymentid) ", deploymentid)
    res = select_by_query("Deployment", ["station_source"], {"deploymentid": deploymentid})
    return res["station_source"]


def getGamificationOption(deploymentid):
    print("getGamificationOption(deploymentid) ", deploymentid)
    res = select_by_query("Deployment", ["gamification"], {"deploymentid": deploymentid})
    return int(res["gamification"])


# Get all the available years from satellite data given satellite and weather station source
# Return a list of years
def getYears(sat_source, station_source):
    print("getYears(sat_source, station_source) ", [sat_source, station_source])
    years = []
    res_sat = select_by_query("Data", ["year"], {"source_name": sat_source}, False)
    for r in res_sat:
        years.append(r["year"])
    res_sat = select_by_query("Data", ["year"], {"source_name": station_source}, False)
    for r in res_sat:
        years.append(r["year"])
    return years


# gets all user responses given userid
def getUserResponses(userid, deploymentid):
    print("getUserResponses(userid, deploymentid) ", [userid, deploymentid])
    res = select_by_query("Response", ["year1", "year2"], {"userid": userid, "deploymentid": deploymentid}, False)
    responses = []
    for r in res:
        responses.append([r["year1"], r["year2"]])
    return responses


# gets all responses for a particular question combination for given deployment
# return a list of answers (1 for year1, 2 for year2, 3 for same, 4 for unknown)
# return another list of answers for real users only
def getDeployResponses(year_1, year_2, deploymentid):
    print("getDeployResponses(year_1, year_2, deploymentid) ", [year_1, year_2, deploymentid])

    # deprecated
    # DeployResponse view
    # res = select_by_query("DeployResponse", ["answer"],
    #                       {"year1": year_1, "year2": year_2, "deploymentid": deploymentid},
    #                       unique=False, is_view=True)

    res = select_by_query("Response", ["answer"],
                          {"year1": year_1, "year2": year_2, "deploymentid": deploymentid},
                          unique=False)
    responses = []
    for r in res:
        responses.append(r["answer"])

    res_real = select_by_query("Response", ["answer"],
                          {"year1": year_1, "year2": year_2, "deploymentid": deploymentid},
                          unique=False, fake_user=False)
    responses_real = []
    for r in res_real:
        responses_real.append(r["answer"])
    return responses, responses_real


# Gets all user scores for a given deployment
# return a list of tuples consist of scores and last update times
def getDeployScores(deploymentid):
    print("getDeployScores(deploymentid) ", deploymentid)
    res = select_by_query("User", ["score", "scorelastupdatetime"], {"deploymentid": deploymentid}, False)
    scores_times = []
    for r in res:
        scores_times.append((r["score"], r["scorelastupdatetime"]))
    return scores_times


# def getDeployUsers(deploymentid):
#     print("getDeployUsers(deploymentid) ", deploymentid)
#     res = select_by_query("User", [], {"deploymentid": deploymentid}, False)
#     users = []
#     for r in res:
#         users.append(r)
#     return users


def countDeployUsers(deploymentid):
    print("countDeployUsers(deploymentid)", deploymentid)
    res = select_by_query("User", ["count(*)"], {"deploymentid": deploymentid}, True)
    return int(res["count"])


def countDeployRealUsers(deploymentid):
    print("countDeployRealUsers(deploymentid)", deploymentid)
    res = select_by_query("User", ["count(*)"], {"deploymentid": deploymentid}, True, fake_user=False)
    print("countDeployRealUsers(deploymentid)", int(res["count"]))
    return int(res["count"])


# return the number of users under gamified version and non gamified version
def countGamifiedConfigs(deploymentid):
    print("countConfigs(deploymentid)", deploymentid)
    res_g = select_by_query("UserScriptConfig", ["count(*)"], {"deploymentid": deploymentid, "config": "g"})
    res_ng = select_by_query("UserScriptConfig", ["count(*)"], {"deploymentid": deploymentid, "config": "ng"})
    return int(res_g["count"]), int(res_ng["count"])


# check if entry code exists and not obsolete
# return deploymentid
def getDeployByCode(entry_code):
    print("getDeployByCode(entry_code)", entry_code)
    res = select_by_query("Deployment", ["deploymentid"], {"entry_code": entry_code}, True)
    if res:
        return res["deploymentid"]


def getEntryCode(deploymentid):
    print("getEntryCode(deploymentid)", deploymentid)
    res = select_by_query("Deployment", ["entry_code"], {"deploymentid": deploymentid})
    return res["entry_code"]


def getReferralTime(userid, deploymentid):
    print("getReferralTime(userid, deploymentid) ", [userid, deploymentid])
    res = select_by_query("Referral", ["user_timestamp"], {"userid": userid, "deploymentid": deploymentid})
    return res["user_timestamp"]


# insert demographic (gender)
def insertDemographic(userid, gender, age, location, income, deploymentid):
    print("insertGender(userid, gender, location, income, deploymentid)",
          [userid, gender, location, income, deploymentid])
    insert_row_query("Demographic",
                     {"userid": userid, "gender": gender, "age": age, "location": location,
                      "deploymentid": deploymentid, "income": income})


def insertReferralInfo(userid, referral_code, entry_code, deploymentid):
    print("insertUserEntryCode(userid, referral_code, entry_code, deploymentid)",
          [userid, referral_code, entry_code, deploymentid])
    insert_row_query("Referral",
                     {"userid": userid, "referral_code": referral_code, "entry_code": entry_code, "deploymentid": deploymentid})


# returns a dictionary (key: index, value: location)
def getDeployLocations(deploymentid):
    print("getDeployLocations(deploymentid) ", deploymentid)
    res = select_by_query("DeployLocation", ["location", "listorder"], {"deploymentid": deploymentid}, False)
    location_dict = {}
    for r in res:
        location_dict[int(r["listorder"])+1] = r["location"]

    return location_dict


def deleteUser(userid, deploymentid):
    print("deleteUser(userid, deploymentid) ", [userid, deploymentid])
    try:
        cur.execute('''DELETE FROM "Referral" WHERE userid=\'%s\' and deploymentid=\'%s\' ''' % (userid, deploymentid))
        cur.execute('''DELETE FROM "Response" WHERE userid=\'%s\' and deploymentid=\'%s\' ''' % (userid, deploymentid))
        cur.execute('''DELETE FROM "Demographic" WHERE userid=\'%s\' and deploymentid=\'%s\' ''' % (userid, deploymentid))
        cur.execute('''DELETE FROM "UserScriptConfig" where userid=\'%s\' and deploymentid=\'%s\' ''' % (userid, deploymentid))
    except Exception as e:
        conn.rollback()
        print('ERROR in "deleteUser(userid)" ' + userid + ';\n error:' + repr(e))
        return
    else:
        conn.commit()

        try:
            cur.execute('''DELETE FROM "User" WHERE userid=\'%s\' and deploymentid=\'%s\' ''' % (userid, deploymentid))
        except Exception as e:
            conn.rollback()
            print('ERROR in "deleteUser(userid)" ' + userid + ';\n error:' + repr(e))
        else:
            conn.commit()
