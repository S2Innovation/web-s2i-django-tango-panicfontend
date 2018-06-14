import django_tables2 as tables
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from django.utils.safestring import mark_safe


class AlarmHistoryTable(tables.Table):
    """Table for presenting history of one alarm """
    # alarm = tables.Column(accessor=tables.A('alarm.tag'), verbose_name='Alarm')
    # severity = tables.Column(accessor=tables.A('alarm.severity'), verbose_name='Severity')
    date = tables.DateTimeColumn(verbose_name='Date/Time')
    event = tables.Column(verbose_name='Event', accessor=tables.A('comment'), orderable=False)

    def render_date(self, value, table):
        return str(parse_datetime(value)).split('+')[0]

    class Meta:
        sequence = ('date', 'event', )

class FullHistoryTable(AlarmHistoryTable):
    """This table is to present a full alarm history"""
    alarm = tables.Column(accessor=tables.A('alarm.tag'), verbose_name='Alarm')
    severity = tables.Column(accessor=tables.A('alarm.severity'), verbose_name='Severity')

    def render_alarm(self, value, table):
        return mark_safe('<a href="%s">%s</a>' % (reverse('alarm_details', args=[value]), value))

    class Meta:
        sequence = ('date', 'severity', 'alarm', 'event' )


def alarm_row_class(record):
    ret = str(record['severity']).lower()
    if record['is_active']:
        ret += ' active'
    return ret


class AlarmsTable(tables.Table):
    """This table is to present a full alarm history"""
    tag = tables.Column(accessor=tables.A('tag'), verbose_name='Alarm')

    def render_alarm(self, value, table):
        return mark_safe('<a href="%s">%s</a>' % (reverse('alarm_details', args=[value]), value))

    class Meta:
        sequence = ('date', 'severity', 'alarm', 'event')
        row_attrs = {
            'class': lambda record: alarm_row_class(record)
        }