#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import argparse
import os
import time
import yaml
import cv2
import jieba
from qa_image import *
from question import *
from engine.sougou import sogou_qe
from engine.baidu import baidu_qe
from ConfigParser import ConfigParser
from six.moves import input
import threading
from websocket_server import WebsocketServer
import logging
import base64

sys.setrecursionlimit(1000000)

class answer_assist(object):
    def new_client(self,client, server):
        server.send_message_to_all("answer assist connected !!")
    def message_received(self,client, server, message):
        print("Client(%d) said: %s" % (client['id'], message))
    def client_left(self,client, server):
        print("Client(%d) disconnected" % client['id'])

    pre_head_wb = None
    def load_config(self,conf_file):
        conf_file = os.path.expanduser(conf_file)
        if not os.path.exists(conf_file):
            print("%s not exits" % conf_file)
            sys.exit(-1)
        self.conf = ConfigParser()
        self.conf.read(conf_file)
        return self.conf
    def load_yaml(self,yaml_file):
        conf_file = os.path.expanduser(yaml_file)
        if not os.path.exists(conf_file):
            print("%s not exits" % conf_file)
            sys.exit(-1)

        with open(conf_file,"r") as yf:
            return yaml.load(yf)
        return {}


    def build_args(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-o','--os',type=str,help='device os type android|ios',default="ios")
        self.parser.add_argument('-i','--img',type=str,help='input-img answer',default=None)
        self.parser.add_argument('-q','--question',type=str,help='input question file',default=None)
        self.parser.add_argument('-t','--game_type',type=int,help='game type 1 xigua,2 zhishi',default=1)
        self.parser.add_argument('-m','--method',type=int,help='0 auto 1 manual',default=0)
        self.parser.add_argument('-p','--port',type=int,help='websocket port',default=12345)
        self.parser.add_argument('-ocr','--ocr',type=int,help='0 baidu 1 tesseract',default=0)
        self.parser.add_argument('-cc','--custom_config',type=str,help='custom api config file default:~/.config/answer_assist.conf',default='~/.config/answer_assist.conf')
        self.parser.add_argument('-c','--config',type=str,help='custom config file default:conf/app.ini',default='conf/app.ini')
        self.args = self.parser.parse_args()
        return self.args

    def ocr_img_to_qa(self,img_arr):
        # str
        text_list = self.ocr.detext_text(img_arr)
        qa = gen_qa(text_list)
        return qa

    def try_answer(self,img_arr):
        #print(img_arr.mean())
        self.time_stat = {}
        if img_arr.mean() < 180:
            return
        head_wb = cv2.Canny(img_arr[:int(img_arr.shape[0] / 3)], 40, 60)
        if type(self.pre_head_wb).__name__ == 'ndarray':
            diff = np.mean(np.abs(self.pre_head_wb - head_wb))
            if diff > 2.0:
                start = time.time()
                cv2.imwrite('imgs/cut_%.2f_%dX%d.png' % (start,img_arr.shape[0],img_arr.shape[1]),img_arr, [int( cv2.IMWRITE_JPEG_QUALITY), 95])
                # if question change,wait 0.8 s fix xiguan
                time.sleep(0.8)
                screen_cut_nd = self.get_screen_cut_nd()

                x = cv2.imencode(".png",screen_cut_nd)[1].tostring()
                self.server.send_message_to_all('{"type":"img","data":"'+base64.b64encode(x)+'"}')

                self.time_stat["screen-cut"] = time.time() - start

                start = time.time()
                qa = self.ocr_img_to_qa(screen_cut_nd)
                self.time_stat["ocr-img-2-qa"] = time.time() - start

                start = time.time()
                self.qe.resolve(qa)
                self.time_stat["query"] = time.time() - start

                start = time.time()
                self.question_file.write(qa.question + "\n")
                for asw in qa.answer:
                    self.question_file.write(asw + "\n")
                self.question_file.write("-----------------------\n")
                self.question_file.flush()
                self.time_stat["query"] = time.time() - start

                for tt in self.time_stat:
                    self.server.send_message_to_all("%s:%f s" % (tt,self.time_stat[tt]))

        self.pre_head_wb = head_wb

    def wait_for_key(self):
        enter = input(u"按Enter键开始，按ESC键退出...")
        if enter == chr(27):
            return False
        else:
            return True
    def gen_device(self,os_type):
        if os_type == 'ios':
            from device import ios
            self.device = ios.ios_device()
        elif os_type == 'android':
            from device import android
            self.device = android.android_device()


    def get_screen_cut_nd(self):
        screen = self.device.get_screen()
        if screen == None:
            raise IOError("device error,check your device is connected!!!")
        screen_nd = decode_from_bytes(screen)
        cut_img_arr = get_qa_image(screen_nd,self.screen_begin,self.screen_end)
        return cut_img_arr


    def answer_process(self,stop_event):
        while not stop_event.is_set():
            if self.args.method == 1:
                if not self.wait_for_key():break
            try:
                screen_cut_nd = self.get_screen_cut_nd()
                self.try_answer(screen_cut_nd)
            except Exception as e:
                print(str(e))
            time.sleep(0.5)


    def main(self):
        args = self.build_args()
        self.server = WebsocketServer(self.args.port)

        os_type = self.args.os
        jieba.initialize()

        # merge conf with custom config yaml
        c_conf = self.load_yaml(self.args.custom_config)
        conf = self.load_yaml(self.args.config)
        conf.update(c_conf)

        game_type = self.args.game_type
        self.question_file = open("data/question.txt","a")
        if game_type == 1:
            self.screen_begin = 180
            self.screen_end = -460
        elif game_type == 2:
            self.screen_begin = 180
            self.screen_end = -550

        if self.args.ocr == 0:
            from ocr import baidu
            self.ocr = baidu.baidu_ocr(conf)
        elif self.args.ocr == 1:
            from ocr import tesseract
            self.ocr = tesseract.tesseract_ocr(conf)

        self.gen_device(os_type)
        #self.qe = sogou_qe(conf,self)
        self.qe = baidu_qe(conf,self)

        if self.args.img:
            img_nd = decode_from_file(self.args.img)
            if type(img_nd).__name__ != 'ndarray':
                print("error not img")
                return
            img_arr = get_qa_image(img_nd,self.screen_begin,self.screen_end)
            qa = self.ocr_img_to_qa(img_arr)
            self.qe.resolve(qa)
            return

        question = self.args.question
        if question:
            qa = load_qa_from_file(question)
            start = time.time()
            self.qe.resolve(qa)
            print("query cost %.2f" % (time.time() - start))
            return

        self.answer_stop = threading.Event()
        self.answer_thread = threading.Thread(target=self.answer_process,args = (self.answer_stop,))
        self.answer_thread.start()

        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)
        self.server.run_forever()

        self.answer_stop.set()
        self.answer_thread.join()
        print("Quit Answer Assit,Thank You For Use")

if __name__  == '__main__':
    answer_assist().main()
