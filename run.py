
cid = 'android0'

import time, keyboard

import utils.autoandroid3 as autoandroid

import hottaui

from motions.autointeract import autoInteract
from motions.exitparty import exitParty
from motions.announce import guildAnnounceEN, worldAnnounceEN

if __name__ == '__main__':

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
                if guildAnnounceEN(globals(), 'Self-service_Bot_Beta_:p'):
                    lastAnnounceTs = time.time()
                
            
            elif time.time()-lastBusyTs>180:
                
                if time.time()-lastExitPartyTs>180:
                    if exitParty(globals()):
                        lastExitPartyTs = time.time()
                        idle = True
                
            print(f'\r采样帧率：{autoandroid.minicap.realfps:.2f}, 待机状态：{idle}  ', end='')
            
            ti = time.time()
            time.sleep(0.1)
            
            
            
            
            
        
