# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django_tables2 import RequestConfig
import json
import requests


from models import AlarmsFrontendSettingsModel
from tables import AlarmHistoryTable, FullHistoryTable, AlarmsTable
# Create your views here.

app_settings = None


def get_app_settings():
    global app_settings
    if app_settings is not None:
        return app_settings

    if AlarmsFrontendSettingsModel.objects.count() > 0:
        app_settings = AlarmsFrontendSettingsModel.objects.last()
        app_settings.panicapi_url_base='http://localhost:8000/panicapi/'
        app_settings.save()
    else:
        app_settings = AlarmsFrontendSettingsModel()
        app_settings.save()

    return app_settings


def _url(path):
    return app_settings.panicapi_url_base + path


def alarms_history(request):

    get_app_settings()

    resp = requests.get(_url('history/?page_size='+str(5000)))
    # print resp.json()

    history_table = FullHistoryTable(resp.json()['results'])
    RequestConfig(request, paginate={'per_page': 20}).configure(history_table)

    return render(
        request,
        'history.html',
        {
            'history_table': history_table,
        }
    )

def alarms(request):

    get_app_settings()

    resp = requests.get(_url('alarms/?page_size='+str(5000)))
    # print resp.json()

    alarms_table = FullHistoryTable(resp.json()['results'])
    RequestConfig(request, paginate={'per_page': 20}).configure(alarms_table)

    return render(
        request,
        'list.html',
        {
            'alarms_table': alarms_table,
        }
    )

def alarm_details(request,tag):

    get_app_settings()

    resp = requests.get(_url('alarms/%s' % tag))

    alarm = resp.json()

    resp = requests.get(_url('history/?alarm__tag=%s' % tag))

    history_table = AlarmHistoryTable(resp.json()['results'])
    RequestConfig(request, paginate={'per_page':20}).configure(history_table)

    return  render(
        request,
        'details.html',
        {
            'alarm': alarm,
            'history_table': history_table,
        }
    )