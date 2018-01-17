import cv2
import numpy as np

def decode_from_bytes(image_bytes):
    return cv2.imdecode(np.fromstring(image_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)

def decode_from_file(ifile):
    img_bytes = cv2.imread(ifile, cv2.IMREAD_GRAYSCALE)
    return img_bytes


# gen qa cut image str
def get_qa_image(screen,height_begin,height_end):
    return screen[height_begin:height_end]

def encode_image(image_arr):
    return cv2.imencode('.png', image_arr)[1].tostring()
