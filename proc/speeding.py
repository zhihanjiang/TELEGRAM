# _*_ coding: utf-8 _*_

import urllib.request
import threading
from optparse import OptionParser
#from bs4 import BeautifulSoup
import sys
import re
#import urlparse
#import Queue
#import hashlib
import sqlite3
import math
import json

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率

#f=open('test.txt','w')
def wgs84togcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]

def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
        0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False

def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
        0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

conn = sqlite3.connect("/mnt/d/Zhihan/driving_behaviors_detection/data/info.db")
c = conn.cursor()

c.execute('select pid,longitude,latitude from location_xiamen')
rows=c.fetchall()
index=0

for row in rows:
    print(index)
    index=index+1
    if(index<2196):
        continue
    pid=row[0]
    timestamp="1,2,3"
    lng=row[1]
    lat=row[2]
    [lng,lat]=wgs84togcj02(lng,lat)
    locations=str(lng)+","+str(lat)+"|"+str(lng-0.00001)+","+str(lat-0.00001)+"|"+str(lng-0.00002)+","+str(lat-0.00002)
    direction="1,1,1"
    speed="1,1,1"
    url = "https://restapi.amap.com/v3/autograsp?carid=1&time="+timestamp+"&locations="+locations+"&direction="+direction+"&speed="+speed+"&output=json&key=yourkey"
    # f.write(url)
    # f.close()
    try:
        open_url = urllib.request.urlopen(url)
    except urllib.error.URLError:
        print(urllib.error.URLError)
        open_url = urllib.request.urlopen(url)
    #data = json.dumps(str(open_url.read()))
    s=bytes.decode(open_url.read())
    #print(s)
    data=json.loads(s)
    print(data)
    if len(data["roads"])==0:
        continue
    roadname=data["roads"][0]["roadname"]
    roadlevel=data["roads"][0]["roadlevel"]
    maxspeed=data["roads"][0]["maxspeed"]
    # print(roadname)
    if(isinstance(maxspeed,str)==False):
        continue
    sql3='update location_xiamen set speed='+ maxspeed+' where pid='+str(pid)
    cursor=c.execute(sql3)
    if(isinstance(roadname,str)==True):
        sql1='update location_xiamen set roadname=\''+roadname+'\' where pid='+str(pid)
        cursor=c.execute(sql1)
    if(isinstance(roadlevel,str)==False):
        continue
    sql2='update location_xiamen set level=\''+ roadlevel+'\' where pid='+str(pid)
    cursor=c.execute(sql2)
    
    conn.commit()
conn.close()