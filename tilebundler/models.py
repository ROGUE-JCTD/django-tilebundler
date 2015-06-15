from django.db import models
from django.conf import settings
from .helpers import generate_confs
from mapproxy.seed.seeder import seed
from mapproxy.seed.cleanup import cleanup
import json


class Tileset(models.Model):
    name = models.CharField(unique=True, max_length=30)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    ## server
    server_url = models.URLField()
    server_service_type = models.CharField(max_length=10)
    server_username = models.CharField(blank=True, max_length=30)
    server_password = models.CharField(blank=True, max_length=30)

    layer_name = models.CharField(unique=True, max_length=200)
    layer_zoom_start = models.IntegerField()
    layer_zoom_stop = models.IntegerField()

    geom = models.TextField()

    #models.FilePathField

    # TODO: add a map proxy layer here
    #layer = models.ForeignKey(Layer)

    def __unicode__(self):
        return self.name
        #return "name: {}, created_at: {}".format(self.name, self.created_at)

    def to_minimal_dict(self):
        fields = ['id', 'name', 'geom', 'layer_name', 'server_url', 'server_service_type']
        d = {}
        for attr in fields:
            d[attr] = getattr(self, attr)
        return d

    def to_json(self):
        return json.dumps(self.to_minimal_dict())

    def generate_tileset(self):
        mapproxy_conf, seed_conf = generate_confs(self)
        tasks = seed_conf.seeds(['osm_seed'])
        seed(tasks, dry_run=False)
        #cleanup(cleanup_tasks, verbose=False, dry_run=False)