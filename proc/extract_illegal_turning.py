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

conn = sqlite3.connect("D:\\zhihan\\driving_behaviors_detection\\data\\turning.db")
c = conn.cursor()

c.execute('select lid from illegal_tn_lid_xm_add')
lid_list=c.fetchall()
for row in lid_list:
	lid=row[0]
	print(lid)
	c.execute('insert into illegal_turning_xiamen_add select * from turning_xiamen where lid='+str(lid))
	conn.commit()

conn.close()