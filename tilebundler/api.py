from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from django.conf.urls import url
from .models import Tileset
import helpers


class TilesetResource(ModelResource):

    class Meta:
        queryset = Tileset.objects.all()
        excludes = ['server_password']

    def determine_format(self, request):
        return 'application/json'

    def prepend_urls(self):
        """ Add the following array of urls to the Tileset base urls """
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/generate%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('generate'), name="api_tileset_generate"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/download%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('download'), name="api_tileset_download"),
        ]

    def generate(self, request, **kwargs):
        """ proxy for the tileset.generate method """

        # method check to avoid bad requests
        self.method_check(request, allowed=['get'])

        # create a basic bundle object for self.get_cached_obj_get.
        basic_bundle = self.build_bundle(request=request)

        # using the primary key defined in the url, obtain the tileset
        tileset = self.cached_obj_get(
            bundle=basic_bundle,
            **self.remove_api_resource_names(kwargs))

        # Return what the method output, tastypie will handle the serialization
        return self.create_response(request, tileset.generate())

    def download(self, request, **kwargs):
        """ proxy for the helpers.tileset_download method """

        # method check to avoid bad requests
        self.method_check(request, allowed=['get'])

        # create a basic bundle object for self.get_cached_obj_get.
        basic_bundle = self.build_bundle(request=request)

        # using the primary key defined in the url, obtain the tileset
        tileset = self.cached_obj_get(
            bundle=basic_bundle,
            **self.remove_api_resource_names(kwargs))

        return helpers.tileset_download(request, tileset)
