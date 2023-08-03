import cv2
import numpy as np


def kpdetsMatchPoints(skpdets, mkpdets, match_params=(0.5,1000)):
    skps, sdets = skpdets
    mkps, mdets = mkpdets
    
    if len(sdets)<=0 or len(mdets)<=0:
        return None, 9999
    #print(sdets.shape)
    #print(mdets.shape)
    matches = calBFMatch(sdets , mdets)
    cutlen = int(len(matches)*match_params[0])
    judged = matches[:cutlen if cutlen>3 else 3]
    
    if len(judged)<2:
        return None, 9999
        
    score = np.mean([x.distance  for x in judged])    
    exists = score<match_params[1]
    
    if not exists:
        return None, score
    matchPoints = [(skps[judged[i].queryIdx], mkps[judged[i].trainIdx]) for i in range(len(judged))]
    return matchPoints, score

BFMatcher = None

def calBFMatch(sdets, mdets):
    global BFMatcher
    
    if BFMatcher is None:
        BFMatcher = cv2.BFMatcher(cv2.NORM_L1, crossCheck=False)
        
    matches = BFMatcher.match(sdets, mdets)
    matches = sorted(matches, key = lambda x:x.distance)
    return matches
    

def kpdetsYRectFilter(kpdets, yrect):
    def pointinyrect(pt, yrp):
        return pt[0]<=yrp[2] and pt[0]>=yrp[0] and pt[1]<=yrp[3] and pt[1]>=yrp[1]
    
    kps, dets = kpdets
    yrp = [yrect[0]-yrect[2]/2, yrect[1]-yrect[3]/2, yrect[0]+yrect[2]/2, yrect[1]+yrect[3]/2]
        
    #if debug:
    #    print(yrp)
    ids = [pointinyrect(p, yrp) for p in kps]
    return kps[ids], dets[ids]