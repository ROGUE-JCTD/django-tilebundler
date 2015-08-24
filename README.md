TileBundler
==========
A service that caches all the tiles in specified "bounds" for provided layer(s) in [mbtiles][6] files and exposes the resulting 'tilesets' for download. More specifically, TileBundler is a [Django][1] application and it uses [MapProxy][2] to generate the tileset from local and remote layers. The purpose of the application is to simplify creation and distribution of tilesets particularly to mobile applications that need to operate in disconnected environments. 

It is an open-source application that has been developed under the [ROGUE][4] project and is part of the [GeoSHAPE][3] eco-system. You can incorporate TileBundler in other applications and can create a 

Notes
=============
- The `geom` of a tileset can specified as:
    - bounding box: `[-77.47, 38.72, -76.72, 39.08]`
    - geojson: `{...}`
    - WKT polygon or multipolygon: `POLYGON((-4.5703125 84.0228901101526,165.5859375 84.0228901101526,165.5859375 6.031310707125822,-4.5703125 6.031310707125822,-4.5703125 84.0228901101526))`

- you can create tilesets from layers on your local geoserver. Be sure to prefix `<workspace>:` before your layer name such as: `geonode:ne_50m_admin_0_countries`. If local server has ssl enabled but doesn't have a valid certificate, you can provide the http url instead of https. 

- If your tileset's service type is "tile", it can either be an XYZ layer, or a TMS layer. These types of layers handle bounds differently, and needs to be addressed. This could mean that caching the bounds on this layer will need a different origin, specifically one that mirrors the equator. This is done by inverting the y-values of the geometry. An example will be shown below. Do this before generating the tileset. If your tileset is on the wrong side of the world, and/or all of the tiles end upside-down, re-generate the tileset after inversion. More documentation about this concept can be found [here][8].

- If you plan on caching from OpenStreetMap or HIU TMS servers:
    - OpenStreetMap - follow the information below. When getting your bounds from an outside source (or OpenStreetMap.org's export feature) make sure that the bounds mirror the equator.
    - HIU TMS - Make sure to use the flipped URL (For example: Honduras, Tegucigalpa = http://hiu-maps.net/hot/1.0.0/tegu-15feb2010-flipped/%(z)s/%(x)s/%(y)s.png), and also have bounds that mirror the equator.
    - An example on how to mirror the equator will be [here][9].
    - Example output for OSM + TMS caching will be [here][10].

- Making MBTiles from WMS layers on GeoServer is currently not supported.

Example - Mirroring the Equator:
--------
    Ordering of bounds is:
    [Left, Bottom, Right, Top]

    Normal OpenStreetMap bounds of Falls Church, VA:
    [-77.21917, 38.85804, -77.21295, 38.86337]

    Bottom = -Top
    38.85804 = -38.86337

    Top = -Bottom
    38.86337 = -38.85804

    Mirrored OpenStreetMap bounds of Falls Church, VA:
    [-77.21917, -38.86337, -77.21295, -38.85804]

&nbsp;&nbsp;&nbsp;

Example Output - OSM and TMS:
--------
*OpenStreetMap: Falls Church, VA*
```
{
    "created_at": "2015-08-19T13:58:54.002882",
    "created_by":
        {
            "first_name": "",
            "last_name": "",
            "resource_uri": "",
            "username": "admin"
        },
    "file_size": 820224,
    "file_updated": "2015-08-19T14:26:08.959459",
    "geom": "[-77.21917, -38.86337, -77.21295, -38.85804]",
    "id": 15,
    "layer_name": "osm",
    "layer_zoom_start": 0,
    "layer_zoom_stop": 18,
    "name": "OpenStreetMapdotOrg",
    "resource_uri": "/api/tileset/15/",
    "server_service_type": "tile",
    "server_url": "http://b.tile.openstreetmap.org/%(z)s/%(x)s/%(y)s.png",
    "server_username": ""
}
```

*OpenStreetMap Local GeoServer VM: Falls Church, VA*
```
{
    "created_at": "2015-08-04T14:14:52.977549",
    "created_by":
        {
            "first_name": "",
            "last_name": "",
            "resource_uri": "",
            "username": "admin"
        },
    "file_size": 820224,
    "file_updated": "2015-08-19T10:41:33.265202",
    "geom": "[-77.21917, -38.86337, -77.21295, -38.85804]\r\n",
    "id": 4,
    "layer_name": "osm",
    "layer_zoom_start": 0,
    "layer_zoom_stop": 18,
    "name": "OSMLocal",
    "resource_uri": "/api/tileset/4/",
    "server_service_type": "tile",
    "server_url": "http://(Location_Of_Your_OSM_VM)/osm_tiles/%(z)s/%(x)s/%(y)s.png",
    "server_username": ""
}
```

*TMS - Honduras, Tegucigalpa:*
```
{
    "created_at": "2015-08-04T15:19:49.048624",
    "created_by":
        {
            "first_name": "",
            "last_name": "",
            "resource_uri": "",
            "username": "admin"
        },
    "file_size": 118784,
    "file_updated": "2015-08-19T10:41:33.265202",
    "geom": "[-87.20499, 14.09714, -87.20273, 14.09966]",
    "id": 7,
    "layer_name": "tegu_layer",
    "layer_zoom_start": 0,
    "layer_zoom_stop": 18,
    "name": "HiuTegu_TMS",
    "resource_uri": "/api/tileset/7/",
    "server_service_type": "tile",
    "server_url": "http://hiu-maps.net/hot/1.0.0/tegu-15feb2010-flipped/%(z)s/%(x)s/%(y)s.png",
    "server_username": ""
}
```

&nbsp;&nbsp;&nbsp;

API Quick Guide
=============
To create tileset objects, use the django admin API. We would like to embed the creation of the tileset object in [MapLoom][6] where the user can add all layers of interest to the map, draw the geometry, and specify zoom range for the tile set. They would also be able to to trigger generation, view progress, and manage tilesets on the server from within [MapLoom][6]. 

`/api/tileset`
---------------------------
Get list of all tileset objects as JSON

**Sample response**
```
{
  "meta": {
    "limit": 20,
    "next": null,
    "offset": 0,
    "previous": null,
    "total_count": 3
  },
  "objects": [
    {
      "created_at": "2015-07-15T12:45:39",
      "created_by": {
        "first_name": "",
        "last_name": "",
        "resource_uri": "",
        "username": "admin"
      },
      "filesize": "3145728",
      "geom": "POLYGON((-4.5703125 84.0228901101526,165.5859375 84.0228901101526,165.5859375 6.031310707125822,-4.5703125 6.031310707125822,-4.5703125 84.0228901101526))",
      "id": 1,
      "layer_name": "geonode:ne_50m_admin_0_countries",
      "layer_zoom_start": 0,
      "layer_zoom_stop": 5,
      "name": "country_boundaries",
      "resource_uri": "/api/tileset/1/",
      "server_service_type": "wms",
      "server_url": "http://192.168.99.100/geoserver/wms",
      "server_username": "admin"
    },
    {
      "created_at": "2015-07-15T12:16:07",
      "created_by": {
        "first_name": "",
        "last_name": "",
        "resource_uri": "",
        "username": "admin"
      },
      "filesize": "1368064",
      "geom": "[-77.6843, 38.4299, -76.3152, 39.2982]",
      "id": 2,
      "layer_name": "osm",
      "layer_zoom_start": 0,
      "layer_zoom_stop": 12,
      "name": "osm_wms_dc",
      "resource_uri": "/api/tileset/2/",
      "server_service_type": "wms",
      "server_url": "http://osm.omniscale.net/proxy/service",
      "server_username": ""
    },
    {
      "created_at": "2015-07-15T12:43:56",
      "created_by": {
        "first_name": "",
        "last_name": "",
        "resource_uri": "",
        "username": "admin"
      },
      "filesize": "4706304",
      "geom": "",
      "id": 3, 
      "layer_name": "syrus",
      "layer_zoom_start": 0,
      "layer_zoom_stop": 5,
      "name": "openstreetmap",
      "resource_uri": "/api/tileset/3/",
      "server_service_type": "tile",
      "server_url": "http://a.tile.openstreetmap.org/%(z)s/%(x)s/%(y)s.png",
      "server_username": ""
    }
  ]
}
```


`/api/tileset/1`
---------------------------
Get tileset object with id 1 as JSON

**sample response**
```
{
  "created_at": "2015-07-15T04:33:07",
  "created_by": {
    "first_name": "",
    "last_name": "",
    "resource_uri": "",
    "username": "admin"
  },
  "filesize": "8192000",
  "geom": "[-83.507, 25.160, -78.030, 29.128]",
  "id": 1,
  "layer_name": "osm",
  "layer_zoom_start": 0,
  "layer_zoom_stop": 12,
  "name": "osm_fl",
  "resource_uri": "/api/tileset/1/",
  "server_service_type": "wms",
  "server_url": "http://osm.omniscale.net/proxy/service",
  "server_username": ""
}
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
will retrive the status of tileset with id 1 and it will indicate the status of both the `current` tilset as well as a `pending` status for when the tileset is being generated. Note that when a tileset is generated, it is saved as a .generating file as opposed to .mbtiles and it only replaces the mbtiles file when generate completes. The previous mbtiles is backed up for good measure since a mistakenly trigger generate would otherwise discard a tileset that might have taken a while to generate. Note that if an mbtiles already exists and the tileset is generated again, during the generate process, the previous tileset will still be available to for download. Similarly, if the current generate is stopped, the main tileset will still be valid and usable. 

**expected statuses** 
- `not generated`: an mbtiles corresponding to this tileset object does not exist.
- `ready`: an mbtiles file is available for download. Note when a tileset is generated, it does not replace any existing tileset until it has been fully generated. If the tileset has been generated and then the following `generate` is stopped, the last completed tileset will be used. 
- `stopped`: generation of the mbtiles was stopped before it was completed. Note that normally unless the tileset generation is completed, the mbtile file will not replace a previous tileset.  
- `in progress`: generation of the mbtiles is currently in progress
- `in progress, but log not found`: the mbtiles was found but a corresponding log file was not found.   

**sample response**
```
{
  "current": {
    "filesize": 1155072, 
    "status": "ready", 
    "updated": "2015-07-23T04:05:07"
  }, 
  "pending": {
    "current_zoom_level": "4", 
    "estimated_completion_time": "2015-07-23T04:38:40", 
    "filesize": 237568, 
    "progress": "37.50", 
    "status": "in progress", 
    "updated": "2015-07-23T04:35:41"
  }
}
```

`/api/tileset/1/download`
------------------------------------
Download the mbtiles file generated from tileset with id 1

**expected statuses**
- `not generated`: could not find an mbtiles corresponding to this tileset object.

------
&nbsp;&nbsp;&nbsp;

Known Issues
=============
 - An invalid URL will lock the generation of the tileset. Progress will not go above 0%, and the progress log will reflect this.
    - `NOTE: If on the VM, the generated .lck will have a PID, and the rogue_geonode log file will print that there is a ServerError.`
 - An invalid username / password will lock the generation of the tileset, and yield similar results to the invalid URL.
 - Invalid geometry will be generated, but will not be able to be shown on a map.

  [1]: http://djangoproject.com "Django"
  [2]: http://mapproxy.org "MapProxy"
  [3]: http://geoshape.org "GeoSHAPE"
  [4]: http://github.com/rogue-jctd/ "ROGUE"
  [5]: http://github.com/ROGUE-JCTD/Arbiter-Android "Arbiter"
  [6]: http://github.com/mapbox/mbtiles-spec "mbtiles"
  [7]: http://github.com/ROGUE-JCTD/MapLoom  "MapLoom"
  [8]: https://alastaira.wordpress.com/2011/07/06/converting-tms-tile-coordinates-to-googlebingosm-tile-coordinates/
  [9]: https://github.com/ROGUE-JCTD/django-tilebundler#example---mirroring-the-equator
  [10]: https://github.com/ROGUE-JCTD/django-tilebundler#example-output---osm-and-tms
