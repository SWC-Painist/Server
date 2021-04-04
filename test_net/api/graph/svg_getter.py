from selenium import webdriver

option = webdriver.ChromeOptions()
option.add_argument('--headless')
#将下面的executable_path改为服务器上chrome的driver的地址
chrome_driver = webdriver.Chrome(executable_path=r"/home/painist/webdriver/chromedriver",options=option)

def getSVGStr(file_path:str) -> str:
    global chrome_driver
    chrome_driver.get(r"file://"+file_path)
    svg_text = chrome_driver.find_element_by_tag_name("SVG").get_attribute("outerHTML")
    svg_text = svg_text[0:5] + "xmlns=\"http://www.w3.org/2000/svg\" " + svg_text[5:]
    return svg_text

if __name__ == '__main__':
    svg_text = getSVGStr(r'/home/painist/Test_Network/test_net/html/trans1.txt.html')
    with open('./data/out_1.svg','wt',encoding='utf-8') as f:
        f.write(svg_text)