from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^history', views.alarms_history, name='history'),
    url(r'^alarms', views.alarms, name='alarms'),
    url(r'^alarm/(?P<tag>\w+)/$', views.alarm_details, name='alarm_details')
]