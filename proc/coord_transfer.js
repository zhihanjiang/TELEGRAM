var util = require('util');
var os = require('os');
var osrm = require('osrm');
var database = require('better-sqlite3');
var moment = require('moment');
var dateformat = require('dateformat');
var time = require('node-tictoc');
var fs = require('fs');
data_layer = {};
data_layer.database = {};
data_layer.database.taxi = new database('/mnt/d/zhihan/driving_behaviors_detection/data/chengdu_11.db');
//data_layer.database.turn_by_turn = new database('/mnt/d/zhihan/Data/conf/behavior.db');
var engine = new osrm('../data/map/china/china.osrm');
const insert = data_layer.database.taxi.prepare('INSERT INTO behavior(traj_id,timestamp,longitude,latitude,behavior,bearing_before,bearing_after) VALUES(@traj_id,@timestamp,@longitude,@latitude,@behavior,@bearing_before,@bearing_after)');
util.log('load all trajectories');
var query = 'SELECT traj_id FROM did_oid';
var stmt = data_layer.database.taxi.prepare(query);
data_layer.traj = stmt.all();
util.log('done.');

function gcj02towgs84(lng, lat) {
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
        return [lng * 2 - mglng, lat * 2 - mglat]
    }
}