import sys

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup

from credentials import (
    SUBSCRIPTION_ID,
    CLIENT_ID,
    TEST_KEY,
    TENANT_ID,
)


def get_or_create_resource_group(resource_groups, group_name):
    # I'm guessing it's actually OK just to create_or_update the group
    # but I'll check for it explicitly for demonstration purposes.
    # if resource_groups.check_existence(group_name):
    #     return resource_groups.get(group_name)
    # else:
    print('Trying to create resource group {}...'.format(group_name))
    return resource_groups.create_or_update(
        group_name,
        ResourceGroup(
            location='westus',
        )
    )


def create_resource(credentials, group_name):
    resource_client = ResourceManagementClient(
        credentials,
        SUBSCRIPTION_ID,
    )

    resource_group = get_or_create_resource_group(
        resource_client.resource_groups,
        group_name,
    )

    print(resource_group)


def main():
    credentials = ServicePrincipalCredentials(
        client_id=CLIENT_ID,
        secret=TEST_KEY,
        tenant=TENANT_ID,
    )
    group_name = 'vm_monitoring'

    create_resource(credentials, group_name)


if __name__ == '__main__':
    sys.exit(main())
