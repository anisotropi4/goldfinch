'use strict';
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();

module.context.use(router);

router.get('/hello-world', function (req, res) {
  res.send('Hello from volpe 0.1, a simple shortest-path implementation');
})
.response(['text/plain'], 'A generic greeting')
.summary('Generic greeting')
.description('Prints a generic greeting and simple usage');

const joi = require('joi');

const db = require('@arangodb').db;
const errors = require('@arangodb').errors;
const DOC_NOT_FOUND = errors.ERROR_ARANGO_DOCUMENT_NOT_FOUND.code;
const aql = require('@arangodb').aql;

router.get('/run_aql', function (req, res) {
  const keys = db._query(aql`
    FOR i IN [ 1, 2, 3, 4 ]
    RETURN i * 2
  `);
  res.send(keys);
})
.response(joi.array().items(
  joi.string().required()
).required(), '.')
    .summary('List entry keys')
    .description('Runs a simple test query');

const collection = db._collection('fullnodes');
router.get('/node/:key', function (req, res) {
  try {
    const data = collection.document(req.pathParams.key);
    res.send(data["id"])
  } catch (e) {
    if (!e.isArangoError || e.errorNum !== DOC_NOT_FOUND) {
      throw e;
    }
    res.throw(404, 'The entry does not exist', e);
  }
})
.pathParam('key', joi.string().required(), 'Key of the entry')
.response(joi.object().required(), 'Node ID stored in the collection')
.summary('Retrieve a node entry')
.description('Retrieves the ID for an entry from the "fullnodes" collection by key');

router.get('/shortestpath/', function (req, res) {
    const keys = db._query(aql`for i in any shortest_path "fullnodes/20913296" to "fullnodes/2512646997" fulledges
  return merge({node: i.id, lat: i.lat, lon: i.lon}, (i.tags ? {tags: i.tags} : {}))`);
  res.json(keys.toArray());
})
.response(joi.array().items(
  joi.string().required()
).required(), 'API shortest path between York and Scarborough')
.summary('Shortest path between York and Scarborough')
.description('All nodes in the shortest path between nodes York and Scarborough. Equivalent to shortestpath/20913296/2512646997');

router.get('/shortestpath/:start/:end/', function (req, res) {
  res.set("Content-Type", "text/plain; charset=utf-8");
    const keys = db._query(aql`for i in any shortest_path
			   concat("fullnodes/",${req.pathParams.start}) to
			   concat("fullnodes/",${req.pathParams.end}) fulledges
			   return merge({node: i.id, lat: i.lat, lon: i.lon}, (i.tags ? {tags: i.tags} : {}))`);
  res.send(keys);
})
.response(joi.array().items(
  joi.string().required()
).required(), 'API shortestpath/start node/end node/')
.summary('Shortest path all nodes')
.description('Assembles all nodes in the shortest path between nodes in url /shortestpath/start/finish');
