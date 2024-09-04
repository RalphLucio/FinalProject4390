import cv2
import math
from matplotlib import pyplot as plt
import numpy as np

#hashing
import hashlib

def md5checksum(fname):
    md5 = hashlib.md5()
    with open(fname, "rb") as f:
        while chunk := f.read(4096):
            md5.update(chunk)
    return md5.hexdigest()

#print(os.getcwd()) #to get current working directory
#hardcoded directory with image, change this
file_path = "C:\\Users\\ryanw\\jupyter\\MediScanCode\\rekt.jpg"
example = cv2.imread(file_path)

result = md5checksum(file_path)
print(result)