from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^(?P<tileset_id>\d+)/download', views.download_view, name='download_view'),
    url(r'^(?P<tileset_id>\d+)/json', views.json_view, name='json_view'),
    url(r'^json', views.json_view_all, name='json_view_all'),
    #url(r'^tilesets.json', views.json_view, name='json_view'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),
    url(r'^(?P<tileset_id>\d+)/update/$', views.generate, name='generate')
)
