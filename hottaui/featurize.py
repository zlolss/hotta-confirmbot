import cv2
import numpy as np

SIFTDetector = None

def calSIFT(gmat):
        # 计算sift特征点和算子
        # 输入：灰度图片矩阵
        # 输出：（特征点集，对应特征算子集）
    global SIFTDetector
        
    if SIFTDetector is None:
        SIFTDetector = cv2.SIFT_create()
            
    if gmat is None:
        return None
    kp, dst = SIFTDetector.detectAndCompute(gmat, None)
    h,w = gmat.shape[:2]
    kpn = np.array([p.pt for p in kp])
    if len(kpn)<=0:
        #print(f'没有提取到特征 shape:{gmat.shape}')
        return [],np.array([])
    kpn /= np.array((w,h))
    #kpn = [(p.pt[0]/w, p.pt[1]/h) for p in kp]
    return kpn, dst