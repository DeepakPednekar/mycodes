#!/usr/bin/env python3

from flask import jsonify, Flask

app = Flask(__name__)

with app.app_context():

	@app.route('/')
	def root():
		return jsonify({'msg':'success', 'type': '+OK'})


	@app.route('/sitemap')
	def sitemap():
		d = {'GET':[],'POST':[]}
		for rule in app.url_map.iter_rules():
			if 'GET' in rule.methods:
				d.get('GET').append(rule.rule)
			if 'POST' in rule.methods:
				d.get('POST').append(rule.rule)
		return jsonify(d)



if __name__ == '__main__':
	app.run(debug=True)