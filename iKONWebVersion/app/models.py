from flask_login import UserMixin
from flask import session


def getRank(deploy_users, userid):
    rank = 0
    for u in deploy_users:
        rank += 1
        if u["id"] == userid:
            break
    return rank


class User(UserMixin):
    def __init__(self, userid, username, score, deployment_id, script_dict, deploy_users,
                 sat_source_name, station_source_name, deploy_years):
        self.id = userid
        self.username = username
        self.score = score
        self.deployment = deployment_id

        self.script_dict = script_dict
        self.deploy_users = deploy_users
        self.sat_source_name = sat_source_name
        self.station_source_name = station_source_name
        self.deploy_years = deploy_years

        self.rank = getRank(deploy_users, userid)

    def __repr__(self):
        return "%s/%s/%d" % (self.id, self.username, self.score)

    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def get_deployment(self):
        return self.deployment

    def get_score(self):
        return self.score

    def get_script_dict(self):
        return self.script_dict

    def get_deploy_users(self):
        return self.deploy_users

    def get_sat_source_name(self):
        return self.sat_source_name

    def get_station_source_name(self):
        return self.station_source_name

    def get_deploy_years(self):
        return self.deploy_years

    def get_rank(self):
        return self.rank

    def set_score(self, new_score):
        self.score = new_score
        session["user_score"] = new_score

    def set_deploy_users(self, deploy_users):
        self.deploy_users = deploy_users
        session["deploy_users"] = deploy_users
