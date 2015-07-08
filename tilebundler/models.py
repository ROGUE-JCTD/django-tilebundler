from django.db import models
from django.conf import settings
from mapproxy.seed import seeder
from mapproxy.seed import util
import multiprocessing
import helpers
import os
import time
import json
import psutil

class Tileset(models.Model):

    # base
    name = models.CharField(unique=True, max_length=30)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # server
    server_url = models.URLField()
    server_service_type = models.CharField(max_length=10)
    server_username = models.CharField(blank=True, max_length=30)
    server_password = models.CharField(blank=True, max_length=30)

    # layer
    layer_name = models.CharField(unique=True, max_length=200)
    layer_zoom_start = models.IntegerField(blank=True, default=0)
    layer_zoom_stop = models.IntegerField()

    # region
    geom = models.TextField(blank=True)

    filesize = models.BigIntegerField(editable=False, default=0)

    def __unicode__(self):
        return self.name

    def to_minimal_dict(self):
        fields = ['id', 'name', 'geom', 'layer_name', 'server_url', 'server_service_type']
        d = {}
        for attr in fields:
            d[attr] = getattr(self, attr)
        return d

    def to_json(self):
        return json.dumps(self.to_minimal_dict())

    def stop(self):
        res = {"status": "not found"}
        with helpers.tasks_lock:
            pid = helpers.tasks_dict.get(self.id, None)
            if pid:
                process = psutil.Process(pid=pid)
                if process:
                    children = process.children()
                    for c in children:
                        c.terminate()
                    process.terminate()
                    helpers.tasks_dict[self.id] = None
                    res = {"status": "terminated"}
        return res

    def generate(self):
        res = ""
        with helpers.tasks_lock:
            pid = helpers.tasks_dict.get(self.id, None)
            if not pid:
                mapproxy_conf, seed_conf = helpers.generate_confs(self)

                # if there is an old _generating one around, back it up
                backup_millis = int(round(time.time() * 1000))
                if os.path.isfile(helpers.get_tileset_filename(self, "generating")):
                    os.rename(helpers.get_tileset_filename(self, "generating"), '{}_{}'.format(helpers.get_tileset_filename(self, "generating"), backup_millis))

                # if there is an old progress_log around, back it up
                if os.path.isfile(helpers.get_tileset_filename(self, "progress_log")):
                    os.rename(helpers.get_tileset_filename(self, "progress_log"), '{}_{}'.format(helpers.get_tileset_filename(self, "generating"), backup_millis))

                # generate the new mbtiles as name.generating file
                progress_log_filename = helpers.get_tileset_filename(self, "progress_log")
                out = open(progress_log_filename, 'w+')
                progress_logger = util.ProgressLog(out=out, verbose=True, silent=False)
                tasks = seed_conf.seeds(['tileset_seed'])
                # launch the task using another process
                process = multiprocessing.Process(target=Tileset.seed_, args=(self, tasks, progress_logger, helpers.tasks_dict, helpers.tasks_lock))
                process.start()
                helpers.tasks_dict[self.id] = process.pid
                res = {"status": "started"}
            else:
                res = {"status": "running"}
        return res

    @staticmethod
    def seed_(tileset, tasks, progress_logger, tasks_dict, tasks_lock):
        process = psutil.Process(pid=os.getpid())
        print '----[ start seeding. tileset {}'.format(tileset.id)
        seeder.seed(tasks=tasks, dry_run=False, progress_logger=progress_logger)

        # now that we have generated the new mbtiles file, backup the last one, then rename
        # the _generating one to the main name
        if os.path.isfile(helpers.get_tileset_filename(tileset)):
            millis = int(round(time.time() * 1000))
            os.rename(helpers.get_tileset_filename(tileset), '{}_{}'.format(helpers.get_tileset_filename(tileset), millis))
        os.rename(helpers.get_tileset_filename(tileset, "generating"), helpers.get_tileset_filename(tileset))

        #TODO: add update back!
        ###helpers.update_tileset_stats(tileset)
        with tasks_lock:
            tasks_dict[tileset.id] = None

    def get_progress(self):
        progress_log_filename = helpers.get_tileset_filename(self, "progress_log")
        res = {"status": "progress not found"}
        if os.path.isfile(progress_log_filename):
            with open(progress_log_filename, 'r') as f:
                lines = f.read().replace('\r', '\n')
                lines = lines.split('\n')

            # an actual progress step update which looks like:
            #   "[15:11:11]  4  50.00% 0.00000, 672645.84891, 18432942.24503, 18831637.78456 (112 tiles) ETA: 2015-07-07-15:11:12"\n
            latest_step = None
            # a progress update on the current step which looks like:
            #    "[15:11:16]  87.50%	0000                 ETA: 2015-07-07-15:11:17"\r
            latest_progress = None
            if len(lines) > 0:
                for line in lines[::-1]:
                    tokens = line.split()
                    if len(tokens) > 2:
                        if helpers.is_int_str(tokens[1]):
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

                status = "running"
                if latest_step[2][0:-1] == "100.00" and latest_step[1] == "0":
                    status = "completed"

                res = {
                    "status": status,
                }

                if status != "completed":
                    res["percent_completed"] = latest_step[2]
                    res["current_zoom_level"] = latest_step[1]
                    res["update_time"] = latest_step[0][1:-1]
                    res["estimated_completion_time"] = latest_step[len(latest_step) - 1]
        return res
