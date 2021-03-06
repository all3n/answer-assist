#!/usr/bin/env python
from .ocr import ocr
from aip import AipOcr
import cv2

# disable warning of not https
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class baidu_ocr(ocr):
    baidu_ocr_sec = "baidu-ocr"
    ocr_client = None
    options = {"language_type": "CHN_ENG"}
    timeout = 3
    def __init__(self,conf):
        super(baidu_ocr,self).__init__(conf)
        self.app_id = str(conf[self.baidu_ocr_sec]["api_id"])
        self.app_key = conf[self.baidu_ocr_sec]["api_key"]
        self.app_secret = conf[self.baidu_ocr_sec]["api_secret"]
        self.ocr_client = AipOcr(appId=self.app_id, apiKey=self.app_key, secretKey=self.app_secret)
        self.ocr_client.setConnectionTimeoutInMillis(self.timeout * 1000)

    def detext_text(self,image):
        if type(image).__name__ == 'ndarray':
            image = cv2.imencode('.png', image)[1].tostring()

        result = self.ocr_client.basicGeneral(image, self.options)
        if 'error_code' in result:
            print('baidu api error: ', result['error_msg'])
            return None
        ret = result["words_result"]
        return map(lambda x:x['words'],ret)
