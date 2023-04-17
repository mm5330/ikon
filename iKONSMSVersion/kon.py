from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils import *
from config import Config
import time

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    # Start our TwiML response
    resp = MessagingResponse()
    # get user phone number as user id
    user_number = str(request.values.get('From'))
    user_id = str(extract_number(user_number))

    # incoming message sanity check
    if not body:
        return ""
    body = remove_spaces(body)

    # for debug purpose
    if body == "bye" or body == "iwannadelete":
        if body == "iwannadelete":
            deleteUser(user_id, getUserDeployment(user_id))
        session.clear()
        resp.message("Bye")
        return str(resp)

    print("body: ", body)
    print("user_id: ", user_id)

    #### NEW USER ####
    user_exist_status = check_user_exist(user_id)
    if not user_exist_status:
        # body = entry_code + referral_code
        entry_code = extract_letters(body)
        # get deployment id by entry code
        deployment_id = getDeployByCode(entry_code)
        if (deployment_id is not None) and (not deployment_obsolete(deployment_id)):
            last4digits = user_id[-4:]
            user_name = "smsuser" + str(deployment_id) + last4digits
            # check if username already existed
            username_exist_cnt = 1
            while getUserByUsername(user_name):
                # add an additional digit to avoid duplicates
                user_name = "smsuser" + str(deployment_id) + str(username_exist_cnt) + last4digits
            # store new user into database
            insertUser(user_id, user_name, 0, deployment_id)
            # generate unique referral code
            user_code = generate_code(user_id)
            # if the code already existed
            user_referral = entry_code + str(user_code)
            while getUserByCode(user_referral):
                # increment the code by 1 and keep last 4 digits
                user_code = (user_code + 1) % 10000
                user_referral = entry_code + str(user_code)
            # store the entry code user used and referral code generated
            # (timestamp auto generated in database)
            insertReferralInfo(user_id, user_referral, body, deployment_id)
            # insert script configs
            insert_config(user_id, deployment_id)
            # initialize user info
            user_info_update(user_id)
            # get message script file for the deployment
            # determine script based on user_referral
            script_dict_base = session["base_script_dict"]
            script_dict_game = session["game_script_dict"]
            script_configs = session["user_config"]

            # overwrite the base script by the gamified version
            if "g" in script_configs:
                for k, v in script_dict_game.items():
                    script_dict_base[k] = v

            # reward points to the referral user
            referral_user = getUserByCode(body)
            if referral_user:
                referral_points = 100
                ref_user_score, _ = getUserScore(referral_user, deployment_id)
                # reward 100 points for successfully inviting a friend
                setUserScore(referral_user, ref_user_score + referral_points, deployment_id)
                # inform the referral user
                referral_reward_script = get_script_word(script_dict_base, script_dict_game,
                                                         "referral_reward", script_configs)
                ref_reward_msg = referral_reward_script % user_number
                sendMessage(user_number, ref_reward_msg, referral_user)

            all_years = getYears(session["sat_source_name"], session["station_source_name"])
            min_year = min(all_years)
            max_year = max(all_years)
            start_word = script_dict_base["start_word"]
            start_msg = script_dict_base["send_start"] % start_word
            session["prev_question"] = start_msg

            sendMessage(user_number, script_dict_base.get("who_we_are", None))
            time.sleep(2)
            sendMessage(user_number, (script_dict_base["purpose"] % (min_year, max_year)))
            time.sleep(1)
            sendMessage(user_number, script_dict_base.get("learning", None))
            time.sleep(2)

            # start_date, end_date = getDeploymentStartEndDate(deployment_id)
            # start_date_str = date_to_string(start_date)
            # end_date_str = date_to_string(end_date)
            # start and end dates are to be entered manually (due to translation issue)
            sendMessage(user_number, (script_dict_base["game_time"]))
            time.sleep(1)

            # reward message
            reward_script = session.get("reward_script", None)
            if "g" in script_configs and reward_script:
                sendMessage(user_number, reward_script["reward_message"])
                time.sleep(1)
                sendMessage(user_number, reward_script["rewards_list"])
                time.sleep(2)
                sendMessage(user_number, reward_script["reward_time"])
                time.sleep(2)

            sendMessage(user_number, (script_dict_base.get("privacy_notice", "") + "\n\n" + start_msg))
            return str(resp)
        else:
            # check if user was in earlier deployment
            if user_exist_status is None:
                script_dict_base = session["base_script_dict"]
                script_dict_game = session["game_script_dict"]
                script_configs = session["user_config"]

                if "g" in script_configs:
                    script_dict_base = script_dict_game

                game_over_msg = script_dict_base["game_over"]
                sendMessage(user_number, game_over_msg)
                return str(resp)
            # invalid entry code message in multiple languages
            sendMessage(user_number,
                        "Lo sentimos. La palabra clave que enviaste no es correcta. Intenta nuevamente. Si continua fallando, puedes confirmar la palabra clave con el contacto que te compartió el juego.\n\n"
                        + "We are sorry. The keyword is incorrect. Try again. If it still is not working, confirm the keyword with the contact that shared the game with you."
                        )
            return str(resp)

    #### EXISTING USER ####
    script_configs = session.get("user_config", None)
    script_dict_base = session.get("base_script_dict", None)
    script_dict_game = session.get("game_script_dict", None)
    memory_trigger_script = session.get("memory_trigger_script", None)
    state = session.get("state", None)
    prev_question = session.get("prev_question", None)

    def game_question_resp():
        if "g" in script_configs:
            game_question = generateQuestion(script_dict_game, user_id)
        else:
            game_question = generateQuestion(script_dict_base, user_id)
        # if question exhausted
        if not game_question:
            exhausted_msg = script_dict_base.get("question_exhausted", None)
            sendMessage(user_number, exhausted_msg)
            session["prev_question"] = exhausted_msg
            session["state"] = "question_exhausted"
        else:
            sendMessage(user_number, game_question)
            session["prev_question"] = game_question
            session["state"] = "game_question"

    # empty session
    if state is None:
        print("===================")
        # time_diff = check_time_diff(user_id)
        # print("time_diff: ", time_diff)
        # if time_diff < 3:
        #     return str(resp)
        user_info_update(user_id)
        script_configs = session["user_config"]
        script_dict_base = session["base_script_dict"]
        script_dict_game = session["game_script_dict"]
        start_word = script_dict_base["start_word"]
        resume_word = script_dict_base["resume_word"]
        if "g" in script_configs:
            for k, v in script_dict_game.items():
                script_dict_base[k] = v
        # initial state, entering game
        body = extract_letters(body)

        if body == start_word or body == resume_word:
            # if user has already entered demographic info
            if getUserDemographic(user_id, session["deployment_id"]):
                # simply send question
                game_question_resp()
                return str(resp)
            else:
                sendMessage(user_number, script_dict_base.get("demographic_intro", None))
                time.sleep(2)

                # ask for user gender
                demographic_gender_question = script_dict_base.get("demographic_gender", None)
                sendMessage(user_number, demographic_gender_question)
                session["prev_question"] = demographic_gender_question
                session["state"] = "demographic_gender"
                return str(resp)
        else:
            # session expired, send start to resume
            start_msg = script_dict_base["resume_start"] % resume_word
            sendMessage(user_number, start_msg)
            session["prev_question"] = start_msg
            return str(resp)

    if state == "demographic_gender":
        user_gender = extract_number(body)
        # sanity check (1: Female 2: Male 3: I don’t want to answer)
        if user_gender and user_gender in range(1, 4):
            # store user response for gender in session
            # and insert new demographic info after getting all demographic info
            session["demographic_info"] = {"gender": user_gender}

            # ask for user age
            sendMessage(user_number, script_dict_base.get("demographic_age", None))
            session["prev_question"] = script_dict_base.get("demographic_age", None)
            session["state"] = "demographic_age"
            return str(resp)

    def send_location_question():
        location_list = getLocationList()
        location_question = script_dict_base["demographic_location"] % location_list
        sendMessage(user_number, location_question)
        session["prev_question"] = location_question
        session["state"] = "demographic_location"

    if state == "demographic_age":
        user_age = extract_number(body)
        # make sure response is numeric
        if user_age is not None:
            # store user response for user age in session
            # and insert new demographic info after getting all demographic info
            demographic_info = session.get("demographic_info")
            demographic_info["age"] = user_age

            # ask for income (optional)
            income_question = script_dict_base.get("demographic_income", None)
            if income_question:
                sendMessage(user_number, income_question)
                session["prev_question"] = income_question
                session["state"] = "demographic_income"
            else:
                send_location_question()
            return str(resp)

    if state == "demographic_income":
        user_income = extract_number(body)
        # NOTE: do NOT change the script after game starts, as only selection number gets recorded
        # sanity check 
        # 1: Entre 0 y 350 Quetzales
        # 2: Entre 350 y 800 Quetzales
        # 3: Entre 800 y 1400 Quetzales
        # 4: Entre 1400 y 2800 Quetzales
        # 5: Entre 2800 y 3500 Quetzales
        # 6: Entre 3500 y 5600 Quetzales
        # 7: Más de 5600 Quetzales
        # 8: No quiero responder
        if user_income and user_income in range(1, 9):
            # store user response for income in session
            # and insert new demographic info after getting all demographic info
            demographic_info = session.get("demographic_info")
            demographic_info["income"] = user_income

            # ask for location
            send_location_question()
            return str(resp)

    if state == "demographic_location":
        user_resp = extract_number(body)
        location_dict = session.get("location_dict")
        location_num = session.get("location_num")

        # requires the last location in the list to be the out of state (invalid) location
        if user_resp == location_num:
            # let user know their region is not included
            sendMessage(user_number, script_dict_base["out_of_state_message"])
            session["prev_question"] = script_dict_base["out_of_state_message"]
            session["state"] = "out_of_region"
            return str(resp)

        # get actual location string
        user_location = location_dict.get(str(user_resp), None)
        if user_location:
            demographic_info = session.get("demographic_info")
            user_gender = demographic_info.get("gender")
            user_age = demographic_info.get("age")
            user_income = demographic_info.get("income")
            # insert all demographic info (timestamp auto generated in database)
            insertDemographic(user_id, user_gender, user_age, user_location, user_income, session["deployment_id"])
            # game start
            sendMessage(user_number, script_dict_base.get("game_start", None))
            time.sleep(3)
            # generate a question
            game_question_resp()
            return str(resp)

    if state == "game_question":
        user_resp = extract_number(body)
        # sanity check (1: year1 2: year2 3: Same 4: I don’t know 5: Back to main menu)
        if user_resp and user_resp in range(1, 6):
            deployment_id = session["deployment_id"]
            # back to main menu
            if user_resp == 5:
                # if gamified version, include leaderboard and invite friend reward
                if "g" in script_configs:
                    script_dict = script_dict_game
                # else non-gamified version
                else:
                    script_dict = script_dict_base
                sendMessage(user_number, script_dict["main_menu"])
                session["prev_question"] = script_dict["main_menu"]
                session["state"] = "main_menu"
            else:
                question_year_1 = session["question_year_1"]
                question_year_2 = session["question_year_2"]
                if user_resp != 4:
                    # check if the user message their answer repeatedly
                    if checkResponseExist(user_id, question_year_1, question_year_2, deployment_id):
                        wait_message = script_dict_base.get("wait_for_question")
                        sendMessage(user_number, wait_message)
                        return str(resp)

                    # give user feedback
                    feedback, score_rank_msg, points, match_sat, match_wea, match_neighbour, neighbour_answered, match_neighbour_real, neighbour_answered_real = \
                        checkResponse(user_id, question_year_1, question_year_2, user_resp, user_id, script_dict_game, memory_trigger_script)
                    # insert response into database (timestamp auto generated in database)
                    insertResponse(user_id, question_year_1, question_year_2, user_resp, points, deployment_id,
                                   match_sat, match_wea, match_neighbour, neighbour_answered, match_neighbour_real,
                                   neighbour_answered_real)

                    # send feedback if in gamified version
                    if "g" in script_configs:
                        sendMessage(user_number, (feedback + score_rank_msg))

                # reward 25 points to don't know response
                else:
                    not_know_points = 25
                    deploy_responses, deploy_responses_real = \
                        getDeployResponses(question_year_1, question_year_2, deployment_id)
                    neighbour_answered = len(deploy_responses)
                    neighbour_answered_real = len(deploy_responses_real)
                    # insert response into database (timestamp auto generated in database)
                    insertResponse(user_id, question_year_1, question_year_2, user_resp, not_know_points,
                                   deployment_id, 0, 0, 0, neighbour_answered, 0, neighbour_answered_real)
                    user_score, _ = getUserScore(user_id, deployment_id)
                    new_user_score = user_score + not_know_points
                    setUserScore(user_id, new_user_score, deployment_id)

                    # send current score and rank if in gamified version
                    if "g" in script_configs:
                        msg = script_dict_game["earn_points"] % int(not_know_points)
                        score_msg, rank_msg = user_score_rank(script_dict_game, memory_trigger_script, user_id)
                        msg += score_msg + rank_msg
                        time.sleep(2)
                        sendMessage(user_number, msg)

                # check if gamified version and memory trigger script is defined
                if "g" in script_configs and memory_trigger_script is not None:
                    # message after every 5 responses
                    user_responses = getUserResponses(user_id, deployment_id)
                    user_resp_num = len(user_responses)
                    if user_resp_num % 5 == 0:
                        five_resp_msg = ""
                        if "1" in script_configs \
                                or "2" in script_configs \
                                or "3" in script_configs:
                            five_resp_msg = memory_trigger_script["per_five_resp"] % user_resp_num
                        else:
                            all_years = session["deploy_years"]
                            min_year = min(all_years)
                            max_year = max(all_years)
                            interval = max_year - min_year + 1
                            combs = interval * (interval - 1)
                            if "4a" in script_configs:
                                five_resp_msg = memory_trigger_script["per_five_resp"] \
                                                % (user_resp_num, combs / 2, min_year, max_year)
                            if "4b" in script_configs:
                                five_resp_msg = memory_trigger_script["per_five_resp"] \
                                                % (user_resp_num, combs, min_year, max_year)
                        time.sleep(2)
                        sendMessage(user_number, five_resp_msg)

                # continue posing questions
                time.sleep(2)
                game_question_resp()
            return str(resp)

    if state == "out_of_region":
        sendMessage(user_number, script_dict_base["out_of_state_message"])
        return str(resp)

    if state == "question_exhausted":
        sendMessage(user_number, script_dict_base["question_exhausted"])
        return str(resp)

    if state == "main_menu":
        user_resp = extract_number(body)
        if user_resp:
            # gamified
            # sanity check (1: Start iKON game 2: Check latest leaderboard 3: Invite a friend)
            # non-gamified
            # sanity check (1: Start iKON game 2: Invite a friend)
            if ("g" in script_configs and user_resp in range(1, 4)) \
                    or ("ng" in script_configs and user_resp in range(1, 3)):

                # (gamified) Check latest leaderboard
                if "g" in script_configs and user_resp == 2:
                    score_msg, rank_msg = user_score_rank(script_dict_game, memory_trigger_script, user_id)
                    sendMessage(user_number, (score_msg + rank_msg))
                    time.sleep(2)

                # Invite a friend
                elif ("g" in script_configs and user_resp == 3) \
                        or ("ng" in script_configs and user_resp == 2):
                    invite_code = session["user_code"]
                    invite_script = get_script_word(script_dict_base, script_dict_game, "invite", script_configs)
                    forward_invite_script = get_script_word(script_dict_base, script_dict_game, "forward_invite",
                                                            script_configs)
                    sendMessage(user_number, (invite_script % invite_code))
                    time.sleep(2)
                    sendMessage(user_number, (forward_invite_script % invite_code))
                    time.sleep(2)

            # generate the next question
            game_question_resp()
            return str(resp)

    # universal error message
    sendMessage(user_number, script_dict_base["invalid_response"])
    time.sleep(1)
    # send previous message again in case of invalid user response
    sendMessage(user_number, prev_question)
    return str(resp)


if __name__ == "__main__":
    app.run(use_reloader=False)
