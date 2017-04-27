import datetime
import os
import sys

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.monitor import MonitorClient

import pytz
import tzlocal

from flask import Flask

app = Flask(__name__)

app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update(dict(
    CLIENT_ID=os.environ['AZURE_CLIENT_ID'],
    CLIENT_SECRET=os.environ['AZURE_CLIENT_SECRET'],
    TENANT_ID=os.environ['AZURE_TENANT_ID'],
    SUBSCRIPTION_ID=os.environ['AZURE_SUBSCRIPTION_ID']
))
app.config.from_envvar('AZURE_VM_MONITOR_SETTINGS', silent=True)


class AzureMonitor(object):
    def __init__(self, subscription_id,
                 resource_group_name='azure-python-deployment-sample',
                 vm_name='azure-deployment-sample-vm'):
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.vm_name = vm_name
        self.resource_id = (
            "subscriptions/{}/"
            "resourceGroups/{}/"
            "providers/Microsoft.Compute/virtualMachines/{}"
        ).format(self.subscription_id, self.resource_group_name, self.vm_name)

        credentials = ServicePrincipalCredentials(
            client_id=app.config['CLIENT_ID'],
            secret=app.config['CLIENT_SECRET'],
            tenant=app.config['TENANT_ID'],
        )

        resource_client = ResourceManagementClient(credentials, self.subscription_id)
        resource_client.providers.register('Microsoft.Insights')

        self.client = MonitorClient(credentials, self.subscription_id)

    def show_metrics(self):
        # You can get the available metrics of this specific resource

        # Example of result for a VM:
        # Percentage CPU: id=Percentage CPU, unit=Unit.percent
        # Network In: id=Network In, unit=Unit.bytes
        # Network Out: id=Network Out, unit=Unit.bytes
        # Disk Read Bytes: id=Disk Read Bytes, unit=Unit.bytes
        # Disk Write Bytes: id=Disk Write Bytes, unit=Unit.bytes
        # Disk Read Operations/Sec: id=Disk Read Operations/Sec, unit=Unit.count_per_second
        # Disk Write Operations/Sec: id=Disk Write Operations/Sec, unit=Unit.count_per_second

        print('Available metrics for', self.subscription_id)
        for metric in self.client.metric_definitions.list(self.resource_id):
            # metric is an azure.monitor.models.MetricDefinition
            print("{}: id={}, unit={}".format(
                metric.name.localized_value,
                metric.name.value,
                metric.unit
            ))

    def get_metric_totals(self, metric_name='Network Out'):
        # Get a metric per hour for the last 24 hours.

        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        tz_now = utc_now.astimezone(tzlocal.get_localzone())
        end_of_this_hour = tz_now + datetime.timedelta(hours=1)
        end_time = end_of_this_hour.replace(minute=0, second=0, microsecond=0)
        start_time = end_time - datetime.timedelta(days=1)

        metric_filter = " and ".join([
            "name.value eq '{}'".format(metricName),
            "aggregationType eq 'Total'",
            "startTime eq {}".format(start_time.isoformat()),
            "endTime eq {}".format(end_time.isoformat()),
            "timeGrain eq duration'PT1H'",
        ])

        return self.client.metrics.list(
            self.resource_id,
            filter=metric_filter,
        )
    
    def show_metric_totals(metric_name='Network Out'):
        metrics_data = get_metric_totals(metric_name)

        print(start_time, '-', end_time)

        for item in metrics_data:
            # azure.monitor.models.Metric
            print("{} ({})".format(item.name.localized_value, item.unit.name))
            for data in item.data:
                # azure.monitor.models.MetricData
                print("{}: {}".format(data.time_stamp, data.total))


@app.route('/')
def display_metrics():
    monitor = AzureMonitor(app.config['SUBSCRIPTION_ID'])
    return render_template('show_metrics.html',
                           metrics=monitor.get_metric_totals())


if __name__ == '__main__':
    sys.exit(main())
