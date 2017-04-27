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
            client_id=os.environ['AZURE_CLIENT_ID'],
            secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant=os.environ['AZURE_TENANT_ID'],
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

    def show_metric_totals(self):
        # Get CPU total of yesterday for this VM, by hour

        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        tz_now = utc_now.astimezone(tzlocal.get_localzone())
        end_of_this_hour = tz_now + datetime.timedelta(hours=1)
        end_time = end_of_this_hour.replace(minute=0, second=0, microsecond=0)
        start_time = end_time - datetime.timedelta(days=1)

        metric_filter = " and ".join([
            "name.value eq 'Network Out'",
            "aggregationType eq 'Total'",
            "startTime eq {}".format(start_time.isoformat()),
            "endTime eq {}".format(end_time.isoformat()),
            "timeGrain eq duration'PT1H'"
        ])

        metrics_data = self.client.metrics.list(
            self.resource_id,
            filter=metric_filter
        )

        print(start_time, '-', end_time)

        for item in metrics_data:
            # azure.monitor.models.Metric
            print("{} ({})".format(item.name.localized_value, item.unit.name))
            for data in item.data:
                # azure.monitor.models.MetricData
                print("{}: {}".format(data.time_stamp, data.total))


def main():
    monitor = AzureMonitor(os.environ['AZURE_SUBSCRIPTION_ID'])
    monitor.show_metrics()
    monitor.show_metric_totals()


if __name__ == '__main__':
    sys.exit(main())
