# 输入图像矩阵imat，彩色默认BGR模式

from . import const, preprocessing, postprocessing, featurize, matcher
import pickle
from utils.loghelper import Log

def load():
    with open(const.patternPath, 'rb') as fp:
        ld = pickle.load(fp)
        return ld['innerheight'], ld['classes']
        
innerHeight , classes = load()


def matchClassAndFixYrect( imat, classname, match_yrect=(0.5,0.5,1.,1.)):
    
    classitems = classes.get(classname, None)
    if not(classitems):
        return False, f'no classname: {classname}'
        
    for classitem in classitems:
        #classYRect, classSIFTFeature, classMatchParams = classitem
        exists, yrect = _matchClassAndFixYrect( imat, classitem, match_yrect)
        if exists:
            return exists, yrect
    return False, f'no matches {classname}'
    

def _matchClassAndFixYrect( imat, classitem, match_yrect=[0.5,0.5,1.,1.]):
    classYRect, classSIFTFeature, classMatchParams = classitem
    gmat = preprocessing.preprocessingSIFT(imat, height=innerHeight)
    mgmat = preprocessing.cutImatYRect(gmat, match_yrect)
    #Log(match_yrect)
    mkps, mdets = featurize.calSIFT(mgmat)
    mkps = [preprocessing.localYPoint2Global(pt, match_yrect) for pt in mkps]
    
    matchPoints, score = matcher.kpdetsMatchPoints(classSIFTFeature, (mkps, mdets), classMatchParams)
    if not matchPoints:
        return False, score
    
    yrect = postprocessing.fixYRect(classYRect, matchPoints)
    
    return True, yrect
    
    
def matchClassAndFixYrectFlex(classname, imat, flex=(.1,.01)):
        # 扩大区域匹配类别
        # 返回：是否存在，第一个匹配到的模板区域yrect

    classitems = classes.get(classname, None)
    if not(classitems):
        return False, f'no classname: {classname}'
    
    
    for classitem in classitems:
        classYRect, classSIFTFeature, classMatchParams = classitem
        matchYRect = preprocessing.enlargeYRect(classYRect, flex)
        exists, yrect = _matchClassAndFixYrect( imat, classitem, matchYRect)
        if exists:
            return exists, yrect
            
    return False, f'no matches {classname} in {matchYRect} based {classYRect} with score {yrect}'


def detectAllClassesAndFixYrect(imat, classflex = (.1,.01)):
    # return detected:[(classname, fixedyrect)]
    detected = []
    gmat = preprocessing.preprocessingSIFT(imat, height=innerHeight)
    fkpdets = featurize.calSIFT(gmat)
    #mkpdets = matcher.kpdetsYRectFilter(fkpdets, match_yrect)
    for classname, classitems in classes.items():
        ctype = classname.split('_')[-1]
        if ctype in ['rct', 'var']:
            continue
        for classitem in classitems:
            classYRect, classSIFTFeature, classMatchParams = classitem
            
            if classname not in ['ptn', 'tptn']:
                matchYRect = preprocessing.enlargeYRect(classYRect, classflex)
                mkpdets = matcher.kpdetsYRectFilter(fkpdets, matchYRect)
            else:
                mkpdets = fkpdets
                
            matchPoints, score = matcher.kpdetsMatchPoints(classSIFTFeature, mkpdets, classMatchParams)
            if not matchPoints:
                continue
            yrect = postprocessing.fixYRect(classYRect, matchPoints)
            detected.append((classname, yrect))
            break
            
    return detected    
    
    
def getClassYRect0(classname):
    classitems =  classes.get(classname, None)
    if not classitems:
        return None
    return classitems[0][0]
    
    
## old version 
def detectClass(classname, imat):
    return *matchClassAndFixYrectFlex(classname, imat), 0

def existClass(classname, imat):
    return matchClassAndFixYrectFlex(classname, imat)[0]
    
def getClassCenter(classname):
    return getClassYRect0(classname)[:2]
## ------------------------------