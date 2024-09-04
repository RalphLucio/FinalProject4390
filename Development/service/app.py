from flask import Flask, jsonify
from flask_cors import CORS # type: ignore
from ImageToHash import *

app = Flask(__name__)
CORS(app)

@app.route('/data')
def index():
  #hardcoded directory built for one given image, for test purposes of course
  file_path = "C:\\Users\\jobey\\Documents\\Final Project 4390\\FinalProject4390\\Development\\service\\images\\concord.png"
  result = md5checksum(file_path)
  return jsonify(result)

# Dog Hash: d705ef4a93e84a4ecaf64e8d53531c93 Works
# Concord Hash: 1fa5bd8494efc127c09c55514b8c668a Works
if __name__ == '__main__':
  app.run()