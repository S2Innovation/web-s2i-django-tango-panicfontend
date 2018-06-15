# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import AlarmsFrontendSettingsModel, AlarmsGroups

# Register your models here.
@admin.register( AlarmsFrontendSettingsModel, AlarmsGroups)
class AlarmsFrontendAdminPanel(admin.ModelAdmin):
    pass
