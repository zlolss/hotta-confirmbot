import time
from utils.loghelper import Log


def exitParty(_g):
    upt = _g['hottaui']
    imat = _g['imat']
    touch = _g['autoandroid'].touch
    Log('尝试退队')
    exists, yrect, score = upt.detectClass('world_team_getout_trans', imat)
    if exists:
        touch.tap(*yrect[:2])
        return True
        
    if upt.existClass('world_team_teamcreate_trans', imat):
        return True
        
    exists, yrect, score = upt.detectClass('world_team_team_trans', imat)
    if exists:
        touch.tap(*yrect[:2])
        return False
    elif upt.existClass('world_chat_trans', imat):
        yrect = upt.getClassCenter('world_team_team_trans')
        touch.tap(*yrect)
        return False
        
        
    exists, yrect, score = upt.detectClass('team_myteam_getout_static', imat)
    if exists:
        touch.tap(*yrect[:2])
        return True
        
    return False
    