# 数据序列化工具2
# pub,pri = rsa.newkeys(1024) 生成密钥

import json,base64,shelve,pickle,rsa
import zlib

Logout = print

__rsahead = "rsa+"
__defaulthead = "raw+"

def headcheck(s:str, head:str)->bool:
    # 检查字符串左边是否匹配head
    if len(s)>=len(head):
        return s[:len(head)]==head
    return False

def long_encrypt(msg:str, publickey:str)->str:
        msg = msg.encode('utf-8')
        length = len(msg)
        encrypt_length = 117
        if length < encrypt_length:
            return rsa.encrypt(msg, publickey)
        offset = 0
        res = []
        while length - offset > 0:
            if length - offset > encrypt_length:
                res.append(rsa.encrypt(msg[offset:offset + encrypt_length],publickey))
            else:
                res.append(rsa.encrypt(msg[offset:],publickey))
            offset += encrypt_length
        data = b''.join(res)
        return data.decode('utf-8')

def long_decrypt(msg:str, privatekey:str)->str:
    length = len(msg)
    decrypt_length = 128
    if length < decrypt_length:
        return rsa.decrypt(msg, privatekey)
    offset = 0
    res = []
    while length - offset > 0:
        if length - offset > default_length:
            res.append(rsa.decrypt(msg[offset:offset + default_length], privatekey))
        else:
            res.append(rsa.decrypt(msg[offset:],privatekey))
        offset += default_length
    return b''.join(res).decode('utf-8')

def py_websave_pack(obj:any, compressed:bool=True, rsa_public:str=None)->str:
    # 打包python对象
    bytesdata = zlib.compress(pickle.dumps(obj)) if compressed else pickle.dumps(objw)
    b64str = base64.encodebytes(bytesdata).decode("utf-8")
    if rsa_public==None:
        return __defaulthead + b64str
    else:
        regstr = '。' * (0 if len(b64str)>=200 else 200-len(b64str))
        print(len(regstr))
        return  __rsahead + long_encrypt(regstr + b64str, rsa_public)

def py_websave_unpack(data:str, compressed:bool=True, rsa_private:str=None)->any:
    # 解包python对象，必须预先import相关的类
    if headcheck(data, __defaulthead):
        b64str = data[len(__defaulthead):]
    elif headcheck(data, __rsahead) and rsa_private:
        b64str = rsa.decrypt(data[len(__rsahead):],rsa_private).lstrip(' ')
    else:
        Logout("无法解码：%s"%(data))
        return None
    bytesdata = base64.decodebytes(b64str.encode("utf-8"))
    pkldata = zlib.decompress(bytesdata) if compressed else bytesdata
    return pickle.loads(pkldata)
        
def web_data_pack(dat, compressed=True):
    # web 传输用标准数据打包
    if compressed:
        return base64.encodebytes(zlib.compress(json.dumps(dat).encode("utf-8"))).decode("utf-8")
    return base64.encodebytes(json.dumps(dat).encode("utf-8")).decode("utf-8")

def web_data_unpack(dat, compressed=True):
    # web 传输用标准数据解包
    if compressed:
        return json.loads(zlib.decompress(base64.decodebytes(dat.encode("utf-8"))))
    return json.loads(base64.decodebytes(dat.encode("utf-8")).decode("utf-8"))

