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
data_layer.drivers = stmt.all();
const dele = data_layer.database.taxi.prepare('delete from gps where  timestamp =@ts and did=@did and rowid>(select min(rowid) from gps where timestamp=@ts and did=@did)');
for(var k=826152;k<data_layer.drivers.length;++k){
  var did=data_layer.drivers[k].did;
  console.log(did);
  query = 'select timestamp from gps where did=? ORDER BY timestamp;'
  stmt = data_layer.database.taxi.prepare(query);
  data_layer.trajectory = stmt.all(did);
  var i, j;
  // var op = new Array();
  var info = new Array();
  // var op_index = 0;
  var index = 0;
  for(i=0;i < data_layer.trajectory.length - 1;++i){
    ts1 = data_layer.trajectory[i].timestamp;
    var count=0;
    for(j=i+1;j<data_layer.trajectory.length;++j){
      ts2 = data_layer.trajectory[j].timestamp;
      if(ts1!=ts2)
        break;
      ++count;
    }
    if(count==0)
    	continue;
   // op[op_index++] = 'delete from gps where  timestamp =? and did=? and rowid>(select min(rowid) from gps where timestamp=? and did=?)';
    info[index++] = {ts: ts1,did:did};
    // info[index++] = did;
    // info[index++] = ts1;
    // info[index++] = did;
    i+=count;
  }
  if (index > 0) {
  	const deleteMany=data_layer.database.taxi.transaction((cats)=>{
  		for (const cat of cats) dele.run(cat);
  	});
  	deleteMany(info);
    // stmt = data_layer.database.taxi.transaction(op);
    // stmt.run(info);
    util.log("find redundancy.");
    util.log(info);
  }
}
