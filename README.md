# Answer Assit For Online Answer Platform

## IOS Required
    1. libimobiledevice

## Android Required
    1. Adb 


## python:
    1. pip install -r requirements.txt


## Run
    1. Run With Device
        1. python main.py 
        1. python main.py --os android
    1. Run With Img
        1. python main.py --img xxx.png
    1. Run With Question text file
        1. python main.py --q data/q1.txt

## ocr:
    1. baidu ocr:
        1. https://login.bce.baidu.com/ 开通 OCR 获取相关token
        1. api配置文件:~/.config/answer_assist.conf
```
baidu-ocr:
    api_id: YOUR_BAIDU_API_ID
    api_key: YOUR_BAIDU_API_KEY
    api_secret: YOUR_BAIDU_API_SECRET
```
        1. python-sdk
            1. https://ai.baidu.com/download?sdkId=3
            1. unzip
            1. python setup.py install

    2. tesseract (Google Open Source OCR)
        1. debian (deepin)
            1. apt-get install libleptonica-dev libtesseract-dev
            1. pip install tesseract-ocr pytesseract
        1. mac
            1. brew install leptonica
            1. brew install tesseract --with-serial-num-pack --with-all-languages
            1. pip install tesseract-ocr pytesseract
    
