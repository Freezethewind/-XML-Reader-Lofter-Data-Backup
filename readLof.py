# -*- coding: UTF-8 -*-

from tkinter.filedialog import *
from tkinter import *
from xml.dom.minidom import parse
import xml.dom.minidom
import os
import datetime, time
import re
import urllib
import urllib.request
import imghdr



rootwin = Tk()
rootwin.withdraw()

default_dir = r"file_path"
file_path = askopenfilename(title=u'choose xml file', initialdir=(os.path.expanduser(default_dir)))

#print(file_path)

DOMTree = xml.dom.minidom.parse(file_path)

rootNode = DOMTree.documentElement
#print(rootNode.nodeName)

items = rootNode.getElementsByTagName("PostItem")

i = 0


def requestImg(url, i, title, num_retries=3):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
              AppleWebKit/537.36 (KHTML, like Gecko) \
              Chrome/35.0.1916.114 Safari/537.36',
              'Cookie': 'AspxAutoDetectCookieSupport=1'}

    req = urllib.request.Request(url=url, headers=header)
    try:
        response = urllib.request.urlopen(req, timeout=5)
        imgfname = title + '-' + str(i)
        conte = response.read()
        imgtype = imghdr.what("", conte)
        #print(imgtype)
        imgfname += '.'+imgtype
        with open("./Images/"+imgfname, "wb") as f:
            
            f.write(conte)
            response.close()
        
    
    except Exception as e:
        print(e)




for item in items:
    itemType = item.getElementsByTagName("type")[0]
    #print(itemType.nodeName, ":", itemType.childNodes[0].data)
    if itemType.childNodes[0].data != "Text":
        continue
    i += 1

## get all messages

    title = item.getElementsByTagName("title")[0]
    titleText = ''
    if title.childNodes == []:
        titleText = ''
    else:
        titleText = title.childNodes[0].data    #.replace('','')

    
    publishTime = item.getElementsByTagName("publishTime")[0].childNodes[0].data
    publishTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(int(publishTime)/1000)))
    if titleText == '':
        titleText = "无题_"+publishTime
        titleText = titleText.replace(' ', '_')
        
    titleText = titleText.replace('/','-')
    titleText = titleText.replace('\\', '-')
    titleText = titleText.replace('|', '-')
    titleText = titleText.replace(':', '-')    
    titleText = titleText.replace('"', '-')
    titleText = titleText.replace('*', '-')
    titleText = titleText.replace('?', '-')
    titleText = titleText.replace('<', '-')
    titleText = titleText.replace('>', '-')
    
    modifyTime = publishTime
    if item.getElementsByTagName("modifyTime") == []:
        modifyTime = publishTime
    else:
        modifyTime = item.getElementsByTagName("modifyTime")[0].childNodes[0].data
        modifyTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(int(modifyTime)/1000)))
    tag = []
    if item.getElementsByTagName("tag") == []:
        tag = []
    else:
        tag = item.getElementsByTagName("tag")[0]
        if tag.childNodes == []:
            tag = []
        else:
            tag = tag.childNodes[0].data.split(',')
    #print(tag)
    content = item.getElementsByTagName("content")[0].childNodes[0].data
    content = content.replace('<p>', '')
    content = content.replace('</p>', '')
    content = content.replace('<br />', '\r\n')


    linkSrc = r'href="(.*?)"'
    linkSrc = re.findall(linkSrc, content)

    imgSrc = r'<img src="(.*?)"'
    imgSrc = re.findall(imgSrc, content)
    #iS2 = r'<img src=(.*?)smallsrc='
    #imgSrc = imgSrc + re.findall(iS2, content)
    #for j in range(0, len(imgSrc)):
    #    imgSrc[j] = imgSrc[j].replace('"', '')
    #    imgSrc[j] = imgSrc[j].replace(' ', '')

    content = re.compile(r'<[^>]+>', re.S).sub('', content)


    #if i == 1:
    #    print(content)
    cList = item.getElementsByTagName("commentList")
    comments = []
    for comm in cList:
        pubid = comm.getElementsByTagName("publisherUserId")[0].childNodes[0].data
        pubnick = comm.getElementsByTagName("publisherNick")[0].childNodes[0].data
        comcon = comm.getElementsByTagName("content")[0].childNodes[0].data
        comtime = comm.getElementsByTagName("publishTime")[0].childNodes[0].data
        repid = comm.getElementsByTagName("replyToUserId")[0].childNodes[0].data
        comments.append({"pubid":pubid, "pubnick":pubnick, "comcon":comcon, "comtime":comtime, "repid":repid})

## save as txt and images

    if not os.path.exists('Articles'):
        os.mkdir('Articles')
    if not os.path.exists('Images'):
        os.mkdir('Images')

    with open("./Articles/"+titleText+".txt", "w", encoding="utf-8") as f:
        f.write(titleText+'\n\n')
        f.write("发表时间："+publishTime+'\n')
        f.write("修改时间："+modifyTime+'\n\n')
        f.write("Tag：")
        if tag != []:
            for t in range(0, len(tag)-1):
                f.write(tag[t]+', ')
            f.write(tag[len(tag)-1]+'\n\n\n')
        else:
            f.write('\n\n\n')
        f.writelines(content)

        f.write("\n\n插入链接：\n")
        for lk in linkSrc:
            f.write(lk+'\n')

        f.write('\n\n\n评论：\n\n')
        for comm in comments:
            f.write("发表人："+comm["pubnick"]+'  '+"UserId："+comm["pubid"]+'  '+"回复时间："+comm["comtime"]+'\n')
            f.write("回复给："+comm["repid"]+'\n')
            f.writelines(comm["comcon"]+'\n\n')

    for img in range(0, len(imgSrc)):
        requestImg(imgSrc[img], img, titleText)
    
    print(titleText+": finished.")

print("Complete!")
