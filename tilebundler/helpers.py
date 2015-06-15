from mapproxy.seed.seeder import seed
from mapproxy.seed.config import SeedingConfiguration, SeedConfigurationError, ConfigurationError
from mapproxy.seed.spec import validate_seed_conf
from mapproxy.config.loader import ProxyConfiguration
from mapproxy.config.spec import validate_mapproxy_conf

import json
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
          "name":"osm",
          "title":"Omniscale OSM WMS - osm.omniscale.net",
          "sources":[
            "osm_cache"
          ]
        },
        {
          "name":"world",
          "title":"Worls bounds from local geoserver",
          "sources":[
            "world_cache"
          ]
        }
      ],
      "caches":{
        "osm_cache":{
          "grids":[
            "webmercator"
          ],
          "sources":[
            "osm_wms"
          ],
          "cache":{
            "type":"mbtiles"
          }
        },
        "world_cache":{
          "grids":[
            "webmercator"
          ],
          "sources":[
            "world_wms"
          ],
          "cache":{
            "type":"mbtiles"
          }
        }
      },
      "sources":{
        "osm_wms":{
          "type":"wms",
          "req":{
            "url":"http://osm.omniscale.net/proxy/service?",
            "layers":"osm"
          }
        },
        "world_wms":{
          "type":"wms",
          "http":{
            "headers":{
              "Authorization":"Basic YWRtaW46Z2Vvc2VydmVy"
            }
          },
          "req":{
            "url":"http://admin:geoserver@192.168.99.100/geoserver/wms?",
            "layers":"geonode:ne_50m_admin_0_countries"
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
        "austria": {
          "bbox": [
            9.36,
            46.33,
            17.28,
            49.09
          ],
          "srs": "EPSG:4326"
        }
      },

      "seeds": {
        "osm_seed": {
          "caches": [
            "osm_cache"
          ],
          "levels": {
            "to": 5
          }
        },
        "world_seed": {
          "caches": [
            "world_cache"
          ],
          "levels": {
            "to": 10
          }
        }
      }
    }
    """

    seed_conf = yaml.safe_load(seed_conf_json)
    mapproxy_conf = yaml.safe_load(mapproxy_conf_json)

    seed_conf["seeds"]["world_seed"]["levels"]["to"] = tileset.layer_zoom_stop

    conf_base_dir = './'

    errors, informal_only = validate_mapproxy_conf(mapproxy_conf)
    for error in errors:
        print error
    if not informal_only or (errors and not ignore_warnings):
        raise ConfigurationError('invalid configuration')
    cf = ProxyConfiguration(mapproxy_conf, conf_base_dir=conf_base_dir, seed=seed, renderd=renderd)

    errors, informal_only = validate_seed_conf(seed_conf)
    for error in errors:
        print error
    if not informal_only:
        raise SeedConfigurationError('invalid configuration')

    seed_cf = SeedingConfiguration(seed_conf, mapproxy_conf=cf)

    return cf, seed_cf

