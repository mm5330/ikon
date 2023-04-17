import random
import string
from flask import session
from .database import *
from .models import User
from datetime import datetime
import atexit

# close database connection when the program terminates
atexit.register(closeConnection)


# sorts users by score
def sortByScore(user_list):
    list_len = len(user_list)
    for i in range(0, list_len):
        for j in range(0, list_len - i - 1):
            if user_list[j]["score"] < user_list[j + 1]["score"]:
                temp = user_list[j]
                user_list[j] = user_list[j + 1]
                user_list[j + 1] = temp
    return user_list


def generateTwoYears(user_id, all_years):
    # the max num of possible 2-year combos
    comb_num = len(all_years) * (len(all_years)-1)
    random.seed(datetime.now())
    # get two random years from all the available years
    two_years = random.sample(all_years, 2)
    user_responses = getUserResponses(user_id, two_years[0], two_years[1])
    # num of combo tried
    count = 0
    # make sure that the user has not answer the same question and that the two years are not the same
    while user_responses or (two_years[0] == two_years[1]):
        # if exhausted all possible combos
        if count >= comb_num:
            return None
        two_years = random.sample(all_years, 2)
        user_responses = getUserResponses(user_id, two_years[0], two_years[1])
        count += 1
    question_year_1 = two_years[0]
    question_year_2 = two_years[1]
    return [question_year_1, question_year_2]


# return 1 for data_1 greater, 2 for data_2 greater, 3 for same
# TODO: add std dev component
def getAnswer(data_1, data_2):
    diff = data_1 - data_2
    if diff > 0:
        return 1
    if diff < 0:
        return 2
    if not diff:
        return 3


def update_deploy_users(deployment_id):
    # get all the users in current deployment
    deploy_users = []
    deploy_users_db = getDeployUsers(deployment_id)
    # tuples in deploy_users are in the form (userid, location, score, deploymentid, username)
    for u in deploy_users_db:
        u_name = u["username"]
        # truncate username if longer than 7 chars
        if len(u_name) > 9:
            u_name = u_name[-9:]
        u_id = u["userid"]
        u_score = u["score"]
        user = {"id": u_id, "name": u_name, "score": u_score}
        deploy_users.append(user)
    deploy_users = sortByScore(deploy_users)
    return deploy_users


# determine the score weights by the number of users in the current deployment
# return score weight for matching neighbour
# TODO: may want to change the function for the matching neighbour weight
def getNeighborWeights(deploymentid):
    neighbor_num = countDeployUsers(deploymentid)
    neighbor_weight = 2 * neighbor_num
    # cap at 75 percent
    if neighbor_weight > 75:
        neighbor_weight = 75
    return neighbor_weight


def user_info_update(user_id):
    session["user_name"] = getUsername(user_id)
    # session["user_location"] = getRegion(user_id)
    session["user_score"] = getUserScore(user_id)
    deployment_id = getUserDeployment(user_id)
    session["deployment_id"] = deployment_id
    # get message script file for the deployment
    session["script_dict"] = getScript(deployment_id, "web")
    # get all the users in current deployment
    session["deploy_users"] = update_deploy_users(deployment_id)
    # get the source names
    session["sat_source_name"] = getSatSource(deployment_id)
    session["station_source_name"] = getStationSource(deployment_id)
    session["deploy_years"] = getYears(session["sat_source_name"], session["station_source_name"])


def user_info_initialize(user_id):
    return User(user_id, session["user_name"], session["user_score"],
                session["deployment_id"], session["script_dict"], session["deploy_users"],
                session["sat_source_name"], session["station_source_name"], session["deploy_years"])


# generate uppercase code with given length
def generate_code(length):
    random.seed(datetime.now())
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(length))
