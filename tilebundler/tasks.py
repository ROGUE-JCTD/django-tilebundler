from celery.task import task
from models import Tileset
#from helpers import seed_celery
from helpers import seed_process_db_connection


# logger = get_task_logger('joojoomesdaghi')
# from celery.utils.log import get_task_logger

#from celery.task.schedules import crontab
#from celery.decorators import periodic_task

# this will run every minute, see http://celeryproject.org/docs/reference/celery.task.schedules.html#celery.task.schedules.crontab
#@periodic_task(run_every=crontab(hour="*", minute="*", day_of_week="*"))
#def test():
#    print "firing test task"

#(name='tilebundler.tasks.add', track_started=True)
@task(name='tilebundler.tasks.add')
def add(tileset_id, x, y):
    print "xxxxxxxxxxxxxxxxxxxxxxxx tasks.add called. tileset_id: {}".format(tileset_id)
    #print '-------------- debug from host'; import sys; sys.stdout.flush()
    #import pdb; pdb.set_trace()
    tileset = Tileset.objects.get(id=tileset_id)
    res = x + y + tileset.id
    print "==================== msg: {}".format(res)
    return res

#(name='tilebundler.tasks.generate', track_started=True)
@task(name='tilebundler.tasks.generate')
def generate(tileset_id):
    print "xxxxxxxxxxxxxxxxxxxxxxxx tasks.generated called. tileset_id: {}".format(tileset_id)
    #temp hack, fix circular dependancy
    #import pdb; pdb.set_trace()

    ###tileset = Tileset.objects.get(id=tileset_id)
    ###seed_celery(tileset)

    seed_process_db_connection(tileset_id)

