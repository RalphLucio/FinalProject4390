from flask import Flask, jsonify, g, request, render_template
from flask_cors import CORS  # type: ignore
import sqlite3
import os
from werkzeug.utils import secure_filename

from ImageToHash import md5checksum
from uploadToBucket import upload_blob
from tfServe import prepare_and_predict

#Database file
DATABASE = 'image-database.db'

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
  UPLOAD_FOLDER = r'Development\\service\\images\\uploads'
  ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
  app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

  #Function to check if image is allowed
  def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    return render_template('upload.html')

  #When you upload a file that has the correct extension
  @app.route('/upload', methods=['POST'])
  def upload_file():
    if 'file' not in request.files:
      return 'No file part'
    
    file = request.files['file']

    if file.filename == '':
      return 'No selected file'
    
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
      file.save(file_path)

      #File hash
      file_hash = md5checksum(file_path)
      bucket_name = 'mediscan-images'
      destination_blob_name = f"{file_hash}.jpg"  #or whatever else
      file_url = upload_blob(bucket_name, file_path, destination_blob_name)

      #Save info to db
      db = get_db()
      db.execute("INSERT INTO images (name, hash, url) VALUES (?, ?, ?)",
                (filename, file_hash, file_url))
      db.commit()

      #Prep and predict
      print(f"Preparing to predict for image: {file_path}")
      predictions = prepare_and_predict(file_path)

      #delete the image after so it doesnt clog up
      # we have it in the bucket now
      try:
        os.remove(file_path)
        print(f"Deleted the uploaded image: {file_path}")
      except OSError as e:
        print(f"Error deleting file: {file_path}, {str(e)}")

      if predictions:
        return f'File successfully uploaded, stored at URL: {file_url}, Predictions: {predictions}'
      else:
        return 'File uploaded but prediction failed.'
      
    return 'File type not allowed'

  return app

if __name__ == '__main__':
  app = create_app()
  app.run(debug=True)