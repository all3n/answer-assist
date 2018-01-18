#!/usr/bin/env python
from .ocr import ocr
from aip import AipOcr

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
        self.app_id = conf.get(self.baidu_ocr_sec,"api_id")
        self.app_key = conf.get(self.baidu_ocr_sec,"api_key")
        self.app_secret = conf.get(self.baidu_ocr_sec,"api_secret")
        self.ocr_client = AipOcr(appId=self.app_id, apiKey=self.app_key, secretKey=self.app_secret)
        self.ocr_client.setConnectionTimeoutInMillis(self.timeout * 1000)

    def detext_text(self,image):
        result = self.ocr_client.basicGeneral(image, self.options)
        if 'error_code' in result:
            print('baidu api error: ', result['error_msg'])
            return None
        ret = result["words_result"]
        return map(lambda x:x['words'],ret)






if __name__ == '__main__':
    import os
    import cv2
    import ConfigParser
    import sys
    if len(sys.argv) !=2 :
        print("need image")
        sys.exit(-1)
    conf_file = os.path.expanduser("~/.config/answer_assist.conf")
    conf = ConfigParser.ConfigParser()
    conf.read(conf_file)
    test_img = os.path.expanduser(sys.argv[1])
    test_img_bytes = cv2.imread(test_img, cv2.IMREAD_GRAYSCALE)
    p_bytes = cv2.imencode('.png', test_img_bytes[180:-450])[1].tostring()

    ret = baidu_ocr(conf).detext_text(p_bytes)
    print("\n".join(ret))

