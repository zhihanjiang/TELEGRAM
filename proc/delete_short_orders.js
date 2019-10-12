var util = require('util');
var os = require('os');
var database = require('better-sqlite3');

data_layer = {};
data_layer.database = {};
data_layer.database.taxi = new database('/mnt/d/zhihan/driving_behaviors_detection/data/chengdu_11.db');

query = 'select did,oid,count(*) as num from gps group by did,oid;';
stmt = data_layer.database.taxi.prepare(query);
data_layer.order_count = stmt.all();
var info = new Array();
var index = 0;
const dele = data_layer.database.taxi.prepare('delete from gps where did=@did and oid=@oid');
for (var i = 0; i < data_layer.order_count.length; ++i) {
  if(data_layer.order_count[i].num<2){
    util.log(data_layer.order_count[i].did);
    util.log(data_layer.order_count[i].oid);
    util.log('-------------------');
    info[index++] = {did:data_layer.order_count[i].did,oid:data_layer.order_count[i].oid};
  }
}
if (index > 0) {
  const deleteMany=data_layer.database.taxi.transaction((cats)=>{
    for (const cat of cats) dele.run(cat);
  });
  deleteMany(info);
  util.log("done.");
}