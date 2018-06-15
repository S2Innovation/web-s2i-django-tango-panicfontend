from django.conf.urls import url, include
from . import views

urlpatterns = [

    url(r'^history', views.alarms_history, name='history'),
    url(r'^alarms', views.alarms, name='alarms'),
    url(r'^alarm/(?P<tag>\w+)/$', views.alarm_details, name='alarm_details'),
    url(r'^group/(?P<grouping>\w+)/(?P<group>\w+)', views.alarms_group, name='alarms_group'),
    url(r'^groups/(?P<grouping>\w+)', views.alarms_groups, name='alarms_groups'),
    url(r'', views.alarms, name='index'),
]