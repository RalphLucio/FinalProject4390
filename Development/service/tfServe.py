import os
import json
import numpy as np
import requests
#dont worry about the yellow
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input

def prepare_and_predict(img_path):
    img = image.load_img(img_path, target_size=(224, 224))  #VGG16 expects 224x224 images
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)  #Normalize image

    #Convert image array to list
    data = json.dumps({"signature_name": "serving_default", "instances": img_array.tolist()})

    #Send request to tf REST API
    headers = {"content-type": "application/json"}
    try:
        response = requests.post('http://18.117.92.57:8501/v1/models/VGG16_model:predict', data=data, headers=headers)
        
        #debugging
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

        #Check response
        if response.status_code == 200:
            #Prediction
            predictions = response.json().get('predictions', [])
            return predictions
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None