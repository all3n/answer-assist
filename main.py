#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import argparse
import os
from qa_image import get_qa_image
from question import gen_qa
from engine.sougou import sogou_qe
from ConfigParser import ConfigParser
from six.moves import input

screen_begin = 180
screen_end = -450

sys.setrecursionlimit(1000000)

class answer_assist(object):
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
        self.parser.add_argument('--os',type=str,required=True,help='device os type android|ios')
        self.args = self.parser.parse_args()
        return self.args

    def try_answer(self):
        screen = self.device.get_screen()
        if not screen:
            return
        screen = get_qa_image(screen,screen_begin,screen_end)
        if screen.mean() < 180:
            return
        ocr = baidu.baidu_ocr(conf)
        text_list = ocr.detext_text(screen)
        qa = gen_qa(text_list)
        qe = sogou_qe()
        qe.resolve(qa)

    def main(self):
        args = self.build_args()
        os_type = args.os
        conf = self.load_config()

        from ocr import baidu

        if os_type == 'ios':
            from device import ios
            self.device = ios.ios_device()
        elif os_type == 'android':
            from device import android
            self.device = android.android_device()

        while True:
            enter = input(u"按Enter键开始，按ESC键退出...")
            if enter == chr(27):
                break
            try:
                self.try_answer()
            except Exception as e:
                print(str(e))



if __name__  == '__main__':
    answer_assist().main()
