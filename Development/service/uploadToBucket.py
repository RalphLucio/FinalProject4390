from google.cloud import storage
import os

def upload_blob(source_file, dest_name, secret_folder):
    '''upload an image to the google bucket'''
    service_account_file = os.path.join(secret_folder, 'meditensor-2178cd54ff6e.json')
    storage_client = storage.Client.from_service_account_json(service_account_file) #LEAVE THIS ALONE. Unless it changes.
    bucket = storage_client.get_bucket("mediscan-images") #LEAVE THIS ALONE. Unless it changes.

    blob = bucket.blob(dest_name) #What to call it; in the bucket
    blob.upload_from_filename(source_file) #Upload 'this' file
    print(f"UPLOAD_BLOB: File {source_file} has been uploaded to bucket as: \"{dest_name}\".")
    return f"https://storage.cloud.google.com/mediscan-images/{dest_name}"

if __name__ == '__main__':
    pass
    #you have to hardcode the file here unless you want to make a helper function, import os
    # file = DIRECTORY/IMAGE.PNG
    # what_to_call_it = os.path.basename(file)
    # file_url = upload_blob(file, what_to_call_it)