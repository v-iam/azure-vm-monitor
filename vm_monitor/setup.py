from setuptools import setup

setup(
    name='vm_monitor',
    packages=['vm_monitor'],
    include_package_data=True,
    install_requires=[
        'flask',
        'azure>=2.0.0rc6',
        'azure-mgmt-compute>=0.30.0rc6',
        'azure-mgmt-network>=1.0.0rc1',
        'pytz',
        'tzlocal',
    ],
)