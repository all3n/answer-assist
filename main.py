#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import argparse
import os
import time
import cv2
from qa_image import *
from question import *
from engine.sougou import sogou_qe
from ConfigParser import ConfigParser
from six.moves import input

screen_begin = 180
screen_end = -450

sys.setrecursionlimit(1000000)

class answer_assist(object):
    pre_head_wb = None
    def load_config(self):
        conf_file = os.path.expanduser("~/.config/answer_assist.conf")
        if not os.path.exists(conf_file):
            print("%s not exits" % conf_file)
            sys.exit(-1)
        self.conf = ConfigParser()
        self.conf.read(conf_file)
        return self.conf


    def build_args(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--os',type=str,help='device os type android|ios',default="ios")
        self.parser.add_argument('--img',type=str,help='input-img answer',default=None)
        self.parser.add_argument('--q',type=str,help='input question file',default=None)
        self.args = self.parser.parse_args()
        return self.args

    def ocr_img_to_qa(self,img_arr):
        # str
        encode_img_str = encode_image(img_arr)
        text_list = self.ocr.detext_text(encode_img_str)
        qa = gen_qa(text_list)
        return qa

    def try_answer(self,screen):
        img_arr = get_qa_image(screen,screen_begin,screen_end)
        if img_arr.mean() < 180:
            return
        head_wb = cv2.Canny(img_arr[:int(img_arr.shape[0] / 3)], 40, 60)
        if type(self.pre_head_wb).__name__ == 'ndarray':
            diff = np.mean(np.abs(self.pre_head_wb - head_wb))
            if diff > 2.0:
                qa = self.ocr_img_to_qa(img_arr)
                self.qe.resolve(qa)
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


    def main(self):
        args = self.build_args()
        os_type = args.os
        conf = self.load_config()

        from ocr import baidu
        self.ocr = baidu.baidu_ocr(conf)
        self.gen_device(os_type)
        self.qe = sogou_qe()

        if args.img:
            img_nd = decode_from_file(args.img)
            if type(img_nd).__name__ != 'ndarray':
                print("error not img")
                return
            img_arr = get_qa_image(img_nd,screen_begin,screen_end)
            qa = self.ocr_img_to_qa(img_arr)
            self.qe.resolve(qa)
            return

        if args.q:
            print("%s" % args.q)
            qa = load_qa_from_file(args.q)
            self.qe.resolve(qa)
            return

        while True:
            #if not self.wait_for_key():break
            try:
                screen = self.device.get_screen()
                if not screen:
                    continue
                screen_nd = decode_from_bytes(screen)
                self.try_answer(screen_nd)
            except Exception as e:
                print(str(e))
            time.sleep(0.5)



if __name__  == '__main__':
    answer_assist().main()
