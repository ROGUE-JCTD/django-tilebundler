TileBundler
==========
A service that caches all the tiles in specified "bounds" for provided layer(s) in [mbtiles][6] files and exposes the resulting 'tilesets' for download. More specifically, TileBundler is a [Django][1] application and it uses [MapProxy][2] to generate the tileset from local and remote layers. The purpose of the application is to simplify creation and distribution of tilesets particularly to mobile applications that need to operate in disconnected environments. 

It is an open-source application that has been developed under the [ROGUE][4] project and is part of the [GeoSHAPE][3] eco-system. You can incorporate TileBundler in other applications and can create a 

----------


API Quick Guide
=============
To create tileset objects, use the django admin API. We would like to embed the creation of the tileset object in [MapLoom][6] where the user can add all layers of interest to the map, draw the geometry, and specify zoom range for the tile set. They would also be able to to trigger generation, view progress, and manage tilesets on the server from within [MapLoom][6]. 

`/api/tileset`
---------------------------
Get list of all tileset objects as JSON

**Sample response**
```
{"meta": {"limit": 20, "next": null, "offset": 0, "previous": null, "total_count": 1}, "objects": [{"created_at": "2015-07-09T18:45:15", "created_by": {"first_name": "", "last_name": "", "resource_uri": "", "username": "admin"}, "filesize": "1556480", "geom": "POLYGON((-4.5703125 84.0228901101526,165.5859375 84.0228901101526,165.5859375 6.031310707125822,-4.5703125 6.031310707125822,-4.5703125 84.0228901101526))", "id": 1, "layer_name": "osm", "layer_zoom_start": 0, "layer_zoom_stop": 5, "name": "osm", "resource_uri": "/api/tileset/1/", "server_service_type": "wms", "server_url": "http://osm.omniscale.net/proxy/service", "server_username": ""}]}
```


`/api/tileset/1`
---------------------------
Get tileset object with id 1 as JSON

**sample response**
```
{"created_at": "2015-07-09T18:45:15", "created_by": {"first_name": "", "last_name": "", "resource_uri": "", "username": "admin"}, "filesize": "1556480", "geom": "POLYGON((-4.5703125 84.0228901101526,165.5859375 84.0228901101526,165.5859375 6.031310707125822,-4.5703125 6.031310707125822,-4.5703125 84.0228901101526))", "id": 1, "layer_name": "osm", "layer_zoom_start": 0, "layer_zoom_stop": 5, "name": "osm", "resource_uri": "/api/tileset/1/", "server_service_type": "wms", "server_url": "http://osm.omniscale.net/proxy/service", "server_username": ""}
```

`/api/tileset/1/generate`
-------------------------------------
Trigger creation of the tileset file for tileset with id 1

**expected statuses** 
- `started`: generation of the mbtiles was just started 
- `already started`: generation of the mbtiles was not started because it was already satrted and currently running

**sample response**
`{"status": "started"}`

`/api/tileset/1/stop`
-------------------------------
Stop the generation of the tileset with id 1

**expected statuses** 
- `not in progress`: generating of the tileset was not in progress
- `stopped`: generation of the mbtiles was stopped

`/api/tileset/1/status`
---------------------------------
will retrive the status of tileset with id 1. the return `file_size` and  `file_last_update` will be read from the actual tileset file on disk

**expected statuses** 
- `not generated`: could not find an mbtiles corresponding to this tileset object.
- `in progress`: generation of the mbtiles is currently in progress
- `ready`: an mbtiles file is available for download. Note when a tileset is generated, it does not replace any existing tileset until it has been fully generated. If the tileset has been generated and then the following `generate` is stopped, the last completed tileset will be used. As an indication that the last generate was `stopped`, the response will contain `stopped_file_last_update` and `stopped_file_file_size` in addition to the `file_last_update` and `file_size`
- `stopped`: generation of the mbtiles was stopped before it was completed. Note that normally unless the tileset generation is completed, the mbtile file will not replace a previous tileset.  
- `in progress, but log not found`: the mbtiles was found but a corresponding log file was not found.   

**sample response**
`{"file_last_update": "2015-07-09T21:44:29", "file_size": 1544192, "status": "ready"}`

`/api/tileset/1/download`
------------------------------------
Download the mbtiles file generated from tileset with id 1

**expected statuses**
- `not generated`: could not find an mbtiles corresponding to this tileset object.


  [1]: http://djangoproject.com "Django"
  [2]: http://mapproxy.org "MapProxy"
  [3]: http://geoshape.org "GeoSHAPE"
  [4]: http://github.com/rogue-jctd/ "ROGUE"
  [5]: http://github.com/ROGUE-JCTD/Arbiter-Android "Arbiter"
  [6]: http://github.com/mapbox/mbtiles-spec "mbtiles"
  [6]: http://github.com/ROGUE-JCTD/MapLoom  "MapLoom"
