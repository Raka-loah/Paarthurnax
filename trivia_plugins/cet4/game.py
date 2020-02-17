from random import choice, sample
from math import floor
from os import path, mkdir
from shutil import rmtree
from datetime import datetime
import json

class cet4_game:
    def __init__(self):
        # Load data
        self.data = []
        with open(path.join(path.dirname(path.realpath(__file__)),'cet4.json'), encoding='utf-8', mode='r') as f:
            self.data = json.loads(f.read())

    require_image = False

    def clean(self):
        pass

    def generate(self, identifier):
        question = random.sample(list(self.data), k=1).pop()

        result = {
            'question': f'请根据音标和含义写出对应英文单词：\n{self.data[question][0]}\n{self.data[question][1]}',
            'answer': f'{question}',
            'answer_announce': f'回答正确！答案是：{question}',
        }

        return result