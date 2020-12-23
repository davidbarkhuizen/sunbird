arduino --upload ../arduino/sunbird/sunbird.ino

export FLASK_APP=server.py
flask run  --port=8888 --host=0.0.0.0
