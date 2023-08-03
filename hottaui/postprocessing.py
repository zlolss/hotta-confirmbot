import numpy as np

def fixYRect(yrect, matchpoints):
    # matchpoints: [(spoint, dpoint)]
    if len(matchpoints)<2:
        return yrect
    po0, pd0 = matchpoints[0]
    po1, pd1 = matchpoints[1]
    oyr = yrect
    #po0 = kps0[judged[0].queryIdx]
    #pd0 = kps1[judged[0].trainIdx]
    #po1 = kps0[judged[1].queryIdx]
    #pd1 = kps1[judged[1].trainIdx]
    if abs(po1[0]-po0[0])<=0.01 or abs(pd1[0]-pd0[0])<=0.01:
        fx = 1.
    else:
        fx = abs((pd1[0]-pd0[0]) / (po1[0]-po0[0]))
    if abs(po1[1]-po0[1]) <= 0.01 or abs(pd1[1]-pd0[1])<=0.01:
        fy = 1.
    else:
        fy = abs((pd1[1]-pd0[1]) / (po1[1]-po0[1]))
    #oyr = ptn[1]
    yct = [pd0[0]+ (oyr[0]-po0[0])*fx, pd0[1]+ (oyr[1]-po0[1])*fy]
    ywh = [oyr[2]*fx, oyr[3]*fy]
    yr = yct+ywh
    return yr