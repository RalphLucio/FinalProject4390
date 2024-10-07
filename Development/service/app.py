from flask import Flask, jsonify, g, request, render_template
from flask_cors import CORS  # type: ignore
from werkzeug.utils import secure_filename
import sqlite3
import os


from ImageToHash import md5checksum
from uploadToBucket import *
from tfServe import *

#Database file
#NOTE FOR ME LATER LAPTOP PWD: C:\Users\ryanw\Downloads\Final Project
#this will solve the Jobey issue
db_dir = os.path.join(r'FinalProject4390\Development\service', 'databases')
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
  UPLOAD_FOLDER = r'FinalProject4390\Development\service\images\uploads'
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
        return 1
    else:
      print("The hash has no flag as it does not exist...")
      return 0
    
  #function to wipe /uploads if anythings there
  def wipe_uploads_folder():
    #wipe anything thats left over in the uploads folder
    uploadsList = os.listdir(r'FinalProject4390\Development\service\images\uploads')
    if(len(uploadsList) > 0):
      for item in uploadsList:
        temp_file_path = os.path.join(r'FinalProject4390\Development\service\images\uploads', item)
        if os.path.isfile(temp_file_path):
            os.remove(temp_file_path)
    print("Uploads wiped.")
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
      return 'No file part' #the post did not yield a file
    file = request.files['file']  #grab the file from the request payload
    if file.filename == '':
      return 'No selected file' #form was submitted without a file
    
    if file and allowed_file(file.filename):
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
          return f"Name: {name}, Cancer Prediction: {cancer_pred}, Hash: {file_hash}, URL: {url}"

      #Otherwise uploadto Google Bucket because its NEW NEW!
      call_file_this = f"{file_hash}.jpg"  #name the file for export
      file_url = upload_blob(file_path, call_file_this)  #upload the file given the source and export name
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

      #delete the image after so it doesnt clog up 'uploads'
      # we have it in the bucket now
      wipe_uploads_folder()

      #we got a successful prediction back, set the flag to show the image got a proper checking :)
      if predictions:
        cancer_pred = predictions[0][1]
        db.execute("UPDATE images SET predicted = 1, cancer_pred = ? WHERE hash = ?", (cancer_pred, file_hash))
        db.commit()
        return f'File successfully uploaded, stored at URL: {file_url}, Predictions: {predictions}'
      else:
        #they can requeue
        return 'File uploaded but prediction failed.'
      
    return 'File type not allowed'
  
  return app

if __name__ == '__main__':
  app = create_app()
  # app.run(debug=True)
  app.run()