
import socket, subprocess, time, os

## ------------------------- utils
def getsourcedir(d2):
    basepath = os.path.abspath(__file__)
    folder = os.path.dirname(basepath)
    data_path = os.path.join(folder, d2)
    return data_path

def popen(cmd, read=True):
    psub = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    if read:
        return psub.stdout.read().decode('utf-8').strip()
    return psub
    
def pathjoin(p1,p2): # linux path /
    p1l = p1.split('/')
    p2l = p2.split('/')
    return '/'.join(p1l+p2l)
    
## ------------------------- utils end

_config = {'path': getsourcedir(r'external-plugs/minitouch'),
        'port': 15544} #,

rate = 100 # 触控模拟的采样率
space = 1000/rate


def start():
    pass
    
def _parseHeader(text):
    global _header
    #print(text)
    hl = text.split('\n')
    for msg in hl:
        l = msg.split(' ')
        if l[0] == 'v':
            _header['version'] = int(l[1])
        elif l[0] == '^':
            _header['max-contacts'] = int(l[1])
            _header['max-x'] = int(l[2])
            _header['max-y'] = int(l[3])
            #_header['max-x'] = int(1280)
            #_header['max-y'] = int(720)
            _header['max-pressure'] = int(l[4])
        elif l[0] == '$':
            _header['pid'] = int(l[1])
    return _header

    
def initMinitouch():
    global _config, _connection, _minitouchsubprocess, _cs
    # generate path
    print('正在安装minitouch服务...', end='')
    abi = popen(r"adb shell getprop ro.product.cpu.abi")
    sdk = popen(r'adb shell getprop ro.build.version.sdk')
    bin_name = 'minitouch' if int(sdk)>=16 else 'minitouch-nopie'
    remote_path = '/data/local/tmp'
    remote_bin_path = pathjoin(remote_path,bin_name)
    bin_path = pathjoin(_config['path'],f'{abi}/bin/{bin_name}')
    # kill exists
    _ = popen('adb shell pkill minitouch')
    # push bin
    _ = popen(f'adb push {bin_path} {remote_path}')
    _ = popen(f'adb shell chmod 777 {remote_bin_path}')
    # start subprocess
    _minitouchsubprocess = popen(f'adb shell {remote_bin_path}' ,False)
    for i in range(10):
        unixsocksinfo = popen('adb shell "lsof | grep @minitouch | grep unix"')
        if len(unixsocksinfo)>0:
            break
        time.sleep(0.2)
    if len(unixsocksinfo)<=0:
        raise RuntimeError('通过adb启动minitouch进程超时或错误。')
        return None
    print('ok')
    _ = popen(f'adb forward tcp:{_config["port"]} localabstract:minitouch')
    # connect
    _connection = socket.socket()
    _connection.connect(('127.0.0.1',_config["port"]))
    headertext = _connection.recv(1024).decode('utf-8')
    while len(headertext.split('\n'))<3:
        headertext+=_connection.recv(1024).decode('utf-8')
    header = _parseHeader(headertext)
    print(header)
    _cs = [[] for i in range(header['max-contacts'])]
    _ct = [{} for i in range(header['max-contacts'])]
    return _connection
    
def exit():
    _ = popen('adb shell pkill minitouch')
    _minitouchsubprocess.terminate()
    if _minitouchsubprocess.poll():
        print('minitouch服务已关闭.')
    else:
        print('关不掉，请用直接关闭窗口')


def getParam(p):
    global _header
    return _header.get(p,None)

def autoAxis(x, y):
    # 自动转换百分比int坐标
    # 设备横屏坐标基准点转换
    global _header
    if x<=1. and x>=0. and y<=1. and y>=0.:
        return int(_header['max-x']*x), int(_header['max-y']*y)
    return int(x), int(y)

def send(cmd):
    # 传送原始的minitouch指令
    global _connection
    if cmd[-1]!='\n':
        cmd += '\n'
    return _connection.send(cmd.encode('utf-8'))


def press(x, y, contact=0):
    x,y = autoAxis(x, y)
    cmd = f'd {contact} {x} {y} {_header["max-pressure"]}\n'
    send(cmd)
    commit()
    
    
def release(contact=0):
    send(f'u {contact}\n')
    commit()
    
    
def reset(contact=0):
    send(f'r\n')   


def move(x,y, contact=0):
    x,y = autoAxis(x, y)
    cmd = f'm {contact} {x} {y} {_header["max-pressure"]}\n'
    send(cmd)
    commit()

    
def commit():
    send('c\n')


def _wait(duration=10):
    send(f'w {duration}\n')

def tap(x, y, duration=50, contact=0):
    # 简化点击指令
    x,y = autoAxis(x, y)
    press(x, y, contact = contact)
    _wait(duration)
    release(contact = contact)


def swipe(x1, y1, x2, y2, duration=100, contact=0):
    # 匀速拖动
    global space
    frames = int(duration/space)
    xp = (x2-x1)/frames
    yp = (y2-y1)/frames
    press(x1, y1, contact = contact)
    for i in range(1,frames):
        _wait(space)
        move(x1+xp*i, y1+yp*i, contact = contact)
    release()


if '_connection' not in vars():
    _header = {}
    _connection = initMinitouch()