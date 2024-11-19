from flask import Flask, jsonify, g, request, render_template
from flask_cors import CORS  # type: ignore
from werkzeug.utils import secure_filename
import sqlite3
import os

#For the primitive 'bad-actor' model
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from scipy.spatial.distance import cosine

from ImageToHash import md5checksum #Hash a file
from uploadToBucket import *  #Google Bucket API
from tfServe import * #Tensorflow serving API
from Bad_Actor import * #Primitive model to discern bad-actors



'''=============== GLOBAL DIRECTORY SETUP ==============='''
''' Sets up dynamic use between multiple computers such that
    the directories will be the same computer-to-computer.
    This clears up issues of relative/full pathing.'''

BASE_DIR = os.path.abspath(os.path.dirname(__file__)) #Where this script is, is the base path
SECRET_FOLDER = os.path.join(BASE_DIR, 'secret')  #Holds important do-not-upload data
UPLOAD_FOLDER = os.path.join(BASE_DIR,'images', 'uploads')  #upload folder for incoming images
REFERENCE_IMAGES_DIR = os.path.join(BASE_DIR, 'images', 'Bad_Actor_Images') #folder for reference images for bad-actor
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'} #the file extensions that we'll allow for incoming images

db_dir = os.path.join(BASE_DIR, 'databases')
if not os.path.exists(db_dir):
  os.makedirs(db_dir) #make the database dir. if it does not exist

DATABASE = os.path.join(db_dir, 'image-database.db')#assumes it already exists, schema will make if it doesnt
'''=============== =============== ==============='''

def get_db():
  '''Connect to the database'''
  db = getattr(g, '_database', None)  # g is 'global'
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  return db

def init_db(app):
  '''Initialize the database schema'''
  db = get_db()
  with app.open_resource('schema.sql', mode='r') as f:
    db.executescript(f.read())
  db.commit()

def create_app():
  app = Flask(__name__)
  CORS(app)

  '''=============== PRE-SETUP APP SCOPE ==============='''
  app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
  app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
  if 1:
    print(f'Reference images path: {REFERENCE_IMAGES_DIR}')

  '''=============== BAD ACTOR MODEL ==============='''
  '''We need to use a light-weight model to discern 
     whether an uploaded image is relevant or not.  '''
  
  model = models.resnet50(pretrained=True)  #ResNet50 pre-trained model
  model.eval()  #We need to set the model to evaluate

  #Define image transformations
  transform = transforms.Compose([
      transforms.Resize((224, 224)),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
  ])
  
  #Load our reference embeddings
  reference_embeddings = load_reference_embeddings(REFERENCE_IMAGES_DIR, model, transform)
  '''=============== =============== ==============='''

  '''=============== HELPER FUNCTIONS ==============='''
  
  def allowed_file(filename):
    '''Checks if a given image is allowed based off of our ALLOWED_EXTENSIONS'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  
  def check_hash_exists(db, hash):
    '''Checks if a given hash is already in the DB database'''
    hash_exists = db.execute("SELECT EXISTS(SELECT 1 FROM images WHERE hash = ?)",(hash,)).fetchone()[0] == 1  #1 if exists, otherwise 0
    if hash_exists:
      print("The hash exists.")
      return 1
    else:
      print("The hash does not exist.")
      return 0
  
  def check_pred_of_hash(db, hash):
    '''Checks the prediction flag of a given hash in the DB database'''
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
  
  def wipe_uploads_folder():
      '''Wipes uploads so we have a clean directory everytime'''

      # working_dir = os.getcwd() #Get the current working directory

      # # Construct the full path to the uploads folder dynamically
      # uploads_path = os.path.join(working_dir, 'images', 'uploads')
      uploads_path = UPLOAD_FOLDER

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
  
  @app.teardown_appcontext
  def close_db(exception):
    '''CLOSE DATABASE CONNECTION'''
    db = g.pop('_database', None) #NEW, testing
    # db = getattr(g, '_database', None) #OLD, reliable
    if db is not None:
      db.close()


  with app.app_context():
    '''Create the DB'''
    init_db(app)  #Pass app instance to init_db

  
  @app.route('/')
  def upload_form():
    ''' The 'main menu' (index) '''
    wipe_uploads_folder()
    return render_template('upload.html')
  
  @app.route('/lookup_page', methods=['GET'])
  def lookup_page():
    return render_template('lookup.html')
  
  @app.route('/lookup', methods=['POST'])
  def lookup():
    #grab the data
    data = request.get_json(silent=True)

    if data and 'hash' in data:
      hash_value = data['hash']
    else:
      hash_value = request.form.get('hash')

    #if we get nothing then complain
    if not hash_value:
      return jsonify({"error": "Hash not provided"}), 400

    #sync to db
    db = get_db()

    #does the hash provided even exist?
    check_exists = check_hash_exists(db, hash_value)
    if not check_exists:
      return jsonify({"Reply": "Hash does not exist"}), 200
    
    #grab the information from the hash
    row = db.execute(
      "SELECT name, predicted, relevant, cancer_pred FROM images WHERE hash = ?"
      ,(hash_value,)).fetchone()

    #respond with the corresponding data
    if row:
      response_data = {
        "name": row[0],   
        "predicted": row[1],
        "relevant": row[2],
        "cancer_pred": row[3]
      }
      return jsonify(response_data), 200
    else:
      #i dunno there was an error
      return jsonify({"error": "Unexpected issue retrieving data"}), 500

  @app.route('/upload', methods=['POST'])
  def upload_file():
    '''=============== PRIMARY APP FUNCTION ==============='''
    '''Mostly everything will happen upon uploading an image.
       When you do that, everything below will run, including
       things from other scripts.'''

    '''=============== PRELIMINARY SETUPS ==============='''
    db = get_db() #connect and open the database
    wipe_uploads_folder() #wipe the uploads folder to destroy remnants from previous operations
    
    '''=============== INCOMING FILE CHECKS ==============='''
    if 'file' not in request.files:
      return jsonify({"error": "No file part"}), 400  # Changed to JSON response AND #the post did not yield a file
    
    file = request.files['file']  #grab the file from the request payload
    
    if file.filename == '':
      return jsonify({"error": "No selected file"}), 400  # Changed to JSON response AND #form was submitted without a file
    
    '''=============== MAIN OPERATION ==============='''
    if file and allowed_file(file.filename):
      #print(f'Base directory: {BASE_DIR}')

      '''=============== INCOMING FILE ==============='''
      filename = secure_filename(file.filename) #anti-malware
      file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #get the file path of the newly uploaded file
      file.save(file_path)  #save that file path to the server
      file_hash = md5checksum(file_path)  #HASH THE FILE -> name of the file when hashed

      '''Check IF there are duplicates in the DB database AND IF the prediction flag is TRUE, otherwise continue onwards'''
      if (check_hash_exists(db, file_hash) == 1):
        '''-> the hash exists, but did they get a prediction?'''
        if (check_pred_of_hash(db, file_hash) == 1):
          '''-> the hash exists AND they already have a prediction flag of TRUE
                show them info of that item, pulled from the DB database  '''
          name, url, cancer_pred = db.execute("SELECT name, url, cancer_pred FROM images WHERE hash = ?",(file_hash,)).fetchone()
          #Convert to JSON and send back to server
          response_data = {
            "name": name,
            "cancer_pred" : cancer_pred,
            "hash" : file_hash,
            "url" : url
          }
          wipe_uploads_folder()
          return jsonify(response_data), 200 # returning JSON response with HTTP status of 200 (ok)
      
      '''=============== PASSED FILE CHECKS AND PRE-EXISTING DATA CHECKS ==============='''

      #Upload the file to Google Bucket
      call_file_this = f'{file_hash}.jpg'  #name the file for export
      file_url = upload_blob(file_path, call_file_this, SECRET_FOLDER)  #upload the file given the source and export name
      #print(file_url)

      #Save the file info to the database
      if (check_hash_exists(db, file_hash) == 1):
        '''if the given hash exists in the database, we'll UPDATE the table
           its new name we generated, url we got back from Google API, and Hash that was generated'''
        db.execute("UPDATE images SET name = ?, url = ? WHERE hash = ?", (filename, file_url, file_hash))
        db.commit()
      else:
        '''otherwise we need to INSERT all that new information to the table.'''
        db.execute("INSERT INTO images (name, hash, url) VALUES (?, ?, ?)", (filename, file_hash, file_url))
        db.commit()

      '''=============== BAD ACTOR CHECKS ==============='''
      uploaded_image_path = os.path.join(UPLOAD_FOLDER, file_path) #grab the image path
      uploaded_image_tensor = process_image(uploaded_image_path, transform) #just a small preprocess to the image
      uploaded_image_embedding = get_embedding(model, uploaded_image_tensor) #ADVANCED -  grab features from our reference images

      #print(f'FILE HASH: {file_hash}')

      #compare the uploaded image to our reference images to see whether its relevant or not
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
        wipe_uploads_folder()
        return jsonify(response_data), 200
      
      '''=============== POST CHECKS -> DOING PREDICTION ON IMAGE ==============='''

      #print(f"Preparing to predict for image: {file_path}")
      predictions = prepare_and_predict(file_path)

      '''-> we sent the image off for predictions
         In an ideal world this worked flawlessly and we can now set the predicted flag to TRUE
         otherwise it had an issue and we need to exit operations and leave the predicted flag as FALSE
         so they can send the image again later.'''
      
      if predictions:
        cancer_pred = predictions[0][1] #grab the float of cancer prediction in image
        db.execute("UPDATE images SET predicted = 1, cancer_pred = ? WHERE hash = ?", (cancer_pred, file_hash)) #update DB info accordingly
        db.commit()

        response_data = {
            "name": filename,
            "cancer_pred" : cancer_pred,
            "hash" : file_hash,
            "url" : file_url
          }
        wipe_uploads_folder()
        return jsonify(response_data), 200 # uploading JSON file
      else:
        '''there was an issue and they didn't get a prediction back
           but how we've set up our system, they can resubmit their picture to be predicted again.'''
        wipe_uploads_folder()
        return 'File uploaded but prediction failed.'
      #TO-DO: attempting to returning JSON
    wipe_uploads_folder()
    return 'File type not allowed'
  return app

if __name__ == '__main__':
  app = create_app()
  # app.run(debug=True)
  app.run()