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
import threading
import types
import os.path
from pathlib import Path
import shutil

global false, null, true

false = null = true = ""

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


header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
              AppleWebKit/537.36 (KHTML, like Gecko) \
              Chrome/35.0.1916.114 Safari/537.36',
              'Cookie': 'AspxAutoDetectCookieSupport=1'}
glock = threading.Lock()
pho_list = []
url_list = []
title_list = []

sameTitle = {}
scount = 0


def get_url():

    while True:
        glock.acquire()
        if len(url_list) == 0:
            print("Get photos: finished.")
            glock.release()
            
            break
        else:
            u = url_list.pop()
            count = 0
            title = title_list.pop()

            glock.release()


            glock.acquire()
            for phurl in u:

                picu = phurl['orign']
                #req = urllib.request.Request(url=picu, headers=header)
                #pic = urllib.request.urlopen(req, timeout=30).read()

                pho_list.append({'pic':picu, 'title':title+'_'+str(count)})
                count += 1
            #print(title+": get request successfully.")
            glock.release()
            


def download_pho():
   
    while True:
        glock.acquire()
        if len(pho_list) == 0:
            glock.release()
            print("This thread finished downloading.")
            if len(pho_list) == 0 and len(url_list) == 0:
                break
            continue
        else:
            pic = pho_list.pop()
            glock.release()
            imgfname = pic['title'] 

            path = "./Photos/"+imgfname
            requestImg(pic['pic'], path)
            #urllib.request.urlretrieve(pic['pic'], filename=path)
            print(pic['title']+": download successfully.")
            #with open("./Photos/"+imgfname, "wb") as f:            
                #f.write(pic['pic'])



def requestImg(url, path, num_retries=3):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
              AppleWebKit/537.36 (KHTML, like Gecko) \
              Chrome/35.0.1916.114 Safari/537.36',
              'Cookie': 'AspxAutoDetectCookieSupport=1'}

    req = urllib.request.Request(url=url, headers=header)
    try:
        response = urllib.request.urlopen(req, timeout=10)
        conte = response.read()
        imgfname = path
        imgtype = imghdr.what("", conte)
        #print(imgtype)
        imgfname += '.'+imgtype
        with open(imgfname, "wb") as f:
            
            f.write(conte)
            response.close()
        
    
    except Exception as e:
        print(e)





for item in items:
    itemType = item.getElementsByTagName("type")[0]
    #print(itemType.nodeName, ":", itemType.childNodes[0].data)
    if itemType.childNodes[0].data != "Photo":
        continue
    i += 1


## get all messages

    titleText = ''

    publishTime = item.getElementsByTagName("publishTime")[0].childNodes[0].data
    publishTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(int(publishTime)/1000)))
    
    titleText = "插图_"+publishTime
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
    titleText = titleText.replace('', '')
    
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
    #print(type(item.getElementsByTagName("caption")[0]))
    #print(i)
    if item.getElementsByTagName("caption") == [] or item.getElementsByTagName("caption")[0].childNodes == []:
        content = ''
    else:
        content = item.getElementsByTagName("caption")[0].childNodes[0].data
    #print(content)
    content = content.replace('<p>', '')
    content = content.replace('</p>', '')
    content = content.replace('<br />', '\r\n')
    content = content.replace('', '')

    linkSrc = r'href="(.*?)"'
    linkSrc = re.findall(linkSrc, content)
    #iS2 = r'<img src=(.*?)smallsrc='
    #imgSrc = imgSrc + re.findall(iS2, content)
    #for j in range(0, len(imgSrc)):
    #    imgSrc[j] = imgSrc[j].replace('"', '')
    #    imgSrc[j] = imgSrc[j].replace(' ', '')

    content = re.compile(r'<[^>]+>', re.S).sub('', content)

    photos = item.getElementsByTagName("photoLinks")[0].childNodes[0].data
    photos = eval(photos)
    #if i == 1:
    #    print(photos)


    title_list.append(titleText)
    url_list.append(photos)

    if not os.path.exists('Photos'):
        os.mkdir('Photos')
    else:
        shutil.rmtree('Photos')
        os.mkdir('Photos')



    #if i == 1:
    #    print(content)
    
    cList = item.getElementsByTagName("comment")
    comments = []
    for comm in cList:
        pubid = comm.getElementsByTagName("publisherUserId")[0].childNodes[0].data
        pubnick = comm.getElementsByTagName("publisherNick")[0].childNodes[0].data
        comcon = comm.getElementsByTagName("content")[0].childNodes[0].data
        comtime = comm.getElementsByTagName("publishTime")[0].childNodes[0].data
        repid = comm.getElementsByTagName("replyToUserId")[0].childNodes[0].data
        comments.append({"pubid":pubid, "pubnick":pubnick, "comcon":comcon, "comtime":comtime, "repid":repid})

## save as txt


    with open("./Photos/"+titleText+".txt", "w", encoding="utf-8") as f:
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


    
def main():

    for xx in range(5):
        product = threading.Thread(target=get_url)
        product.start()
    for xx in range(6):
        consumer = threading.Thread(target=download_pho)
        consumer.start()


if __name__ == '__main__':
    main()
