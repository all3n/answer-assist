#!/usr/bin/env python
import argparse
import os
from qa_image import get_qa_image
from question import gen_qa

screen_begin = 180
screen_end = -450



def build_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--os',type=str,required=True,help='device os type android|ios')
    return parser.parse_args()


def main():
    args = build_args()
    os_type = args.os

    from ocr import baidu

    if os_type == 'ios':
        from device import ios
        device = ios.ios_device()
    elif os_type == 'android':
        from device import android
        device = android.android_device()

    screen = device.get_screen()
    if not screen:
        return
    screen = get_qa_image(screen,screen_begin,screen_end)
    if screen.mean() < 180:
        return

    ocr = baidu.baidu_ocr()
    text_list = ocr.detext_text(screen)
    print gen_qa(text_list)



if __name__  == '__main__':
    main()
