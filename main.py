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


sys.setrecursionlimit(1000000)

class answer_assist(object):
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
        self.parser.add_argument('-cc','--custom_config',type=str,help='custom api config file default:~/.config/answer_assist.conf',default='~/.config/answer_assist.conf')
        self.parser.add_argument('-c','--config',type=str,help='custom config file default:conf/app.ini',default='conf/app.ini')
        self.args = self.parser.parse_args()
        return self.args

    def ocr_img_to_qa(self,img_arr):
        # str
        encode_img_str = encode_image(img_arr)
        text_list = self.ocr.detext_text(encode_img_str)
        qa = gen_qa(text_list)
        return qa

    def try_answer(self,img_arr):
        if img_arr.mean() < 180:
            return
        head_wb = cv2.Canny(img_arr[:int(img_arr.shape[0] / 3)], 40, 60)
        if type(self.pre_head_wb).__name__ == 'ndarray':
            diff = np.mean(np.abs(self.pre_head_wb - head_wb))
            if diff > 2.0:
                # if question change,wait 0.8 s fix xiguan
                time.sleep(0.8)
                screen_cut_nd = self.get_screen_cut_nd()
                qa = self.ocr_img_to_qa(screen_cut_nd)
                start = time.time()
                self.qe.resolve(qa)
                print("query cost %.2f" % (time.time() - start))

                start = time.time()
                self.question_file.write(qa.question + "\n")
                for asw in qa.answer:
                    self.question_file.write(asw + "\n")
                self.question_file.write("-----------------------\n")
                self.question_file.flush()
                print("save file cost %.2f" % (time.time() - start))
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

    def main(self):
        args = self.build_args()
        os_type = args.os
        jieba.initialize()

        # merge conf with custom config yaml
        c_conf = self.load_yaml(args.custom_config)
        conf = self.load_yaml(args.config)
        conf.update(c_conf)

        game_type = args.game_type
        self.question_file = open("data/question.txt","a")
        if game_type == 1:
            self.screen_begin = 180
            self.screen_end = -460
        elif game_type == 2:
            self.screen_begin = 180
            self.screen_end = -550

        from ocr import baidu
        self.ocr = baidu.baidu_ocr(conf)
        self.gen_device(os_type)
        #self.qe = sogou_qe(conf)
        self.qe = baidu_qe(conf)

        if args.img:
            img_nd = decode_from_file(args.img)
            if type(img_nd).__name__ != 'ndarray':
                print("error not img")
                return
            img_arr = get_qa_image(img_nd,self.screen_begin,self.screen_end)
            qa = self.ocr_img_to_qa(img_arr)
            self.qe.resolve(qa)
            return

        question = args.question
        if question:
            print("%s" % question)
            qa = load_qa_from_file(question)
            start = time.time()
            self.qe.resolve(qa)
            print("query cost %.2f" % (time.time() - start))
            return

        while True:
            if args.method == 1:
                if not self.wait_for_key():break
            try:
                screen_cut_nd = self.get_screen_cut_nd()
                self.try_answer(screen_cut_nd)

            except Exception as e:
                print(str(e))
            time.sleep(0.5)



if __name__  == '__main__':
    answer_assist().main()
