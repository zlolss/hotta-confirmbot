from PIL import Image
import cv2

def imshow(imatbgr):
    if len(imatbgr.shape)==3:
        imat = cv2.cvtColor(imatbgr, cv2.COLOR_BGR2RGB)
    else:
        imat = imatbgr
    img = Image.fromarray(imat)
    display(img)



def drawrect(imat, rect, color=(0,0,255)):
    return cv2.rectangle(imat, rect[:2], rect[2:], color)
    
    
def drawyrect(imat, lmrect, color=(0,0,255)):
    h,w,c = imat.shape
    cp = [w*lmrect[0], h*lmrect[1]]
    wh = [w*lmrect[2], h*lmrect[3]]
    rect = [(int(cp[0]-wh[0]/2), int(cp[1]-wh[1]/2)), (int(cp[0]+wh[0]/2), int(cp[1]+wh[1]/2))]   
    result = cv2.rectangle(imat, *rect, color)
    return result
    
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