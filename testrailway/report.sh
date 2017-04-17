${HOME}/bin/aqlx.sh 'for i in fullnodes return merge({node: i.id, latitude: i.lat, longitude: i.lon},is_null(i.tags) ? {} : {tags: i.tags})' 

