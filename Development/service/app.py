from flask import Flask, jsonify, g, request, render_template
from flask_cors import CORS  # type: ignore
from werkzeug.utils import secure_filename
import sqlite3
import os
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from scipy.spatial.distance import cosine

from ImageToHash import md5checksum
from uploadToBucket import *
from tfServe import *
from Bad_Actor import *


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_FOLDER = os.path.join(BASE_DIR, 'secret')
#Database file
db_dir = os.path.join(BASE_DIR, 'databases')
if not os.path.exists(db_dir):
  os.makedirs(db_dir)
DATABASE = os.path.join(db_dir, 'image-database.db')

def get_db():
  #Connect to the database
  db = getattr(g, '_database', None)  # g is 'global'
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  return db

def init_db(app):
  #Initialize the database schema
  db = get_db()
  with app.open_resource('schema.sql', mode='r') as f:
    db.executescript(f.read())
  db.commit()

def create_app():
  app = Flask(__name__)
  CORS(app)

  '''=============== SETUP FOLDERS ==============='''
  UPLOAD_FOLDER = os.path.join(BASE_DIR,'images', 'uploads')
  ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
  app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
  REFERENCE_IMAGES_DIR = os.path.join(BASE_DIR, 'images', 'Bad_Actor_Images')

  print(f"Reference images path: {REFERENCE_IMAGES_DIR}")

  '''=============== HELPER FUNCTIONS ==============='''


  '''----- BAD ACTOR MODEL -----'''
  # Load the pre-trained model
  model = models.resnet50(pretrained=True)  # Use a pre-trained ResNet50 model
  model.eval()  # Set to evaluation mode

  # Define image transformations
  transform = transforms.Compose([
      transforms.Resize((224, 224)),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
  ])
  
  # Load reference embeddings
  reference_embeddings = load_reference_embeddings(REFERENCE_IMAGES_DIR, model, transform)
  ''' --------------------------- '''


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
  
  '''=============== APP ROUTES / FUNCTIONS ==============='''
  
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
  
  '''=============== PRIMARY APP FUNCTION ==============='''

  #When you upload a file that has the correct extension
  @app.route('/upload', methods=['POST'])
  def upload_file():

    '''=============== PRELIMINARY CHECKS ==============='''
    db = get_db() #connect and open the database
    wipe_uploads_folder() #wipe the uploads folder to destroy remnants from previous operations
    
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
      file_hash = md5checksum(file_path)  #HASH THE FILE -> name of the file when hashed

      #Check if dupes in the database and if they got a prediction back
      if (check_hash_exists(db, file_hash) == 1):
        #the hash exists but did they get a prediction?
        if (check_pred_of_hash(db, file_hash) == 1):
          #the hash exists and they already have a prediction, show them old info thats been saved to the database
          name, url, cancer_pred = db.execute("SELECT name, url, cancer_pred FROM images WHERE hash = ?",(file_hash,)).fetchone()

          #Convert to JSON and send back to server
          response_data = {
            "name": name,
            "cancer_pred" : cancer_pred,
            "hash" : file_hash,
            "url" : url
          }
          return jsonify(response_data), 200 # returning JSON response with HTTP status of 200 (ok)
      
      #Otherwise upload to Google Bucket because its NEW NEW!
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

      '''--------- BAD ACTOR PRE-CHECK --------'''
      #check an uploaded image
      uploaded_image_path = os.path.join(UPLOAD_FOLDER, file_path)
      uploaded_image_tensor = process_image(uploaded_image_path, transform)
      uploaded_image_embedding = get_embedding(model, uploaded_image_tensor)

      print(f'FILE HASH: {file_hash}')

      #compare the uploaded image to the reference embeddings
      if compare_embeddings(uploaded_image_embedding, reference_embeddings):
        print("The uploaded image is relevant.")
        db.execute("UPDATE images SET relevant = 1 WHERE hash = ?", (file_hash,))
        db.commit()
        print('Continuing normal operations')
      else:
        print("The uploaded image is not relevant.")
        db.execute("UPDATE images SET relevant = 0 WHERE hash = ?", (file_hash,))
        db.commit()
        print('Halting...Pulling up relevant information...')

        #Convert to JSON and send back to server
        response_data = {
          "name": filename,
          "hash" : file_hash,
          "relevant" : 0,
          "url" : file_url
        }
        return jsonify(response_data), 200
      
      '''=============== POST CHECKS -> NOW NORMAL OPERATION ==============='''
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