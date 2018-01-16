#!/usr/bin/env python
#coding:utf-8
from aip import AipOcr
import cv2
from six.moves import urllib
from six.moves.urllib import parse
from bs4 import BeautifulSoup
import time
import re
import sys
from multiprocessing import Pool
import subprocess
import numpy as np
import ios
import os
from ConfigParser import ConfigParser

screenshot_path = './screenshot.png'
line_split = "=" * 50
sys.setrecursionlimit(1000000)
conf_file = os.path.expanduser("~/.config/answer_assist.conf")

if not os.path.exists(conf_file):
    print("%s not exits" % conf_file)
    sys.exit(-1)

conf = ConfigParser()
conf.read(conf_file)

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/51.0.2704.63 Safari/537.36'
           }

# configurations
baidu_ocr_sec = "baidu-ocr"
app_id = conf.get(baidu_ocr_sec,"api_id")
app_key = conf.get(baidu_ocr_sec,"api_key")
app_secret = conf.get(baidu_ocr_sec,"api_secret")
timeout = 3
# scale to speed up network transfer
top_n = 5

ocr_client = None
options = {"language_type": "CHN_ENG"}

#芝士超人参数
height_begin = 180
height_end = -450

num_choises = 3
# 从图片中识别文字, image为图片bytes, 图片裁剪需调参
def get_text_from_image(image):
  global ocr_client
  if not ocr_client:
    ocr_client = AipOcr(appId=app_id, apiKey=app_key, secretKey=app_secret)
    ocr_client.setConnectionTimeoutInMillis(timeout * 1000)
  result = ocr_client.basicGeneral(image, options)
  if 'error_code' in result:
    print('baidu api error: ', result['error_msg'])
    return ''
  return result["words_result"]

def parse_question_and_answers(words):
  question = ''.join([word['words'] \
                      for word in words[:(len(words) - num_choises)]])
  # 此处开始检索
  choices = [word['words'] for word in words[-num_choises:]]
  return (question, choices)

def get_qa_image(screen):
  cutted_image = screen[height_begin:height_end]
  return cv2.imencode('.png', cutted_image)[1].tostring()

def sogou_search(question):
  prefix = 'https://www.sogou.com/web?query='
  url = prefix + parse.quote(question)
  req = urllib.request.Request(url=url, headers=headers)
  res = urllib.request.urlopen(req, timeout=3)
  if res.getcode() != 200:
    print('search error, error code: ', res.getcode())
  return res.read().decode('utf-8')

def high_light_question(content):
  res = re.sub('<em><!--red_beg-->', '\x1b[1m\x1b[31m', content)
  res = re.sub('<!--red_end--></em>', '\x1b[0m', res)
  return res

def high_light_answer(content):
  res = re.sub('<em><!--red_beg-->', '\x1b[1m\x1b[34m', content)
  res = re.sub('<!--red_end--></em>', '\x1b[0m', res)
  return res

def parse_answers(html):
  soup = BeautifulSoup(html, "lxml")
  search_result = soup.find("div", {"class": "results"})
  answers = search_result.find_all("div", {"class": "vrwrap"})
  # multi processors
  pool = Pool(top_n)
  res = pool.map(_parser_single_answer, answers[:top_n])
  pool.close()
  pool.join()
  for _res in res:
    if _res:
      print(_res)
  print(line_split)

def _parser_single_answer(answer):
  question_desc = answer.find("a", {"target": "_blank"})
  if not question_desc:
    return None
  answer_box = line_split
  answer_box += '\n'
  answer_box += '>>>'
  answer_box += high_light_question(''.join(map(str, question_desc.contents)))
  answer_box += '\n'
  texts = answer.find_all("div", {"class": "str-text-info"})
  for text in texts:
    text_str = str(text)
    if u'问题说明' in text_str:
      continue
    span = text.find("span")
    if not span:
      continue
    answer_desc = high_light_answer(''.join(map(str, span.contents)))
    if u'最佳答案' in text_str:
      answer_desc = u'最佳答案: %s' % answer_desc
    answer_box += answer_desc
  return answer_box

def get_screen():
  # os.system("adb shell /system/bin/screencap -p /sdcard/screenshot.png")
  # os.system("adb pull /sdcard/screenshot.png ./screenshot.png")
  # return cv2.imread('./screenshot.png', cv2.IMREAD_GRAYSCALE)

  # directly read image bytes from pipe

  #pipe = subprocess.Popen("adb shell screencap -p",
  #                        stdin=subprocess.PIPE,
  #                        stdout=subprocess.PIPE, shell=True)
  #image_bytes = pipe.stdout.read().replace(b'\r\n', b'\n')

  image_bytes = ios.get_screen_data()
  return cv2.imdecode(np.fromstring(image_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)

def run_job(screen):
  print('asking new question...')
  start = time.time()
  qa_image = get_qa_image(screen)


  text = get_text_from_image(qa_image)
  question, choices = parse_question_and_answers(text)

  print(u'问题:%s'%  question)
  query = question.strip('?') + ' ' + ' '.join(choices)
  html = sogou_search(query)
  parse_answers(html)
  print(u'use {0} 秒'.format(time.time() - start))
  with open('./question-choices', 'a+') as out_file:
    out_file.write(query + '\n')

pre_head_wb = None

def main():
  global pre_head_wb
  screen = get_screen()
  qc_box = screen[height_begin:height_end]

  with open("a.png","w") as cut:
      cut.write(qc_box)

  if qc_box.mean() < 180:
    return
  if type(pre_head_wb).__name__ == 'NoneType':
    try:
      run_job(screen)
    except Exception as e:
      print(str(e))
  head_wb = cv2.Canny(qc_box[:int(qc_box.shape[0] / 3)], 40, 60)
  if type(pre_head_wb).__name__ == 'ndarray':
    diff = np.mean(np.abs(pre_head_wb - head_wb))
    if diff > 2.0:
      print(u'diff:%s ' % diff)
      print(u'invoke...')
      run_job(screen)
  pre_head_wb = head_wb

if __name__ == '__main__':
  while True:
    try:
      main()
      break
      time.sleep(0.5)
    except Exception as e:
      print(str(e))
    except KeyboardInterrupt:
      print(u'欢迎下次使用')
      sys.exit()
