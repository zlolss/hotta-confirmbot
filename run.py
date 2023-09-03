
cid = 'android0'

import time, keyboard

#import utils.autoandroid3 as autoandroid
import anhelper

import hottaui

from motions.autointeract import autoInteract
from motions.exitparty import exitParty
from motions.announce import guildAnnounceEN, worldAnnounceEN

class AutoAndroidCompatible:
    def __init__(self):
        self.dev = anhelper.device.getDevice()
        print(self.dev)
        self.dev.setWM(**anhelper.device.CONST.TABLET_720P, fit_orientation = True)
        self.minicap = anhelper.minicap.getMinicap(self.dev.id)
        self.minitouch = anhelper.minitouch.getMinitouch(self.dev.id)
        self.touch = self.Touch(self.minitouch)
        self.ime = anhelper.ime.getIME(self.dev.id)
        self.minicap.start()
        self.minitouch.start()
        self.ime.ensure()
        
    def cap(self):
        return self.minicap.cap()
        
    def inputchar(self, txt):  
        self.ime.inputSafe(txt)
        
    class Touch:
        
        def __init__(self, minitouch):
            self.minitouch = minitouch
        
        def tap(self, x, y):
            with self.minitouch.useContact() as c:
                c.tap(x, y)
        
    
        

if __name__ == '__main__':
    print(anhelper.device.listDevices())
    autoandroid = AutoAndroidCompatible()
    ti = 0
    tt = time.time()
    lastMissionExitTs = 0
    lastAnnounceTs = 0
    lastExitPartyTs = 0
    lastBusyTs = 0
    idle = True
    status = 0
    framecount = 0
    print('关闭窗口退出')
    while True:
        

        if time.time() - ti>1:
        
            imat = autoandroid.cap()
            '''
            if keyboard.is_pressed('esc'):
                print('\n正在退出...')
                autoandroid.exit()
                break
            '''
            clickclass = autoInteract(globals())
            
            if clickclass:
                idle = False
                lastBusyTs = time.time()
            
            # 回归团
                if clickclass == 'mission_exit_trans':
                    lastMissionExitTs = time.time()
            
            
            elif idle and time.time()-lastAnnounceTs>1800:
                #if guildAnnounceEN(globals(), '回归自动机，点击邀请组队即可使用（）'):
                if worldAnnounceEN(globals(), '回归自动机，点击邀请组队即可使用（）'):
                    lastAnnounceTs = time.time()
                
            
            elif time.time()-lastBusyTs>180:
                
                if time.time()-lastExitPartyTs>180:
                    if exitParty(globals()):
                        lastExitPartyTs = time.time()
                        idle = True
                
            #print(f'\r采样帧率：{autoandroid.minicap.realfps:.2f}, 待机状态：{idle}  ', end='')
            print(f'\r待机状态：{idle}  ', end='')
            
            ti = time.time()
            time.sleep(0.1)
            
            
            
            
            
        
