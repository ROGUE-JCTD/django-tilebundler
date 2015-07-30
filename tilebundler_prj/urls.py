from django.conf.urls import patterns, include, url
from tilebundler.api import TilesetResource
from django.contrib import admin

admin.autodiscover()
tileset_resource = TilesetResource()

urlpatterns = patterns('',
    url(r'^tileset/', include('tilebundler.urls', namespace='tilesets')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(tileset_resource.urls)),
)