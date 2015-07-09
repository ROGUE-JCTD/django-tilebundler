from django.conf import settings

from mapproxy.seed.seeder import seed
from mapproxy.seed.config import SeedingConfiguration, SeedConfigurationError, ConfigurationError
from mapproxy.seed.spec import validate_seed_conf
from mapproxy.config.loader import ProxyConfiguration
from mapproxy.config.spec import validate_mapproxy_conf
from mapproxy.seed import seeder
from mapproxy.seed import util

from datetime import datetime
import base64
import yaml
import os
import time
import multiprocessing


tasks_dict = multiprocessing.Manager().dict()
tasks_lock = multiprocessing.Lock()


def generate_confs(tileset, ignore_warnings=True, renderd=False):
    """
    Takes a Tileset object and returns mapproxy and seed config files
    """
    mapproxy_conf_json = """
    {
      "services":{
        "wms":{
          "on_source_errors":"raise",
          "image_formats": ["image/png"]
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
          "base":"GLOBAL_MERCATOR"
        }
      },
      "globals": {
        "image": {
          "paletted": false
        }
      }
    }
    """

    seed_conf_json = """
    {
      "coverages": {
        "tileset_geom": {
          "bbox": [-77.47, 38.72, -76.72, 39.08],
          "datasource": "path/to/geom/file.xxx",
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

    print '---- mbtiles file to generate: {}'.format(get_tileset_filename(tileset))

    mapproxy_conf['sources']['tileset_source']['type'] = u_to_str(tileset.server_service_type)
    mapproxy_conf['sources']['tileset_source']['req']['url'] = u_to_str(tileset.server_url)
    mapproxy_conf['sources']['tileset_source']['req']['layers'] = u_to_str(tileset.layer_name)
    mapproxy_conf['layers'][0]['name'] = u_to_str(tileset.layer_name)
    mapproxy_conf['layers'][0]['title'] = u_to_str(tileset.layer_name)
    mapproxy_conf['caches']['tileset_cache']['cache']['filename'] = get_tileset_filename(tileset, 'generating')

    seed_conf['seeds']['tileset_seed']['levels']['from'] = tileset.layer_zoom_start
    seed_conf['seeds']['tileset_seed']['levels']['to'] = tileset.layer_zoom_stop
    # any specified refresh before for mbtiles will result in regeneration of the tile set
    seed_conf['seeds']['tileset_seed']['refresh_before']['minutes'] = 0

    if tileset.geom:
        geom_type = 'other'
        if tileset.geom.startswith('{"'):
            geom_type = 'geojson'
        elif tileset.geom.lower().startswith('polygon') or tileset.geom.lower().startswith('multipolygon'):
            geom_type = 'txt'
        elif tileset.geom.startswith('['):
            geom_type = 'bbox'

        if geom_type in ['geojson', 'txt']:
            geom_dir = '{}/geoms'.format(get_tileset_dir())
            if not os.path.exists(geom_dir):
                os.makedirs(geom_dir)
            # TODO: remove geom files when done
            geom_filename = '{}/geoms/{}.{}'.format(get_tileset_dir(), tileset.name, geom_type)
            with open(geom_filename, 'w+') as geom_file:
                geom_file.write(tileset.geom)
            seed_conf['coverages']['tileset_geom']['datasource'] = geom_filename
            seed_conf['coverages']['tileset_geom'].pop('bbox', None)
        elif geom_type is 'bbox':
            seed_conf['coverages']['tileset_geom']['bbox'] = yaml.safe_load(tileset.geom)
            seed_conf['coverages']['tileset_geom'].pop('datasource', None)
        else:
            # if not bbox or file, just set it as is to the datasource since mapproxy can handle other datastores
            # and they should work as is
            seed_conf['coverages']['tileset_geom']['datasource'] = yaml.safe_load(tileset.geom)

        print '---- tileset geom_type: {}, geom: {}'.format(geom_type, tileset.geom)

    else:
        # if a geom is not specified, remove the coverages key from tileset_seed
        seed_conf['seeds']['tileset_seed'].pop('coverages', None)
        seed_conf['coverages']['tileset_geom'].pop('datasource', None)
        seed_conf['coverages']['tileset_geom'].pop('bbox', None)

    print '--[ mapproxy_conf: '
    print yaml.dump(mapproxy_conf)
    print '--[ seed_conf: '
    print yaml.dump(seed_conf)

    if tileset.server_username and tileset.server_password:
        encoded = base64.b64encode('{}:{}'.format(tileset.server_username, tileset.server_password))
        mapproxy_conf['sources']['tileset_source']['http']['headers']['Authorization'] = 'Basic {}'.format(encoded)

    errors, informal_only = validate_mapproxy_conf(mapproxy_conf)
    for error in errors:
        print error
    if not informal_only or (errors and not ignore_warnings):
        raise ConfigurationError('invalid configcduration')
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


def get_tileset_filename(tileset, extension='mbtiles'):
    return '{}/{}.{}'.format(get_tileset_dir(), tileset.name, extension)


def update_tileset_stats(tileset):
    tileset_filename = get_tileset_filename(tileset)
    if os.path.isfile(tileset_filename):
        stat = os.stat(tileset_filename)
        tileset.created_at = datetime.fromtimestamp(stat.st_ctime)
        tileset.filesize = stat.st_size
        tileset.save()


def u_to_str(string):
    return string.encode('ascii', 'ignore')


def is_int_str(v):
    v = str(v).strip()
    return v == '0' or (v if v.find('..') > -1 else v.lstrip('-+').rstrip('0').rstrip('.')).isdigit()


def get_status(tileset):
    res = {'status': 'unknown'}

    pid = tasks_dict.get(tileset.id, None)
    # if tileset generation is not in progress
    if not pid:
        # if there is a .mbtiles file on disk, get the size and time last updated
        tileset_filename = get_tileset_filename(tileset)
        if os.path.isfile(tileset_filename):
            res['status'] = 'ready'
            stat = os.stat(tileset_filename)
            if stat:
                res['file_last_update'] = datetime.fromtimestamp(stat.st_ctime)
                res['file_size'] = stat.st_size
        else:
            res['status'] = 'not generated'

        # if there is a file .generating file on disk, it mean that last generation was stopped!
        # get the size and time last updated
        tileset_generating_filename = get_tileset_filename(tileset, 'generating')
        if os.path.isfile(tileset_generating_filename):
            stat = os.stat(tileset_generating_filename)
            if stat:
                res['stopped_file_last_update'] = datetime.fromtimestamp(stat.st_ctime)
                res['stopped_file_file_size'] = stat.st_size
    else:
        # if tileset generation is in progress
        res['status'] = 'in progress'
        progress_log_filename = get_tileset_filename(tileset, 'progress_log')
        if os.path.isfile(progress_log_filename):
            with open(progress_log_filename, 'r') as f:
                lines = f.read().replace('\r', '\n')
                lines = lines.split('\n')

            # an actual progress step update which looks like:
            # "[15:11:11]  4  50.00% 0.00000, 672645.84891, 18432942.24503, 18831637.78456 (112 tiles) ETA: 2015-07-07-15:11:12"\n
            latest_step = None
            # a progress update on the current step which looks like:
            # "[15:11:16]  87.50%	0000                 ETA: 2015-07-07-15:11:17'\r
            latest_progress = None
            if len(lines) > 0:
                for line in lines[::-1]:
                    tokens = line.split()
                    if len(tokens) > 2:
                        if is_int_str(tokens[1]):
                            latest_step = tokens
                            break
                        elif tokens[1].endswith('%'):
                            if latest_progress is None:
                                # keep going, don't break
                                latest_progress = tokens
                                continue
            if latest_step:
                # if we have a step %, up date the progress %
                if latest_progress:
                    latest_step[2] = latest_progress[1]

            res['percent_completed'] = latest_step[2][0:-1]
            res['current_zoom_level'] = latest_step[1]
            res['update_time'] = latest_step[0][1:-1]
            res['estimated_completion_time'] = latest_step[len(latest_step) - 1]
        else:
            res['status'] = 'in progress, but log not found'
    return res


# since thread has access to the applications memory space, use a thread to gather and setup info needed for the
# process that will do the seeding. Mapproxy will create child processes from the process we create here. The thread
# will wait for the process to complete. When process completes, the thread will update information about the tileset
def seed_thread(tileset):
    mapproxy_conf, seed_conf = generate_confs(tileset)

    # if there is an old _generating one around, back it up
    backup_millis = int(round(time.time() * 1000))
    if os.path.isfile(get_tileset_filename(tileset, 'generating')):
        os.rename(get_tileset_filename(tileset, 'generating'), '{}_{}'.format(get_tileset_filename(tileset, 'generating'), backup_millis))

    # if there is an old progress_log around, back it up
    if os.path.isfile(get_tileset_filename(tileset, 'progress_log')):
        os.rename(get_tileset_filename(tileset, 'progress_log'), '{}_{}'.format(get_tileset_filename(tileset, 'generating'), backup_millis))

    # generate the new mbtiles as name.generating file
    progress_log_filename = get_tileset_filename(tileset, 'progress_log')
    out = open(progress_log_filename, 'w+')
    progress_logger = util.ProgressLog(out=out, verbose=True, silent=False)
    tasks = seed_conf.seeds(['tileset_seed'])
    # launch the task using another process
    process = multiprocessing.Process(target=seed_process, args=(tileset, tasks, progress_logger, tasks_dict, tasks_lock))
    process.start()
    tasks_dict[tileset.id] = process.pid
    # thread will wait for process to complete (or terminate)
    process.join()
    # update the tileset object with teh actual size of the generated mbtile
    update_tileset_stats(tileset)


# use a process to do the actual seeding. This allows the app to terminate the seeding process which is not really
# possible with a thread. When a seeding is stopped by the user, the thread that created this process can still
# update the filesize of the tileset
def seed_process(tileset, tasks, progress_logger, tasks_dict, tasks_lock):
    print '----[ start seeding. tileset {}'.format(tileset.id)
    seeder.seed(tasks=tasks, progress_logger=progress_logger)

    # now that we have generated the new mbtiles file, backup the last one, then rename
    # the _generating one to the main name
    if os.path.isfile(get_tileset_filename(tileset)):
        millis = int(round(time.time() * 1000))
        os.rename(get_tileset_filename(tileset), '{}_{}'.format(get_tileset_filename(tileset), millis))
    os.rename(get_tileset_filename(tileset, 'generating'), get_tileset_filename(tileset))

    with tasks_lock:
        tasks_dict[tileset.id] = None
