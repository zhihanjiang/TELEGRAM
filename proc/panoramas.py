# _*_ coding: utf-8 _*_
__author__ = 'jzhizhi'

import urllib.request
import threading
from optparse import OptionParser
import sys
import re
import sqlite3
import math
import time

conn = sqlite3.connect("D:\\zhihan\\driving_behaviors_detection\\data\\point4.db")
c = conn.cursor()


c.execute('select lid, latitude, longitude,bearing_before,indexm,rowid as row_id,count from map_xm_13980_16000')
lid_list=c.fetchall()


path = "D:\\zhihan\\driving_behaviors_detection\\data\\xiamen_pano09_add2\\"       
#path = "pano/"
count=0
for row in lid_list: #每次一行
    num=int(row[6])
    if(num>=500 or num<300):
        continue
    row_id=row[5]
    count+=1
    if(count==12001):
        break
    lid=row[0]
    lat=row[1]
    lng=row[2]
    direction=round(float(row[3]))
    indexm=row[4]
    print(str(row_id)+" "+str(lid))
    heading=((direction+90)%360+270)%360
    name = path+str(lid)+"_"+str(lat)+"_"+str(lng)+"_"+str(indexm)+".jpg"
    url = "http://api.map.baidu.com/panorama/v2?ak=yourkey&width=1024&height=512&location="+str(lng)+","+str(lat)+"&fov=74&pitch=10&heading="+str(heading)+"&coordtype=wgs84ll"
    try:
        open_url = urllib.request.urlopen(url)
    except urllib.error.URLError:
        print(urllib.error.URLError)
        open_url = urllib.request.urlopen(url)
    f = open(name, 'wb')
    f.write(open_url.read())
    f.close()

conn.close()