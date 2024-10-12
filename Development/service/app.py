from flask import Flask, jsonify, g, request, render_template
from flask_cors import CORS  # type: ignore
from werkzeug.utils import secure_filename
import sqlite3
import os
from ImageToHash import md5checksum
from uploadToBucket import *
from tfServe import *


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_FOLDER = os.path.join(BASE_DIR, 'secret')
#Database file
db_dir = os.path.join(BASE_DIR, 'databases')
if not os.path.exists(db_dir):
  os.makedirs(db_dir)
DATABASE = os.path.join(db_dir, 'image-database.db')

def get_db():
  """Connect to the database."""
  db = getattr(g, '_database', None)  # g is 'global'
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  return db

def init_db(app):
  """Initialize the database schema."""
  db = get_db()
  with app.open_resource('schema.sql', mode='r') as f:
    db.executescript(f.read())
  db.commit()

def create_app():
  app = Flask(__name__)
  CORS(app)

  #SETUP FOLDERS
  
  
  UPLOAD_FOLDER = os.path.join(BASE_DIR,'images', 'uploads')
  ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
  app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

  #Function to check if image is allowed
  def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  
  #Function to check if hash is already in the database
  def check_hash_exists(db, hash):
    hash_exists = db.execute("SELECT EXISTS(SELECT 1 FROM images WHERE hash = ?)",(hash,)).fetchone()[0] == 1  #1 if exists, otherwise 0
    if hash_exists:
      print("The hash exists.")
      return 1
    else:
      print("The hash does not exist.")
      return 0
  
  #Function to check pred flag of hash
  def check_pred_of_hash(db, hash):
    hash_exists = check_hash_exists(db, hash)
    if hash_exists:
      prediction_status = db.execute("SELECT predicted FROM images WHERE hash = ?",(hash,)).fetchone()
      has_prediction = prediction_status[0]
      if has_prediction == 0:
        print("Hash exists but no prediction made. Requeue them...")
        return 0
      else:
        print("Hash exists and prediction made. Give them old info...")
        #WIPE HERE
        return 1
    else:
      print("The hash has no flag as it does not exist...")
      return 0
  

  #function to wipe /uploads if anythings there
  def wipe_uploads_folder():
      # Get the current working directory
      working_dir = os.getcwd()

      # Construct the full path to the uploads folder dynamically
      uploads_path = os.path.join(working_dir, 'images', 'uploads')

      try:
        uploads_list = os.listdir(uploads_path)
        if len(uploads_list) > 0:
          for item in uploads_list:
            temp_file_path = os.path.join(uploads_path, item)
            if os.path.isfile(temp_file_path):
              os.remove(temp_file_path)
            print("Uploads wiped.")
        else:
          print("Uploads folder is already empty.")
      except FileNotFoundError:
        print(f"Error: The path '{uploads_path}' does not exist.")
      except Exception as e:
        print(f"An error occurred: {e}")
      return
  
  #CLOSE DATABASE CONNECTION
  @app.teardown_appcontext
  def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
      db.close()

  with app.app_context():
    init_db(app)  #Pass app inst to init_db

  #This is the 'main menu'
  @app.route('/')
  def upload_form():
    wipe_uploads_folder()
    return render_template('upload.html')

  #When you upload a file that has the correct extension
  @app.route('/upload', methods=['POST'])
  def upload_file():
    db = get_db() #open database

    wipe_uploads_folder()
    
    if 'file' not in request.files:
      return jsonify({"error": "No file part"}), 400  # Changed to JSON response AND #the post did not yield a file
    file = request.files['file']  #grab the file from the request payload
    
    if file.filename == '':
      return jsonify({"error": "No selected file"}), 400  # Changed to JSON response AND #form was submitted without a file
    
    if file and allowed_file(file.filename):
      print("This is the base directory")
      print(BASE_DIR)
      filename = secure_filename(file.filename) #primitive anti-malicious
      file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #give the file path of the newly uploaded file
      
      file.save(file_path)  #save the info to the server




      

      #File hashing
      file_hash = md5checksum(file_path)  #name of the file when hashed

      #Check if dupes in the database and if they got a prediction back
      if (check_hash_exists(db, file_hash) == 1):
        #the hash exists but did they get a prediction?
        if (check_pred_of_hash(db, file_hash) == 1):
          #the hash exists and they already have a prediction, show them old info thats been saved to the database
          name, url, cancer_pred = db.execute("SELECT name, url, cancer_pred FROM images WHERE hash = ?",(file_hash,)).fetchone()

          #TODO: Convert to JSON and send back to server
          response_data = {
            "name": name,
            "cancer_pred" : cancer_pred,
            "hash" : file_hash,
            "url" : url
          }

          return jsonify(response_data), 200 # returning JSON response with HTTP status of 200 (ok)

      #Otherwise uploadto Google Bucket because its NEW NEW!
      call_file_this = f"{file_hash}.jpg"  #name the file for export
      file_url = upload_blob(file_path, call_file_this, SECRET_FOLDER)  #upload the file given the source and export name
      print(file_url)

      #Save info to the database
      if (check_hash_exists(db, file_hash) == 1):
        #update
        db.execute("UPDATE images SET name = ?, url = ? WHERE hash = ?", (filename, file_url, file_hash))
        db.commit()
      else:
        #add it
        db.execute("INSERT INTO images (name, hash, url) VALUES (?, ?, ?)", (filename, file_hash, file_url))
        db.commit()

      #Prep and predict
      print(f"Preparing to predict for image: {file_path}")
      predictions = prepare_and_predict(file_path)

      #delete the image after so it doesn't clog up 'uploads'
      # we have it in the bucket now
      #wipe_uploads_folder()

      #we got a successful prediction back, set the flag to show the image got a proper checking :)
      if predictions:
        cancer_pred = predictions[0][1]
        db.execute("UPDATE images SET predicted = 1, cancer_pred = ? WHERE hash = ?", (cancer_pred, file_hash))
        db.commit()
        response_data = {
            "name": filename,
            "cancer_pred" : cancer_pred,
            "hash" : file_hash,
            "url" : file_url
          }
        return jsonify(response_data), 200 # uploading json file
      else:
        #they can requeue
        return 'File uploaded but prediction failed.'
      

      #TODO: attempting to returning Json


    return 'File type not allowed'
  
  return app

if __name__ == '__main__':
  app = create_app()
  # app.run(debug=True)
  app.run()