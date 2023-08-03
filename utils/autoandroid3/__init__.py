
from . import minicap
minicap.start()
from . import minitouch
import subprocess
import os


def getsourcedir(d2):
    basepath = os.path.abspath(__file__)
    folder = os.path.dirname(basepath)
    data_path = os.path.join(folder, d2)
    return data_path



cap = minicap.cap
touch = minitouch
tap = minitouch.tap
swipe = lambda p:minitouch.swipe(*p)

inputchar = lambda x:subprocess.Popen(f'adb shell input text {x}', stdout=subprocess.PIPE, shell=True).stdout.read()


def exit():
    minicap.exit()
    minitouch.exit()

