var util = require('util');
var os = require('os');
var osrm = require('osrm');
var database = require('better-sqlite3');
var moment = require('moment');
var dateformat = require('dateformat');
var time = require('node-tictoc');
var fs = require('fs');



var x_PI = 3.14159265358979324 * 3000.0 / 180.0;
var PI = 3.1415926535897932384626;
var a = 6378245.0;
var ee = 0.00669342162296594323;

data_layer = {};
data_layer.database = {};
data_layer.database.taxi = new database('/mnt/d/zhihan/driving_behaviors_detection/data/temp/chengdu_11.db');
//data_layer.database.turn_by_turn = new database('/mnt/d/zhihan/Data/conf/behavior.db');
var query = 'SELECT traj_id FROM did_oid';
var stmt = data_layer.database.taxi.prepare(query);
data_layer.traj = stmt.all();



for(var i=4956748;i<data_layer.traj.length;++i){
    var traj_id = data_layer.traj[i].traj_id;
    util.log(traj_id);
    query = 'SELECT * from parking where traj_id=?';
    stmt = data_layer.database.taxi.prepare(query);
    data_layer.gps = stmt.all(traj_id);
    var index=0;
    var info=new Array();
    //const insert = data_layer.database.taxi.prepare('INSERT INTO gps_wgs84(traj_id,timestamp,longitude,latitude,oid,did) VALUES(@traj_id,@timestamp,@longitude,@latitude,@oid,@did)');
    const insert = data_layer.database.taxi.prepare('INSERT INTO parking_wgs84(traj_id,st_ts,ed_ts,longitude,latitude) VALUES(@traj_id,@st_ts,@ed_ts,@longitude,@latitude)');
    for(var j=0;j<data_layer.gps.length;++j){
        [lng,lat]=gcj02towgs84(data_layer.gps[j].longitude, data_layer.gps[j].latitude);
        info[index++]={traj_id:traj_id,st_ts:data_layer.gps[j].st_ts,ed_ts:data_layer.gps[j].ed_ts,longitude:lng,latitude:lat};
    } 
    if(index>0){
        const insertMany=data_layer.database.taxi.transaction((cats)=>{
            for (const cat of cats) insert.run(cat);
        });
        insertMany(info);
        util.log("done.");
    }
}


function gcj02towgs84(lng, lat) {
  //util.log(lng);
    if (out_of_china(lng, lat)) {
        return [lng, lat];
    }
    else {
        var dlat = transformlat(lng - 105.0, lat - 35.0);
        var dlng = transformlng(lng - 105.0, lat - 35.0);
        var radlat = lat / 180.0 * PI;
        var magic = Math.sin(radlat);
        magic = 1 - ee * magic * magic;
        var sqrtmagic = Math.sqrt(magic);
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI);
        dlng = (dlng * 180.0) / (a / sqrtmagic * Math.cos(radlat) * PI);
        mglat = lat + dlat;
        mglng = lng + dlng;
      //  util.log([lng * 2 - mglng, lat * 2 - mglat]);
        return [lng * 2 - mglng, lat * 2 - mglat];
    }
}
function transformlat(lng, lat) {
    var ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * Math.sqrt(Math.abs(lng));
    ret += (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0;
    ret += (20.0 * Math.sin(lat * PI) + 40.0 * Math.sin(lat / 3.0 * PI)) * 2.0 / 3.0;
    ret += (160.0 * Math.sin(lat / 12.0 * PI) + 320 * Math.sin(lat * PI / 30.0)) * 2.0 / 3.0;
    return ret
}

function transformlng(lng, lat) {
    var ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * Math.sqrt(Math.abs(lng));
    ret += (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0;
    ret += (20.0 * Math.sin(lng * PI) + 40.0 * Math.sin(lng / 3.0 * PI)) * 2.0 / 3.0;
    ret += (150.0 * Math.sin(lng / 12.0 * PI) + 300.0 * Math.sin(lng / 30.0 * PI)) * 2.0 / 3.0;
    return ret
}

/**
 * 判断是否在国内，不在国内则不做偏移
 * @param lng
 * @param lat
 * @returns {boolean}
 */
function out_of_china(lng, lat) {
    return (lng < 72.004 || lng > 137.8347) || ((lat < 0.8293 || lat > 55.8271) || false);
}