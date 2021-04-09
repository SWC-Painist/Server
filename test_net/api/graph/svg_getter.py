from selenium import webdriver
from skimage import io
import cairosvg
import os

option = webdriver.ChromeOptions()
option.add_argument('--headless')
#将下面的executable_path改为服务器上chrome的driver的地址
chrome_driver = webdriver.Chrome(executable_path=r"/home/painist/webdriver/chromedriver",options=option)
print("Chrome driver ready")

def cut(path : str) :
    img = io.imread(path)
    img2=img.sum(axis=2)
    (row,col)=img2.shape
    tempr0=0
    tempr1=0

    for r in range(0,row):
        if img2.sum(axis=1)[r]!=0:
            tempr0=r
            break

    for r in range(row-1,0,-1):
        if img2.sum(axis=1)[r]!=0:
            tempr1=r
            break

    new_img=img[tempr0:tempr1+1,:,0:4]
    io.imsave(path,new_img)


def getSVGStr(file_path:str) -> str:
    global chrome_driver
    chrome_driver.get(r"file://"+file_path)
    svg_text = chrome_driver.find_element_by_tag_name("SVG").get_attribute("outerHTML")
    svg_text = svg_text[0:5] + "xmlns=\"http://www.w3.org/2000/svg\" " + svg_text[5:]
    return svg_text

def SaveAsPng(file_path : str) -> str:
    print("Start process picture")
    file_name_no_root = file_path.split('/')[-1]
    save_path = os.path.join(os.getcwd(),'media/SVG',file_name_no_root)
    with open(save_path+".svg","wt", encoding='utf-8') as f:
        f.write(getSVGStr(file_path))
    cairosvg.svg2png(url=save_path+".svg",write_to=save_path+".png",scale=2.0)
    cut(save_path+".png")
    return "SVG/" + file_name_no_root + ".png"

if __name__ == "__main__":
    SaveAsPng(r"/home/painist/Test_Network/test_net/html/trans1.txt.html.res.html")