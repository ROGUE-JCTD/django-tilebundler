from django.db import models
from django.conf import settings
import psutil
import helpers


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
    layer_name = models.CharField(blank=True, max_length=200)
    layer_zoom_start = models.IntegerField(blank=True, default=0)
    layer_zoom_stop = models.IntegerField()

    # region
    geom = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    # terminate the seeding of this tileset!
    def stop(self):
        print '---- tileset.stop'
        res = {'status': 'not in progress'}
        pid = helpers.get_pid_from_lock_file(self.id)
        if pid:
            print '---- tileset.stop, will stop, pid: {}'.format(pid)
            res = {'status': 'stopped'}
            if pid != 'preparing_to_start':
                process = psutil.Process(pid=pid)
                if process:
                    children = process.children()
                    for c in children:
                        c.terminate()
                    process.terminate()
                    helpers.remove_lock_file(self.id)
            else:
                # TODO: prevent it from starting!
                res = {'status': 'debug, prevernted started!'}
        else:
            print '---- tileset.stop, will NOT stop. not running'

        return res

    # use the tileset object as input to start creation of the mbtiles
    def generate(self):
        print '---- tileset.generate'
        lock_file = helpers.get_lock_file(self.id)
        if lock_file:
            print '---- tileset.generate, will generate'
            pid = helpers.seed_process_spawn(self)
            lock_file.write("{}\n".format(pid))
            lock_file.flush()
            lock_file.close()
            res = {'status': 'started'}
        else:
            print '---- tileset.generate, will NOT generate. already running, pid: {}'.format(helpers.get_pid_from_lock_file(self.id))
            res = {'status': 'already started'}

        return res

    # TODO: the the log for the mbtiles being generated should be seperate from the log for the last successfully downloaded
    #       file.
    def status(self):
        return helpers.get_status(self)
