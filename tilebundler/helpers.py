from mapproxy.seed.seeder import seed
from mapproxy.seed.config import SeedingConfiguration, SeedConfigurationError, ConfigurationError
from mapproxy.seed.spec import validate_seed_conf
from mapproxy.config.loader import ProxyConfiguration
from mapproxy.config.spec import validate_mapproxy_conf
from django.conf import settings
from django.views.static import serve
import os
import base64
import yaml


def generate_confs(tileset, ignore_warnings=True, renderd=False):
    """
    Takes a Tileset object and returns mapproxy and seed config files
    """
    mapproxy_conf_json = """
    {
      "services":{
        "wms":{
          "on_source_errors":"raise"
        }
      },
      "layers":[
        {
          "name":"",
          "title":"",
          "sources":[
            "tileset_cache"
          ]
        }
      ],
      "caches":{
        "tileset_cache":{
          "grids":[
            "webmercator"
          ],
          "sources":[
            "tileset_source"
          ],
          "cache":{
            "type":"mbtiles",
            "filename": "/provide/valid/path/to/file.mbtiles"
          }
        }
      },
      "sources":{
        "tileset_source":{
          "type":"wms",
          "req":{
            "url":"http://admin:geoserver@192.168.99.100/geoserver/wms?",
            "layers":"geonode:ne_50m_admin_0_countries"
          },
          "http":{
            "headers":{
              "Authorization":"Basic YWRtaW46Z2Vvc2VydmVy"
            }
          }
        }
      },
      "grids":{
        "webmercator":{
          "base":"GLOBAL_WEBMERCATOR"
        }
      }
    }
    """

    seed_conf_json = """
    {
      "coverages": {
        "tileset_geom": {
          "bbox": [-77.47, 38.72, -76.72, 39.08],
          "srs": "EPSG:4326"
        }
      },

      "seeds": {
        "tileset_seed": {
          "refresh_before": {
            "minutes": 0
          },
          "caches": [
            "tileset_cache"
          ],
          "levels": {
            "from": 0,
            "to": 2
          },
          "coverages": ["tileset_geom"]
        }
      }
    }
    """

    seed_conf = yaml.safe_load(seed_conf_json)
    mapproxy_conf = yaml.safe_load(mapproxy_conf_json)

    mapproxy_conf["sources"]["tileset_source"]["type"] = u_to_str(tileset.server_service_type)
    mapproxy_conf["sources"]["tileset_source"]["req"]["url"] = u_to_str(tileset.server_url)
    mapproxy_conf["sources"]["tileset_source"]["req"]["layers"] = u_to_str(tileset.layer_name)
    mapproxy_conf["layers"][0]["name"] = u_to_str(tileset.layer_name)
    mapproxy_conf["layers"][0]["title"] = u_to_str(tileset.layer_name)
    mapproxy_conf["caches"]["tileset_cache"]["cache"]["filename"] = get_tileset_filename(tileset)

    seed_conf["seeds"]["tileset_seed"]["levels"]["from"] = tileset.layer_zoom_start
    seed_conf["seeds"]["tileset_seed"]["levels"]["to"] = tileset.layer_zoom_stop
    # any specified refresh before for mbtiles will result in regeneration of the tile set
    seed_conf["seeds"]["tileset_seed"]["refresh_before"]["minutes"] = 0
    # assume only bbox for now, dc should be "[-77.47, 38.72, -76.72, 39.08]"
    seed_conf["coverages"]["tileset_geom"]["bbox"] = yaml.safe_load(tileset.geom)

    print "---- mbtiles file to generate: {}".format(get_tileset_filename(tileset))

    if tileset.server_username and tileset.server_password:
        encoded = base64.b64encode("{}:{}".format(tileset.server_username, tileset.server_password))
        mapproxy_conf["sources"]["tileset_source"]["http"]["headers"]["Authorization"] = 'Basic {}'.format(encoded)

    errors, informal_only = validate_mapproxy_conf(mapproxy_conf)
    for error in errors:
        print error
    if not informal_only or (errors and not ignore_warnings):
        raise ConfigurationError('invalid configuration')
    cf = ProxyConfiguration(mapproxy_conf, conf_base_dir=get_tileset_dir(), seed=seed, renderd=renderd)

    errors, informal_only = validate_seed_conf(seed_conf)
    for error in errors:
        print error
    if not informal_only:
        raise SeedConfigurationError('invalid configuration')

    seed_cf = SeedingConfiguration(seed_conf, mapproxy_conf=cf)

    return cf, seed_cf


"""
example settings file
TILEBUNDLER_CONFIG = {
    'tileset_dir': '/var/lib/mbtiles'
}
"""
def get_tileset_dir():
    conf = getattr(settings, 'TILEBUNDLER_CONFIG', {})
    return conf.get('tileset_dir', './')


def get_tileset_filename(tileset):
    return "{}/{}.{}".format(get_tileset_dir(), tileset.name, "mbtiles")


def u_to_str(string):
    return string.encode('ascii', 'ignore')


def tileset_download(request, tileset):
    filename = get_tileset_filename(tileset)
    filename = os.path.abspath(filename)
    response = serve(request, os.path.basename(filename), os.path.dirname(filename))
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(filename))
    return response
