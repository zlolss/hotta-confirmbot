import time
from utils.loghelper import Log
import cv2
from utils.visualizehelper import *

def guildAnnounceEN(_g, txt):
    upt = _g['hottaui']
    imat = _g['imat']
    touch = _g['autoandroid'].touch
    inputchar = _g['autoandroid'].inputchar
    
    Log('尝试冒泡')
    exists, yrect, score = upt.detectClass('world_chat_trans', imat)
    if exists:
        ''' # debug
        print(yrect[:2])
        print(upt.getClassCenter('world_chat_trans'))
        imat = drawyrect(imat, yrect)
        cv2.imwrite('debug.png', imat)
        time.sleep(100)
        ''' #debug end
        touch.tap(*yrect[:2])
        return False
    
    exists, yrect, score = upt.detectClass('world_chat_setting_static', imat)
    #Log(f'{exists}, {yrect}')
    if exists:

        touch.tap(*upt.getClassCenter('world_chat_guild_rct'))
        time.sleep(1)
        
        touch.tap(*upt.getClassCenter('world_chat_input_var'))
        time.sleep(1)
        
        inputchar(txt)
        time.sleep(1)
        
        touch.tap(*upt.getClassCenter('world_chat_send_trans'))
        time.sleep(1)
        
        exists, yrect, score = upt.detectClass('world_chat_exit_trans', imat)
        if exists:
            touch.tap(*yrect[:2])
        else:
            touch.tap(*upt.getClassCenter('world_chat_exit_trans'))
        time.sleep(1)
        
        return True # 流程完成
    
    return False
    
    
def worldAnnounceEN(_g, txt):
    upt = _g['hottaui']
    imat = _g['imat']
    touch = _g['autoandroid'].touch
    inputchar = _g['autoandroid'].inputchar
    
    Log('尝试冒泡')
    exists, yrect, score = upt.detectClass('world_chat_trans', imat)
    if exists:
        touch.tap(*yrect[:2])
        return False
    
    exists, yrect, score = upt.detectClass('world_chat_setting_static', imat)
    #Log(f'{exists}, {yrect}')
    if exists:

        touch.tap(*upt.getClassCenter('world_chat_world_bflag'))
        time.sleep(1)
        
        touch.tap(*upt.getClassCenter('world_chat_input_var'))
        time.sleep(1)
        
        inputchar(txt)
        time.sleep(1)
        
        touch.tap(*upt.getClassCenter('world_chat_send_trans'))
        time.sleep(1)
        
        exists, yrect, score = upt.detectClass('world_chat_exit_trans', imat)
        if exists:
            touch.tap(*yrect[:2])
        else:
            touch.tap(*upt.getClassCenter('world_chat_exit_trans'))
        time.sleep(1)
        
        return True # 流程完成
    
    return False