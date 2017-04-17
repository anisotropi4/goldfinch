#!/bin/sh 
# based on arangodb docker here https://github.com/guidoeco/docker/tree/master/arangodb
. ${HOME}/bin/ar-env.sh

# create database, user and grant user read-write permissions to database 
${NODE} <<@@EOF2
sync = require('sync');
request = require('request');
function createdb(callback) {
    Database = require('arangojs').Database;
    db = new Database({url: 'http://root:${ARPASSWORD}@ar-server:8529', databaseName: '_system' });
    db.listDatabases()
    .then(names => { console.log('names: ', names);
    db.createDatabase('${ARDBN}')
    .then(info => { console.log('drop: ', info);
		    db.listDatabases()
    .then(names => { console.log('names: ', names)},
          err => { console.error('names error: ', err)})}),
    err => { console.error('error drop: ', err)}});
}
function createuser(callback) {
    request.post('http://root:${ARPASSWORD}@${ARSVR}:8529/_api/user',
		 { json: { 'user': '${ARUSR}', 'passwd': '${ARPWD}' }},
		 function (error, response, body) {
		     if (!error && response.statusCode == 200) {
			    console.log(body)
			}
		 });
};
sync(function(){
	    createdb.sync(null);
	});
sync(function(){
	    createuser.sync(null);
	});
@@EOF2

sleep 1
${NODE} <<@@EOF3
sync = require('sync');
request = require('request');
function grantpermissions(callback) {
    request.put('http://root:${ARPASSWORD}@${ARSVR}:8529/_api/user/${ARUSR}/database/${ARDBN}',
		{ json: { 'grant': 'rw' }},
	     function (error, response, body) {
		 if (!error && response.statusCode == 200) {
			console.log(body)
		    }
	     });
};
sync(function(){
	    grantpermissions.sync(null);
	});
@@EOF3
