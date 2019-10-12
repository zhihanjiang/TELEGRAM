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
import math
import time
import numpy as np

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

conn = sqlite3.connect("D:\\zhihan\\driving_behaviors_detection\\data\\driving_violation.db")
c_pk = conn.cursor()
c_pk.execute('select longitude,latitude,confidence,npk_id,road_id from parking_segments_chengdu where road_id is not null')
npks=c_pk.fetchall()

conn_pkbeh = sqlite3.connect("D:\\zhihan\\driving_behaviors_detection\\data\\driving_violation.db")
c_pkbeh = conn_pkbeh.cursor()

conn_ipk = sqlite3.connect("D:\\zhihan\\driving_behaviors_detection\\data\\driving_violation.db")
c_ipk = conn_ipk.cursor()

for npk in npks:
	lng=npk[0]
	lat=npk[1]
	conf=npk[2]
	npk_id=npk[3]
	rid=npk[4]
	c_pkbeh.execute('select longitude,latitude,pk_id,st_ts,ed_ts from parking_chengdu_180 where road_id='+str(rid))
	pkbehs=c_pkbeh.fetchall()
	for pkbeh in pkbehs:
		lng1=pkbeh[0]
		lat1=pkbeh[1]
		pk_id=pkbeh[2]
		st_ts=pkbeh[3]
		ed_ts=pkbeh[4]
		d=distance(lat,lat1,lng,lng1)
		#print(d)
		if(d<=200):
			#print("insert")
			sql = '''insert into illegal_parking_chengdu(npk_id,lat1,lng1,pk_id,lat2,lng2,st_ts,ed_ts,confidence,road_id ) values (?,?,?,?,?,?,?,?,?,?)'''
			para = (npk_id,lat,lng,pk_id,lat1,lng1,st_ts,ed_ts,conf,rid)
			c_ipk.execute(sql,para)
			conn_ipk.commit()

conn.close()