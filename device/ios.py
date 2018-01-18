import sys
from .base_device import base_device
import imobiledevice
from imobiledevice import iDevice
from imobiledevice import LockdownClient
from imobiledevice import ScreenshotrClient


class ios_device(base_device):
    # get screen img data
    def get_screen(self):
        try:
            devices = imobiledevice.get_device_list()
        except imobiledevice.iDeviceError as e:
            print(e)
            return None
        if not devices:
            return None
        uuid = devices[0]
        lck = LockdownClient(iDevice(uuid))
        sc = lck.get_service_client(ScreenshotrClient)
        data = sc.take_screenshot()
        return data




if __name__ == '__main__':
    ios_device().get_screen()

