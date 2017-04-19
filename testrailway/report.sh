${HOME}/bin/aqlx.sh 'for i in fullnodes return merge({node: i.id, lat: i.lat, lon: i.lon},is_null(i.tags) ? {} : {tags: i.tags})' 

