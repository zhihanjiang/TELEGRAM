var util = require('util');
var os = require('os');
var database = require('better-sqlite3');
var moment = require('moment');
var dateformat = require('dateformat');
var time = require('node-tictoc');
var fs = require('fs');
data_layer = {};
data_layer.database = {};
data_layer.database.taxi = new database('/mnt/d/zhihan/driving_behaviors_detection/data/chengdu_11.db');

query = 'select did from drivers';
stmt = data_layer.database.taxi.prepare(query);
data_layer.vehicle = stmt.all();

const dele = data_layer.database.taxi.prepare('delete from gps where did=@did and timestamp=@ts');
for (var vid = 0; vid < data_layer.vehicle.length; ++vid) {
  util.log(vid);
  var vehicle = data_layer.vehicle[vid].did;
  query = 'select latitude,longitude,timestamp from gps where did=? ORDER BY timestamp;'
  stmt = data_layer.database.taxi.prepare(query);
  data_layer.trajectory = stmt.all(vehicle);


  //删除不合规的点
  var info = new Array();
  var index = 0;
  for (var i = 0; i < data_layer.trajectory.length; ++i) {
    var longitude = data_layer.trajectory[i].longitude;
    var latitude = data_layer.trajectory[i].latitude;
    if (longitude < 104.042102 || longitude > 104.129591 || latitude > 30.727818 || latitude < 30.652828) {
      info[index++] = {did:did,ts:data_layer.trajectory[i].timestamp};
    }
  }
  if (index > 0) {
    const deleteMany=data_layer.database.taxi.transaction((cats)=>{
      for (const cat of cats) dele.run(cat);
    });
    deleteMany(info);
    util.log("done.");
  }
}