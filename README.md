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
        1. 配置文件:~/.config/answer_assist.conf
```                                                                        
    [baidu-ocr]
    api_id=
    api_key=
    api_secret=
```
    1. python-sdk
        1. https://ai.baidu.com/download?sdkId=3

