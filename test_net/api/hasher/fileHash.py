from hashlib import md5

def GetMD5Code(filePath : str)->str:
    F = open(filePath,'rb')
    mder = md5()
    mder.update(F.read())
    return mder.hexdigest()

def MD5Check(filePath : str, md5Code : str)->bool:
    return GetMD5Code(filePath) == md5Code
