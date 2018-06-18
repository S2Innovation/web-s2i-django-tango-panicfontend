# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django_tables2 import RequestConfig
from django.urls import reverse
from django.utils import timezone
import json
import requests


from models import AlarmsFrontendSettingsModel, AlarmsGroups
from tables import AlarmHistoryTable, FullHistoryTable, AlarmsTable
# Create your views here.

app_settings = None

resp_cache = {}

def json_result(url):
    global resp_cache
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            resp_cache[url] = resp.json()
            return resp.json()
        else:
            return resp_cache.get(url, {})
        # print resp.json()
    except:
        return resp_cache.get(url,{})

def get_app_settings():
    global app_settings
    if app_settings is not None:
        return app_settings

    if AlarmsFrontendSettingsModel.objects.count() > 0:
        app_settings = AlarmsFrontendSettingsModel.objects.last()
        # app_settings.panicapi_url_base='http://localhost:8000/panicapi/'
        # app_settings.save()
    else:
        app_settings = AlarmsFrontendSettingsModel()
        app_settings.save()

    return app_settings


def _url(path):
    return app_settings.panicapi_url_base + path


def prepare_groups(grouping, prefix="alarms/?"):
    """prepare groups"""

    groups = []

    get_app_settings()

    for group in AlarmsGroups.objects.filter(grouping=grouping):
        assert isinstance(group, AlarmsGroups)

        resp = json_result(_url('alarms/?'+group.query))

        alarms = resp.get('results', [])

        prefix_with_group = prefix + '&group=' + group.group + '&grouping=' + group.grouping + '&'

        unacks = [a for a in alarms if a['state'] in ['UNACK','ERROR'] ]

        if len(unacks)>0:
            if any([a['severity'] in ['ALARM', 'ERROR'] for a in unacks]):
                groups.append({
                    'cls': 'btn-danger',
                    'name': group.group,
                    'href': prefix_with_group + group.query
                })
            elif any([a['severity'] in ['WARNING'] for a in unacks]):
                groups.append({
                    'cls': 'btn-warning',
                    'name': group.group,
                    'href': prefix_with_group + group.query
                })
            else:
                groups.append({
                    'cls': 'btn-info',
                    'name': group.group,
                    'href': prefix_with_group + group.query
                })
            continue

        acks = [a for a in alarms if a['state'] in ['ACKED', 'RTNUN']]

        if len(acks) > 0:
            if any([ a['severity'] in ['WARNING','ALARM','ERROR'] for a in acks]):
                groups.append({
                    'cls': 'btn-warning',
                    'name': group.group,
                    'href': prefix_with_group + group.query
                })
            else:
                groups.append({
                    'cls': 'btn-info',
                    'name': group.group,
                    'href': _url(prefix_with_group + group.query)
                })
            continue

        groups.append({
            'cls': 'btn-success',
            'name': group.group,
            'href': prefix_with_group + group.query
        })
    return groups


def alarms_history(request):

    get_app_settings()

    groups = prepare_groups('history', prefix=str(reverse('history'))+'/?')

    additional_query = ''
    for k in request.GET.keys():
        if str(k).startswith('tag') or str(k).startswith('severity'):
            additional_query += '&alarm__'+k+'='+request.GET[k]
        elif k not in ['page', 'per_page', 'page_size', 'sort', 'order', 'sort_by', 'order_by', 'group', 'grouping']:
            additional_query += '&'+str(k) + '=' + request.GET[k]
    try:
        resp = requests.get(_url('sync'))
    except:
        pass

    resp = json_result(_url('history/?page_size='+str(5000)+additional_query))
    history_table = FullHistoryTable(resp.get('results',[]))

    RequestConfig(request, paginate={'per_page': 20}).configure(history_table)

    if request.is_ajax():
        templ = 'inc/history_content.html'
    else:
        templ = 'history.html'

    return render(
        request,
        templ,
        {
            'history_table': history_table,
            'groups': groups,
            'selected_group': request.GET.get('group', ''),
            'clock': timezone.now(),
        }
    )


def alarms(request):

    get_app_settings()

    groups = prepare_groups(request.GET.get('grouping','alarms'), prefix=str(reverse('alarms')) + '/?')

    additional_query = ''
    for k in request.GET.keys():
        if k not in ['page', 'per_page', 'page_size', 'sort', 'order', 'sort_by', 'order_by', 'group', 'grouping']:
            additional_query += '&' + str(k) + '=' + request.GET[k]

    try:
        resp = requests.get(_url('sync'))
    except:
        pass

    resp = json_result(_url('alarms/?page_size='+str(5000)+additional_query))

    alarms_result = resp.get('results',[])

    active_alarms = [a for a in alarms_result if a['state'] in ['UNACK','RTNUN','ACKED','ERROR']]

    if 'sort' in request.GET.keys():
        key = request.GET['sort']
        rev = False
        if key.startswith('-'):
            key = key[1:]
            rev = True
        active_alarms_sorted = sorted(active_alarms, key=lambda k: k[key], reverse=rev)
    else:
        active_alarms_sorted = active_alarms

    active_alarms_table = AlarmsTable(active_alarms_sorted)

    nonactive_alarms = [a for a in alarms_result if a['state'] not in ['UNACK','RTNUN','ACKED','ERROR']]

    alarms_table = AlarmsTable(nonactive_alarms)
    RequestConfig(request, paginate={'per_page': 20}).configure(alarms_table)

    if request.is_ajax():
        templ = 'inc/alarms_content.html'
    else:
        templ = 'list.html'

    return render(
        request,
        templ,
        {
            'alarms_table': alarms_table,
            'active_alarms_table': active_alarms_table,
            'groups': groups,
            'selected_group': request.GET.get('group', ''),
            'clock': timezone.now(),
        }
    )

def alarm_details(request,tag):

    get_app_settings()

    try:
        resp = requests.get(_url('sync'))
    except:
        pass

    resp = json_result(_url('alarms/%s' % tag))

    alarm = resp

    resp = requests.get(_url('history/?alarm__tag=%s' % tag))

    history_table = AlarmHistoryTable(resp.json()['results'])
    RequestConfig(request, paginate={'per_page':20}).configure(history_table)

    if request.is_ajax():
        templ = 'inc/details_content.html'
    else:
        templ = 'details.html'

    return render(
        request,
        templ,
        {
            'alarm': alarm,
            'history_table': history_table,
            'clock': timezone.now(),
        }
    )

def alarms_group(request, group_name):
    pass

def alarms_groups(request, group_name):
    pass
