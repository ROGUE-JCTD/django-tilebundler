# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tileset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('server_url', models.URLField()),
                ('server_service_type', models.CharField(max_length=10)),
                ('server_username', models.CharField(max_length=30, blank=True)),
                ('server_password', models.CharField(max_length=30, blank=True)),
                ('layer_name', models.CharField(max_length=200, blank=True)),
                ('layer_zoom_start', models.IntegerField(default=0, blank=True)),
                ('layer_zoom_stop', models.IntegerField()),
                ('geom', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
