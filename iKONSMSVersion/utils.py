from database import *
import atexit
import random
import re
from twilio.rest import Client
from flask import session
from hashlib import md5
import html
import datetime
from pytz import timezone

# close database connection when the program terminates
atexit.register(closeConnection)

# IRI Account
# Your Account SID from twilio.com/console
account_sid = "sid"
# Your Auth Token from twilio.com/console
auth_token = "auth"
client = Client(account_sid, auth_token)

medals = {1: "🥇🏆", 2: "🥈", 3: "🥉"}


# send message if not none
def sendMessage(user_number, message, to_number=None):
    if message:
        if to_number is None:
            to_number = extract_number(user_number)
        ikon_number = "00000000"
        if "whatsapp" in user_number:
            ikon_number = "whatsapp:+" + ikon_number
            to_number = "whatsapp:+" + str(to_number)
        client.messages.create(
            body=message,
            from_=ikon_number,
            to=to_number
        )


def generateTwoYears(userid):
    all_years = session["deploy_years"]
    # the max num of possible 2-year combos
    comb_num = len(all_years) * (len(all_years) - 1)
    random.seed(datetime.datetime.now())
    # get two random years from all the available years
    two_years = random.sample(all_years, 2)
    user_responses = getUserResponses(userid, session["deployment_id"])
    # num of combo tried
    count = 0
    # make sure that the user has not answer the same question and that the two years are not the same
    while two_years in user_responses:  # or (two_years[0] == two_years[1])
        # if exhausted all possible combos
        if count >= comb_num:
            return None
        two_years = random.sample(all_years, 2)
        count += 1
    question_year_1 = two_years[0]
    question_year_2 = two_years[1]
    return [question_year_1, question_year_2]


# return rank for the user in the given deployment
# and settle ties
def getRank(userid, deploymentid):
    user_score, last_update_time = getUserScore(userid, deploymentid)
    scores_times = getDeployScores(deploymentid)
    # if score is 0, rank last
    if int(user_score) == 0:
        return len(scores_times)

    # sort the scores_times pair list by scores
    scores_times.sort(key=lambda x: x[0], reverse=True)
    # get best possible score rank, update time not yet considered
    scores = [st[0] for st in scores_times]
    rank = scores.index(user_score) + 1

    # get all pairs with the same score
    same_scores = filter(lambda x: x[0] == user_score, scores_times)
    same_scores_lst = list(same_scores)
    # the user with LATER update time will get BETTER ranking
    for t in same_scores_lst:
        if last_update_time < t[1]:
            rank += 1

    session["user_rank"] = rank
    return rank


def user_info_update(user_id):
    deployment_id = getUserDeployment(user_id)
    session["deployment_id"] = deployment_id
    # get user rank
    session["user_rank"] = getRank(user_id, deployment_id)
    # get number of users in the deployment
    session["user_num"] = countDeployUsers(deployment_id)
    # get message script file for the deployment
    user_code = getReferralCode(user_id, deployment_id)
    session["user_code"] = user_code
    # the list of script configs
    user_configs = getUserScriptConfig(user_id, deployment_id)
    session["user_config"] = user_configs
    get_script_dicts(user_id, deployment_id)
    # get the source names
    session["sat_source_name"] = getSatSource(deployment_id)
    session["station_source_name"] = getStationSource(deployment_id)
    session["deploy_years"] = getYears(session["sat_source_name"], session["station_source_name"])


# Generates combination given Year 1 and Year 2
def generateQuestion(script_dict, userid):
    print("generateQuestion(userid, script, deploymentid) ", userid)
    years = generateTwoYears(userid)
    if not years:
        return None
    question_year_1 = years[0]
    question_year_2 = years[1]
    session["question_year_1"] = question_year_1
    session["question_year_2"] = question_year_2
    question = script_dict["question"] % (question_year_1, question_year_2, question_year_1, question_year_2)
    return question


# return 1 for data_1 greater, 2 for data_2 greater, 3 for same
# return None if either one data is None (not found)
def getAnswer(data_1, data_2):
    if (data_1 is None) or (data_2 is None):
        return None

    diff = data_1 - data_2
    if diff > 0:
        return 1
    if diff < 0:
        return 2
    if not diff:
        return 3


# return messages for current user score and rank
def user_score_rank(script_dict, memory_trigger_script, user_id):
    deployment_id = session["deployment_id"]
    user_score, _ = getUserScore(user_id, deployment_id)
    # user score message
    score_msg = script_dict["user_score"] % int(user_score)
    user_rank = getRank(user_id, deployment_id)
    user_num = countDeployUsers(deployment_id)

    # check is memory trigger script is defined
    if memory_trigger_script is not None:
        # congratulation message for first three places
        if user_rank in range(1, 4):
            rank_msg = memory_trigger_script["good_user_rank"] % (user_rank, user_num) + medals[user_rank]
        # congratulation message for fourth to seventh
        elif user_rank in range(4, 7):
            rank_msg = memory_trigger_script["good_user_rank"] % (user_rank, user_num)
        else:
            rank_msg = memory_trigger_script["user_rank"] % (user_rank, user_num)
    else:
        rank_msg = script_dict["user_rank"] % (user_rank, user_num)

    return score_msg, rank_msg


# Checks response and updates scores based on response
# answer: 1 for year1, 2 for year2, 3 for same, 4 for unknown
# return the message string
def checkResponse(userid, year_1, year_2, answer, user_id, script_dict, memory_trigger_script):
    deployment_id = session["deployment_id"]
    sat_source_name = session["sat_source_name"]
    station_source_name = session["station_source_name"]
    user_score, last_update_time = getUserScore(user_id, deployment_id)
    session["user_score"] = user_score
    session["score_update_time"] = last_update_time
    deploy_user_weight = 5
    sat_source_weight = 30
    station_source_weight = 30
    # return message
    msg = ""
    # points gained
    points = 0
    match_sat = 0
    match_wea = 0

    # get actual satellite and weather station data for each year
    sat_data_1 = getSatValue(sat_source_name, year_1)
    sat_data_2 = getSatValue(sat_source_name, year_2)
    station_data_1 = getSatValue(station_source_name, year_1)
    station_data_2 = getSatValue(station_source_name, year_2)

    # answer based on satellite and weather station data
    sat_answer = getAnswer(sat_data_1, sat_data_2)
    station_answer = getAnswer(station_data_1, station_data_2)
    # match with satellite data
    if sat_answer == answer:
        match_sat = 1
        msg += script_dict["satellite_matched"] % sat_source_name
        points += sat_source_weight
    # match with weather station data
    if station_answer == answer:
        match_wea = 1
        msg += script_dict["station_matched"] % station_source_name
        points += station_source_weight
    # match with other user responses in the deployment
    deploy_responses, deploy_responses_real = getDeployResponses(year_1, year_2, deployment_id)
    match_neighbour = deploy_responses.count(answer)
    match_neighbour_real = deploy_responses_real.count(answer)
    neighbour_answered = len(deploy_responses)
    neighbour_answered_real = len(deploy_responses_real)
    if match_neighbour > 0:
        matched_percent = (match_neighbour / len(deploy_responses)) * 100
        msg += script_dict["user_matched"] % int(matched_percent)
        real_user_num = countDeployRealUsers(deployment_id)
        points += real_user_num * deploy_user_weight

    print("total points gained: ", points)
    if points > 0:
        msg += script_dict["earn_points"] % int(points)
        new_user_score = user_score + int(points)
        setUserScore(userid, new_user_score, deployment_id)
        session["user_score"] = new_user_score
    # message for no match
    else:
        msg = script_dict["no_match"]

    score_msg, rank_msg = user_score_rank(script_dict, memory_trigger_script, user_id)

    score_rank_msg = score_msg + rank_msg
    return msg, score_rank_msg, points, match_sat, match_wea, \
           match_neighbour, neighbour_answered, match_neighbour_real, neighbour_answered_real


def getLocationList():
    location_list = ""
    # get current deployment
    deployment_id = session.get("deployment_id")
    # ask for location
    location_dict = getDeployLocations(deployment_id)
    # store location dict in session
    session["location_dict"] = location_dict
    session["location_num"] = len(location_dict.keys())
    for i in sorted(location_dict):
        location_list += "\n" + str(i) + " " + location_dict[i]
    return location_list


# generate a user referral code by hashing phone number
# number: string type
def generate_code(number):
    b_number = bytes(number, 'utf-8')
    hash_hex = md5(b_number).hexdigest()
    # get last 4 digits as referral code
    code = int(hash_hex, base=16) % 10000
    return code

    # random.seed(datetime.now())
    # numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    # return ''.join(random.choice(numbers) for i in range(length))


# not in use, applying a different way of randomization
def get_config(code):
    code_num = extract_number(code)
    mod8 = code_num % 8
    # Script I
    if mod8 in [0, 1]:
        return "1"
    # Script II
    if mod8 in [2, 3]:
        return "2"
    # Script III
    if mod8 in [4, 5]:
        return "3"
    # Script IVa
    if mod8 == 6:
        return "4a"
    # Script IVb
    if mod8 == 7:
        return "4b"


def set_gamification_config(user_num_g, userid, deployment_id):
    # reward script
    reward_config = "r1"  # reward script 1
    mod2 = user_num_g % 2
    if mod2 == 1:
        reward_config = "r2"  # reward script 2

    # general script
    general_config = "1"  # Script 1
    mod8 = user_num_g % 8
    if mod8 in [2, 3]:
        general_config = "2"  # Script 2
    elif mod8 in [4, 5]:
        general_config = "3"  # Script 3
    elif mod8 == 6:
        general_config = "4a"  # Script 4a
    elif mod8 == 7:
        general_config = "4b"  # Script 4b

    insertUserScriptConfig(userid, reward_config, deployment_id)
    insertUserScriptConfig(userid, general_config, deployment_id)


# The script config is assigned to user on a rolling basis
# outer-most layer: game/non-game;
# within game layer: reward 1/2, general 1/2/3/4a/4b
def insert_config(userid, deployment_id):
    gamification_option = getGamificationOption(deployment_id)
    # completely non-gamified version
    if gamification_option == 0:
        gamified_config = "ng"

    else:
        # get the number of users under gamified and non gamified version respectively
        user_num_g, user_num_ng = countGamifiedConfigs(deployment_id)
        # completely gamified version
        if gamification_option == 1:
            gamified_config = "g"  # gamified version
            set_gamification_config(user_num_g + user_num_ng, userid, deployment_id)
        # half and half
        else:
            # gamified or non-gamified
            gamified_config = "ng"  # non-gamified version
            user_num = user_num_g + user_num_ng
            mod2_g = user_num % 2
            if mod2_g == 0:
                gamified_config = "g"  # gamified version
                set_gamification_config(user_num_g, userid, deployment_id)

    insertUserScriptConfig(userid, gamified_config, deployment_id)


def get_script_dicts(user_id, deployment_id):
    script_dict_deploy = getScript(deployment_id)
    user_configs = getUserScriptConfig(user_id, deployment_id)
    session["user_config"] = user_configs
    # will throw an error if these keys are not found in the script file, so they are required
    session["base_script_dict"] = script_dict_deploy["sms"]["base"]
    session["game_script_dict"] = script_dict_deploy["sms"]["gamified"]["general"]
    # NOTE: the keys "question", "invite", "main_menu" are present in both "base" and "gamified"

    for config in user_configs:
        # identify the config number for memory trigger script
        try:
            if config in ["1", "2", "3", "4a", "4b"]:
                session["memory_trigger_script"] = script_dict_deploy["sms"]["gamified"][config]
        # return none if no memory trigger script assigned
        except KeyError:
            session["memory_trigger_script"] = None

        # identify the config number for reward message script
        try:
            if config in ["r1", "r2"]:
                session["reward_script"] = script_dict_deploy["sms"]["gamified"][config]
        # return none if no reward script assigned
        except KeyError:
            session["reward_script"] = None


def extract_number(body):
    number = ""
    digits = re.findall("\d+", body)
    for d in digits:
        number += d
    if number:
        return int(number)


def extract_letters(body):
    letters = ""
    chars = re.findall("[a-zA-Z]+", body)
    for c in chars:
        letters += c
    if letters:
        return letters


def remove_spaces(body):
    body = body.lower()
    s = ""
    digits = re.findall("\S+", body)
    for d in digits:
        s += d
    return s


# create a log file for new user info and config
def create_log(user_id, code, config):
    f = open("./logs/%s.txt" % user_id, "a")
    d = datetime.utcnow()
    f.write("Userid: %s\nTime started (UTC): %s\nUnique code: %s\nScript assigned: %d\n\n"
            % (user_id, d, code, config))
    f.close()


def log_user_resp(user_id, resp):
    f = open("./logs/%s.txt" % user_id, "a")
    d = datetime.utcnow()
    f.write("\nTimestamp: %s\nUser: %s\n" % (d, resp))
    f.close()


# write user interaction to log
def log_response(user_id, resp):
    f = open("./logs/%s.txt" % user_id, "a")
    d = datetime.utcnow()
    f.write("\nTimestamp: %s\n" % d)
    messages = re.findall(r'<Message>([\s\S]*?)</Message>', resp)
    i = 1
    for m in messages:
        f.write("%s\n" % html.unescape(m))
        i += 1
    f.close()


# may not needed anymore
# get the time difference between user registration and current time
# return value in hour
def check_time_diff(user_id):
    deploymentid = getUserDeployment(user_id)
    register_timestamp = getReferralTime(user_id, deploymentid)
    register_timestamp = register_timestamp - datetime.timedelta(minutes=12)
    print(register_timestamp)
    utc_time = datetime.datetime.utcnow()
    utc_time = utc_time.replace(tzinfo=datetime.timezone.utc)
    print(utc_time)
    diff = utc_time - register_timestamp
    print(diff)
    sec = diff.total_seconds()
    return sec


def check_user_exist(user_id):
    if getUser(user_id) is None:
        return False

    # get user's latest deployment id
    deploymentid = getUserDeployment(user_id)
    if deployment_obsolete(deploymentid):
        get_script_dicts(user_id, deploymentid)
        return None
    else:
        return True


# check if the end date for the deployment has passed
def deployment_obsolete(deploymentid):
    _, end_date = getDeploymentStartEndDate(deploymentid)
    tz = timezone('EST')
    end_date_time = datetime.datetime.combine(end_date, datetime.datetime.max.time(), tz)
    est_now = datetime.datetime.now(tz=tz)
    if est_now > end_date_time:
        return True
    else:
        return False


def get_script_word(script_dict_base, script_dict_game, script_word, script_configs):
    # the list of words that have both a game and a non-game version
    word_list = ["who_we_are", "purpose", "learning", "privacy_notice", "send_start", "resume_start",
                 "demographic_intro", "game_start", "forward_invite", "game_time", "game_over", "question", "main_menu",
                 "invite", "referral_reward"]

    if ("g" in script_configs) and (script_word in word_list):
        return script_dict_game.get(script_word)

    return script_dict_base.get(script_word)


def date_to_string(d):
    return d.strftime("%A, %B %d")
