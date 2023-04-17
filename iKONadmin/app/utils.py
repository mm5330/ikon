import flask
from .models import DeployLocation, Script, DataSource, Data, Deployment, AdminDeploy, Player, Referral, \
    db_session, engine, AdminProject
from flask_login import current_user


def updateLocationList(locations, deploy_id, d_locations):
    location_list = locations.split('\r\n')
    location_list = list(filter(lambda a: a != '', location_list))
    location_dict = {}
    loc_ord = 0
    # remove duplicates and get ordering
    for loc in location_list:
        if loc not in location_dict:
            location_dict[loc] = loc_ord
            loc_ord += 1
    # remove all old locations
    for d_loc in d_locations:
        db_session.delete(d_loc)
    db_session.commit()
    # add new ones
    for loc in location_dict.keys():
        deploy_loc = DeployLocation(deploymentid=deploy_id, location=loc, listorder=location_dict[loc])
        db_session.add(deploy_loc)
    db_session.commit()


def getScripts():
    scripts = db_session.query(Script)
    lang_options = []
    for s in scripts:
        lang_option = (s.language, s.language)
        lang_options.append(lang_option)
    return lang_options


def getGamificationOptions():
    gamified_option = [(0, "Non-Gamified"), (1, "Gamified"), (2, "Semi-Gamified")]
    return gamified_option


def getDataSources():
    source_arr = []
    sat_options = []
    wea_options = []
    sat_sources = db_session.query(DataSource).filter_by(source_type='Satellite')
    wea_sources = db_session.query(DataSource).filter_by(source_type='Weather Station')
    for s in sat_sources:
        source_arr.append(s)
        sat_option = (s.source_name, s.source_name)
        sat_options.append(sat_option)
    for w in wea_sources:
        source_arr.append(w)
        wea_option = (w.source_name, w.source_name)
        wea_options.append(wea_option)
    return source_arr, sat_options, wea_options


def getProjectName():
    proj_names = []
    projects = db_session.query(AdminProject)
    for p in projects:
        proj_names.append(p.project_name)
    return proj_names


# create a new project if project not exists
def getProjectIdByName(project_name):
    project = db_session.query(AdminProject).filter_by(project_name=project_name).first()
    if project:
        return project.project_id

    # create a new project
    p = AdminProject(project_name=project_name)
    db_session.add(p)
    db_session.commit()
    project = db_session.query(AdminProject).filter_by(project_name=project_name).first()
    return project.project_id


def getProjectNameById(project_id):
    project = db_session.query(AdminProject).filter_by(project_id=project_id).first()
    return project.project_name


# create a new deployment and add admin-deploy relationship
def createDeployment(deploy_name, script_name, sat_source, station_source,
                     end_date, start_date, gamification, entry_code, project_name):
    deploy_id = 0
    ds = db_session.query(Deployment)
    for de in ds:
        if de.deploymentid >= deploy_id:
            deploy_id = de.deploymentid + 1
    d = Deployment(deploymentid=deploy_id,
                   deploymentname=deploy_name,
                   script_name=script_name,
                   sat_source=sat_source,
                   station_source=station_source,
                   entry_code=entry_code,
                   end_date=end_date,
                   start_date=start_date,
                   gamification=gamification,
                   admin_project=getProjectIdByName(project_name))
    db_session.add(d)
    db_session.commit()
    userid = current_user.admin_id
    db_session.add(AdminDeploy(admin_id=userid, deploymentid=deploy_id))
    db_session.commit()
    # add fake user
    addFakeUser(deploy_id, entry_code)
    return d


# add fake users
def addFakeUser(deploy_id, entry_code):
    # define ten fake users: fakeuser1-10
    fake_scores = [10, 40, 80, 160, 320, 640, 1280, 2560, 1500, 2500]
    for i in range(10):
        fake_id = 'fakeuser0' + str(deploy_id) + str(i+1)
        fake_score = fake_scores[i]
        fake_name = 'smsuser' + str(deploy_id * 10000 + i + 1)
        db_session.add(Player(userid=fake_id, score=fake_score, deploymentid=deploy_id, username=fake_name))
        db_session.commit()
        db_session.add(Referral(userid=fake_id, referral_code=None, entry_code=entry_code, deploymentid=deploy_id))
    db_session.commit()


def getDataSourceCSV(source_name):
    csv = 'year, value\n'
    sql_stmt = 'SELECT year, value FROM "Data" WHERE source_name=\'%s\'' % source_name
    res = engine.execute(sql_stmt)
    for row in res:
        for c in range(len(row)):
            # add a comma after first attribute
            if c == 0:
                csv += str(row[c]) + ','
            else:
                csv += str(row[c])
        csv += '\n'
    return csv


def getUniqueUserNumber(deploy_id):
    sql_stmt = 'SELECT count(*) AS num FROM "User" INNER JOIN "Referral" ' \
               'ON "User".userid = "Referral".userid AND "User".deploymentid = "Referral".deploymentid ' \
               'WHERE "User".deploymentid=%s AND "Referral".referral_code IS NOT NULL;' % deploy_id
    res = engine.execute(sql_stmt).fetchone()
    return res[0]


def getUniqueUserNumberAfter(deploy_id, start_date):
    sql_stmt = 'SELECT count(*) AS num FROM "User" INNER JOIN ' \
               '(SELECT * FROM "Referral" WHERE user_timestamp>\'%s\') as r ' \
               'ON "User".userid = r.userid AND "User".deploymentid = r.deploymentid ' \
               'WHERE "User".deploymentid=%s AND r.referral_code IS NOT NULL;' % (start_date, deploy_id)
    res = engine.execute(sql_stmt).fetchone()
    return res[0]


def getTotalResponses(deploy_id):
    sql_stmt = 'SELECT count(*) FROM ' \
               '(SELECT "User".userid, "User".deploymentid, username ' \
               'FROM "Response" LEFT JOIN "User" ' \
               'ON "Response".userid = "User".userid AND "User".deploymentid = "Response".deploymentid ' \
               'WHERE "User".deploymentid=%s AND username IS NOT NULL) AS R;' % deploy_id
    res = engine.execute(sql_stmt).fetchone()
    return res[0]


def getTotalResponsesAfter(deploy_id, start_date):
    sql_stmt = 'SELECT count(*) FROM ' \
               '(SELECT "User".userid, "User".deploymentid, username ' \
               'FROM "Response" LEFT JOIN "User" ' \
               'ON "Response".userid = "User".userid AND "User".deploymentid = "Response".deploymentid ' \
               'WHERE "User".deploymentid=%s AND "Response".timestamp>\'%s\' ' \
               'AND username IS NOT NULL) AS R;' % (deploy_id, start_date)
    res = engine.execute(sql_stmt).fetchone()
    return res[0]


def getYearSpan(sat_name, wea_name):
    sql_stmt = 'SELECT max(year), min(year) FROM "Data" ' \
               'WHERE source_name=\'%s\' OR source_name=\'%s\';' % (sat_name, wea_name)
    res = engine.execute(sql_stmt).fetchone()
    return res[0], res[1]


def getTopUserResponse(deploy_id):
    user_arr = []
    resp_num_arr = []
    sql_stmt = 'SELECT username, count(*) AS resp FROM ' \
               '(SELECT "User".userid AS userid, username, "User".deploymentid as deploymentid ' \
               'FROM "Response" LEFT JOIN "User" ' \
               'ON "Response".userid = "User".userid AND "User".deploymentid = "Response".deploymentid ' \
               'WHERE "User".deploymentid=%s AND username IS NOT NULL) AS R GROUP BY username ' \
               'ORDER BY resp DESC LIMIT 10;' % deploy_id
    res = engine.execute(sql_stmt)
    for row in res:
        user_arr.append(row[0])
        resp_num_arr.append(row[1])
    user_arr.reverse()
    resp_num_arr.reverse()
    return user_arr, resp_num_arr


def getTopUserResponseAfter(deploy_id, start_date):
    user_arr = []
    resp_num_arr = []
    sql_stmt = 'SELECT username, count(*) AS resp FROM ' \
               '(SELECT "User".userid AS userid, username, "User".deploymentid as deploymentid ' \
               'FROM "Response" LEFT JOIN "User" ' \
               'ON "Response".userid = "User".userid AND "User".deploymentid = "Response".deploymentid ' \
               'WHERE "User".deploymentid=%s AND "Response".timestamp>\'%s\' ' \
               'AND username IS NOT NULL) AS R GROUP BY username ' \
               'ORDER BY resp DESC LIMIT 10;' % (deploy_id, start_date)
    res = engine.execute(sql_stmt)
    for row in res:
        user_arr.append(row[0])
        resp_num_arr.append(row[1])
    user_arr.reverse()
    resp_num_arr.reverse()
    return user_arr, resp_num_arr


def getAges(deploy_id):
    age_arr = []
    sql_stmt = 'SELECT count(*) FROM "Demographic" LEFT JOIN "User" ' \
               'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
               'WHERE age=0 AND "User".deploymentid=%s;' % deploy_id
    res = engine.execute(sql_stmt).fetchone()
    age_arr.append(res[0])
    for a in [1, 11, 21, 31, 41, 51]:
        sql_stmt = 'SELECT count(*) FROM "Demographic" LEFT JOIN "User" ' \
                   'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
                   'WHERE age>=%s AND age<=%s AND "User".deploymentid=%s;' % (a, a+9, deploy_id)
        res = engine.execute(sql_stmt).fetchone()
        age_arr.append(res[0])
    num_users = sum(age_arr)
    age_percent_arr = map(lambda x: round(x / num_users * 100, 2), age_arr)
    return list(age_percent_arr)


def getAgesAfter(deploy_id, start_date):
    age_arr = []
    sql_stmt = 'SELECT count(*) FROM "Demographic" LEFT JOIN "User" ' \
               'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
               'WHERE age=0 AND "User".deploymentid=%s AND "Demographic".timestamp>\'%s\';' % (deploy_id, start_date)
    res = engine.execute(sql_stmt).fetchone()
    age_arr.append(res[0])
    for a in [1, 11, 21, 31, 41, 51]:
        sql_stmt = 'SELECT count(*) FROM "Demographic" LEFT JOIN "User" ' \
                   'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
                   'WHERE age>=%s AND age<=%s AND "User".deploymentid=%s AND "Demographic".timestamp>\'%s\';' \
                   % (a, a + 9, deploy_id, start_date)
        res = engine.execute(sql_stmt).fetchone()
        age_arr.append(res[0])
    num_users = sum(age_arr)
    age_percent_arr = map(lambda x: round(x / num_users * 100, 2), age_arr)
    return list(age_percent_arr)


def getGenders(deploy_id):
    gender_arr = [0] * 3
    sql_stmt = 'SELECT gender, count("Demographic".userid) ' \
               'FROM "Demographic" LEFT JOIN "User" ' \
               'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
               'WHERE "User".deploymentid=%s GROUP BY gender ORDER BY gender;' % deploy_id
    res = engine.execute(sql_stmt).fetchall()
    for r in res:
        ind = int(r["gender"]) - 1
        gender_arr[ind] = r["count"]
    return gender_arr


def getGendersAfter(deploy_id, start_date):
    gender_arr = [0] * 3
    sql_stmt = 'SELECT gender, count("Demographic".userid) ' \
               'FROM "Demographic" LEFT JOIN "User" ' \
               'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
               'WHERE "User".deploymentid=%s AND "Demographic".timestamp>\'%s\' ' \
               'GROUP BY gender ORDER BY gender;' % (deploy_id, start_date)
    res = engine.execute(sql_stmt).fetchall()
    for r in res:
        ind = int(r["gender"]) - 1
        gender_arr[ind] = r["count"]
    return gender_arr


def getIncomes(deploy_id):
    income_arr = [0] * 8
    sql_stmt = 'SELECT income, count("Demographic".userid) ' \
               'FROM "Demographic" LEFT JOIN "User" ' \
               'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
               'WHERE "User".deploymentid=%s GROUP BY income ORDER BY income;' % deploy_id
    res = engine.execute(sql_stmt).fetchall()
    for r in res:
        if r["income"]:
            ind = int(r["income"]) - 1
            income_arr[ind] = r["count"]
    return income_arr


def getIncomesAfter(deploy_id, start_date):
    income_arr = [0] * 8
    sql_stmt = 'SELECT income, count("Demographic".userid) ' \
               'FROM "Demographic" LEFT JOIN "User" ' \
               'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
               'WHERE "User".deploymentid=%s AND "Demographic".timestamp>\'%s\' ' \
               'GROUP BY income ORDER BY income;' % (deploy_id, start_date)
    res = engine.execute(sql_stmt).fetchall()
    for r in res:
        if r["income"]:
            ind = int(r["income"]) - 1
            income_arr[ind] = r["count"]
    return income_arr


def getLocations(deploy_id):
    loc_arr = []
    loc_cnt_arr = []
    sql_stmt = 'SELECT location, count("Demographic".userid) ' \
               'FROM "Demographic" LEFT JOIN "User" ' \
               'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
               'WHERE "User".deploymentid=%s GROUP BY location ORDER BY location;' % deploy_id
    res = engine.execute(sql_stmt).fetchall()
    for r in res:
        loc_arr.append(r["location"])
        loc_cnt_arr.append(r["count"])
    return loc_arr, loc_cnt_arr


def getLocationsAfter(deploy_id, start_date):
    loc_arr = []
    loc_cnt_arr = []
    sql_stmt = 'SELECT location, count("Demographic".userid) ' \
               'FROM "Demographic" LEFT JOIN "User" ' \
               'ON "User".userid = "Demographic".userid AND "User".deploymentid = "Demographic".deploymentid ' \
               'WHERE "User".deploymentid=%s AND "Demographic".timestamp>\'%s\' ' \
               'GROUP BY location ORDER BY location;' % (deploy_id, start_date)
    res = engine.execute(sql_stmt).fetchall()
    for r in res:
        loc_arr.append(r["location"])
        loc_cnt_arr.append(r["count"])
    return loc_arr, loc_cnt_arr


def getScores(deploy_id):
    scores = []
    users = []
    sql_stmt = 'SELECT username, score FROM "User" RIGHT JOIN "Referral" ' \
               'on "User".userid = "Referral".userid AND "User".deploymentid = "Referral".deploymentid ' \
               'WHERE "User".deploymentid=%s AND "Referral".referral_code IS NOT NULL ' \
               'ORDER BY score DESC;' % deploy_id
    res = engine.execute(sql_stmt)
    for row in res:
        users.append(row[0])
        scores.append(row[1])
    return users, scores


def getScoresAfter(deploy_id, start_date):
    scores = []
    users = []
    sql_stmt = 'SELECT username, score FROM "User" RIGHT JOIN "Referral" ' \
               'ON "User".userid = "Referral".userid AND "User".deploymentid = "Referral".deploymentid ' \
               'WHERE "User".deploymentid=%s AND user_timestamp>\'%s\' AND "Referral".referral_code IS NOT NULL ' \
               'ORDER BY score DESC;' % (deploy_id, start_date)
    res = engine.execute(sql_stmt)
    for row in res:
        users.append(row[0])
        scores.append(row[1])
    return users, scores


def getYearComparisons(deploy_id):
    year_comparisons = dict()
    sql_stmt = 'SELECT year1, year2, count(*) FROM "Response" LEFT JOIN ' \
               '(SELECT "User".userid, "User".deploymentid, username FROM "User") AS U ' \
               'ON "Response".userid = U.userid AND "Response".deploymentid = U.deploymentid ' \
               'WHERE "Response".deploymentid=%s AND username IS NOT NULL ' \
               'GROUP BY year1, year2 ORDER BY year1, year2;' % deploy_id
    res = engine.execute(sql_stmt)
    for row in res:
        year_comparisons[(row[0], row[1])] = row[2]
    return year_comparisons


def getYearComparisonsAfter(deploy_id, start_date):
    year_comparisons = dict()
    sql_stmt = 'SELECT year1, year2, count(*) FROM "Response" LEFT JOIN ' \
               '(SELECT "User".userid, "User".deploymentid, username FROM "User") AS U ' \
               'ON "Response".userid = U.userid AND "Response".deploymentid = U.deploymentid ' \
               'WHERE "Response".deploymentid=%s AND "Response".timestamp>\'%s\' AND username IS NOT NULL ' \
               'GROUP BY year1, year2 ORDER BY year1, year2;' % (deploy_id, start_date)
    res = engine.execute(sql_stmt)
    for row in res:
        year_comparisons[(row[0], row[1])] = row[2]
    return year_comparisons


def getUserReferrals(deploy_id):
    referrers = []
    referee_num = []
    sql_stmt = 'SELECT username, count(*) FROM ' \
               '(SELECT username, userid FROM "User" WHERE deploymentid=%s) AS U RIGHT JOIN ' \
               '(SELECT R1.userid, R1.referral_code FROM "Referral" AS R1 JOIN "Referral" AS R2 ' \
               'ON R1.referral_code = R2.entry_code) AS R ON R.userid = U.userid ' \
               'WHERE username IS NOT NULL GROUP BY username' % deploy_id
    res = engine.execute(sql_stmt)
    for row in res:
        referrers.append(row[0])
        referee_num.append(row[1])
    return referrers, referee_num


def getUserReferralsAfter(deploy_id, start_date):
    referrers = []
    referee_num = []
    sql_stmt = 'SELECT username, count(*) FROM ' \
               '(SELECT username, userid FROM "User" WHERE deploymentid=%s) AS U RIGHT JOIN ' \
               '(SELECT R1.userid, R1.referral_code FROM "Referral" AS R1 JOIN "Referral" AS R2 ' \
               'ON R1.referral_code = R2.entry_code WHERE R1.user_timestamp>\'%s\') AS R ON R.userid = U.userid ' \
               'WHERE username IS NOT NULL GROUP BY username' % (deploy_id, start_date)
    res = engine.execute(sql_stmt)
    for row in res:
        referrers.append(row[0])
        referee_num.append(row[1])
    return referrers, referee_num


# remove from database both data source info and data
def deleteSourceByName(source_name):
    db_session.query(Data).filter_by(source_name=source_name).delete()
    db_session.commit()
    # db_session.query(DataSource).filter_by(source_name=source_name).delete()
    # db_session.commit()
    return


# replace or add new data source info
def addDataSource(source_name, source_type, source_country, source_region, source_description, exist_data=None):
    if exist_data:
        exist_data.source_type = source_type
        exist_data.location = source_region
        exist_data.country = source_country
        exist_data.description = source_description
        db_session.commit()
        return

    s = DataSource(source_name=source_name,
                   source_type=source_type,
                   location=source_region,
                   country=source_country,
                   owner=current_user.admin_id,
                   description=source_description)
    db_session.add(s)
    db_session.commit()


def insertDataOfSource(data_year, data_value, source_name):
    sd = Data(year=data_year,
              value=data_value,
              source_name=source_name)
    db_session.add(sd)
    db_session.commit()


def addScript(script_name, script_content, script_lang):
    s = Script(script_name=script_name,
               content=script_content,
               language=script_lang)
    db_session.add(s)
    db_session.commit()


def is_json_request(request: flask.Request, properties: list = []) -> bool:
    """Check whether the request's body could be parsed to JSON format, and all necessary properties specified by `properties` are in the JSON object
    Args:
        request (flask.Request): the flask request object wrapping the real HTTP request data
        properties (list[str]): list of property names to check. By default its an empty list
    Returns:
        boolean: whether the request is a JSON-content request and contains all the properties
    """
    try:
        body = request.get_json()
    except TypeError:
        return False
    if body is None:
        return False
    for prop in properties:
        if prop not in body:
            return False
    return True


def getMainName(name):
    main_name = ''
    for c in name:
        if c == '-':
            break
        main_name += c
    return main_name


# input: csv text string
def checkCsvDataType(source_data):
    data_arr = []
    data_years = []
    source_data = source_data.split('\n')
    for row_str in source_data[1:]:
        row = row_str.split(',')
        data_year = row[0]
        # check for duplicate year
        if data_year not in data_years:
            data_years.append(data_year)
            data_value = row[1]
            try:
                float(data_value)
                int(data_year)
                data_arr.append(row)
            except ValueError:
                return None
    return data_arr


# Defines content for response downloading
def getResponsesCSV(deploymentid):
    csv = 'useridlastfour, timestamp, deploymentid, configs, config_reward, year1, year2, answer, points, matchsat, matchwea, ' \
          'matchneighbour, matchneighbour_real, neighbouranswered, neighbouranswered_real, playerregistered, ' \
          'responsetime, gender, age, location, inviteaccepted,\n'

    response_view = 'SELECT RIGHT(userid, 4), "time_stamp", deploymentid, configs, config_reward, year1, year2, answer, points, matchsat, matchwea, ' \
                    'matchneighbour, matchneighbour_real, neighbouranswered, neighbouranswered_real, ' \
                    'playerregistered, responsetime, gender, age, location, inviteaccepted ' \
                    'FROM get_response_view_by_deployid(%s);' % deploymentid

    res = engine.execute(response_view)
    for row in res:
        for c in row:
            csv += str(c) + ','
        csv += '\n'
    return csv


