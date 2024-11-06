import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from scipy.spatial.distance import cosine
import os
import numpy as np


#process the Image and Generate Embedding
def process_image(image_path, transform):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0)  #apply transformations
    return image


#generate Embedding using the Model
def get_embedding(model, image_tensor):
    with torch.no_grad():
        features = model.conv1(image_tensor)
        features = model.bn1(features)
        features = model.relu(features)
        features = model.maxpool(features)
        features = model.layer1(features)
        features = model.layer2(features)
        features = model.layer3(features)
        features = model.layer4(features)
        features = features.mean([2, 3])
        return features.squeeze().numpy()


#compare Embeddings with Reference Set
def compare_embeddings(new_embedding, reference_embeddings, threshold=0.65):
    similarities = [np.dot(new_embedding, ref) / (np.linalg.norm(new_embedding) * np.linalg.norm(ref)) 
                    for ref in reference_embeddings]
    max_similarity = max(similarities)
    return max_similarity >= threshold  #return True if close enough


#load Reference Embeddings
def load_reference_embeddings(reference_images_dir, model, transform):
    reference_embeddings = []
    for filename in os.listdir(reference_images_dir):
        if filename.endswith(('png', 'jpg', 'jpeg')):
            print(f'{filename} is creating reference')
            image_path = os.path.join(reference_images_dir, filename)
            image_tensor = process_image(image_path, transform)
            embedding = get_embedding(model, image_tensor)
            reference_embeddings.append(embedding)
    return reference_embeddings