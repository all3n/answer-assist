import sys
import imobiledevice
from imobiledevice import iDevice
from imobiledevice import LockdownClient
from imobiledevice import ScreenshotrClient


def get_screen_data():
    devices = imobiledevice.get_device_list()
    if not devices:
        print "device not connect"
        sys.exit()
    uuid = devices[0]
    lck = LockdownClient(iDevice(uuid))
    sc = lck.get_service_client(ScreenshotrClient)
    data = sc.take_screenshot()
    with open("a.png","w") as f:
        f.write(data)
    return data
if __name__ == '__main__':
    get_screen_data()

