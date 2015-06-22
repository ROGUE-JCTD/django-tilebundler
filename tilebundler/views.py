from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from .models import Tileset
import time


class IndexView(generic.ListView):
    template_name = 'tilesets/index.html'

    def get_queryset(self):
        return Tileset.objects.order_by('-created_at')[:5]


class DetailView(generic.DetailView):
    model = Tileset
    template_name = 'tilesets/detail.html'


class ResultsView(generic.DetailView):
    model = Tileset
    template_name = 'tilesets/results.html'


def generate(request, tileset_id):
    tileset = get_object_or_404(Tileset, pk=tileset_id)
    print 'generate(), tileset: ', tileset
    print 'created_at: ', int(time.mktime(tileset.created_at.timetuple())*1000)
    print 'created_by: ', tileset.created_by
    tileset.generate()
    return HttpResponseRedirect(reverse('tilesets:results', args=(tileset_id,)))
