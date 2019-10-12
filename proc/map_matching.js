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
data_layer.database.taxi = new database('/mnt/d/zhihan/driving_behaviors_detection/data/chengdu_11.db');
//data_layer.database.turn_by_turn = new database('/mnt/d/zhihan/Data/conf/behavior.db');
var engine = new osrm('../data/map/chengdu/chengdu.osrm');
const insert = data_layer.database.taxi.prepare('INSERT INTO behavior(traj_id,timestamp,longitude,latitude,behavior,bearing_before,bearing_after,confidence) VALUES(@traj_id,@timestamp,@longitude,@latitude,@behavior,@bearing_before,@bearing_after,@conf)');
util.log('load all trajectories');
var query = 'SELECT traj_id FROM did_oid';
var stmt = data_layer.database.taxi.prepare(query);
data_layer.traj = stmt.all();
util.log('done.');

data_layer.traj_id = 5310656;

data_layer.max_traj=6096021;

load_trajectory_for_behavior(data_layer.traj_id);

function load_trajectory_for_behavior(traj_id) {
  //  var vid = data_layer.vid;
  var query = 'SELECT latitude,longitude, timestamp FROM gps WHERE traj_id = ? ORDER BY timestamp';
  var stmt = data_layer.database.taxi.prepare(query);
  var traj = stmt.all(data_layer.traj[data_layer.traj_id].traj_id);
  //util.log(data_layer.traj[data_layer.traj_id].traj_id);
 // util.log("update options")
  data_layer.options = {
    coordinates: traj.map(a => gcj02towgs84(a.longitude,a.latitude)),
    timestamps: traj.map(a => +moment(a.timestamp)),
    steps: true,
    tidy: true
  };
 // util.log(vid + "(" + data_layer.vehicle[vid].vehicle + ")(" + tnum + ") : " + traj.length);
  if (traj.length < 2) {
    fs.appendFileSync("/mnt/d/zhihan/driving_behaviors_detection/data/error.txt", data_layer.traj_id  + ",too few points\r\n");
    data_layer.traj_id += 1;
    if (data_layer.traj_id > data_layer.max_traj) {
      return;
    } 
    else {
      load_trajectory_for_behavior(data_layer.traj_id);
      return;
    }
  } else
    save_behavior();
}

function save_behavior() {
//  util.log('match_map');
  engine.match(data_layer.options, function(err, response) {
    //data_layer.response = response;
    //data_layer.err = err;
    if (err) {
      util.log(err + " " + data_layer.traj_id);
      fs.appendFileSync("/mnt/d/zhihan/driving_behaviors_detection/data/error.txt", data_layer.traj_id + "," + err + "\r\n");
      data_layer.traj_id+=1;
      if (data_layer.traj_id >data_layer.max_traj) {
        return
      }
      else {
        load_trajectory_for_behavior(data_layer.traj_id);
        return;
      }
    }
    var tracepoints_index = new Array();
    for (var i = 0; i < response.matchings.length; ++i) {
      tracepoints_index[i] = new Array();
      for (var j = 0; j < response.matchings[i].legs.length + 1; ++j) {
        tracepoints_index[i][j] = "";
      }
    }
    for (var i = 0; i < response.tracepoints.length; ++i) {
      if (response.tracepoints[i] == null)
        continue;
      //  var rt = response.tracepoints[i];
      //  util.log(rt);
      tracepoints_index[response.tracepoints[i].matchings_index][response.tracepoints[i].waypoint_index] = i;
    }
  //  util.log('save behavior ' + data_layer.vid + ' ' + data_layer.tnum);
   // var insert = new Array();
   // var insert_index = 0;
    var info = new Array();
    var info_index = 0;
    var vid
    for (var mt = 0; mt < response.matchings.length; ++mt) {
      var matching_index = mt;
      var conf=response.matchings[mt].confidence;
      // if(conf<0.9){
      //   continue;
      // }
      for (var i = 0; i < response.matchings[mt].legs.length; ++i) {
        var waypoint_index = i;
        var tp = tracepoints_index[matching_index][waypoint_index];
        var leg_duration = response.matchings[mt].legs[i].duration; //seconds
        var timestamp_duration = data_layer.options.timestamps[tp + 1] - data_layer.options.timestamps[tp];
        var step_duration = 0;
        var duration = 0;
        for (var j = 0; j < response.matchings[mt].legs[i].steps.length; ++j) {
          if (j == 0) {
            step_duration = 0;
          } else {
            step_duration += duration; //seconds
          }
          duration = response.matchings[mt].legs[i].steps[j].duration; //seconds
          var time = step_duration / leg_duration * timestamp_duration;

          var temp = response.matchings[mt].legs[i].steps[j].maneuver;
          var k = 1;
          switch (temp.type) {
            case "depart":
              k = 0;
              break;
            case "arrive":
              k = 0;
              break;
            default:
              break;
          }
          if (k == 1) {
            var modifier = "";
            if (temp.modifier) {
              modifier = temp.modifier;
            }
            timestamp = dateformat(new Date(data_layer.options.timestamps[tp] * 1000 + time * 1000).getTime(), 'yyyy-mm-dd HH:MM:ss').substr(5, 14);
          //  insert[insert_index] = 'INSERT INTO behavior(vehicle,timestamp,longitude,latitude,behavior,bearing_before,bearing_after,tnum) VALUES(?,?,?,?,?,?,?,?)';
            info[info_index++] = {traj_id:data_layer.traj[data_layer.traj_id].traj_id,timestamp:timestamp,longitude:temp.location[0],latitude:temp.location[1],
              behavior:temp.type + " " + modifier,bearing_before:temp.bearing_before,bearing_after:temp.bearing_after,conf:conf};
          }
        }
      }
    }
    if (info_index > 0) {
      const insertMany=data_layer.database.taxi.transaction((cats)=>{
        for (const cat of cats) insert.run(cat);
      });
      insertMany(info);
      util.log(data_layer.traj[data_layer.traj_id].traj_id+" done.");
    }// else util.log("no turn.");
    data_layer.traj_id+=1;
    if (data_layer.traj_id >data_layer.max_traj) {
      return;
    }
    load_trajectory_for_behavior(data_layer.traj_id);
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