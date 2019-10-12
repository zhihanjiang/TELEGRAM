# -*- coding: utf-8 -*-
import json
import urllib.request
import sqlite3
import math

conn = sqlite3.connect("D:\\zhihan\\driving_behaviors_detection\\data\\driving_violation.db")
c = conn.cursor()
c.execute('select lid,latitude,longitude from illegal_tn_lid_cd')
rows=c.fetchall()
for row in rows:
    npk_id=row[0]
    # if(int(npk_id)>13):
    #     break
    lat=row[1]
    lon=row[2]
    url='http://api.map.baidu.com/geoconv/v1/?coords='+str(lon)+','+str(lat)+'&from=1&to=5&ak=yourkey'
    try:
        open_url = urllib.request.urlopen(url)
    except urllib.error.URLError:
        print(urllib.error.URLError)
        open_url = urllib.request.urlopen(url)
    s=bytes.decode(open_url.read())
    res=json.loads(s)
    if(res["status"]==0):
       # print(res["result"])
        lon_bd=res["result"][0]["x"]
        lat_bd=res["result"][0]["y"]
        c.execute('update illegal_tn_lid_cd set lat_bd='+str(lat_bd)+' where lid='+str(npk_id))
        c.execute('update illegal_tn_lid_cd set lon_bd='+str(lon_bd)+' where lid='+str(npk_id))
        conn.commit()
conn.close()