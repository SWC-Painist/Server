from skimage import io

def getColorPosition(path : str, color : str)-> int:
    r,g,b = int(color[1:3],16),int(color[3:5],16),int(color[5:7],16)
    img = io.imread(path)
    ht,wd,dp = img.shape
    for h in range(ht):
        for w in range(wd):
            if [img[h][w][0],img[h][w][1],img[h][w][2]] == [r,g,b]:
                return w
    return -1