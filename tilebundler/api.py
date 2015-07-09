from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.utils import trailing_slash
from django.conf.urls import url
from django.views.static import serve
from .models import Tileset
from tastypie import fields
from django.contrib.auth import get_user_model
import helpers
import os


class UserResource(ModelResource):
    class Meta:
        queryset = get_user_model().objects.all()
        fields = ['username', 'first_name', 'last_name']
        resource_name = 'created_by'


class TilesetResource(ModelResource):
    created_by = fields.ToOneField(UserResource, 'created_by',  full=True)

    class Meta:
        queryset = Tileset.objects.all()
        excludes = ['server_password']
        authentication = BasicAuthentication()

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
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/status%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('status'), name="api_tileset_status"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/stop%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('stop'), name="api_tileset_stop"),
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

        filename = helpers.get_tileset_filename(tileset)
        filename = os.path.abspath(filename)
        if os.path.isfile(filename):
            response = serve(request, os.path.basename(filename), os.path.dirname(filename))
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(filename))
        else:
            response = self.create_response(request, {'status': 'not generated'})
        return response

    def status(self, request, **kwargs):
        """ proxy for the helpers.tileset_download method """

        # method check to avoid bad requests
        self.method_check(request, allowed=['get'])

        # create a basic bundle object for self.get_cached_obj_get.
        basic_bundle = self.build_bundle(request=request)

        # using the primary key defined in the url, obtain the tileset
        tileset = self.cached_obj_get(
            bundle=basic_bundle,
            **self.remove_api_resource_names(kwargs))

        return self.create_response(request, tileset.status())

    def stop(self, request, **kwargs):
        """ proxy for the helpers.tileset_download method """

        # method check to avoid bad requests
        self.method_check(request, allowed=['get'])

        # create a basic bundle object for self.get_cached_obj_get.
        basic_bundle = self.build_bundle(request=request)

        # using the primary key defined in the url, obtain the tileset
        tileset = self.cached_obj_get(
            bundle=basic_bundle,
            **self.remove_api_resource_names(kwargs))

        return self.create_response(request, tileset.stop())
