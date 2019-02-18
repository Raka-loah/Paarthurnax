import requests
import time


# States
# 0 - Standby
# 1 - Ready for new question
# 2 - Question fired, waiting for answer
# 3 - Answer accepted or time up
curr = {
    'time': 0,
    'question': '',
    'answer': '',
    'state': 0
}

questions = {
    'question1': 'answer1',
    'question2': 'answer2'
}

score = {}


def new_question():
    pass


def check_answer(answer):
    pass


def get_score(user_id=0):
    # when user_id == 0 return all players' score
    pass


def generate_hint(answer):
    pass

# Main function
# Command: on/off


def triviabot(command):
    # Check current state
    # if 0, pass
    # if 1, new_question, state => 2
    # if 2, check_answer, if ture, state => 3

    pass
