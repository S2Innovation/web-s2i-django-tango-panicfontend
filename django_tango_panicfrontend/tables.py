import django_tables2 as tables
from django.utils.dateparse import parse_datetime
from django.urls import reverse
from django.utils.safestring import mark_safe


def history_row_class(record):
    if str(record['comment']).startswith('ALARM'):
        if str(record['alarm']['severity']) == 'ALARM':
            return 'danger'
        if str(record['alarm']['severity']) == 'WARNING':
            return 'warning'
        else:
            return 'info'

    if str(record['comment']).startswith('ACKNOWLEDGED: RESET'):
        return 'success'

    return 'warning'


class AlarmHistoryTable(tables.Table):
    """Table for presenting history of one alarm """
    # alarm = tables.Column(accessor=tables.A('alarm.tag'), verbose_name='Alarm')
    # severity = tables.Column(accessor=tables.A('alarm.severity'), verbose_name='Severity')
    date = tables.DateTimeColumn(verbose_name='Date/Time')
    event = tables.Column(verbose_name='Event', accessor=tables.A('comment'), orderable=False)

    def render_date(self, value, table):
        return str(parse_datetime(value)).split('+')[0]

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        sequence = ('date', 'event', )
        # attrs = {'class': 'table'}
        row_attrs = {
            'class': lambda record: history_row_class(record)
        }

class FullHistoryTable(AlarmHistoryTable):
    """This table is to present a full alarm history"""
    alarm = tables.Column(accessor=tables.A('alarm.tag'), verbose_name='Alarm')
    severity = tables.Column(accessor=tables.A('alarm.severity'), verbose_name='Severity')

    def render_alarm(self, value, table):
        return mark_safe('<a href="%s">%s</a>' % (reverse('alarm_details', args=[value]), value))

    class Meta:
        sequence = ('date', 'severity', 'alarm', 'event' )
        template_name = 'django_tables2/bootstrap.html'
        # attrs = {'class': 'table'}
        row_attrs = {
            'class': lambda record: history_row_class(record)
        }


def alarm_row_class(record):

    if record['state'] in ['UNACK','ERROR']:
        if record['severity'] in ['ALARM', 'ERROR']:
            return 'danger'
        elif record['severity'] in ['WARNING']:
            return 'warning'
        else:
            return 'info'

    if record['state'] in ['ACKED','RTNUN']:
        if record['severity'] in ['ALARM', 'ERROR']:
            return 'warning'
        else:
            return 'info'
    if record['state'] in ['NORM']:
        return 'success'

    return 'active'


class AlarmsTable(tables.Table):
    """This table is to present a full alarm history"""
    tag = tables.Column(accessor=tables.A('tag'), verbose_name='Alarm')
    severity = tables.Column(accessor=tables.A('severity'), verbose_name='Severity')
    state = tables.Column(accessor=tables.A('state'), verbose_name='State')
    activation_time = tables.Column(accessor=tables.A('activation_time'), verbose_name='Active since')
    description = tables.Column(accessor=tables.A('description'), verbose_name='Description')

    _active_alarms = []

    def get_top_pinned_data(self):
        return self._active_alarms

    def render_tag(self, value, table):
        return mark_safe('<a href="%s">%s</a>' % (reverse('alarm_details', args=[value]), value))

    def render_activation_time(self, value, table):
        if value is None or value == 'None':
            return '-'
        return str(parse_datetime(value)).split('+')[0]

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        sequence = ('tag', 'severity', 'state', 'activation_time', 'description')
        # attrs = {'class': 'table'}
        row_attrs = {
            'class': lambda record: alarm_row_class(record)
        }