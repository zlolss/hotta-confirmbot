
import time

# interval[interval, lastts]
intervals = {'mission_bosstp_trans':[180,0]}


def autoInteract(_g):
    # 自动同意和开箱交互
    global intervals
    upt = _g['hottaui']
    #htm = _g['htm']
    imat = _g['imat']
    touch = _g['autoandroid'].touch
    
    
    clickifexists = ['msgbox_yes_trans',
                     'world_interact_trans',
                     'mission_death_reborn_trans',
                     'mission_bosstp_trans',
                     'world_invite_yes_trans',
                     'world_menu_exit_static',
                     'common_exit_trans',
                     'team_exit_flag']
    for classname in clickifexists:
        exists, yrect, score = upt.detectClass(classname, imat)
        interval = intervals.get(classname, None)
        if interval:
            isininterval = time.time()-interval[1]<interval[0]
        else:
            isininterval = False
        if exists:
            #htm.stop()
            touch.tap(*yrect[:2])
            if interval:
                interval[1] = time.time()
            time.sleep(5)
            return classname
            break
    
    
    if upt.existClass('mission_finish_title_trans', imat):
        exists, yrect, score = upt.detectClass('mission_exit_trans', imat)
        if exists:
            touch.tap(*yrect[:2])
        else:
            touch.tap(*upt.getClassCenter('mission_exit_trans'))
        return 'mission_exit_trans'
        
    '''
    exists, yrect, score = upt.detectClass('world_chat_setting_static', imat)
    if exists:
        exists, yrect, score = upt.detectClass('world_chat_exit_trans', imat)
        if exists:
            touch.tap(*yrect[:2])
        else:
            touch.tap(*upt.getClassCenter('world_chat_exit_trans'))
        return 'world_chat_exit_trans'
    '''        
            
    exists, yrect, score = upt.detectClass('common_clickexit_trans', imat)        
    if exists:
        touch.tap(*yrect[:2])
        time.sleep(0.1)
        touch.tap(*upt.getClassCenter('miacook_raisefood_static'))
        return 'common_clickexit_trans'
        

    if upt.existClass('origin_finish_trans', imat):
        exists, yrect, score = upt.detectClass('origin_finish_exit_trans', imat)
        if exists:
            touch.tap(*yrect[:2])
        else:
            touch.tap(*upt.getClassCenter('origin_finish_exit_trans'))
        return 'origin_finish_exit_trans'
    