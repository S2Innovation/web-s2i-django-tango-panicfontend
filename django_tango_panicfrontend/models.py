# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class AlarmsFrontendSettingsModel(models.Model):
    """Model to keep settings for the application"""
    panicapi_url_base = models.URLField(
        default='http://localhost:8000/panicapi',
        verbose_name='PANIC REST api URL',
    )
    # items_limit = models.IntegerField(
    #     default=10000,
    #     verbose_name='Items limit in REST responses'
    # )


class AlarmsGroups(models.Model):
    grouping = models.CharField(max_length=32, verbose_name='Grouping shema')
    group = models.CharField(max_length=32, verbose_name='Group name')
    description = models.TextField(verbose_name='Description', default='', blank=True)
    query = models.CharField(max_length=255, verbose_name='URL query')

    def __str__(self):
        return "%s -> %s" % (self.grouping, self.group)