from celery.task import task
from celery.utils.log import get_task_logger

import helpers

logger = get_task_logger('joojoomesdaghi')

#(name='tilebundler.tasks.add', track_started=True)
@task(name='tilebundler.tasks.add')
def add(tileset_id, x, y):
    print "yyyyyyyyyyyyyyyyyyyyyyy add tileset_id: {}".format(tileset_id)
    #print '-------------- debug from host'; import sys; sys.stdout.flush()
    #import pdb; pdb.set_trace()
    from models import Tileset
    tileset = Tileset.objects.get(id=tileset_id)
    res = x + y + tileset.id
    print "==================== msg: {}".format(res)
    return res

#(name='tilebundler.tasks.generate', track_started=True)
@task(name='tilebundler.tasks.generate')
def generate(tileset_id):
    print "xxxxxxxxxxxxxxxxxxxxxxxx generate tileset_id: {}".format(tileset_id)
    #temp hack, fix circular dependancy
    #import pdb; pdb.set_trace()
    from models import Tileset
    tileset = Tileset.objects.get(id=tileset_id)
    helpers.seed_task(tileset)

