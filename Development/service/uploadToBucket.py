from google.cloud import storage
import os

def upload_blob(source_file_name, destination_blob_name):
    '''upload an image to the google bucket'''
    storage_client = storage.Client.from_service_account_json(r'Development\\service\\meditensor-2178cd54ff6e.json') #grab the stupid credentials itself
    bucket = storage_client.get_bucket("mediscan-images") #pull the name
    blob = bucket.blob(destination_blob_name) #What do you want it to be called when its in the bucket?
    blob.upload_from_filename(source_file_name) #What is it called so I can find it?
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
    return f"UPLOADED!"


def get_latest_file(directory):
    '''get the most recent file by modification time'''
    files = os.listdir(directory)
    full_paths = [os.path.join(directory, f) for f in files]
    latest_file = max(full_paths, key=os.path.getmtime)  
    return latest_file


if __name__ == '__main__':
    uploads_folder = r'Development\\service\\images\\uploads'   #look in this folder
    source_file_name = get_latest_file(uploads_folder)  #grab the latest file from it
    destination_blob_name = os.path.basename(source_file_name) #give it this name
    file_url = upload_blob(source_file_name, destination_blob_name) #upload it
    print(f"File uploaded and accessible at: {file_url}")