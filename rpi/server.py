from flask import Flask, request, jsonify, json
import os

app = Flask(__name__)
app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'sunbird.sqlite'),
    )

@app.route('/', methods = ['GET'])
def get():
    return 'sunbird'

@app.route('/', methods = ['POST'])
def post():

    content = request.json
    print(content)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 