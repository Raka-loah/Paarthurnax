# -*- coding: utf-8 -*-

import importlib
import requests
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse

from message_handler import Message_handler

import wfstate as wf

app = Flask(__name__)
api = Api(app)

handler = Message_handler()

class wfst(Resource):
    def post(self):
        try:
            # POSTed data as json
            j = request.get_json(force=True)

            return handler.handle(j)
        except Exception as e:
            print(e)
            return '', 204

    def patch(self):
        try:
            try:
                request_token = request.get_json(force=True)['token']
            except:
                request_token = ''
            handler.reload(request_token)
        except Exception as e:
            return print(e), 500

api.add_resource(wfst, '/')

if __name__ == '__main__':  
    handler.add_job(wf.get_new_alerts, second='00')
    handler.add_job(wf.get_cetus_transition, second='05')
    handler.add_job(wf.get_new_acolyte, second='00')
    app.run(debug=False, port=8888)
