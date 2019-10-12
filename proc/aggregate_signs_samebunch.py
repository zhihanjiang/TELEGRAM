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

conn = sqlite3.connect("D:\\zhihan\\traffic_signs_detection\\yolov3\\keras-yolo3\\signs.db")
#conn = sqlite3.connect("point.db")
c = conn.cursor()
c.execute('select id from bunch_type_chengdu')
bunch_list=c.fetchall()

for row in bunch_list: 
    bunch_id=row[0]
    print(bunch_id)
    c.execute('select *,rowid as row_id from signs_chengdu_all where bunch_type= '+str(bunch_id))
    signs=c.fetchall()
    max_conf=0;
    max_rowid=int(signs[0][15])
    for sign in signs:
        conf=float(sign[8])
        if(conf>=max_conf):
            max_rowid=sign[15]
            max_conf=conf
    c.execute('insert into signs_chengdu_all_selected select * from signs_chengdu_all where rowid='+str(max_rowid))
    conn.commit()

conn.close()