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