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
data_layer.database.taxi = new database('/mnt/d/zhihan/driving_behaviors_detection/data/driving_violation.db');
//data_layer.database.turn_by_turn = new database('/mnt/d/zhihan/Data/conf/behavior.db');
var query = 'SELECT rowid as row_id,latitude,longitude FROM parking_segments_chengdu';
var stmt = data_layer.database.taxi.prepare(query);
data_layer.traj = stmt.all();
var engine = new osrm('../data/map/chengdu/chengdu.osrm')
data_layer.i=0;

const ins= data_layer.database.taxi.prepare('update parking_segments_chengdu set road_name=@road_name where rowid=@row_id');
data_layer.insert=ins;
data_layer.info=[];
data_layer.info_index=0;
insert(data_layer.i);

function insert(i){
	data_layer.rowid=data_layer.traj[i].row_id;
	var lat=data_layer.traj[i].latitude;
	var lng=data_layer.traj[i].longitude;
	util.log(data_layer.rowid);
	var options = {
		coordinates:[[lng,lat]]
	};
	engine.nearest(options,function(err,response){
		name=response.waypoints[0].name;
		if(name!=''){
		//	util.log(name);
			data_layer.info[data_layer.info_index++]={road_name:name,row_id:data_layer.rowid}
			// query = 'update parking_chengdu set road_name=? where rowid=?';
			// stmt = data_layer.database.taxi.prepare(query);
			// stmt.run(name,data_layer.rowid);
		}
		if(i==data_layer.traj.length-1){
			util.log('write database.');
			if (data_layer.info_index > 0) {
		      const insertMany=data_layer.database.taxi.transaction((cats)=>{
		        for (const cat of cats) data_layer.insert.run(cat);
		      });
		      insertMany(data_layer.info);
		    }// else util.log("no turn.");
			util.log('end');
			exit(0);
		}
		i=i+1;
		insert(i);
	})
}
