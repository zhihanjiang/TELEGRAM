# _*_ coding: utf-8 _*_
__author__ = 'jzhizhi'

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
import numpy as np
import math

def distance(lat1,lat2,lon1,lon2):
    R = 6371393
    a1 = lat1*math.pi/180
    a2 = lat2*math.pi/180
    delta_lat = (lat2-lat1)*math.pi/180
    delta_lon = (lon2-lon1)*math.pi/180
    theta = math.atan2(math.sin(delta_lon)*math.cos(a2),math.cos(a1)*math.sin(a2)-math.sin(a1)*math.cos(a2)*math.cos(delta_lon))
    a = math.sin(delta_lat/2)*math.sin(delta_lat/2)+math.cos(a1)*math.cos(a2)*math.sin(delta_lon/2)*math.sin(delta_lon/2)
    b = (theta*180/math.pi+360)%360
    c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    d = R*c
    return d

def dis(point1,point2):
    lat1=point1.lat
    lat2=point2.lat
    lon1=point1.lon
    lon2=point2.lon
    d=distance(lat1,lat2,lon1,lon2)
    return d


class point:
    def __init__(self,lid,bb,conf,lat,lon,bunch_type):
        self.lid=lid
        self.bb=bb
        self.conf=conf
        self.lat=lat
        self.lon=lon
        self.bunch_type=bunch_type
    def get_lat(self):
        return self.lat
    def get_lon(self):
        return self.lon
    def get_lid(self):
        return self.lid

def get_lon(lat,dis): #纬度相同，经度不同
    R = 6371393
    delta_lon = dis/(math.pi/180*R)*math.cos(lat*math.pi/180)
    return delta_lon

def merge(Syl,Syr,dmin,p1_inx,p2_inx,l,S):
    syll=[]
    syrr=[]
    for i in range(0,len(Syl)):
        if(S[Syl[i]].lon>l-get_lon(S[Syl[i]].lat,dmin)):
            syll.append(Syl[i])
    for i in range(0,len(Syr)):
        if(S[Syr[i]].lon<l+get_lon(S[Syr[i]].lat,dmin)):
            syrr.append(Syr[i])
    t=0
    for i in range(0,len(syll)):
        while(t<len(syrr)-1 and S[syrr[t]].lat<S[syll[i]].lat):
            t+=1
        for j in range(max(0,t-3),min(t+4,len(syrr))):
            d=dis(S[syll[i]],S[syrr[j]])
            if(d<dmin):
                dmin=d
                p1_inx=syll[i]
                p2_inx=syrr[j]
    return dmin,p1_inx,p2_inx


def divide_conquer(Sx,Sy,dmin,S):
    if(len(Sx)==1):
        return float('inf'),Sx[0],Sx[0]
    elif(len(Sx)==2):
        dmin=dis(S[Sx[0]],S[Sx[1]])
        return dmin,Sx[0],Sx[1]
    else:
        Sxl=[]
        Sxr=[]
        Syl=[]
        Syr=[]
        mid=int(len(Sx)/2)
        l=S[Sx[mid]].lon
        for i in range(0,len(Sx)):
            if(i<=mid):
                Sxl.append(Sx[i])
            else:
                Sxr.append(Sx[i])
        for i in range(0,len(Sy)):
            if(Sy[i] in Sxl):
                Syl.append(Sy[i])
            else:
                Syr.append(Sy[i])
    dl,pl1_inx,pl2_inx=divide_conquer(Sxl,Syl,dmin,S)
    dr,pr1_inx,pr2_inx=divide_conquer(Sxr,Syr,dmin,S)
    if(dl<dr):
        dmin=dl
        p1_inx=pl1_inx
        p2_inx=pl2_inx
    else:
        dmin=dr
        p1_inx=pr1_inx
        p2_inx=pr2_inx
    dmin,p1_inx,p2_inx=merge(Syl,Syr,dmin,p1_inx,p2_inx,l,S)
    return dmin,p1_inx,p2_inx

def Xsort(S):
    slon=[]
    for p in S:
        slon.append(p.lon)
    Sx=np.argsort(slon)
    return Sx

def Ysort(S):
    slat=[]
    for p in S:
        slat.append(p.lat)
    Sy=np.argsort(slat)
    return Sy

def find_closest(S):
    Sx=Xsort(S) #Sx中按lat从小到大存点对应在S中的index
    Sy=Ysort(S)
    # print(len(Sx))
    # print(len(Sy))
    dmin=float('inf')
    dmin,p1_inx,p2_inx=divide_conquer(Sx,Sy,dmin,S)
    return dmin,p1_inx,p2_inx


conn = sqlite3.connect("D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\signs.db")
c = conn.cursor()

tp='no_parking'

c.execute('select lid,latitude,longitude,type,confidence,bearing_before,bunch_type from signs_chengdu_all_selected where type=\''+tp+'\'')
lid_list=c.fetchall()
S=[]
dis_thre=5
for row in lid_list:
    lid=row[0]
    lat=row[1]
    lon=row[2]
   # tp=row[3]
    bb=row[5]
    bunch_type=row[6]
    conf=row[4]
    S.append(point(lid,bb,conf,lat,lon,bunch_type))
dmin,p1_inx,p2_inx=find_closest(S)
while(dmin<=dis_thre and len(S)>1):
    print(len(S))
    lid=S[p1_inx].lid
    bunch_type=S[p1_inx].bunch_type
    lat=(S[p1_inx].lat+S[p2_inx].lat)/2
    lon=(S[p1_inx].lon+S[p2_inx].lon)/2
    bb=(S[p1_inx].bb+S[p2_inx].bb)/2
    conf=(S[p1_inx].conf+S[p2_inx].conf)/2
    if(p2_inx>p1_inx):
        del S[p2_inx]
        del S[p1_inx]
    elif(p2_inx<p1_inx):
        del S[p1_inx]
        del S[p2_inx]
    S.append(point(lid,bb,conf,lat,lon,bunch_type))
    dmin,p1_inx,p2_inx=find_closest(S)
for p in S:
    conn.execute('insert into signs_chengdu_all_selected_cluster(lid,latitude,longitude,bearing_before,confidence,bunch_type,type) values(?,?,?,?,?,?,?)',(p.lid,p.lat,p.lon,p.bb,p.conf,p.bunch_type,tp))
    conn.commit()

conn.close()