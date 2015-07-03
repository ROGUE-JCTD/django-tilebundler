from django.db import models
from django.conf import settings
import helpers
import os
import time

from mapproxy.seed.seeder import seed
import json


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

    def generate(self):
        mapproxy_conf, seed_conf = helpers.generate_confs(self)

        # TODO: if a tile set is actually being generated, do not regenerate it.
        # TODO: and force user to cancel it job and then start another one
        # if there is an old _generating one around, back it up
        if os.path.isfile(helpers.get_tileset_filename(self, True)):
            millis = int(round(time.time() * 1000))
            print 'wwww',  helpers.get_tileset_filename(self, True)
            print 'xxx', '{}_{}'.format(millis, helpers.get_tileset_filename(self, True))
            os.rename(helpers.get_tileset_filename(self, True), '{}_{}'.format(helpers.get_tileset_filename(self, True), millis))

        # generate the cache
        tasks = seed_conf.seeds(['tileset_seed'])
        seed(tasks, dry_run=False)

        # back up the last one, renamed the _generating one to the main name
        if os.path.isfile(helpers.get_tileset_filename(self)):
            millis = int(round(time.time() * 1000))
            os.rename(helpers.get_tileset_filename(self), '{}_{}'.format(helpers.get_tileset_filename(self), millis))

        os.rename(helpers.get_tileset_filename(self, True), helpers.get_tileset_filename(self))
        helpers.update_tileset_stats(self)
        return 'completed. filesize: {}, created_at: {}'.format(self.filesize, self.created_at)

