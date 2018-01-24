import sys
from .base_device import base_device
import subprocess


class android_device(base_device):
    # get screen img data
    def get_screen(self):
        # os.system("adb shell /system/bin/screencap -p /sdcard/screenshot.png")
        # os.system("adb pull /sdcard/screenshot.png ./screenshot.png")
        # return cv2.imread('./screenshot.png', cv2.IMREAD_GRAYSCALE)

        # directly read image bytes from pipe

        pipe = subprocess.Popen("adb -P 7555 shell screencap -p",
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, shell=True)
        image_bytes = pipe.stdout.read().replace(b'\r\n', b'\n')
        return image_bytes



if __name__ == '__main__':
    android_device().get_screen()

