import os
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.http import HttpResponse
from django.views.static import serve
import json

from .models import Tileset
import time


class IndexView(generic.ListView):
    template_name = 'tilesets/index.html'

    def get_queryset(self):
        return Tileset.objects.order_by('-created_at')[:5]


#TODO: use as part of index view
def json_view_all(request):
    objects = []
    for obj in Tileset.objects.all():
        objects.append(obj.to_minimal_dict())
    return HttpResponse(json.dumps(objects), content_type='json')


def json_view(request, tileset_id):
    tileset = get_object_or_404(Tileset, pk=tileset_id)
    return HttpResponse(tileset.to_json(), content_type='json')


#TODO: serve through nginx instead
#TODO: use as part of detail view
def download_view(request, tileset_id):
    tileset = get_object_or_404(Tileset, pk=tileset_id)
    file_path = '{}/{}.{}'.format('./cache_data', tileset.name, 'mbtiles')
    file_path = os.path.abspath(file_path)
    response = serve(request, os.path.basename(file_path), os.path.dirname(file_path))
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(file_path))
    return response


class DetailView(generic.DetailView):
    model = Tileset
    template_name = 'tilesets/detail.html'


class ResultsView(generic.DetailView):
    model = Tileset
    template_name = 'tilesets/results.html'


def generate(request, tileset_id):
    tileset = get_object_or_404(Tileset, pk=tileset_id)
    try:
        print 'generate(), tileset: ', tileset
        print 'created_at: ', int(time.mktime(tileset.created_at.timetuple())*1000)
        print 'created_by: ', tileset.created_by
        tileset.generate_tileset()
    except Exception:
        return render(request, 'tilesets/detail.html', {
            'tileset': tileset,
            'error_message': 'Name must be unique',
        })
    else:

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('tilesets:results', args=(tileset_id,)))
