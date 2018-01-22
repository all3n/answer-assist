#!/usr/bin/env python
from .ocr import ocr
import cv2
from PIL import Image
import pytesseract

class tesseract_ocr(ocr):
    tesseract_ocr_sec = "tesseract"
    def __init__(self,conf):
        super(tesseract_ocr,self).__init__(conf)
        self.lang = conf[self.tesseract_ocr_sec]["lang"]

    def detext_text(self,image):
        code = pytesseract.image_to_string(Image.fromarray(image), lang=self.lang)
        code = map(lambda x:x.strip(),code.split("\n"))
        text_list = filter(lambda x:len(x)>0,code)
        return text_list

