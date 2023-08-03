import numpy as np
from utils.loghelper import Log
import cv2

def resizeImgToHeight(imat, height = 720):
    h, w = imat.shape[:2]
    p = height / h
    if p!=1.:
        return cv2.resize(imat , dsize=None, fx = p, fy=p)
    return imat
        
        
def preprocessingSIFT(imat, **params):
    gmat = cv2.cvtColor(imat, cv2.COLOR_RGB2GRAY)
    gmat = resizeImgToHeight(gmat, params.get('height', 720))
    return gmat
    

def enlargeYRect(yrect, flex=(.05,.01)):
    enlargedYRect = yrectFixOutOfRange([*yrect[:2], yrect[2]+flex[0], yrect[3]+flex[1]])
    return enlargedYRect


def yrect2rect(yrect, wh):
        # yolo矩形区域(cxp,cyp,wp,hp)->两点矩形区域(x0,y0,x1,y1)
    if type(wh) is not np.ndarray:
        wh = np.array(wh)
    if type(yrect) is not np.ndarray:
        yrect = np.array(yrect)
    rcp = yrect[:2]*wh
    hrwh = yrect[2:]*wh/2
    rect = np.hstack(((rcp-hrwh),(rcp+hrwh))).astype(np.int32)
    return rect
        
        
def rectFixOutOfRange(rect, wh):
    # 修剪超出图像区域的rect
    if type(wh) is not np.ndarray:
        wh = np.array(wh)
    if type(rect) is not np.ndarray:
        rect = np.array(yrect)
    lt = np.max((rect[:2], np.zeros((2,))), axis=0)
    rb = np.min((rect[2:], wh), axis=0)
    fixedRect = np.hstack((lt,rb))
    return fixedRect


def yrectFixOutOfRange(yrect):
    if type(yrect) is not np.ndarray:
        yrect = np.array(yrect)
    lt = np.max((yrect[:2]-yrect[2:]/2, np.zeros((2,))), axis=0)
    rb = np.min((yrect[:2]+yrect[2:]/2, np.ones((2,))), axis=0)
    ct = (lt+rb)/2
    wh = rb-lt
    fixedYRect = np.hstack((ct,wh))
    #Log(fixedYRect)
    return fixedYRect
    

def cutImat(imat, cut_rect):
    if len(imat.shape)==3:
        return imat[cut_rect[1]:cut_rect[3], cut_rect[0]:cut_rect[2], :]
    elif len(imat.shape)==2:
        return imat[cut_rect[1]:cut_rect[3], cut_rect[0]:cut_rect[2]]
    Log(f'ycutImg with wrong shape:{imat.shape}')
    return None
    
    
def cutImatYRect(imat, yrect):
    #h, w = imat[:2]
    yrect = yrectFixOutOfRange(yrect)
    cut_rect = yrect2rect(yrect, imat.shape[1::-1] )
    return cutImat(imat, cut_rect)
    

def localYPoint2Global(ypt, lyrect):
    # 坐标转换，局部比例坐标到全局比例坐标
    if type(ypt) is not np.ndarray:
        ypt = np.array(ypt)
    if type(lyrect) is not np.ndarray:
        lyrect = np.array(lyrect)
    return (ypt-0.5)*lyrect[2:]+lyrect[:2]
    #return (pt[0]-0.5)*lyrect[2]+lyrect[0], (pt[1]-0.5)*lyrect[3]+lyrect[1]