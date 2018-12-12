from flask import Flask
from flask_restful import Api, Resource, reqparse
import wfstate as wf

app = Flask(__name__)
api = Api(app)

class wfst(Resource):
	def post(self, query):
		parser = reqparse.RequestParser()
		parser.add_argument('content')
		args = parser.parse_args()
		resp = ''

		suffix = '\n更多命令请输入"帮助"。'
		if args['content'] == '警报':
			resp = wf.get_alerts() + suffix

		return resp, 200

# Usage:
# POST "content": "chat message" to /api/query
api.add_resource(wfst, '/api/<string:query>')
app.run(debug=True, port=8888)