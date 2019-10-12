var util = require('util');
var os = require('os');
var database = require('better-sqlite3');

data_layer = {};
data_layer.database = {};
data_layer.database.taxi = new database('/mnt/d/zhihan/driving_behaviors_detection/data/chengdu_11.db');
query = 'select traj_id from did_oid';
stmt = data_layer.database.taxi.prepare(query);
data_layer.did_oid = stmt.all();
var speed_thre = 0.01; //m/s
const insert = data_layer.database.taxi.prepare('insert into parking(traj_id,st_ts,ed_ts,longitude,latitude) values(@traj_id,@st_ts,@ed_ts,@lon,@lat)');
for(var i=0;i<data_layer.did_oid.length;++i){
  var traj_id=data_layer.did_oid[i].traj_id;
  if(traj_id<4009904)
    continue;
  util.log(traj_id);

  query = 'select timestamp,longitude,latitude from gps where traj_id=? order by timestamp';
  stmt= data_layer.database.taxi.prepare(query);
  data_layer.trajectory = stmt.all(traj_id);
  var info = new Array();
  var index = 0;
  for(var ii=0;ii<data_layer.trajectory.length-1;++ii){
    var k=0;
    var sum_lat=0,sum_lon=0;
    for(var jj=ii+1;jj<data_layer.trajectory.length;++jj){
      delta_t=data_layer.trajectory[jj].timestamp-data_layer.trajectory[ii].timestamp;
    //  util.log(geo(data_layer.trajectory[ii],data_layer.trajectory[jj]));
     // util.log(delta_t);
      if(geo(data_layer.trajectory[ii],data_layer.trajectory[jj])/delta_t>speed_thre){
        break;
      }
      ++k;
      sum_lat+=data_layer.trajectory[jj].latitude;
      sum_lon+=data_layer.trajectory[jj].longitude;
    }
    if(k>0){
      sum_lon+=data_layer.trajectory[ii].longitude;
      sum_lat+=data_layer.trajectory[ii].latitude;
      st_time=data_layer.trajectory[ii].timestamp;
      ed_time=data_layer.trajectory[ii+k].timestamp;
      info[index++]={traj_id:traj_id,st_ts:st_time,ed_ts:ed_time,lon:sum_lon/(k+1),lat:sum_lat/(k+1)};
    }
    ii+=k;
  }
  if (index > 0) {
    const insertMany=data_layer.database.taxi.transaction((cats)=>{
      for (const cat of cats) insert.run(cat);
    });
    insertMany(info);
    util.log("done.");
  }
}


function geo(p1, p2) {
  var R = 6371393;
  var q1 = to_radian(p1.latitude);
  var q2 = to_radian(p2.latitude);
  var delta_q = to_radian(p2.latitude - p1.latitude);
  var delta_l = to_radian(p2.longitude - p1.longitude);
  var theta = Math.atan2(Math.sin(delta_l) * Math.cos(q2), Math.cos(q1) * Math.sin(q2) - Math.sin(q1) * Math.cos(q2) * Math.cos(delta_l));
  var a = Math.sin(delta_q/2) * Math.sin(delta_q / 2) + Math.cos(q1) * Math.cos(q2) * Math.sin(delta_l / 2) * Math.sin(delta_l / 2);
///  var b = (to_degree(theta) + 360) % 360;
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  var d = R * c;
  return d;
};

function to_radian(d) {
  return d * Math.PI / 180;
};

function to_degree(r) {
  return r * 180 / Math.PI;
}