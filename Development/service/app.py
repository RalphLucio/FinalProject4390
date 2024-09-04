from flask import Flask, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/data')
def index():
  data = {
    "name": "John",
    "age": 30,
    "city": "New York"
  }
  return jsonify(data)




if __name__ == '__main__':
  app.run()