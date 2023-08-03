# mimicap 的特性：当画面没有发生改变时不会传送数据，此时接收端口会阻塞

import os, re
import subprocess
import threading
import socket
import time
from PIL import Image
import cv2
import numpy as np
import copy
import gc
import sys

#socket.setdefaulttimeout(5)

debug = True

def getsourcedir(d2):
    basepath = os.path.abspath(__file__)
    folder = os.path.dirname(basepath)
    data_path = os.path.join(folder, d2)
    return data_path
    
gconf = {'minicap_path': getsourcedir(r'external-plugs/minicap'),
        'minicap_port': 15534, 'minicap_maxfps':15, 'minicap_quality':80, 
        'minicap_sync_delay':0.1, 'minicap_frame_cache_size':60,
        'cap_socket':15536} #,
        #'minitouch_path':getsourcedir(r'external-plugs/minitouch_arm64-v8a')}
_RUNNING = False
realtime_fps = 0
#_IS_MINICAP_RUNING = False
_capthread = None
_capremotethread = None
_tag = '_MiniCap_'
toheight = 720 # 抓图的目标高度720/1080
#toheight = 1080
gcache = [(0,None) for i in range(gconf['minicap_frame_cache_size']+1)] # 缓存原始的jpeg bytes，(timestamp,jpeg_bytes), 只在capThread中写入故不加锁
gcache_seek = 0
ghead = {} # 包含图像宽高信息的头
#cap_condition = threading.Condition()
realfps = 0
        
def bindGlobal(g):

    global gcache, gconf, gcache_seek #, gstatus
    if 'minicap_config' in g:
        for k,v in g['minicap_config'].items():
            gconf[k] = v
    gcache = [(0,None) for i in range(gconf['minicap_frame_cache_size']+1)]
    g['minicap_cache_seek'] = gcache_seek
    g['minicap_cache'] = gcache
    #gstatus = g['']

# ============================================ ADB ===========================================

def popen(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout.read().decode('utf-8').strip()

def pathjoin(p1,p2): # linux path /
    p1l = p1.split('/')
    p2l = p2.split('/')
    return '/'.join(p1l+p2l)

def initMinicap(rotation=3, csize = (1280,720), density=240, cuthead = 77, pad=False):
    global gconf, _tag, _capremotethread
    print('正在安装minicap服务...', end='')
    rotation = int(rotation)
    rotation = rotation if rotation>=0 and rotation<=4 else 0
    # pkill
    pkill = popen(f'adb shell pkill minicap')
    #if _capremotethread:
    #    print(_tag+'minicap adb thread already exists')
    #    return gconf["minicap_port"]
        #threading.Thread._Thread__stop(_capremotethread)
    # run minicap
    abi = popen(r"adb shell getprop ro.product.cpu.abi")
    sdk = int(popen(r'adb shell getprop ro.build.version.sdk'))
    if sdk == 32 and abi == "x86_64":
        abi = "x86"
    bin_name = 'minicap' if int(sdk)>=16 else f'minicap-nopie'
    lib_name = 'minicap.so'
    remote_path = '/data/local/tmp/minicap_exec'
    remote_bin_path = pathjoin(remote_path, bin_name)
    bin_path = pathjoin(gconf['minicap_path'],f'{abi}/bin/{bin_name}')
    lib_path = pathjoin(gconf['minicap_path'],f'{abi}/lib/android-{sdk}/{lib_name}')
    _ = popen(f'adb shell "mkdir {remote_path} 2>/dev/null || true"')
    #screen_size = popen(r'adb shell wm size').split(':')[-1].strip()
    if not pad:
        wm_size = f'{csize[1]}x{csize[0]}'
        screen_size = f'{csize[1]}x{csize[0]}'
    else:
        wm_size = f'{csize[0]}x{csize[1]}'
        screen_size = f'{csize[0]}x{csize[1]}'
    popen(f'adb shell wm size {wm_size}')
    popen(f'adb shell wm density {density}')
    w,h  = csize
    #w += cuthead
    '''
    #traw = popen('adb shell dumpsys window displays')
    #match = re.findall(r' app=(\d+x\d+)',traw)
    #if match:
    #    screen_size = match[0]
    #print(screen_size)
    #只录制app区域， 异形屏隐藏摄像头左横屏， s10e 调整屏幕大小爱adb shell wm size 720x1429  density 240
    if len(screen_size)<=1:
        w = popen('adb shell dumpsys window | grep -Eo "DisplayWidth=[0-9]+" | head -1 | cut -d= -f 2')
        h = popen('adb shell dumpsys window | grep -Eo "DisplayHeight=[0-9]+" | head -1 | cut -d= -f 2')
        screen_size = f'{w}x{h}'
    if len(screen_size)<=1:
        screen_size = popen(r'adb shell dumpsys window | grep -Eo "init=[0-9]+x[0-9]+" | head -1 | cut -d= -f 2')
    # push exec'''
    
    #print(f'chmod minicap:{remote_bin_path}')
    _ = popen(f'adb push {bin_path} {remote_path}')
    _ = popen(f'adb push {lib_path} {remote_path}')
    _ = popen(f'adb shell chmod 777 {remote_bin_path}')
    '''
    if rotation%2 == 1:
        h,w = list(map(lambda x:int(x), screen_size.split('x')))
    else:
        w,h = list(map(lambda x:int(x), screen_size.split('x')))
        '''
    #vzoom = toheight/h
    #vw,vh = int(vzoom*w), toheight
    vw,vh = w,h
    vscreen_size = f'{vh}x{vw}'
    screen_size = f'{h}x{w}'
    # run 
    #print('run minicap')
    cmd = f'adb shell LD_LIBRARY_PATH={remote_path} {remote_bin_path} -P {screen_size}@{vscreen_size}/{rotation*90} -r {gconf["minicap_maxfps"]} -Q {gconf["minicap_quality"]}'
    #cmd = f'adb shell LD_LIBRARY_PATH={remote_path} {remote_bin_path} -P {screen_size}@{vscreen_size}/{rotation*90}'
    #print(cmd)
    _capremotethread = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    for i in range(10):
        unixsocksinfo = popen('adb shell "lsof | grep minicap | grep unix"')
        if len(unixsocksinfo)>0:
            break
        time.sleep(0.2)
    if len(unixsocksinfo)<=0:
        raise RuntimeError('通过adb启动minicap进程超时或错误。')
        return None
    #= threading.Thread(target=popen,args=[cmd])
    #_capremotethread.start()
    ##_ = popen(f'adb shell LD_LIBRARY_PATH={remote_path} {remote_bin_path} -P {screen_size}@{screen_size}/0 -S -r {gconf["minicap_maxfps"]} -Q {gconf["minicap_quality"]}')
    print('ok')
    _ = popen(f'adb forward tcp:{gconf["minicap_port"]} localabstract:minicap')
    return gconf["minicap_port"]

# ============================================ Reciever ===========================================

def parseHead(buff, seek=0):
    # b返回解析头
    seekl, seekr = seek, seek+24
    hbuff = buff[seekl:seekr]
    ''' 0 	1 	unsigned char 	Version (currently 1)
        1 	1 	unsigned char 	Size of the header (from byte 0)
        2-5 	4 	uint32 (low endian) 	Pid of the process
        6-9 	4 	uint32 (low endian) 	Real display width in pixels
        10-13 	4 	uint32 (low endian) 	Real display height in pixels
        14-17 	4 	uint32 (low endian) 	Virtual display width in pixels
        18-21 	4 	uint32 (low endian) 	Virtual display height in pixels
        22 	1 	unsigned char 	Display orientation
        23 	1 	unsigned char 	Quirk bitflags (see below)'''
    width, height = np.frombuffer(hbuff[14:18],dtype=np.uint32).squeeze(), np.frombuffer(hbuff[18:22],dtype=np.uint32).squeeze()
    rotation = np.frombuffer(hbuff[0:1],dtype=np.uint8).squeeze()
    head = {
        'version': np.frombuffer(hbuff[0:1],dtype=np.uint8).squeeze(),
        'header_size': np.frombuffer(hbuff[1:2],dtype=np.uint8).squeeze(),
        'minicap_pid': np.frombuffer(hbuff[2:6],dtype=np.uint32).squeeze(),
        'real_width': np.frombuffer(hbuff[6:10],dtype=np.uint32).squeeze(),
        'real_height': np.frombuffer(hbuff[10:14],dtype=np.uint32).squeeze(),
        'virtual_width': width,
        'virtual_height': height,
        'rotation': rotation,
        'quirk': np.frombuffer(hbuff[0:1],dtype=np.uint8).squeeze(),
        'width': width if rotation==0 else height,
        'height': height if rotation==0 else width
    }
    return head

def capThread(port):
    # connect to minicap and recv jpgs
    global gcache, ghead, gconf, _RUNNING, realtime_fps, gcache_seek, realfps
    print('初始化视觉.', end='')
    #base_buff_size = 300*1024*int(gconf['minicap_maxfps']*gconf['minicap_sync_delay']*3)
    base_buff_size = 1280*720*4
    sync_delay = gconf['minicap_sync_delay']
    frame_cache_size = gconf['minicap_frame_cache_size']
    frame_delay = 1/gconf['minicap_maxfps'] # 按照帧率确定读取的频率
    
    
    def collectBuff(conn, req_len=0, buff=b''):
        if len(buff)<req_len:
            try:
                new_buff = conn.recv(base_buff_size)
                buff += new_buff
            except:
                pass
        while len(buff)<req_len:
            try:
                new_buff = conn.recv(base_buff_size)
                buff += new_buff
            except:
                pass
            if not(_RUNNING):
                break
        return buff
        
    
    def initSocket():# 开启端口并处理头
        #print(_tag + 'capThread start conn')
        conn = socket.socket()
        conn.settimeout(5)
        conn.connect(('127.0.0.1',port)) # todo 判断端口是否正确连接并采取相应措施
        #print(_tag + 'capThread connected')
        # header
        buff = collectBuff(conn, 24)
        ghead = parseHead(buff)
        print(ghead)
        buff = buff[24:]
        time.sleep(sync_delay)
        return conn, buff, ghead
        
    conn, buff, ghead = initSocket()
    last_frame_time = 0
    last_gc_time = 0
    conn_start_time = time.time()
    _RUNNING = True
    #print(_tag + 'capThread loop')
    #print('ok')
    while _RUNNING:
        '''
        t = time.time()
        if t-conn_start_time > 3600: # 每小时重启端口
            print('Minicap: reopen socket')
            conn.close()
            time.sleep(sync_delay)
            conn, buff, ghead = initSocket()
            conn_start_time = t
        '''
        #if t-last_frame_time < frame_delay:
        #    time.sleep(frame_delay-(t-last_frame_time))
        # frame len
        
        buff = collectBuff(conn, 4, buff)
        req_len = np.frombuffer(buff[:4],dtype=np.uint32).squeeze()
        buff = buff[4:]
        buff = collectBuff(conn, req_len, buff)
        nextseek = gcache_seek + 1 if gcache_seek<gconf['minicap_frame_cache_size'] else 0
        img = Image.frombytes('RGB',(ghead['width'],ghead['height']), buff[:req_len],'jpeg', 'RGB', 'raw')
        buff = buff[req_len:]
        gcache[nextseek] = ((time.time(), img))
        gcache_seek = nextseek
        if gcache_seek>=10:
            realfps = gcache_seek/(time.time() - gcache[0][0])
        
        
        #framecount = 1
        '''
        while len(buff)>req_len: # 处理调残余的buff, 保证获取的帧最新
            framecount += 1
            nextseek = gcache_seek + 1 if gcache_seek<gconf['minicap_frame_cache_size'] else 0
            #gcache.append((time.time(),buff[:req_len]))
            gcache[nextseek] = ((time.time(),copy.copy(buff[:req_len]))) # 不使用copy的情况下已使用的buff疑似无法正常回收
            gcache_seek = nextseek
            buff = buff[req_len:]
            buff = collectBuff(conn, 4, buff)
            req_len = np.frombuffer(buff[:4],dtype=np.uint32).squeeze()
            buff = buff[4:]
        
        buff = collectBuff(conn, req_len, buff)
        
        t = time.time()
        realtime_fps = int(realtime_fps*0.8 + framecount/(t-last_frame_time) * 0.2)
        last_frame_time = time.time()
        nextseek = gcache_seek + 1 if gcache_seek<gconf['minicap_frame_cache_size'] else 0
        gcache[nextseek] = ((time.time(),copy.copy(buff[:req_len])))
        gcache_seek = nextseek
        if gcache_seek>=10:
            realfps = gcache_seek/(time.time() - gcache[0][0])
        #gcache.append((last_frame_time,buff[:req_len]))
        buff = buff[req_len:]
        #if len(gcache)>frame_cache_size:
        #    gcache = gcache[len(gcache)-int(frame_cache_size*0.6):] # 浮动缓存，减少删除次数
        if t - last_gc_time > 60: # 每60秒回收内存
            clt = gc.collect()
            last_gc_time = t
            #print(f'buffsize: {sys.getsizeof(buff)}, gccollected:{clt}') #----------------------------debug
            '''
    conn.close()
    #_RUNNING = False
    print('视觉已关闭.')
    pass

# 引入缓存加速静态画面的处理
_capcache = {'id':None, 'cv2':None}

def cap(mode='cv2'): # 从gcache中获取最新截图, 
    #  mode cv2, pil
    global ghead, gcache, realtime_fps, gcache_seek
    global _capcache
    #print(_tag+'fps:'+str(realtime_fps))
    #while len(gcache)<=0:
    #    time.sleep(0.1)
    #ts, jpg_bytes = gcache[-1]
    #capts = time.time()
    gst = gcache_seek
    ts, img = gcache[gcache_seek]
    gstn = gst + 1 if gst<gconf['minicap_frame_cache_size'] else 0
    while img is None:
        time.sleep(0.05)
        ts, img = gcache[gstn]
    #img = Image.frombytes('RGB',(ghead['width'],ghead['height']),jpg_bytes,'jpeg', 'RGB', 'raw')
    if mode == 'cv2':
        #cvim = cv2.cvtColor(cv2.imdecode(np.frombuffer(jpg_bytes,dtype=np.uint8),cv2.IMREAD_COLOR),cv2.COLOR_RGB2BGR)
        if _capcache['id'] != id(img):
            _capcache['id'] = id(img)
            _capcache['cv2'] = cv2.cvtColor(np.asarray(img, dtype=np.uint8), cv2.COLOR_RGB2BGR)
        return _capcache['cv2']
        #pass #---------------
        #return jpg_bytes       
    return img



def autoParams():
    # 根据机型适配参数
    product = popen('adb shell getprop ro.product.model')
    if product=='SM-G9700':
        return {'rotation':3, 'csize':(1280,720), 'density':240, 'cuthead':77, 'pad':False}
    
    return {'rotation':3, 'csize':(1280,720), 'density':240, 'cuthead':0, 'pad':True}

        
def start():
    global _RUNNING, gcapthread
    if _RUNNING:
        print(_tag+' already started')
        return
    minicap_port = initMinicap(**autoParams())
    gcapthread = threading.Thread(target=capThread, args=[minicap_port])
    #time.sleep(2) # 等待端口就绪 无法检查的情况，直接采用延时
    gcapthread.start()
    
def exit():
    global __RUNNING
    _RUNNING = False
    _ = popen(f'adb shell pkill minicap')
    _capremotethread.terminate()
    if _capremotethread.poll():
        print('minicap服务已关闭.')
    else:
        print('关闭失败了哦，快使用任务管理器')

