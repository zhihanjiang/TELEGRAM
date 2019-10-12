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
data_layer.database.taxi = new database('/mnt/d/zhihan/driving_behaviors_detection/data/point09.db');
//data_layer.database.turn_by_turn = new database('/mnt/d/zhihan/Data/conf/behavior.db');
var engine = new osrm('../data/map/xiamen/xiamen.osrm');
// const insert = data_layer.database.taxi.prepare('INSERT INTO behavior(traj_id,timestamp,longitude,latitude,behavior,bearing_before,bearing_after,confidence) VALUES(@traj_id,@timestamp,@longitude,@latitude,@behavior,@bearing_before,@bearing_after,@conf)');
// util.log('load all trajectories');
var query = 'SELECT rowid as row_id, lid,lon as longitude,lat as latitude FROM map_xm_below';
var stmt = data_layer.database.taxi.prepare(query);
data_layer.traj = stmt.all();
data_layer.i=0;
util.log('done.');
update(data_layer.i)

function update(i){
  util.log(data_layer.traj[i].lid.toString() + " "+ data_layer.i.toString());
  var options = {
    coordinates:[[parseFloat(data_layer.traj[i].longitude), parseFloat(data_layer.traj[i].latitude)]],
    number:1
  }
  engine.nearest(options,function(err,response){
    var lon=response.waypoints[0].location[0];
    var lat=response.waypoints[0].location[1];
    query = 'update map_xm_below set longitude=? where rowid=?';
    stmt = data_layer.database.taxi.prepare(query);
    stmt.run(lon,data_layer.traj[data_layer.i].row_id);
    query = 'update map_xm_below set latitude=? where rowid=?';
    stmt = data_layer.database.taxi.prepare(query);
    stmt.run(lat,data_layer.traj[data_layer.i].row_id);
    if(i==data_layer.traj.length-1)
        return;
    data_layer.i+=1;
    update(data_layer.i);

  });
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