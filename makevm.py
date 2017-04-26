import json
import sys

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.resource.resources.models import (
    ResourceGroup,
    Deployment,
    DeploymentProperties,
    DeploymentMode,
    ParametersLink,
    TemplateLink
)

from credentials import (
    SUBSCRIPTION_ID,
    CLIENT_ID,
    TEST_KEY,
    TENANT_ID,
)

VM_DEPLOYMENT_PROPERTIES_FILE = 'vm_template.json'


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


def create_resource_group(resource_client, group_name):
    resource_group = get_or_create_resource_group(
        resource_client.resource_groups,
        group_name,
    )

    print(resource_group)


def create_vm(resource_client, group_name, deployment_name, template):
    deployment_name = 'MyDeployment'

    template = TemplateLink(
        uri='https://github.com/azure-samples/resource-manager-python-template-deployment/blob/master/templates/template.json'
    )

    parameters = ParametersLink(
        uri='https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/101-create-availability-set/azuredeploy.parameters.json',
    )

    result = resource_client.deployments.create_or_update(
        group_name,
        deployment_name,
        properties=DeploymentProperties(
            mode=DeploymentMode.incremental,
            template_link=template,
            parameters_link=parameters,
        )
    )


def main():
    credentials = ServicePrincipalCredentials(
        client_id=CLIENT_ID,
        secret=TEST_KEY,
        tenant=TENANT_ID,
    )
    group_name = 'vm_monitoring'

    resource_client = ResourceManagementClient(
        credentials,
        SUBSCRIPTION_ID,
    )

    # create_resource_group(resource_client, group_name)

    create_vm(
        resource_client,
        json.load(VM_DEPLOYMENT_PROPERTIES_FILE),
        group_name,
    )


if __name__ == '__main__':
    sys.exit(main())
